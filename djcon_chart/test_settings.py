"""
Overwrites settings for the unit tests
"""

from .dev_settings import *  # pylint: disable=W0401, W0614

MEASUREMENT_FILE_DIR = os.path.join(BASE_DIR, 'test_data')

if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'travisci',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '',

        }
    }

GDAL_LIBRARY_PATH = ''
