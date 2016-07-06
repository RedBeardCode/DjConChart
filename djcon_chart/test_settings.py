"""
Overwrites settings for the unit tests
"""

from .settings import *  # pylint: disable=W0401, W0614

MEASUREMENT_FILE_DIR = os.path.join(BASE_DIR, 'test_data')
