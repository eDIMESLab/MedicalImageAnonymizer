#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

__package__ = "build_mia"
__author__  = ['Enrico Giampieri', 'Nico Curti']
__email__ = [ 'enrico.giampier@unibo.it', 'nico.curit2@unibo.it']

def get_requires (requirements_filename):
  """
  What packages are required for this module to be executed?
  """
  with open(requirements_filename, 'r') as fp:
    requirements = fp.read()

  return list(filter(lambda x: x != '', requirements.split()))

def read_description (readme_filename):
  """
  Description package from filename
  """

  try:

    with open(readme_filename, 'r') as fp:
      description = '\n'
      description += fp.read()

  except Exception:
    return ''
