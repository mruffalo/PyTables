# -*- coding: utf-8 -*-

########################################################################
#
# License: BSD
# Created: 2005-09-29
# Author: Ivan Vilata i Balaguer - ivan@selidor.net
#
# $Id$
#
########################################################################

"""Test module for compatibility with plain HDF files."""

import os
import shutil
import tempfile

import numpy

import tables
from tables.tests import common
from tables.tests.common import allequal
from tables.tests.common import unittest
from tables.tests.common import PyTablesTestCase as TestCase


class EnumTestCase(common.TestFileMixin, TestCase):
    """Test for enumerated datatype.

    See ftp://ftp.hdfgroup.org/HDF5/current/src/unpacked/test/enum.c.

    """

    h5fname = TestCase._testFilename('smpl_enum.h5')

    def test(self):
        self.assertTrue('/EnumTest' in self.h5file)

        arr = self.h5file.get_node('/EnumTest')
        self.assertTrue(isinstance(arr, tables.Array))

        enum = arr.get_enum()
        expectedEnum = tables.Enum(['RED', 'GREEN', 'BLUE', 'WHITE', 'BLACK'])
        self.assertEqual(enum, expectedEnum)

        data = list(arr.read())
        expectedData = [
            enum[name] for name in
            ['RED', 'GREEN', 'BLUE', 'WHITE', 'BLACK',
             'RED', 'GREEN', 'BLUE', 'WHITE', 'BLACK']]
        self.assertEqual(data, expectedData)


class NumericTestCase(common.TestFileMixin, TestCase):
    """Test for several numeric datatypes.

    See
    ftp://ftp.ncsa.uiuc.edu/HDF/files/hdf5/samples/[fiu]l?{8,16,32,64}{be,le}.c
    (they seem to be no longer available).

    """

    def test(self):
        self.assertTrue('/TestArray' in self.h5file)

        arr = self.h5file.get_node('/TestArray')
        self.assertTrue(isinstance(arr, tables.Array))

        self.assertEqual(arr.atom.type, self.type)
        self.assertEqual(arr.byteorder, self.byteorder)
        self.assertEqual(arr.shape, (6, 5))

        data = arr.read()
        expectedData = numpy.array([
            [0, 1, 2, 3, 4],
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
            [4, 5, 6, 7, 8],
            [5, 6, 7, 8, 9]], dtype=self.type)
        self.assertTrue(common.areArraysEqual(data, expectedData))


class F64BETestCase(NumericTestCase):
    h5fname = TestCase._testFilename('smpl_f64be.h5')
    type = 'float64'
    byteorder = 'big'


class F64LETestCase(NumericTestCase):
    h5fname = TestCase._testFilename('smpl_f64le.h5')
    type = 'float64'
    byteorder = 'little'


class I64BETestCase(NumericTestCase):
    h5fname = TestCase._testFilename('smpl_i64be.h5')
    type = 'int64'
    byteorder = 'big'


class I64LETestCase(NumericTestCase):
    h5fname = TestCase._testFilename('smpl_i64le.h5')
    type = 'int64'
    byteorder = 'little'


class I32BETestCase(NumericTestCase):
    h5fname = TestCase._testFilename('smpl_i32be.h5')
    type = 'int32'
    byteorder = 'big'


class I32LETestCase(NumericTestCase):
    h5fname = TestCase._testFilename('smpl_i32le.h5')
    type = 'int32'
    byteorder = 'little'


