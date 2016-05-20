import unittest
from stestdata import TestData
from satio.scene import Scene


class TestScene(unittest.TestCase):

    def setUp(self):
        self.t = TestData('landsat8')
        self.filenames = self.t.files[self.t.names[0]]
        self.bandnames = self.t.bands[self.t.names[0]]

    def test_scene_filenames_only(self):
        """ Test creation of Scene object with only filenames """
        images = Scene(self.filenames)
        self.assertTrue(isinstance(images, Scene))
        self.assertEqual(images.nbands(), len(self.t.files[self.t.names[0]]))

    def test_scene_filenames_and_bands(self):
        """ Test creation of Scene object with filenames and bands"""
        images = Scene(self.filenames)
        self.assertEqual(images.nbands(), len(self.filenames))

    def test_scene_wrong_input(self):

        with self.assertRaises(Exception):
            Scene('path/to/file')

        with self.assertRaises(Exception):
            Scene({'path/to/file': 'red'})

    def test_scene_bands(self):
        scene = Scene(self.filenames)
        # Get bands names after opening the files
        bands = scene.bands
        self.assertTrue(isinstance(bands, list))
        self.assertEqual(len(bands), 10)

    def test_select(self):
        scene = Scene(self.filenames)
        scene.set_bandnames(self.bandnames)
        self.assertEqual(scene.band_numbers, 10)

        scene2 = scene.select(['red', 'nir'])
        self.assertEqual(scene.band_numbers, 10)
        self.assertEqual(scene2.band_numbers, 2)
