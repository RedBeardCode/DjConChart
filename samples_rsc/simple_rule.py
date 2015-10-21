from numpy import genfromtxt


def calculate(measurements):
    value = 0.0
    for meas_file in measurements:
        data = genfromtxt(meas_file)
        value += data.sum()
    return value
