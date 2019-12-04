#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import all the objects in the package

from .DICOM_anonymizer import DICOMAnonymize
from .Nifti_anonymizer import NiftiAnonymize
from .SVS_anonymizer import SVSAnonymize
from .GUI.gui import GUI

__package__ = 'MedicalImageAnonymizer'
__author__  = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampier@unibo.it', 'nico.curti2@unibo.it']

# aliases

