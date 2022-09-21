#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compute power consumption
"""
import numpy as np

def import_holidays(holidays_file):
    """
    Import holidays from file.
    """
    return np.genfromtxt(holidays_file, usecols=(0), dtype='datetime64[D]',
                             skip_header=1, delimiter=',')

def import_consumption(consumption_file):
    """
    Import consumption from file.
    """
    return np.genfromtxt(consumption_file, usecols=(1, 2, 6, 7),
                                dtype=('datetime64[m]', int, float, 'U4'),
                                skip_header=1, delimiter=',')


def main():
    return 0

if __name__ == "__main__":
    main()

