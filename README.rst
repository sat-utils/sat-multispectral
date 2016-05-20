satio
+++++

.. image:: https://travis-ci.org/sat-utils/satio.svg?branch=develop
    :target: https://travis-ci.org/sat-utils/satio

This is a Python library for processing toolkit for Open Raster Data. This is library can be used for creating data specific processing libraries and command line utilities.

Process remote sensing images with this library using two main steps:

1. Assemble all required bands and metadata into a Scene object

2. Create process object with the Scene object and desired functions

Examples
========

**Landsat8:**

.. code-block:: python

    from satio.landsat8 import Landsat8

    filenames = [
        'LC80420362016069LGN00_B11.TIF',
        'LC80420362016069LGN00_B10.TIF',
        'LC80420362016069LGN00_B9.TIF',
        'LC80420362016069LGN00_B8.TIF',
        'LC80420362016069LGN00_B7.TIF',
        'LC80420362016069LGN00_B6.TIF',
        'LC80420362016069LGN00_B5.TIF',
        'LC80420362016069LGN00_B4.TIF',
        'LC80420362016069LGN00_B3.TIF',
        'LC80420362016069LGN00_B2.TIF',
        'LC80420362016069LGN00_B1.TIF'
    ]

    # create a new scene object
    scene = Landsat8(filenames)

    # print list of filenames
    print(scene.filenames())

    # Landsat 8 automatically names each file if the band number is includes in the filename

    print(scene.bands)
    # ['B11', 'B10', 'cirrus', 'pan', 'swir2', 'swir1', 'nir', 'red', 'green', 'blue', 'coastal']

    # select red, green and blue bands, color correct and then save them
    cloud = scene.snow_cloud_coverage()
    rgb = scene.select(['red', 'green', 'blue'])
    rgb.color_correction(cloud).true_color('my_true_color_scene.tif')


**Sentinel2:**

.. code-block:: python

    from satio.sentinel2 import Sentinel2

    filenames = [
        'B01.jp2',
        'B02.jp2',
        'B03.jp2',
        'B04.jp2',
        'B08.jp2',
        'B10.jp2',
        'B11.jp2',
        'B12.jp2',
    ]

    # create a new scene object
    scene = Sentinel2(filenames)

    # print list of filenames
    print(scene.filenames())

    # Sentinel2 automatically names each file if the band number is includes in the filename

    print(scene.bands)
    # ['coastal', 'blue', 'green', 'red', 'nir', 'cirrus', 'swir1', 'swir2']

    # select red, green and blue bands, color correct and then save them
    rgb = scene.select(['red', 'green', 'blue'])
    rgb.color_correction().true_color('my_true_color_scene.tif')


Standard Band Names
===================

Band names are used instead of band numbers, which are unique to each sensor. The average ranges for spectral bandpasses are given in the table below, along with the band numbers for several sensors.

+-----------+-------------+-----------+-----------+-----------+------------+-------+
| Band Name | Band Ranges | Landsat 5 | Landsat 7 | Landsat 8 | Sentinel 2 | MODIS |
+===========+=============+===========+===========+===========+============+=======+
| Coastal   | 0.40 - 0.45 |           |           | 1         | 1          |       |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| Blue      | 0.45 - 0.5  | 1         | 1         | 2         | 2          | 3     |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| Green     | 0.5 - 0.6   | 2         | 2         | 3         | 3          | 4     |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| Red       | 0.6 - 0.7   | 3         | 3         | 4         | 4          | 1     |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| Pan       | 0.5 - 0.7   |           | 8         | 8         |            |       |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| NIR       | 0.77 - 1.00 | 4         | 4         | 5         | 8          | 2     |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| Cirrus    | 1.35 - 1.40 |           |           | 9         | 10         | 26    |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| SWIR1     | 1.55 - 1.75 | 5         | 5         | 6         | 11         | 6     |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| SWIR2     | 2.1 - 2.3   | 7         | 7         | 7         | 12         | 7     |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| LWIR      | 10.5 - 12.5 | 6         | 8         |           |            |       |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| LWIR1     | 10.5 - 11.5 |           |           | 10        |            | 31    |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
| LWIR2     | 11.5 - 12.5 |           |           | 11        |            | 32    |
+-----------+-------------+-----------+-----------+-----------+------------+-------+
