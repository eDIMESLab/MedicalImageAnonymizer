#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk

import os
import json
import shutil
from glob import glob
from pathlib import Path

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
    listfile = tk.filedialog.askopenfilenames(initialdir=local,
                                              title='Select file',
                                              filetypes=(('Dicom', '*.dcm'),
                                                         ('SVS', '*.svs'),
                                                         ('Tiff', '*.tiff'),
                                                         ('Nifti', '*.nii'),
                                                         ('all files', '*.*'))
                                              )

    if not listfile:
      return

    self._files = list(listfile)
    self._indir = os.path.dirname(self._files[-1])
    self._outdir = self._indir + '_anonym'

    log = 'Loading {} file'.format('\n'.join(self._files))
    available_ext = ('.{}'.format(x.lower()) for x in self._anonymizers.keys())

    found = []

    for ext in available_ext:
      found.append((ext, len([x for x in self._files if x.endswith(ext)])))

    dtypes = ''.join('  {}:{}\n'.format(k, v ) for k, v in found)
    log = '{}\nLoad {} files:\n{}\noutput directory: {}\n'.format(log, len(self._files), dtypes, self._outdir)

    self._winfos.insert(tk.INSERT, log)


  def _load_from_directory (self):
    '''
    Load file from a directory
    '''
    self._indir = tk.filedialog.askdirectory()
    if not self._indir:
      return

    available_ext = ('*.{}'.format(x.lower()) for x in self._anonymizers.keys())

    found = []
    files = glob(os.path.join(self._indir, '**', '*'), recursive=True)
    self._files = [x for x in files if Path(x).is_file() and not Path(x).is_symlink() and not Path(x).suffix == '.lnk']

    for ext in available_ext:
      all_files_in_subdirs = glob(os.path.join(self._indir, '**', ext), recursive=True)
      found.append((ext, len(all_files_in_subdirs)))

    self._outdir = self._indir + '_anonym'

    dtypes = ''.join('  {}:{}\n'.format(k, v ) for k, v in found)
    log = 'Found {} files in {}:\n{}\noutput directory: {}\n'.format(len(self._files), self._indir, dtypes, self._outdir)

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

      err = self._anonymize(self._files[i])
      issues += err

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
                           ''.format(len(self._files) - issues, len(self._files)))




  def _anonymize (self, filename):
    '''
    Anonymize the filename given
    '''

    path_filename = Path(filename)
    dtype = path_filename.suffix[1:].upper()
    outfile = Path(self._outdir)/path_filename.absolute().relative_to(self._indir)
    outlog = Path(self._outdir + '_log')/path_filename.absolute().relative_to(self._indir)

    outfile.parent.mkdir(parents=True, exist_ok=True)
    outlog.parent.mkdir(parents=True, exist_ok=True)

    try:

      anonymizer = self._anonymizers[dtype](filename)
      anonymizer.anonymize(infolog=True, outfile=str(outfile), outlog=str(outlog.with_suffix('.json')))

    except KeyError as e:
      # no anonymizer available but it could be a usefull file
      shutil.copy(str(path_filename), str(outfile))

    except Exception as e:
      print(e)
      tk.messagebox.showwarning('Warning!',
                                'Found some troubles in the anonymization'
                                ' of file {}. It can be corrupted or not '
                                'a valid {} file'.format(filename, dtype))
      return True

    return False


  @property
  def file_list (self):
    return self._files
