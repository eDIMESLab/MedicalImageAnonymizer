#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: Although Windows supports chmod(), you can only set the file’s
# read-only flag with it (via the stat.S_IWRITE and stat.S_IREAD constants
# or a corresponding integer value). All other bits are ignored.
import stat

import os
import hashlib
import paramiko
from contextlib import contextmanager

from plumbum import cli
from plumbum.path import Path
from plumbum import local
from plumbum.path.utils import delete
from plumbum.machines.paramiko_machine import ParamikoMachine


__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampieri@unibo.it', 'nico.curti2@unibo.it']



read_only = (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
read_write = (stat.S_IRUSR |
              stat.S_IWUSR |
              stat.S_IRGRP |
              stat.S_IWGRP |
              stat.S_IROTH)


def get_sha1 (filepath):
  """
  calculate the sha1 hash of the content of a given file

  Parameters
  ----------
  filepath : path
    the file of which to calculate the hash.

  Returns
  -------
  hash: str
    the hash of the content of the file.

  """
  sha1sum = hashlib.sha1()

  with open(filepath, 'rb') as source:
    block = source.read(2**16)

    while len(block) != 0:
      sha1sum.update(block)
      block = source.read(2**16)

  return sha1sum.hexdigest()

@contextmanager
def get_destination_local (params, remote_config):
  """
  generate a context manager with the remote connection to the server

  Parameters
  ----------
  params : dict
    parameters of the connection host

  remote_config : dict
    parameters of the remote server

  Yields
  ------
  rem : RemoteConnection
      the actul connection to the remote server.

  todo : path
      the (remote) directory where to write the files in the pushin.

  done : path
      the (remote) directory where to search for the completed results.

  """
  with ParamikoMachine(**params, missing_host_policy=paramiko.AutoAddPolicy()) as rem:

    with rem.cwd(remote_config['base_dir']):

      todo = rem.cwd/remote_config['todo_subdir']
      done = rem.cwd/remote_config['done_subdir']

      yield rem, todo, done

def query_single_file (filename, params, remote):
  '''
  given a filepath, check all the files on the remote server whose
  names contains the hash of the original one.

  Parameters
  ----------
  filepath : path
    filepath (with full locatable path) to search for in the server

  params : dict
    parameters of the connection host

  remote_config : dict
    parameters of the remote server

  Returns
  -------
  origin_hash : str
    the hash of the original file (calculated on the content)

  exists : list of paths
    all the files on the server whose name contains the hash of the
    original file. The list is empty if no files are found

  '''

  with get_destination_local(params, remote) as (rem, todo, done):

    origin = filename
    origin_hash = get_sha1(origin)
    source = done/origin_hash
    find_hash = lambda p : origin_hash in str(p)

    paths = list(done.walk(filter=find_hash))


def push_single_file (filepath, params, remote_config):
  """
  upload a file to the server while changing its name

  Parameters
  ----------
  filepath : path
    the file to upload to the server.

  params : dict
    parameters of the connection host

  remote_config : dict
    parameters of the remote server

  Raises
  ------
  FileExistsError
    if the file that would be generated already exists.

  Returns
  -------
  destination : path
    the location in which it has been copied on the server.

  """
  with get_destination_local(params, remote_config) as (rem, todo, done):

    origin = filepath
    origin_hash = get_sha1(origin)
    destination = todo/origin_hash
    destination = destination.with_suffix(os.path.splitext(str(origin))[-1])
    destination = Path(destination)

    if not destination.exists():
      rem.upload(origin, destination)

    else:
      s = "{} has already been pushed".format(filepath)
      raise FileExistsError(s)

    if False:
      origin.chmod(read_only)

  return destination

def pull_single_file (filepath, destination_dir, params, remote_config):
  """

  Parameters
  ----------
  filepath : plumbum path object
    origin file to pull from the server

  destination_dir : plumbum path object
    the directory in which to copy the files

  params : dict
    parameters of the connection host

  remote_config : dict
    parameters of the remote server

  Returns
  -------
  pulled_file: List[path]
    the list of filepaths downloaded from the server
    (after name-swapping the hash)

  """
  pulled_file = []

  with get_destination_local(params, remote_config) as (rem, todo, done):

    origin_hash, paths = query_single_file(filepath, params, remote_config)

    for path in paths:
      # this operation is necessary because the path keeps track
      # of the identity of the machine and not just of the data
      # so given that it was created in a different context manager
      # it freaks out even if it's not needed
      path.remote = rem
      # the name and extension might be changed, so replace only the hash part
      dest_name = path.name.replace(origin_hash, filepath.stem)
      destination = destination_dir/dest_name
      rem.download(path, destination)
      pulled_file.append(destination)

  return pulled_file