class ChunkedCompoundTestCase(common.TestFileMixin, TestCase):
    """Test for a more complex and chunked compound structure.

    This is generated by a chunked version of the example in
    ftp://ftp.ncsa.uiuc.edu/HDF/files/hdf5/samples/compound2.c.

    """

    h5fname = TestCase._testFilename('smpl_compound_chunked.h5')

    def test(self):
        self.assertTrue('/CompoundChunked' in self.h5file)

        tbl = self.h5file.get_node('/CompoundChunked')
        self.assertTrue(isinstance(tbl, tables.Table))

        self.assertEqual(
            tbl.colnames,
            ['a_name', 'c_name', 'd_name', 'e_name', 'f_name', 'g_name'])

        self.assertEqual(tbl.coltypes['a_name'], 'int32')
        self.assertEqual(tbl.coldtypes['a_name'].shape, ())

        self.assertEqual(tbl.coltypes['c_name'], 'string')
        self.assertEqual(tbl.coldtypes['c_name'].shape, ())

        self.assertEqual(tbl.coltypes['d_name'], 'int16')
        self.assertEqual(tbl.coldtypes['d_name'].shape, (5, 10))

        self.assertEqual(tbl.coltypes['e_name'], 'float32')
        self.assertEqual(tbl.coldtypes['e_name'].shape, ())

        self.assertEqual(tbl.coltypes['f_name'], 'float64')
        self.assertEqual(tbl.coldtypes['f_name'].shape, (10,))

        self.assertEqual(tbl.coltypes['g_name'], 'uint8')
        self.assertEqual(tbl.coldtypes['g_name'].shape, ())

        for m in range(len(tbl)):
            row = tbl[m]
        # This version of the loop seems to fail because of ``iterrows()``.
        # for (m, row) in enumerate(tbl):
            self.assertEqual(row['a_name'], m)
            self.assertEqual(row['c_name'], b"Hello!")
            dRow = row['d_name']
            for n in range(5):
                for o in range(10):
                    self.assertEqual(dRow[n][o], m + n + o)
            self.assertAlmostEqual(row['e_name'], m * 0.96, places=6)
            fRow = row['f_name']
            for n in range(10):
                self.assertAlmostEqual(fRow[n], m * 1024.9637)
            self.assertEqual(row['g_name'], ord('m'))


class ContiguousCompoundTestCase(common.TestFileMixin, TestCase):
    """Test for support of native contiguous compound datasets.

    This example has been provided by Dav Clark.

    """

    h5fname = TestCase._testFilename('non-chunked-table.h5')

    def test(self):
        self.assertTrue('/test_var/structure variable' in self.h5file)

        tbl = self.h5file.get_node('/test_var/structure variable')
        self.assertTrue(isinstance(tbl, tables.Table))

        self.assertEqual(
            tbl.colnames,
            ['a', 'b', 'c', 'd'])

        self.assertEqual(tbl.coltypes['a'], 'float64')
        self.assertEqual(tbl.coldtypes['a'].shape, ())

        self.assertEqual(tbl.coltypes['b'], 'float64')
        self.assertEqual(tbl.coldtypes['b'].shape, ())

        self.assertEqual(tbl.coltypes['c'], 'float64')
        self.assertEqual(tbl.coldtypes['c'].shape, (2,))

        self.assertEqual(tbl.coltypes['d'], 'string')
        self.assertEqual(tbl.coldtypes['d'].shape, ())

        for row in tbl.iterrows():
            self.assertEqual(row['a'], 3.0)
            self.assertEqual(row['b'], 4.0)
            self.assertTrue(allequal(row['c'], numpy.array([2.0, 3.0],
                                                           dtype="float64")))
            self.assertEqual(row['d'], b"d")

        self.h5file.close()


class ContiguousCompoundAppendTestCase(common.TestFileMixin, TestCase):
    """Test for appending data to native contiguous compound datasets."""

    h5fname = TestCase._testFilename('non-chunked-table.h5')

    def test(self):
        self.assertTrue('/test_var/structure variable' in self.h5file)
        self.h5file.close()
        # Do a copy to a temporary to avoid modifying the original file
        h5fname_copy = tempfile.mktemp(".h5")
        shutil.copy(self.h5fname, h5fname_copy)
        # Reopen in 'a'ppend mode
        try:
            self.h5file = tables.open_file(h5fname_copy, 'a')
        except IOError:
            # Problems for opening (probably not permisions to write the file)
            return
        tbl = self.h5file.get_node('/test_var/structure variable')
        # Try to add rows to a non-chunked table (this should raise an error)
        self.assertRaises(tables.HDF5ExtError, tbl.append,
                          [(4.0, 5.0, [2.0, 3.0], 'd')])
        # Appending using the Row interface
        self.assertRaises(tables.HDF5ExtError, tbl.row.append)
        # Remove the file copy
        self.h5file.close()  # Close the handler first
        os.remove(h5fname_copy)


