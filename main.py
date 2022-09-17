import Settings
import DailyWACOutput as dwaco
import numpy as np
import os

def main():
    infile = os.path.join( os.path.curdir, 'input', 'pv_config.csv')
    outfile = os.path.join( os.path.curdir, 'output',
                           'out_lot{}_long{}.csv'.format(Settings.lat,
                                                         Settings.long) )
    #pvArrayArrangement = np.loadtxt( infile, skiprow=0)
    #expectedPowerOut = np.zeros((24, 12))

    dailywacouput = dwaco.DailyWACOutput(
            Settings.lat,
            Settings.long,
            Settings.nrel_api_key, 180, 10, 31, 15)

    dwaco.scan_azimuths_tilts(dailywacouput)
    dwaco.write_average_ac_to_csv( dailywacouput, outfile )
    return 0

if __name__ == "__main__":
    main()
