#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk

import os
from glob import glob
from plumbum.path import Path
from _ssh_utils import push_single_file


__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampieri@unibo.it', 'nico.curti2@unibo.it']


class _Pusher (ttk.Frame):

  def __init__ (self, prev_tab, *args, **kwargs):

    super(_Pusher, self).__init__(*args, **kwargs)
    self._prev_tab = prev_tab

    self._files = []

    # add log
    self._winfos = tk.scrolledtext.ScrolledText(self, width=60, height=20)
    # variables
    self._import_type = tk.IntVar()
    self._num_files = tk.StringVar()

    # add widgets
    self._wload = tk.Button(self, text='Load', command=self._load_cb)
    self._wfile = tk.Radiobutton(self, text='Single File', value=0, variable=self._import_type)
    self._wdir  = tk.Radiobutton(self, text='  Directory', value=1, variable=self._import_type)
    self._wnum_files = tk.Label(self, textvariable=self._num_files)
    #self._wupdate = tk.Button(self, text='Load Anonymize data', command=self._update_cb)
    self._wpush = tk.Button(self, text='Push files', command=self._push_cb)

    # widget on grid
    self._winfos.grid(column=0, row=2, columnspan=3, rowspan=2)
    self._wload.grid(column=2, row=0)
    self._wfile.grid(column=1, row=0)
    self._wdir.grid(column=1, row=1)
    self._wnum_files.grid(column=4, row=1)
    #self._wupdate.grid(column=4, row=1)
    self._wpush.grid(column=4, row=2)

    # widget values
    self._winfos.insert(tk.INSERT, self._template_log())

    self._num_files.set('# of files: {}'.format(len(self._files)))

  def _load_from_file (self):
    '''
    Load a single file
    '''
    local = os.path.abspath('.')
    listfile = tk.filedialog.askopenfilenames(initialdir=local,
                                              title='Select file',
                                              filetypes=(('all files', '*.*'),
                                                         ('Dicom', '*.dcm'),
                                                         ('SVS', '*.svs'),
                                                         ('Tiff', '*.tiff'),
                                                         ('Nifti', '*.nii'))
                                              )

    if not listfile:
      return

    self._files = list(listfile)

    log = 'Loading {} file'.format('\n'.join(self._files))

    available_ext = ('.{}'.format(x.lower()) for x in self._prev_tab[1]._anonymizers.keys())

    found = []

    for ext in available_ext:
      found.append((ext, len([x for x in self._files if x.endswith(ext)])))

    dtypes = ''.join('  {}:{}\n'.format(k, v ) for k, v in found)
    log = '{}\nLoad {} files:\n{}\n'.format(log, len(self._files), dtypes)

    self._winfos.insert(tk.INSERT, log)


  def _load_from_directory (self):
    '''
    Load file from a directory
    '''
    directory = tk.filedialog.askdirectory()
    if not directory:
      return

    available_ext = ('*.{}'.format(x.lower()) for x in self._prev_tab[1]._anonymizers.keys())

    found = []
    self._files = []

    for ext in available_ext:
      all_files_in_subdirs = glob(os.path.join(directory, '**', ext), recursive=True)
      self._files.extend(all_files_in_subdirs)

      found.append((ext, len(all_files_in_subdirs)))

    dtypes = ''.join('  {}:{}\n'.format(k, v ) for k, v in found)
    log = 'Found {} files in {}:\n{}\n'.format(len(self._files), directory, dtypes)

    self._winfos.insert(tk.INSERT, log)

  def _load_cb (self):
    '''
    load files or add to the current list of files
    '''
    if self._import_type.get() == 0:
      self._load_from_file()

    elif self._import_type.get() == 1:
      self._load_from_directory()

    else:
      raise ValueError('Something goes wrong')

    self._num_files.set('# of files: {}'.format(len(self._files)))

  def _template_log (self):
    '''
    Template of the log
    '''

    return 'Config file: {}\n'\
           '# of files loaded: {}\n\n'\
           ''.format(self._prev_tab[0].config, len(self._files))


  def _update_cb (self):
    '''
    Update the variables
    '''
    self._files = sum([self._files, self._prev_tab[1].file_list], [])
    self._winfos.delete(1., tk.END)
    self._winfos.insert(tk.INSERT, self._template_log())


  def _push_cb (self):
    '''
    '''
    self._update_cb()

    if not self._prev_tab[0].config:
      tk.messagebox.showerror('Error', 'No config file loaded!')
      return

    params = self._prev_tab[0].connection_params
    remote = self._prev_tab[0].remote_params
    file_list = self._files

    if not len(file_list):
      tk.messagebox.showerror('Error', 'No file to push!')
      return


    for file in file_list:

      try:
        file = Path(file)
        destination = push_single_file(file, params=params, remote_config=remote)

        log = 'Push {} on {}\n'.format(file, destination)
        self._winfos.insert(tk.INSERT, log)

      except Exception as e:
        print(repr(e))
        tk.messagebox.showerror('Error', repr(e))
        return

    tk.messagebox.showinfo('Push', 'Pushed {} files'.format(len(file_list)))
