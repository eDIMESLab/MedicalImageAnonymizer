#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk

from _ssh_config import _Config
from _load_data import _Anonymizer
from _push import _Pusher
from _pull import _Puller


class GUI:

  def __init__ (self):

    self.window = tk.Tk()
    self.window.title('Medical Image Anonymizer')
    self.window.geometry('600x400')

    tabs = ttk.Notebook(self.window)
    tab_conf = _Config(self.window)
    tab_load = _Anonymizer(self.window)
    tab_push = _Pusher([tab_conf, tab_load], self.window)
    tab_pull = _Puller([tab_conf, tab_load], self.window)

    tabs.add(tab_conf, text='SSH config')
    tabs.add(tab_load, text='Load data')
    tabs.add(tab_push, text='Push data')
    tabs.add(tab_pull, text='Pull data')

    tabs.pack(expand=1, fill='both')

    self.window.mainloop()


if __name__ == '__main__':

  GUI ()
