"""
Test code for creating sample data
"""
from numpy import genfromtxt


def calculate(measurements):
    """
    Creates the sum of the values in the measurement files
    """
    value = 0.0
    for meas_file in measurements:
        data = genfromtxt(meas_file)
        value += data.sum()
    return value
