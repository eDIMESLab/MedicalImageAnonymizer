#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pydicom
from enum import unique
from enum import Enum
from ast import literal_eval

from MedicalImageAnonymizer.Anonymizer import Anonymizer

__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampier@unibo.it', 'nico.curti2@unibo.it']
__package__ = 'DICOM Anonymizer'


class DICOMAnonymize (Anonymizer):

  def __init__ (self, filename, alias='0'):

    super(DICOMAnonymize, self).__init__(filename)
    self.alias = alias


  @unique
  class TAG_CODES (Enum):

    InstanceCreationDate    = ('0008', '0012')
    InstanceCreationTime    = ('0008', '0013')
    StudyDate               = ('0008', '0020')
    SeriesDate              = ('0008', '0021')
    AcquisitionDate         = ('0008', '0022')
    ContentDate             = ('0008', '0023')
    InstitutionName         = ('0008', '0080')
    ReferingPhysicianName   = ('0008', '0090')
    PerformingPhysicianName = ('0008', '1050')
    PhysicianReadingName    = ('0008', '1060')
    OperatorsName           = ('0008', '1070')

    PatientName             = ('0010', '0010')
    PatientID               = ('0010', '0020')
    IssuerofPatientID       = ('0010', '0021')
    PatientBirthDate        = ('0010', '0030')
    PatientSex              = ('0010', '0040')

    AcquisitionNumber       = ('0020', '0012')

    PrivateCreator1         = ('07a1', '0010')
    PrivateData1            = ('07a1', '015d')
    PrivateData2            = ('07a1', '1070')
    PrivateCreator2         = ('07a3', '0010')
    PrivateTag1             = ('07a3', '101c')
    PrivateTag2             = ('07a3', '101d')
    PrivateTag3             = ('07a3', '1022')
    PrivateTag4             = ('07a5', '0010')
    PrivateTag5             = ('07a5', '1054')


  def _get_value_from_tag (self, img):

    infos = {}

    for tag in self.TAG_CODES:
      try:
        infos[str(tag.value)] = str(img[tag.value].value)
      except KeyError:
        pass

    return infos

  def _set_value_from_tag (self, img, infos=None):

    if infos is not None:
      for k, v in infos.items():
        img[literal_eval(k)].value = v

    else:
      for tag in self.TAG_CODES:
        try:
          img[tag.value].value = b'0' # TODO: add alias here for the patient name
        except KeyError:
          pass


  def anonymize (self, infolog=False):

    img = pydicom.dcmread(self._filename)

    infos = self._get_value_from_tag(img)
    self._set_value_from_tag(img)

    if infolog is not None:
      root, ext = os.path.splitext(self._filename)

      img.save_as(root + '_anonym.dcm')

      with open(root + '_info.json', 'w', encoding='utf-8') as log:
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
    raise AssertionError()
  if not list(img_anonim.elements()) == list(img_orig.elements()):
    raise AssertionError()

  # same images
  if not np.sum(img_orig.pixel_array == img_deanonim.pixel_array) == np.prod(img_orig.pixel_array.shape):
    raise AssertionError()
  if not np.sum(img_orig.pixel_array == img_anonim.pixel_array) == np.prod(img_orig.pixel_array.shape):
    raise AssertionError()
