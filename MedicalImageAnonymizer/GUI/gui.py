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

__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampieri@unibo.it', 'nico.curti2@unibo.it']


class AnonymizerGUI (Frame):

  anonymizers = {'SVS' : SVSAnonymize,
                 'DICOM' : DICOMAnonymize,
                 'NII' : NiftiAnonymize}


  def __init__ (self, *args, **kwargs):

    Frame.__init__(self, *args, **kwargs)

    self.filename_or_path = []
    self.anonymized = False

    self.load = Button(window, text='Load File', command=self._load_cb)
    self.load.grid(column=1, row=0, rowspan=2)

    self.copy_file = BooleanVar()
    self.copy_file.set(True)
    self.check = Checkbutton(window, text='CopyFile', variable=self.copy_file)
    self.check.grid(column=3, row=0)

    self.anonym = Button(window, text='Anonymize', fg='red', command=self._anonym_cb)
    self.anonym.grid(column=3, row=2)

    self.push = Button(window, text='Push files', command=self._push_cb)
    self.push.grid(column=3, row=4)

    self.pull = Button(window, text='Pull files', command=self._pull_cb)
    self.pull.grid(column=3, row=6)

    self.infos = scrolledtext.ScrolledText(window, width=40, height=10)
    self.infos.grid(column=0, row=2, columnspan=3, rowspan=5)

    self.import_type = IntVar()
    self.file = Radiobutton(window, text='Single File', value=0, variable=self.import_type)
    self.dir  = Radiobutton(window, text='  Directory',   value=1, variable=self.import_type)
    self.file.grid(column=0, row=0)
    self.dir.grid(column=0, row=1)


  def _anonym_cb (self):

    if not self.filename_or_path:
      messagebox.showerror('Error', 'Filename not set!')
    elif self.anonymized:
      messagebox.showerror('Error', 'The loaded files are already anonymized!')
    else:

      copy = self.copy_file.get()
      troubles = 0

      log  = 'Anonymizing {} file(s)...\n\n'.format(len(self.filename_or_path))
      self.infos.delete(1., END)
      self.infos.insert(INSERT, log)

      for f in self.filename_or_path:

        log += 'Anonymizing {}\n'.format(f)

        self.infos.delete(1., END)
        self.infos.insert(INSERT, log)

        root, ext = os.path.splitext(f)

        try:
          anonym = self.anonymizers[ext[1:].upper()](f)
          anonym.anonymize(infolog=copy)

        except:
          troubles += 1
          log += 'ERROR: Some troubles have occurred in the anonymization of {}'.format(f)

      if troubles:
        messagebox.showwarning('Found some troubles in the anonymization of {} file(s)'.format(troubles))

      else:
        messagebox.showinfo('Anonymizer', 'Done!\nReady to push')
        self.anonymized = True



  def _load_cb (self):

    self.anonymized = False

    if self.import_type.get() == 0:
      local = os.path.abspath('.')
      self.filename_or_path.append(askopenfilename(initialdir=local, title='Select file', filetypes=(('Dicom', '*.dcm'), ('SVS', '*.svs'), ('Nifti', '*.nii'), ('all files', '*.*'))))

    elif self.import_type.get() == 1:
      directory = askdirectory()

      for ext in ('*.dcm', '*.svs', '*nii'):
        self.filename_or_path.extend(glob(os.path.join(directory, ext)))

    dtypes = Counter()
    for f in self.filename_or_path:
      root, ext = os.path.splitext(f)
      dtypes[ext[1:]] += 1

    log  = 'Loading: {} file(s)...\n'.format(len(self.filename_or_path))
    log += ' Found:\n'
    log += ''.join('  {}:{}\n'.format(k.upper(), v) for k, v in dtypes.items())
    log += '\n'

    log += ''.join('files: {}\n'.format(f) for f in self.filename_or_path)

    self.infos.delete(1., END)
    self.infos.insert(INSERT, log)

  def _push_cb (self):

    #################################################################
    messagebox.showerror('Push', 'Push button not yet supported!')
    self.anonymized = False
    self.filename_or_path = []
    return
    #################################################################


    if not self.filename_or_path:
      messagebox.showerror('Error', 'Filename not set!')
    elif not self.anonymized:
      messagebox.showerror('Error', 'I cannot push data without anonymization!')
    else:

      log  = 'Pushing {} file(s)...\n'.format(len(self.filename_or_path))
      self.infos.delete(1., END)
      self.infos.insert(INSERT, log)

      for f in self.filename_or_path:
        root, ext = os.path.splitext(f)
        filename = root + '_anonym' + ext

        # TODO: insert here the pushing command

      messagebox.showinfo('Push', 'Done!')

      # delete variables
      self.anonymized = False
      self.filename_or_path = []


  def _pull_cb (self):

    #################################################################
    messagebox.showerror('Pull', 'Pull button not yet supported!')
    return
    #################################################################

    if not self.filename_or_path:
      messagebox.showerror('Error', 'Filename not set!')
    elif not self.anonymized:
      messagebox.showerror('Error', 'I cannot push data without anonymization!')
    else:

      log  = 'Looking for pulling of {} updated file(s)...\n'.format(len(self.filename_or_path))
      self.infos.delete(1., END)
      self.infos.insert(INSERT, log)

      for f in self.filename_or_path:
        root, ext = os.path.splitext(f)
        filename = root + '_anonym' + ext

        # TODO: insert here the pulling command

      messagebox.showinfo('Pull', 'Done!\nUpdated files downloaded')

      # delete variables
      self.anonymized = False
      self.filename_or_path = []


def GUI ():

  global window

  window = Tk()
  window.title('Medical Image Anonymizer')
  window.geometry('450x250')

  app = AnonymizerGUI(window)

  window.mainloop()



if __name__ == '__main__':

  GUI()