class ExtendibleTestCase(common.TestFileMixin, TestCase):
    """Test for extendible datasets.

    See the example programs in the Introduction to HDF5.

    """

    h5fname = TestCase._testFilename('smpl_SDSextendible.h5')

    def test(self):
        self.assertTrue('/ExtendibleArray' in self.h5file)

        arr = self.h5file.get_node('/ExtendibleArray')
        self.assertTrue(isinstance(arr, tables.EArray))

        self.assertEqual(arr.byteorder, 'big')
        self.assertEqual(arr.atom.type, 'int32')
        self.assertEqual(arr.shape, (10, 5))
        self.assertEqual(arr.extdim, 0)
        self.assertEqual(len(arr), 10)

        data = arr.read()
        expectedData = numpy.array([
            [1, 1, 1, 3, 3],
            [1, 1, 1, 3, 3],
            [1, 1, 1, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0],
            [2, 0, 0, 0, 0]], dtype=arr.atom.type)

        self.assertTrue(common.areArraysEqual(data, expectedData))


class SzipTestCase(common.TestFileMixin, TestCase):
    """Test for native HDF5 files with datasets compressed with szip."""

    h5fname = TestCase._testFilename('test_szip.h5')

    def test(self):
        self.assertTrue('/dset_szip' in self.h5file)

        arr = self.h5file.get_node('/dset_szip')
        filters = ("Filters(complib='szip', shuffle=False, fletcher32=False, "
                   "least_significant_digit=None)")
        self.assertEqual(repr(arr.filters), filters)


# this demonstrates github #203
class MatlabFileTestCase(common.TestFileMixin, TestCase):
    h5fname = TestCase._testFilename('matlab_file.mat')

    def test_unicode(self):
        array = self.h5file.get_node(unicode('/'), unicode('a'))
        self.assertEqual(array.shape, (3, 1))

    # in Python 3 this will be the same as the test above
    def test_string(self):
        array = self.h5file.get_node('/', 'a')
        self.assertEqual(array.shape, (3, 1))

    def test_numpy_str(self):
        array = self.h5file.get_node(numpy.str_('/'), numpy.str_('a'))
        self.assertEqual(array.shape, (3, 1))


def suite():
    """Return a test suite consisting of all the test cases in the module."""

    theSuite = unittest.TestSuite()
    niter = 1

    for i in range(niter):
        theSuite.addTest(unittest.makeSuite(EnumTestCase))
        theSuite.addTest(unittest.makeSuite(F64BETestCase))
        theSuite.addTest(unittest.makeSuite(F64LETestCase))
        theSuite.addTest(unittest.makeSuite(I64BETestCase))
        theSuite.addTest(unittest.makeSuite(I64LETestCase))
        theSuite.addTest(unittest.makeSuite(I32BETestCase))
        theSuite.addTest(unittest.makeSuite(I32LETestCase))
        theSuite.addTest(unittest.makeSuite(ChunkedCompoundTestCase))
        theSuite.addTest(unittest.makeSuite(ContiguousCompoundTestCase))
        theSuite.addTest(unittest.makeSuite(ContiguousCompoundAppendTestCase))
        theSuite.addTest(unittest.makeSuite(ExtendibleTestCase))
        theSuite.addTest(unittest.makeSuite(SzipTestCase))
        theSuite.addTest(unittest.makeSuite(MatlabFileTestCase))

    return theSuite


if __name__ == '__main__':
    import sys
    common.parse_argv(sys.argv)
    common.print_versions()
    unittest.main(defaultTest='suite')


## Local Variables:
## mode: python
## py-indent-offset: 4
## tab-width: 4
## fill-column: 72
## End:
