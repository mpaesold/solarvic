import Settings
import DailyWACOutput as dwaco
import numpy as np
import os

def main():
    infile = os.path.join( os.path.curdir, 'input', 'pv_config.csv')
    data = np.loadtxt( infile, skiprows=1)
    long = data[0,0]
    lat = data[0, 1]
    azimuth_tilts = data[:,2:4]
    areas = data[:,4]

    outfile = os.path.join( os.path.curdir, 'output',
                           'out_lat{}_long{}.csv'.format(lat, long) )

    print('Lat:', lat, 'Long:', long)
    print('Azimuths and tilts:', azimuth_tilts)
    print('Areas:', areas)

    dailywacouput = dwaco.DailyWACOutput(
            lat, long,
            Settings.nrel_api_key, azimuth_tilts)

    dwaco.scan_azimuths_tilts(dailywacouput)
    dwaco.write_average_ac_to_csv( dailywacouput, outfile )
    return 0

if __name__ == "__main__":
    main()
