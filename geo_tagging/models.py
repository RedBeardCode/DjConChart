#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Add the geo data to the Measurement and CharacteristicValues models.
"""

from django.contrib.gis.db import models
from django.db.models.signals import class_prepared


def add_position(sender, **kwargs):  # pylint: disable=W0613
    """
    Adds a PointField for the position to the Measurement,
    CharacteristicValue Model
    """
    if sender.__name__ in ["Measurement", "CharacteristicValue"]:

        if not hasattr(sender, "position"):
            position = models.PointField("Measurement position",
                                         default="SRID=4326;POINT(7.0 50.0)",
                                         srid=4326,
                                         dim=2,
                                         blank=True,
                                         null=True)
            position.contribute_to_class(sender, "position")


def add_altitude(sender, **kwargs):  # pylint: disable=W0613
    """
    Adds a FloatField for the altitude to the Measurement,
    CharacteristicValue Model
    """
    if sender.__name__ in ["Measurement", "CharacteristicValue"]:
        if not hasattr(sender, "altitude"):
            altitude = models.DecimalField("Altitude of the measurement",
                                           default=0.0,
                                           max_digits=5,
                                           decimal_places=1,
                                           blank=True,
                                           null=True)
            altitude.contribute_to_class(sender, "altitude")


class_prepared.connect(add_position)
class_prepared.connect(add_altitude)
