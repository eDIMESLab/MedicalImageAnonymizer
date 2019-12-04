#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampier@unibo.it', 'nico.curti2@unibo.it']
__package__ = 'Biomedical Images Anonymizer Base class'


class Anonymizer (object):

  def __init__ (self, filename):
    '''
    Anonymizer object

    Parameters
    ----------
      filename: str
        filename to anonymize
    '''

    if not os.path.isfile(filename):
      raise FileNotFoundError('Could not open or find the data file. Given: {}'.format(filename))

    self._filename = filename

  def anonymize (self, infolog=False):
    pass

  def deanonymize (self, infolog=False):
    pass
