#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import shutil
import struct
from enum import unique
from enum import IntEnum
from functools import partial
from ast import literal_eval as eval

from MedicalImageAnonymizer.Anonymizer import Anonymizer

__author__ = ['Enrico Giampieri', 'Nico Curti']
__email__ = ['enrico.giampier@unibo.it', 'nico.curti2@unibo.it']
__package__ = 'SVS Anonymizer'



class SVSAnonymize (Anonymizer):

  _DataTypes = {1: ('BYTE', 1, 'unsigned char integer'),
                2: ('ASCII', 1, 'NULL-terminated string'),
                3: ('SHORT', 2, 'unsigned short integer'),
                4: ('LONG', 4, 'unsigned long integer'),
                5: ('RATIONAL', 8, 'Two 32-bit unsigned integers'),
                # The RATIONAL data type is actually two LONG values and is used
                # to store the two components of a fractional value.
                # The first value stores the numerator, and the second value stores
                # the denominator.
                6: ('SBYTE', 1, 'signed char integer'),
                7: ('UNDEFINE', 1, 'generic data structure'),
                8: ('SSHORT', 2, 'signed short integer'),
                9: ('SLONG', 4, 'signed long integer'),
                10: ('SRATIONAL', 8, 'Two 32-bit signed integers'),
                11: ('FLOAT', 4, 'single-precision IEEE floating-point value'),
                12: ('DOUBLE', 8, 'double-precision IEEE floating-point value')
                }

  # this is necessary for a hack to recognize labels:
  # all the normal images have the second row of the image description
  # starting with the image size in the format widthxheight

  _image_size_expression = re.compile(r'\d+x\d+')

  # TODO: the byteorder should be the correct one for the tiff instead of
  #  sys.byteorder by default
  #  can't be bothered right now
  # bytes_to_int(b'a') == 97
  _bytes_to_int = partial(int.from_bytes, byteorder=sys.byteorder, signed=False)

  @unique
  class TAG_CODES (IntEnum):

    IMAGEWIDTH                = 256
    IMAGELENGTH               = 257
    BITSPERSAMPLE             = 258
    COMPRESSION               = 259
    PHOTOMETRICINTERPRETATION = 262
    IMAGEDESCRIPTION          = 270
    STRIPOFFSETS              = 273
    SAMPLESPERPIXEL           = 277
    ROWSPERSTRIP              = 278
    STRIPBYTECOUNTS           = 279
    PLANARCONFIGURATION       = 284
    PREDICTOR                 = 317
    TILEWIDTH                 = 322
    TILELENGTH                = 323
    TILEOFFSETS               = 324
    TILEBYTECOUNTS            = 325
    JPEGTABLES                = 347
    IMAGEDEPTH                = 32997


  def __init__ (self, filename):

    super(SVSAnonymize, self).__init__(filename)

    self._DataType_bytes = {k: v[1] for k, v in self._DataTypes.items()}


  def _read_TifTag (self, bfile):
    '''
    given a binary buffer alredy at the position for a tag, scrape
    the content of the tag.
    Does not load the actual data as it might be massive.
    '''
    TagId      = self._bytes_to_int(bfile.read(2))
    DataType   = self._bytes_to_int(bfile.read(2))
    DataCount  = self._bytes_to_int(bfile.read(4))
    DataOffset = self._bytes_to_int(bfile.read(4))
    return {'TagId':      TagId,
            'DataType':   DataType,
            'DataCount':  DataCount,
            'DataOffset': DataOffset}

  def _read_TifIfd (self, bfile, offset):

    bfile.seek(offset)
    NumDirEntries = self._bytes_to_int(bfile.read(2))
    TagList = [self._read_TifTag(bfile) for i in range(NumDirEntries)]
    NextOffsetPosition = offset + 2 + 12 * len(TagList)
    NextIFDOffset = self._bytes_to_int(bfile.read(4))
    return NumDirEntries, TagList, NextIFDOffset, NextOffsetPosition


  def _get_all_tiffID (self, bfile):
    '''
    browse the given binary file for all the tiffID inside it,
    returns them as a list of dictionaries

    each tiffID is processed as a dictionary containing the:
        * NumDirEntries: number of tags in this tiffID
        * TagList: list of actual tags
        * NextIFDOffset: location of the next tiffID

    it does add two new info:
        * 'IDPosition', to keep track of where that specific tiffID
            is located inside the file
        * 'NextOffsetPosition', to keep track of where the location of the
            file indicating the position about where next offset is
            (given that it is after all the tags and need to be calculated)

    '''
    bfile.seek(0)
    Identifier_Version = bfile.read(4)
    IV = Identifier_Version.hex().upper()
    if not IV == '49492A00':#'4D4D002A' this other value represent little endian,
                            # not supported
      raise AssertionError()
    IFDOffset = bfile.read(4)
    offset = self._bytes_to_int(IFDOffset)
    TifIfd_seq = []
    NextIFDOffset = offset

    while NextIFDOffset != 0: # when it points at 0 means stop reading
      IDPosition = NextIFDOffset
      NumDirEntries, TagList, NextIFDOffset, NextOffsetPosition = self._read_TifIfd(bfile,
                                                                                    NextIFDOffset)
      TifIfd_seq.append({'IDPosition': IDPosition,
                         'NextOffsetPosition': NextOffsetPosition,
                         'NumDirEntries': NumDirEntries,
                         'TagList': TagList,
                         'NextIFDOffset': NextIFDOffset})
    return TifIfd_seq


  def _get_tag_data (self, bfile, tiff_id, tag_code):

    tags = tiff_id['TagList']
    tag = next(tag for tag in tags if tag['TagId'] == tag_code)
    data_type = tag['DataType']
    data_size_in_bytes = self._DataType_bytes[data_type]
    data_offset = tag['DataOffset']
    count = tag['DataCount']
    total_bytes_size = data_size_in_bytes * count
    # if the data is small, the data offset contains the data directly
    if total_bytes_size <= 4:
      return data_offset
    # if the data is bigger than 4 bytes, go to the location
    else:
      bfile.seek(tag['DataOffset'])
      description = bfile.read(total_bytes_size)
      return description


  def _get_ifd (self, filename):

    with open(filename, 'rb') as bfile:
      TifIfd_seq = self._get_all_tiffID(bfile)

    return TifIfd_seq

  def _check (self, filename, ifd_seq):

    with open(filename, 'rb') as bfile:
      for tiff_id in ifd_seq:
        bfile.seek(tiff_id['NextOffsetPosition'])
        NextIFDOffset = self._bytes_to_int(bfile.read(4))
        if not NextIFDOffset == tiff_id['NextIFDOffset']:
          raise AssertionError()

  def _get_position_to_nuke (self, filename, ifd_seq):

    to_nuke_offsets = []
    to_nuke_byte_counts = []

    ID_is_label = []

    with open(filename, 'rb') as bfile:
      for tiff_id in ifd_seq:
        description_0 = self._get_tag_data(bfile, tiff_id, self.TAG_CODES.IMAGEDESCRIPTION)
        description_1 = description_0.decode('utf8')
        description_2 = description_1.splitlines()[1]
        description = description_2.split()[0]
        is_not_label = self._image_size_expression.match(description)
        ID_is_label.append(is_not_label is None)
        if is_not_label:
          continue

        offsets = self._get_tag_data(bfile, tiff_id, self.TAG_CODES.STRIPOFFSETS)
        if not len(offsets) % 4 == 0:
          raise AssertionError()
        dsize = len(offsets) // 4
        offsets = struct.unpack('I' * dsize, offsets)

        byte_counts = self._get_tag_data(bfile, tiff_id, self.TAG_CODES.STRIPBYTECOUNTS)
        if not len(byte_counts) % 4 == 0:
          raise AssertionError()
        byte_counts = struct.unpack('I' * dsize, byte_counts)

        to_nuke_offsets.append(offsets)
        to_nuke_byte_counts.append(byte_counts)

    return (ID_is_label, to_nuke_offsets, to_nuke_byte_counts)


  def _nuke (self, filename, ifd_seq, ID_is_label, to_nuke_offsets, to_nuke_byte_counts, infolog=False):

    infos = dict()

    with open(filename, 'r+b') as bfile:
      EMPTY = b'\x00'

      for offsets, byte_counts in zip(to_nuke_offsets, to_nuke_byte_counts):
        for offset, byte_count in zip(offsets, byte_counts):
          # TODO: offset[1] - offset[0] == byte_count[0]
          if infolog is not None:
            bfile.seek(offset)
            temp = bfile.read(byte_count)
            infos[offset] = temp

          bfile.seek(offset)
          bfile.write(EMPTY * byte_count)

      # FIXME: here I'm working under the assumption that all the images are at the
      # beginning, all the labels are at the end
      # we need to be smarter than this
      position_last_image = sum(not i for i in ID_is_label) - 1
      last_image_id = ifd_seq[position_last_image]
      last_offset = last_image_id['NextOffsetPosition']

      if infolog is not None:
        bfile.seek(last_offset)
        temp = bfile.read(4)
        infos[last_offset] = temp

      bfile.seek(last_offset)
      bfile.write(EMPTY * 4)

    return infos

  def _resurrect (self, filename, ifd_seq, ID_is_label, to_nuke_offsets, to_nuke_byte_counts, infos):

    with open(filename, 'r+b') as bfile:

      for offsets, byte_counts in zip(to_nuke_offsets, to_nuke_byte_counts):
        for offset, byte_count in zip(offsets, byte_counts):

          bfile.seek(offset)
          bfile.write(eval(infos[str(offset)]))

      # FIXME: here I'm working under the assumption that all the images are at the
      # beginning, all the labels are at the end
      # we need to be smarter than this
      position_last_image = sum(not i for i in ID_is_label) - 1
      last_image_id = ifd_seq[position_last_image]
      last_offset = last_image_id['NextOffsetPosition']

      bfile.seek(last_offset)
      bfile.write(eval(infos[str(last_offset)]))


  def anonymize (self, infolog=False):

    TifIfd_seq = self._get_ifd(self._filename)

    if __debug__:
      self._check(self._filename, TifIfd_seq)

    ID_is_label, to_nuke_offsets, to_nuke_byte_counts = self._get_position_to_nuke(self._filename, TifIfd_seq)


    if infolog:

      root, ext = os.path.splitext(self._filename)
      shutil.copyfile(self._filename, root + '_anonym.svs')
      filename = root + '_anonym.svs'

      infos = dict()

    else:
      filename = self._filename

    infos = self._nuke(filename, TifIfd_seq, ID_is_label, to_nuke_offsets, to_nuke_byte_counts, infolog)

    if infolog:

      with open(root + '_info.json', 'w', encoding='utf-8') as log:
        json.dump({str(k) : str(v) for k, v in infos.items()}, log)


  def deanonymize (self, infolog=False):

    if infolog:

      # root, ext = os.path.splitext(self._filename)
      # filename = root + '_anonym.svs'

      TifIfd_seq = self._get_ifd(self._filename)

      if __debug__:
        self._check(self._filename, TifIfd_seq)

      ID_is_label, to_nuke_offsets, to_nuke_byte_counts = self._get_position_to_nuke(self._filename, TifIfd_seq)

      with open(root + '_info.json', 'r', encoding='utf-8') as log:
        infos = json.load(log)

      self._resurrect(self._filename, TifIfd_seq, ID_is_label, to_nuke_offsets, to_nuke_byte_counts, infos)




if __name__ == '__main__':


  svsfile = 'test.svs'

  anonym = SVSAnonymize(svsfile)

  anonym.anonymize(infolog=True)
  anonym.deanonymize(infolog=True)

