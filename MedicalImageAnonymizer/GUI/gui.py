#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob
from collections import Counter

from tkinter import Tk, Frame, IntVar, BooleanVar
from tkinter import Button, Radiobutton, messagebox, scrolledtext, INSERT, END, Checkbutton
from tkinter.filedialog import askdirectory, askopenfilename

from MedicalImageAnonymizer.DICOM_anonymizer import DICOMAnonymize
from MedicalImageAnonymizer.Nifti_anonymizer import NiftiAnonymize
from MedicalImageAnonymizer.SVS_anonymizer import SVSAnonymize

from configparser import ConfigParser

from plumbum import cli
from plumbum.path import Path
from plumbum import local
from plumbum.path.utils import delete
from plumbum.machines.paramiko_machine import ParamikoMachine

from contextlib import contextmanager
import hashlib

# Note: Although Windows supports chmod(), you can only set the file’s
# read-only flag with it (via the stat.S_IWRITE and stat.S_IREAD constants
# or a corresponding integer value). All other bits are ignored.
import stat
read_only = (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
read_write = (stat.S_IRUSR |
              stat.S_IWUSR |
              stat.S_IRGRP |
              stat.S_IWGRP |
              stat.S_IROTH)

parser = ConfigParser()

__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampieri@unibo.it', 'nico.curti2@unibo.it']


def get_sha1(filepath):
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
def get_destination_local(params, remote_config):
  """
  generate a context manager with the remote connection to the server

  Yields
  ------
  rem : RemoteConnection
      the actul connection to the remote server.
  todo : path
      the (remote) directory where to write the files in the pushin.
  done : path
      the (remote) directory where to search for the completed results.

  """
  with ParamikoMachine(**params) as rem:
    with rem.cwd(remote_config['base_dir']):
      todo = rem.cwd/remote_config['todo_subdir']
      done = rem.cwd/remote_config['done_subdir']
      yield rem, todo, done

# %%

def push_single_file(filepath, params, remote_config, log):
  """
  upload a file to the server while changing its name

  Parameters
  ----------
  filepath : path
      the file to upload to the server.

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
      log.insert(INSERT, '[INFO] file pushed with success\n')
    else:
      log.insert(INSERT, '[WARNING] file not pushed, already existing\n')
      s = "{} has already been pushed".format(filepath)
      raise FileExistsError(s)
    if False:
      origin.chmod(read_only)
  return destination

def query_single_file(filepath, params, remote_config):
  """
  given a filepath, check all the files on the remote server whose
  names contains the hash of the original one.

  Parameters
  ----------
  filepath : path
      filepath (with full locatable path) to search for in the server

  Returns
  -------
  origin_hash : str
      the hash of the original file (calculated on the content)
  exists : list of paths
      all the files on the server whose name contains the hash of the
      original file. The list is empty if no files are found

  """
  with get_destination_local(params, remote_config) as (rem, todo, done):
    origin = filepath
    origin_hash = get_sha1(origin)
    source = done/origin_hash
    find_hash = lambda p: origin_hash in str(p)
    paths = list(done.walk(filter=find_hash))
  # returning the hash is necessary for the file pulling, as it needs
  # to replace the name of the files after downloading them
  return origin_hash, paths

def pull_single_file(filepath, destination_dir, params, remote_config, log):
  """

  Parameters
  ----------
  filepath : plumbum path object
      origin file to pull from the server
  destination_dir : plumbum path object
      the directory in which to copy the files

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

      log.insert(INSERT, '[INFO] file pulled with success\n')
  return pulled_file



class AnonymizerGUI (Frame):

  anonymizers = {'SVS' : SVSAnonymize,
                 'DCM' : DICOMAnonymize,
                 'DICOM' : DICOMAnonymize,
                 'NII' : NiftiAnonymize}


  def __init__ (self, *args, **kwargs):

    Frame.__init__(self, *args, **kwargs)

    self.filename_or_path = []

    self.cfg = Button(window, text='Config File', command=self._cfg_cb)
    self.cfg.grid(column=0, row=0, rowspan=2)

    self.import_type = IntVar()
    self.file = Radiobutton(window, text='Single File', value=0, variable=self.import_type)
    self.dir  = Radiobutton(window, text='  Directory', value=1, variable=self.import_type)
    self.file.grid(column=1, row=0)
    self.dir.grid(column=1, row=1)

    self.load = Button(window, text='Load File', command=self._load_cb)
    self.load.grid(column=2, row=0, rowspan=2)

    self.anonymized = BooleanVar()
    self.anonymized.set(False)
    self.check_anonymized = Checkbutton(window, text='Already Anonym', variable=self.anonymized)
    self.check_anonymized.grid(column=3, row=0)

    # Vertical

    self.anonym = Button(window, text='Anonymize', fg='red', command=self._anonym_cb)
    self.anonym.grid(column=3, row=2)

    self.push = Button(window, text='Push files', command=self._push_cb)
    self.push.grid(column=3, row=4)

    self.pull = Button(window, text='Pull files', command=self._pull_cb)
    self.pull.grid(column=3, row=6)

    self.infos = scrolledtext.ScrolledText(window, width=60, height=25)
    self.infos.grid(column=0, row=2, columnspan=3, rowspan=5)


  def _anonym_cb (self):

    if not self.filename_or_path:
      messagebox.showerror('Error', 'Filename not set!')
    elif self.anonymized.get():
      messagebox.showerror('Error', 'The loaded files are already anonymized!')
    else:

      troubles = 0

      log  = '[INFO] Anonymizing {} file(s)...\n\n'.format(len(self.filename_or_path))
      self.infos.insert(INSERT, log)

      for i in range(len(self.filename_or_path)):

        file = self.filename_or_path[i]
        log += '[INFO] Anonymizing {}\n'.format(file)

        self.infos.insert(INSERT, log)

        root, ext = os.path.splitext(file)

        try:
          anonym = self.anonymizers[ext[1:].upper()](file)
          anonym.anonymize(infolog=True)

          filename = root + '_anonym' + ext
          self.filename_or_path[i] = filename

        except Exception:
          troubles += 1
          log += '[ERROR] Some troubles have occurred in the anonymization of {}'.format(file)

      if troubles:
        messagebox.showwarning('Found some troubles in the anonymization of {} file(s)'.format(troubles))

      else:
        messagebox.showinfo('Anonymizer', 'Done!\nReady to push')
        self.anonymized.set(True)


  def _cfg_cb (self):

    local = os.path.abspath('.')
    self.cfg_file = askopenfilename(initialdir=local,
                                    title='Select file',
                                    )
    log = '[INFO] Using {} config file for data transmission...\n\n'.format(self.cfg_file)
    self.infos.delete(1., END)
    self.infos.insert(INSERT, log)

    try:
      parser.read(self.cfg_file)
    except Exception as e:
      messagebox.showerror('Error', e)
      return

    self.params = dict(host=parser.get('CONNECTION', 'host'),
                       user=parser.get('CONNECTION', 'user'),
                       keyfile=Path(parser.get('CONNECTION', 'keyfile')),
                      )
    self.remote_config = dict(base_dir=parser.get('REMOTE', 'base_dir'),
                              done_subdir=parser.get('REMOTE', 'done_subdir'),
                              todo_subdir=parser.get('REMOTE', 'todo_subdir'))

  def _load_cb (self):

    if self.import_type.get() == 0:
      local = os.path.abspath('.')
      listfile = askopenfilename(initialdir=local,
                                 title='Select file',
                                 filetypes=(('Dicom', '*.dcm'),
                                            ('SVS', '*.svs'),
                                            ('Nifti', '*.nii'),
                                            ('all files', '*.*'))
                                 )
      if listfile:
        self.filename_or_path.append(listfile)

    elif self.import_type.get() == 1:
      directory = askdirectory()

      for ext in ('*.dcm', '*.svs', '*nii'):
        self.filename_or_path.extend(glob(os.path.join(directory, ext)))

    dtypes = Counter()
    for f in self.filename_or_path:
      root, ext = os.path.splitext(f)
      dtypes[ext[1:]] += 1

    log  = '[INFO] Loading: {} file(s)...\n'.format(len(self.filename_or_path))
    log += ' Found:\n'
    log += ''.join('  {}:{}\n'.format(k.upper(), v) for k, v in dtypes.items())
    log += '\n'

    log += ''.join('files: {}\n'.format(f) for f in self.filename_or_path)

    self.infos.insert(INSERT, log)
    self.anonymized.set(False)

  def _push_cb (self):

    if not self.filename_or_path:
      messagebox.showerror('Error', 'Filename not set!')
    elif not self.anonymized.get():
      messagebox.showerror('Error', 'I cannot push data without anonymization!')
    else:

      log = '[INFO] Pushing {} file(s)...\n\n'.format(len(self.filename_or_path))
      self.infos.insert(INSERT, log)

      for f in self.filename_or_path:
        try:
          filename = Path(f)
          destination = push_single_file(filename,
                                         params=self.params, remote_config=self.remote_config,
                                         log=self.infos)
          log = '[INFO] Pushed on {}\n'.format(destination)
          self.infos.insert(INSERT, log)

        except Exception as e:
          print(e)
          messagebox.showerror('Error', e)
          return

      messagebox.showinfo('Push', 'Done!')

      # delete variables
      self.filename_or_path = []
      self.anonymized.set(False)


  def _pull_cb (self):

    if not self.filename_or_path:
      messagebox.showerror('Error', 'Filename not set!')

    else:

      log  = 'Looking for pulling of {} updated file(s)...\n'.format(len(self.filename_or_path))
      self.infos.insert(INSERT, log)

      for f in self.filename_or_path:
        try:
          filename = Path(f)
          pull_single_file(filename, destination_dir='.',
                           params=self.params, remote_config=self.remote_config,
                           log=self.infos)
          log = '[INFO] {} pulled\n'.format(filename)
          self.infos.insert(INSERT, log)

        except Exception as e:
          messagebox.showerror('Error', e)
          return

      messagebox.showinfo('Pull', 'Done!\nUpdated files downloaded')

      # delete variables
      self.filename_or_path = []
      self.anonymized.set(False)


def GUI ():

  global window

  window = Tk()
  window.title('Medical Image Anonymizer')
  window.geometry('600x400')

  AnonymizerGUI(window)

  window.mainloop()



if __name__ == '__main__':

  GUI()