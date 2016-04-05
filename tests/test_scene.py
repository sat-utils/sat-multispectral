#!/usr/bin/env python

import os
import shutil
import unittest
from sprocess import Scene
import gippy


class _BaseTestScene(unittest.TestCase):

    scene_class = Scene

    sceneid = 'test'

    testdir = os.path.join(os.path.dirname(__file__), 'images')

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.testdir):
            os.mkdir(cls.testdir)
        gippy.Options.SetVerbose(3)

    @classmethod
    def tearDownClass(cls):
        """ Clean up after tests """
        shutil.rmtree(cls.testdir)

    def setUp(self):
        self.scene = self.scene_class.seed_from_directory(self.testdir)

    def test_create_from_directory(self):
        """ Test creating a scene from directory of images """
        scene = self.scene.seed_from_directory(self.testdir)
        geoimg = scene.process('toa')
        self.assertTrue(geoimg.Basename(), self.sceneid)

    def test_dc(self):
        """ Test DC product (if exists) """
        if 'dc' in self.scene._products:
            geoimg = self.scene.process('dc')
            img = geoimg.Read()
            self.assertTrue(img.shape == (geoimg.NumBands(), 1, geoimg.XSize(), geoimg.YSize()))
            # how else to test DC values ???

    # generalize this into loop through test all products
    def test_ndvi(self):
        """ Test calculating NDVI product """
        self.scene.process('ndvi', outfile=os.path.join(self.testdir, '%s_ndvi.tif' % self.sceneid))
        # check with numpy against original band
        #geoimg1 = scene.products['']


class _TestScene(_BaseTestScene):
    """ Perform all _BaseTestScene tests with small generic images """

    @classmethod
    def setUpClass(cls):
        """ Create some test images """
        super(TestScene, cls).setUpClass()
        fout = os.path.join(cls.testdir, '%s_dc.tif' % cls.sceneid)
        if not os.path.exists(fout):
            geoimg = gippy.GeoImage(fout, 100, 100, 4, gippy.DataType('Float64'))
            # geoimg.SetBandNames(['blue', 'green', 'red', 'nir'])
            geoimg.SetBandName('blue', 1)
            geoimg.SetBandName('green', 2)
            geoimg.SetBandName('red', 3)
            geoimg.SetBandName('nir', 4)
        else:
            geoimg = gippy.GeoImage(fout)
        geoimg['nir'] = geoimg['nir'] + 2
        geoimg['red'] = geoimg['red'] + 1
        # save with some values for nir and red
        geoimg.Process()
        geoimg = None
