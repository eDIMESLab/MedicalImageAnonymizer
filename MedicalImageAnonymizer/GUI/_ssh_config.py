#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk

import os
import plumbum
import paramiko
from glob import glob
from configparser import ConfigParser

__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampieri@unibo.it', 'nico.curti2@unibo.it']


class _Config (ttk.Frame):

  _required_infos = [('CONNECTION', 'host'), ('CONNECTION', 'user'), ('CONNECTION', 'keyfile'),
                     ('REMOTE', 'base_dir'), ('REMOTE', 'done_subdir'), ('REMOTE', 'todo_subdir')]

  def __init__ (self, *args, **kwargs):

    super(_Config, self).__init__(*args, **kwargs)

    self._parser = ConfigParser()
    self._cfg_file = ''

    # try to load the first available .ini file in the
    # current path
    available_cfg = glob('*.ini')

    if available_cfg:
      self._cfg_file = available_cfg[0]
      self._parser.read(self._cfg_file)

    # add log
    self._winfos = tk.scrolledtext.ScrolledText(self, width=60, height=25)
    # add widgets
    self._wcfg = tk.Button(self, text='Load', command=self._cfg_cb)
    self._wscp = tk.Button(self, text='Keygen', fg='Red', command=self._set_pwd_cb)

    # widget on grid
    self._winfos.grid(column=0, row=2, columnspan=3, rowspan=4)
    self._wcfg.grid(column=1, row=0)
    self._wscp.grid(column=0, row=0)

    # widget values
    self._winfos.insert(tk.INSERT, self._template_log())


  def _cfg_cb (self):

    local = os.path.abspath('.')
    self._cfg_file = tk.filedialog.askopenfilename(initialdir=local, title='Select config file',
                                                   filetypes=(('cfg', '*.ini'),
                                                              ('all files', '*.*'))
                                                   )

    try:
      self._parser.read(self._cfg_file)
    except Exception as e:
      tk.messagebox.showerror('Error', e)
      return

    self._winfos.delete(1., tk.END)
    self._winfos.insert(tk.INSERT, self._template_log())


  def _template_log (self):
    '''
    Template of the log
    '''

    try:
      self._check_config()
      values = sum([[self._cfg_file], list(self.connection_params.values()), list(self.remote_params.values())], [])
    except ValueError:
      values = ('', ) * 7

    return 'config file: {0}\n\n'\
           '[CONNECTION]\n' \
           'host={1}\n' \
           'user={2}\n' \
           'keyfile={3}\n\n'\
           '[REMOTE]\n' \
           'base_dir={4}\n' \
           'done_subdir={5}\n' \
           'todo_subdir={6}\n\n'.format(*values)

  def _check_config (self):
    '''
    Check if the config file has the minimum required sections
    '''

    for section, key in self._required_infos:
      if not self._parser.has_option(section, key):
        raise ValueError('Key not found')

    return True

  def _set_pwd_cb (self):
    '''
    Set the password for the remote server and copy the password as remote key
    '''
    if not self._cfg_file:
      tk.messagebox.showerror('Error', 'No config file loaded!')
      return

    username = self.parser.get('CONNECTION', 'user')
    hostname = self.parser.get('CONNECTION', 'host')
    password = tk.simpledialog.askstring('Password', 'Enter password:', show='\u2022', parent=root)

    # generate a new ssh key using ssh-keygen
    keygen = plumbum.local['ssh-keygen']
    command = ('-t rsa',
               '-b 4096',
               #'-f ./id_rsa',
               '-y',
               '-q',
               '-C {0}@{1}'.format(username, hostname),
               '-P "{0}"'.format(password))

    try:
      exit_code, pub_key, stderr = keygen.run(command)

    except plumbum.ProcessExecutionError as e:
      tk.messagebox.showerror('Error', 'Something goes wrong with ssh-keygen')
      return

    # add the id_rsa file to the ssh path
    #ssh_add = plumbum.local['ssh-add']
    #ssh_add.run('.')

    # now copy the id_rsa.pub to the server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port=22,
                username=username,
                password=password)

    try:
      stdin, stdout, stderr = ssh.exec_command('mkdir -p .ssh & echo {} >> known_hosts'.format(pub_key))
    except Exception as e:
      tk.messagebox.showerror('Error', 'Something goes wrong with scp known_hosts')
      return

    ssh.close()


  @property
  def connection_params (self):
    '''
    Return the connection informations as dict
    '''
    return dict(host=self._parser.get('CONNECTION', 'host'),
                user=self._parser.get('CONNECTION', 'user'),
                keyfile=self._parser.get('CONNECTION', 'keyfile'),
                )

  @property
  def remote_params (self):
    '''
    Return the information of the remote host as dict
    '''
    return dict(base_dir=self._parser.get('REMOTE', 'base_dir'),
                done_subdir=self._parser.get('REMOTE', 'done_subdir'),
                todo_subdir=self._parser.get('REMOTE', 'todo_subdir'),
                )

  @property
  def config(self):
    return self._cfg_file
