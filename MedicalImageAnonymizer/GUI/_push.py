#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk

from plumbum.path import Path
from _ssh_utils import push_single_file


__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampieri@unibo.it', 'nico.curti2@unibo.it']


class _Pusher (ttk.Frame):

  def __init__ (self, prev_tab, *args, **kwargs):

    super(_Pusher, self).__init__(*args, **kwargs)
    self._prev_tab = prev_tab

    # add log
    self._winfos = tk.scrolledtext.ScrolledText(self, width=60, height=25)
    # add widgets
    self._wupdate = tk.Button(self, text='Update', command=self._update_cb)
    self._wpush = tk.Button(self, text='Push files', command=self._push_cb)


    # widget on grid
    self._winfos.grid(column=0, row=2, columnspan=3, rowspan=4)
    self._wupdate.grid(column=4, row=1)
    self._wpush.grid(column=4, row=2)

    # widget values
    self._winfos.insert(tk.INSERT, self._template_log())


  def _template_log (self):
    '''
    Template of the log
    '''

    return 'Config file: {}\n'\
           '# of files loaded: {}\n\n'\
           ''.format(self._prev_tab[0].config, len(self._prev_tab[1].file_list))


  def _update_cb (self):
    '''
    Update the variables
    '''
    self._winfos.delete(1., tk.END)
    self._winfos.insert(tk.INSERT, self._template_log())


  def _push_cb (self):
    '''
    '''
    self._update_cb()

    params = self._prev_tab[0].connection_params
    remote = self._prev_tab[0].remote_params
    file_list = self._prev_tab[1].file_list

    if not len(file_list):
      tk.messagebox.showerror('Error', 'No file to push!')


    for file in file_list:

      try:
        file = Path(file)
        destination = push_single_file(file, params=params, remote_config=remote)

        log = 'Push {} on {}\n'.format(file, destination)
        self._winfos.insert(tk.INSERT, log)

      except Exception as e:
        print(e)
        tk.messagebox.showerror('Error', e)
        return

    tk.messagebox.showinfo('Push', 'Pushed {} files'.format(len(file_list)))
