#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import nibabel as nib
from enum import unique
from enum import Enum
from ast import literal_eval

from MedicalImageAnonymizer.Anonymizer import Anonymizer

__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampier@unibo.it', 'nico.curti2@unibo.it']
__package__ = 'Nifti Anonymizer'


class NiftiAnonymize (Anonymizer):


  def __init__ (self, filename):
    '''
    Nifti anonymizer object

    Parameters
    ----------
      filename: str
        nifti filename to anonymize
    '''

    super(NiftiAnonymize, self).__init__(filename)


  @unique
  class TAG_CODES (Enum):
    '''
    TAG name of the informations to delete from nifti metadata
    '''

    db_name = 'db_name'
    descrip = 'descrip'

  def _get_value_from_tag (self, img):
    '''
    Get dictionary of metadata stored in the nifti file

    Parameters
    ----------
      img: nibabel image
        nifti image

    Returns
    -------
      infos: dict
        dictionary of metadata extracted according to the TAG_CODES
    '''

    infos = dict()

    for tag in self.TAG_CODES:
      try:
        infos[str(tag.value)] = str(img.header[tag.value])
      except KeyError:
        pass
    return infos

  def _set_value_from_tag (self, img, infos=None):

    if infos is not None:
      for k, v in infos.items():
        try:
          img.header[k] = literal_eval(v)
        except KeyError:
          pass

    else:
      for tag in self.TAG_CODES:
        try:
          img.header[tag.value] = b'anonymous'
        except KeyError:
          pass

  def anonymize (self, infolog=False):

    img = nib.load(self._filename)

    infos = self._get_value_from_tag(img)
    self._set_value_from_tag(img)

    if infolog is not None:
      root, _ = os.path.splitext(self._filename)

      nib.save(img, root + '_anonym.nii')

      with open(root + '_info.json', 'w', encoding='utf-8') as log:
        json.dump(infos, log)
        log.write('\n')

    else:
      nib.save(img, self._filename)


  def deanonymize (self, infolog=False):

    if infolog:
      root, _ = os.path.splitext(self._filename)
      img = nib.load(root + '_anonym.nii')

      with open(root + '_info.json', 'r', encoding='utf-8') as log:
        infos = json.load(log)

      self._set_value_from_tag(img, infos)

    else:
      img = nib.load(self._filename)


    nib.save(img, self._filename)



if __name__ == '__main__':

  import numpy as np

  niftifile = '11.nii'
  img_orig = nib.load(niftifile)

  anonym = NiftiAnonymize(niftifile)

  anonym.anonymize(infolog=True)
  anonym.deanonymize(infolog=True)

  img_anonim = nib.load('11_anonym.nii')
  img_deanonim = nib.load(niftifile)

  # different header
  if not img_orig.header == img_deanonim.header:
    raise AssertionError()
  if not img_orig.header != img_anonim.header:
    raise AssertionError()

  # same images
  if not np.allclose(img_orig.get_data(), img_deanonim.get_data()):
    raise AssertionError()
  if not np.allclose(img_orig.get_data(), img_anonim.get_data()):
    raise AssertionError()
