#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk

import os
import json
from glob import glob

from MedicalImageAnonymizer import DICOMAnonymize
from MedicalImageAnonymizer import NiftiAnonymize
from MedicalImageAnonymizer import SVSAnonymize


__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampieri@unibo.it', 'nico.curti2@unibo.it']


class _Anonymizer (ttk.Frame):

  _anonymizers = {'SVS' : SVSAnonymize,
                  'TIFF' : SVSAnonymize,
                  'DCM' : DICOMAnonymize,
                  'DICOM' : DICOMAnonymize,
                  'NII' : NiftiAnonymize,
                  'NIFTI' : NiftiAnonymize
                  # add other aliases
                  }


  def __init__ (self, *args, **kwargs):

    super(_Anonymizer, self).__init__(*args, **kwargs)

    self._files = []
    self._outdir = ''
    self._alias = None

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
    self._wanonym = tk.Button(self, text='Anonymize', fg='red', command=self._anonymize_cb)
    self._walias = tk.Button(self, text='Load Aliases', command=self._load_alias_cb)

    # widget on grid
    self._winfos.grid(column=0, row=2, columnspan=3, rowspan=2)
    self._wload.grid(column=2, row=0)
    self._wfile.grid(column=1, row=0)
    self._wdir.grid(column=1, row=1)
    self._wnum_files.grid(column=4, row=1)
    self._walias.grid(column=4, row=2)
    self._wanonym.grid(column=4, row=3)

    # widget values
    self._winfos.insert(tk.INSERT, self._template_log())
    self._num_files.set('# of files: {}'.format(len(self._files)))


  def _load_from_file (self):
    '''
    Load a single file
    '''
    local = os.path.abspath('.')
    listfile = tk.filedialog.askopenfilename(initialdir=local,
                                             title='Select file',
                                             filetypes=(('Dicom', '*.dcm'),
                                                        ('SVS', '*.svs'),
                                                        ('Tiff', '*.tiff'),
                                                        ('Nifti', '*.nii'),
                                                        ('all files', '*.*'))
                                             )

    if not listfile:
      return

    self._files.append(listfile)
    self._outdir = os.path.dirname(self._files[-1]) + '_anonym'

    log = 'Loading {} file'.format(self._files[-1])

    root, ext = os.path.splitext(self._files[-1])
    found = [(ext[1:], 1)]

    dtypes = ''.join('  {}:{}\n'.format(k, v ) for k, v in found)
    log = '{}\nLoad 1 files:\n{}\noutput directory: {}\n'.format(log, dtypes, self._outdir)

    self._winfos.insert(tk.INSERT, log)


  def _load_from_directory (self):
    '''
    Load file from a directory
    '''
    directory = tk.filedialog.askdirectory()
    if not directory:
      return

    available_ext = ('*.{}'.format(x.lower()) for x in self._anonymizers.keys())

    found = []

    for ext in available_ext:
      all_files_in_subdirs = glob(os.path.join(directory, '**', ext), recursive=True)
      self._files.extend(all_files_in_subdirs)

      found.append((ext, len(all_files_in_subdirs)))

    self._outdir = directory + '_anonym'

    dtypes = ''.join('  {}:{}\n'.format(k, v ) for k, v in found)
    log = 'Found {} files in {}:\n{}\noutput directory: {}\n'.format(len(self._files), directory, dtypes, self._outdir)

    self._winfos.insert(tk.INSERT, log)


  def _load_alias_cb (self):
    '''
    load alias file as name look up table
    '''
    # TODO:
    tk.messagebox.showerror('Error', 'Option not yet supported!')
    return

    local = os.path.abspath('.')
    alias_file = tk.filedialog.askopenfilename(initialdir=local, title='Select alias file',
                                               filetypes=(('csv', '*.csv'),
                                                          ('json', '*.json'),
                                                          ('all files', '*.*'))
                                               )

    root, ext = os.path.splitext(self._alias)

    if ext == '.csv':
      self._alias = {}

      with open(alias_file, 'r') as fp:
        lines = fp.read().splitlines()

      for line in lines:
        try:
          original, alias = line.split(',')
        except Exception:
          tk.messagebox.showerror('Error',
                                  'Invalid file format! '
                                  'The file must contain only two items '
                                  '(aka original_name,alias_name')

        self._alias[original] = alias

    elif ext == '.json':
      with open(alias_file, 'r') as fp:
        self._alias = json.load(fp)

    else:
      tk.messagebox.showerror('Error',
                              'Alias file extension not supported.')


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

    return 'Current file loaded: {}\n\n'\
           ''.format(len(self._files))


  def _anonymize_cb (self):
    '''
    Anonymize the loaded file list
    '''

    os.makedirs(self._outdir, exist_ok=True)

    log = 'Anonymizing {} file(s)...\n\n'.format(len(self._files))
    issues = 0

    for i in range(len(self._files)):

      err, outfile = self._anonymize(self._files[i], self._outdir)
      issues += err

      # replace the file as the anonym version
      self._files[i] = outfile

      # log
      log = '{}Anonymize {}...\n'.format(log, self._files[i])
      self._winfos.delete(1., tk.END)
      self._winfos.insert(tk.INSERT, log)

    if issues:
      tk.messagebox.showwarning('Warning!',
                                '{} files have troubles in the anonymization! '
                                'We suggest to not push them before an accurate review!'.format(issues))

    tk.messagebox.showinfo('Anonymizer!',
                           '{}/{} files have been anonymized! '
                           ''.format(len([x for x in self._files if x]), len(self._files)))




  def _anonymize (self, filename, outdir):
    '''
    Anonymize the filename given
    '''

    root, ext = os.path.splitext(filename)
    dirname = os.path.dirname(root)
    dtype = ext[1:].upper()

    try:
      anonymizer = self._anonymizers[dtype](filename)
      anonymizer.anonymize(infolog=True)

      outfile = os.path.basename(root) + '_anonym' + ext
      outinfo = os.path.basename(root) + '_info.json'
      # move the outfile to the outdir (aka "mirror") directory
      os.rename(os.path.join(dirname, outfile), os.path.join(outdir, outfile))
      os.rename(os.path.join(dirname, outinfo), os.path.join(outdir, outinfo))

    except Exception as e:
      print(e)
      tk.messagebox.showwarning('Warning!',
                                'Found some troubles in the anonymization'
                                ' of file {}. It can be corrupted or not '
                                'a valid {} file'.format(filename, dtype))
      return (True, '')

    return (False, os.path.join(outdir, outfile))


  @property
  def file_list (self):
    return self._files
