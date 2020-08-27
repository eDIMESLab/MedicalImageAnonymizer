#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
  from setuptools import setup
  from setuptools import find_packages

except ImportError:
  from distutils.core import setup
  from distutils.core import find_packages

from MedicalImageAnonymizer.build import get_requires
from MedicalImageAnonymizer.build import read_description

here = os.path.abspath(os.path.dirname(__file__))

# Package meta-data.
NAME = 'MedicalImageAnonymizer'
DESCRIPTION = 'Medical Image Anonymizer Toolkit'
URL = 'https://github.com/eDIMESLab/MedicalImageAnonymizer'
EMAIL = ['enrico.giampieri@unibo.it', 'nico.curti2@unibo.it']
AUTHOR = ['Enrico Giampieri', 'Nico Curti']
REQUIRES_PYTHON = '>=3.5'
VERSION = None
KEYWORDS = 'medical-image'

README_FILENAME = os.path.join(here, 'README.md')
REQUIREMENTS_FILENAME = os.path.join(here, 'requirements.txt')
VERSION_FILENAME = os.path.join(here, 'MedicalImageAnonymizer', '__version__.py')

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
  LONG_DESCRIPTION = read_description(README_FILENAME)

except IOError:
  LONG_DESCRIPTION = DESCRIPTION


# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
  with open(VERSION_FILENAME) as fp:
    exec(fp.read(), about)

else:
  about['__version__'] = VERSION

# parse version variables and add them to command line as definitions
Version = about['__version__'].split('.')


setup(
  name                          = NAME,
  version                       = about['__version__'],
  description                   = DESCRIPTION,
  long_description              = LONG_DESCRIPTION,
  long_description_content_type = 'text/markdown',
  author                        = AUTHOR,
  author_email                  = EMAIL,
  maintainer                    = AUTHOR,
  maintainer_email              = EMAIL,
  python_requires               = REQUIRES_PYTHON,
  install_requires              = get_requires(REQUIREMENTS_FILENAME),
  url                           = URL,
  download_url                  = URL,
  keywords                      = KEYWORDS,
  packages                      = find_packages(include=['MedicalImageAnonymizer', 'MedicalImageAnonymizer.*'], exclude=('test', 'testing')),
  #include_package_data          = True, # no absolute paths are allowed
  platforms                     = 'any',
  classifiers                   = [
                                   #'License :: OSI Approved :: GPL License',
                                   'Programming Language :: Python',
                                   'Programming Language :: Python :: 3',
                                   'Programming Language :: Python :: 3.6',
                                   'Programming Language :: Python :: Implementation :: PyPy'
                                  ],
  license                       = 'MIT'
)
