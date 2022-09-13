#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np # Numpy package provides an advanced array type with various in-built functions.

def main(importdata, calculateaverage):
    months = np.arange(12) + 1 # 1 .. 24
    hours = np.arange(24) # 0 .. 23
    azimuths = np.arange(0,360,15) # 0, 15 .. 345
    tilts = np.arange(10,31,10) # 10, 20, 30
    SEP = '\t'

    if importdata:
        # Import raw data. Data will be imported as string since Date is formatted
        # as string.
        data_raw = np.genfromtxt('out.csv', delimiter='\t', dtype=str, skip_header=1)

        # Split the data into Day and Month. Therefore a column is added to
        # data_raw.
        length = data_raw.shape[0]
        data = np.zeros((length, data_raw.shape[1]+1))
        data[:,2:] = data_raw[:,1:]
        for idx in range(length):
            data[idx,0:2] = np.array(data_raw[idx,0].split('-')).astype(int)
        with open('data.npy', 'wb') as f:
            np.save(f, data)
    else:
        data = np.load('data.npy')

    if calculateaverage:
        # Compute average ACWattHour across days in month for each hour and setting
        # of azimuth and tilt.
        res = np.zeros((len(months), len(hours), len(azimuths), len(tilts)))
        for month in months:
            data_for_month = data[ data[:,1] == month ][:,2:] # remove Day and Month column
            for hour in hours:
                data_for_hour = data_for_month[ data_for_month[:,0] == hour][:,1:] # remove Hour column
                for azimuth in azimuths:
                    data_for_azimuth = data_for_hour[ data_for_hour[:,0] == azimuth][:,1:] # remove Azimuth column
                    for tilt in tilts:
                        data_for_tilt = data_for_azimuth[ data_for_azimuth[:,0] == tilt ]
                        res[months == month,
                                hours == hour,
                                azimuths == azimuth,
                                tilts == tilt] = np.average(data_for_tilt, axis=0)[1]
        with open('hourly_ackwh_average.npy', 'wb') as f:
            np.save(f, res)
    else:
        res = np.load('hourly_ackwh_average.npy')
 
    # Write results back to file.
    with open('ac_out_writeline.csv', 'w') as f:
        header = 'Date' + SEP + SEP.join(['{}-{}'.format(a,t) for t in tilts for a in azimuths])
        f.write(header + '\n')
        for month in months:
            m = np.where(months == month)[0][0]
            for h in hours:
                line = '{:02d}-{:02d}'.format(month, h) + SEP
                line += SEP.join( ['{:.4f}'.format(ac)
                    for t in tilts for ac in res[m, h, :, np.where(tilts == t)[0][0]] ])
                f.write(line + '\n')
           
    return 0

if __name__ == "__main__":
    importdata = False
    calculateaverage = False
    main(importdata, calculateaverage)
