#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pydicom
from ast import literal_eval
from configparser import ConfigParser

from MedicalImageAnonymizer.Anonymizer import Anonymizer

__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampier@unibo.it', 'nico.curti2@unibo.it']
__package__ = 'DICOM Anonymizer'


class DICOMAnonymize (Anonymizer):

  def __init__ (self, filename, alias='0'):

    super(DICOMAnonymize, self).__init__(filename)
    self.alias = alias
    self._load_tags_list(os.path.join(os.path.dirname(__file__), 'GUI', 'dicom_tags.ini'))

  def _load_tags_list (self, filename):

    parser = ConfigParser()
    parser.read(filename)

    self.TAG_CODES = parser._sections['DICOM_TAGS']

  def _get_value_from_tag (self, img):

    infos = {}

    for k, tag in self.TAG_CODES.items():
      try:
        infos[tag] = str(img[literal_eval(tag)].value)
      except KeyError:
        pass

    return infos

  def _set_value_from_tag (self, img, infos=None):

    if infos is not None:
      for k, v in infos.items():
        img[literal_eval(k)].value = v

    else:
      for k, tag in self.TAG_CODES.items():
        try:
          img[literal_eval(tag)].value = b'0' # TODO: add alias here for the patient name
        except KeyError:
          pass


  def anonymize (self, outfile=None, outlog=None, infolog=False):

    img = pydicom.dcmread(self._filename)

    infos = self._get_value_from_tag(img)
    self._set_value_from_tag(img)

    if infolog is not None:
      root, ext = os.path.splitext(self._filename)

      if outfile is None:
        outfile = root + '_anonym.dcm'

      img.save_as(outfile)

      if outlog is None:
        outlog = root + '_info.json'

      with open(outlog, 'w', encoding='utf-8') as log:
        json.dump(infos, log)
        log.write('\n')

    else:
      img.save_as(self._filename)


  def deanonymize (self, infolog=False):

    if infolog:
      root, ext = os.path.splitext(self._filename)
      img = pydicom.dcmread(root + '_anonym.dcm')

      with open(root + '_info.json', 'r', encoding='utf-8') as log:
        infos = json.load(log)

      self._set_value_from_tag(img, infos)

    else:
      img = pydicom.dcmread(self._filename)


    img.save_as(self._filename)



if __name__ == '__main__':

  import numpy as np

  dicomfile = '01.dcm'
  img_orig = pydicom.dcmread(dicomfile)

  anonym = DICOMAnonymize(dicomfile)

  anonym.anonymize(infolog=True)
  anonym.deanonymize(infolog=True)

  img_anonim = pydicom.dcmread('01_anonym.dcm')
  img_deanonim = pydicom.dcmread(dicomfile)

  # different header
  if not list(img_deanonim.elements()) == list(img_orig.elements()):
    raise AssertionError('different header deanonim')
  if list(img_anonim.elements()) == list(img_orig.elements()):
    raise AssertionError('different header anonim')

  # same images
  if not np.sum(img_orig.pixel_array == img_deanonim.pixel_array) == np.prod(img_orig.pixel_array.shape):
    raise AssertionError('different image deanonim')
  if not np.sum(img_orig.pixel_array == img_anonim.pixel_array) == np.prod(img_orig.pixel_array.shape):
    raise AssertionError('different header anonim')
