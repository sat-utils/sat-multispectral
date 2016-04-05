import os
import glob
import unittest

from gippy import GeoImage
from sprocess.product import ImageFiles


class TestProduct(unittest.TestCase):

    def setUp(self):

        self.test_dir = os.path.join(os.path.dirname(__file__), 'samples/landsat8')
        self.files = glob.glob(os.path.join(self.test_dir, '*.tif'))

    def test_imagefiles_filenames_only(self):
        """ Test creation of ImageFiles object with only filenames """
        images = ImageFiles(self.files)
        imgs = images.open()
        self.assertTrue(isinstance(imgs, GeoImage))
        self.assertEqual(imgs.NumBands(), len(self.files))

    def test_imagefiles_filenames_and_bands(self):
        """ Test creation of ImageFiles object with filenames and bands"""
        landsat8 = {
            'B1': 'coastal',
            'B2': 'blue',
            'B3': 'green',
            'B4': 'red',
            'B5': 'nir',
            'B6': 'swir1',
            'B7': 'swir22',
            'B8': 'pan',
            'B9': 'cirrus',
            'BQA': 'quality'
        }

        file_dict = {}

        for f in self.files:
            band = f.split('_')[-1].split('.')[0]
            if band in landsat8:
                file_dict[f] = [landsat8[band]]

        images = ImageFiles(file_dict)
        imgs = images.open()
        self.assertTrue(isinstance(imgs, GeoImage))
        self.assertEqual(imgs.NumBands(), len(file_dict))

    def test_imagefiles_wrong_input(self):

        with self.assertRaises(Exception):
            ImageFiles('path/to/file')

        with self.assertRaises(Exception):
            ImageFiles({'path/to/file': 'red'})

    # def test_product(self):
    #     """ Test init of product from ImageFiles """
    #     pass

    # def test_create_from_files(self):
    #     """ Test creation of product from list of filenames (some invalid) """
    #     pass

    # def test_process(self):
    #     """ Test process of product """
    #     pass

    # def test_process_with_dependencies(self):
    #     """ Test processing of product with dependencies """
    #     pass
