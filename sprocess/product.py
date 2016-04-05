"""
    Product classes which represent files on disk and processing required
"""

import os
import re
import gippy
import gippy.algorithms as algs

from six import iteritems, iterkeys, itervalues


# example band descriptions
_band_descriptions = {
    'coastal':  'Coastal band (~0.43um)',
    'pan':      'Panchromatic band',
    'blue':     'Blue band',
    'green':    'Green band',
    'red':      'Red band',
    'nir':      'Near IR band',
    'cirrus':   'Cirrus cloud detection band (~1.38um)',
    'swir1':    'Shortwave IR band (~1.65um)',
    'swir2':    'Shortwave IR band (~2.2um)',
    'quality':  'quality metric'
}


class ImageFiles(object):
    """ Collection of image files """

    def __init__(self, filenames):
        """ Creates gippy GeoImage from the filenames provided.
        filenames could be a list or a dictionary. A list should include the path to every image.
        A dictionary should have the filepath as key and a list of bands as value.
        list of bands should be in the order the bands are saved in the file.
        Make sure to use band names instead of numbers

        Example:

        image1 = ImageFiles(['path/to/file1.tif', 'path/to/file2.tif', 'path/to/file3.tif'])
        image2 = ImageFiles({
            'path/to/file1.tif': ['red', 'green', 'blue'],
            'path/to/file2.tif': ['green']
        })

        image1.open()
        image2.open()

        """
        self.only_files = None
        self.file_bands = None

        if isinstance(filenames, list):
            self.only_files = filenames

        elif isinstance(filenames, dict):
            for bands in itervalues(filenames):
                if not isinstance(bands, list):
                    raise Exception('bands must be list')
            self.file_bands = filenames
        else:
            raise Exception('Filenames must be a list or a dictionary')

    def open(self):
        """ Open filenames as a GeoImage with bandnames """

        if self.only_files:
            return gippy.GeoImage(self.only_files)
        elif self.file_bands:
            # making sure the filenames and bands are in the right order
            # for example if the first file has one band, the second file has 3 bands
            # the third file has 2 bands, iteration below ensures everything are
            # in the right order
            filenames = []
            bands = []
            for f, bs in iteritems(self.file_bands):
                filenames.append(f)
                bands.extend(bs)

            geoimg = gippy.GeoImage(filenames)
            for i, band in enumerate(bands):
                geoimg.SetBandName(band, i + 1)

            return geoimg
        else:
            raise Exception('Unexpected error!')


class Product(object):
    """ A Product is some input (either files, or another series of Products)
        and some processing performed on that input. """

    description = 'Product Base Class'

    # dependencies in the form {product: [bands]}
    dependencies = {}

    # map of original band names to common bandnames
    _bandmap = {}

    def __init__(self, input_products=None, filenames=None):
        """ Create a new output product from input product """
        self.files = filenames
        if filenames is not None:
            # get lists from filenames
            bandnames = sorted(filenames.keys())
            filenames = [filenames[f] for f in sorted(filenames.keys())]
            self.files = ImageFiles(filenames, bandnames)
        self.input_products = input_products
        if self.files is None and self.input_products is None:
            raise Exception('cannot create a product from nothing')

    @classmethod
    def name(cls):
        return cls.__name__.lower()

    @classmethod
    def pattern(cls):
        """ Regular expression for matching product files with 2 groups: basename and product/band """
        return r'(.*)_(%s.*)' % (cls.name())

    def process(self, outfile=None, outpath='./', overwrite=False):
        """ Perform processing on input product and return output GeoImage """
        if overwrite and self.input_products is not None:
            self.files = None
        if self.files is not None:
            # if files already exist just return those
            geoimg = self.files.open()
        else:
            # get first input product. child classes must
            # retrieve others (if any) themselves!
            geoimg = self.input_products[0].process()
        # if outfile is not supplied, generate name based on input image basename
        if outfile is None:
            outfile = os.path.join(outpath, geoimg.Basename() + '_' + self.name())
        # name of output file (when processed), for the benefit of child
        # classes calling this function via super()
        self.outfile = outfile

        return geoimg

    def save(self, geoimg, outfile=None, outpath='./', overwrite=False):
        """ Save geoimg to file and add filenames to instance """
        # reset to force save anyway
        if overwrite and self.input_products is not None:
            self.files = None
        if self.files is None:
            # create an output filename if not provided
            if outfile is None:
                outfile = os.path.join(outpath, geoimg.Basename() + '_' + self.name())
            geoimg.save(outfile)
            self.files = ImageFiles({'': outfile})

    def add_parser(self, parser):
        """ Add options for this product to this command line parser """
        parser.add_argument('--%s' % self.name(), help=self.description, default=False, action='store_true')

    @classmethod
    def parse_filename(cls, filename):
        """ Parse filename for basename and bandname (remapped if _bandmap) """
        m = re.match(cls.pattern(), os.path.basename(filename))
        basename = m.group(1)
        bandname = cls._bandmap.get(m.group(2), m.group(2))
        return basename, bandname

    @classmethod
    def create_from_filenames(cls, filenames):
        """ Parse filenames for any matching this product """
        filenames2 = [f for f in filenames if re.match(cls.pattern(), os.path.basename(f))]
        if len(filenames2) > 1:
            # extract bandnames ('_suffix' of filename, no extension)
            bandnames = [cls.parse_filename(b)[1] for b in filenames2]
            return cls(filenames=dict(zip(bandnames, filenames2)))
        elif len(filenames2) == 1:
            # product in single file (most common outside of original files)
            return cls(filenames={'': filenames2[0]})
        else:
            return None


class DC(Product):
    """ Digital counts from sensor """
    description = 'Digital counts'


class TOA(Product):
    """ Top of the Atmosphere reflectance """
    description = 'Top of the Atmosphere (TOA) Reflectance'
    dependencies = {
        'dc': []
    }

    def process(self, **kwargs):
        geoimg = super(TOA, self).process(**kwargs)
        # set gain and offsets to bring to reflectance
        return geoimg


class NDVI(Product):
    description = 'Normalized Difference Vegetation Index (NDVI) from TOA reflectance'
    dependencies = {
        'toa': ['nir', 'red']
    }

    def process(self, **kwargs):
        geoimg = super(NDVI, self).process(**kwargs)
        if self.files is None:
            prods = {'ndvi': self.outfile}
            fouts = algs.Indices(geoimg, prods)
            self.files = ImageFiles(fouts.values()[0])
            geoimg = self.files.open()
        return geoimg


class Indices(Product):
    description = 'Band Indices'
    dependencies = {
        'toa': {}
    }

    def process(self, **kwargs):
        geoimg = super(NDVI, self).process(**kwargs)
        # get complete product list from kwargs
        #fouts = algs.Indices(geoimg, prods)
        #self.files = ImageFiles(fouts.values())
        return None


class Color(Product):
    """ Stretch 3 input bands to create 3 band color image """

    description = 'Stretch 3 input bands to create 3band color image'

    dependencies = {
        'dc': []
    }

    def process(self, **kwargs):
        """ Process data into output product """
        geoimg = super(Color, self).process(**kwargs)
        geoimg = self.input_product.open()
        return geoimg


class PanSharpen(Product):
    description = 'Sharpen bands with higher resolution panchromatic band'

    def process(self):
        pass
        # geoimage will need to return higher resolution band separately?
