import Settings
import DailyWACOutput as dwaco
import numpy as np
import os

def main():
    dailywacouput = dwaco.DailyWACOutput(
            Settings.lat,
            Settings.long,
            Settings.nrel_api_key, 180, 10, 31, 15)

    dwaco.scan_azimuths_tilts(dailywacouput)
    outfile = os.path.join( os.path.curdir, 'output',
                           'out_lot{}_long{}.csv'.format(Settings.lat,
                                                         Settings.long) )
    dwaco.write_average_ac_to_csv( dailywacouput, outfile )
    return 0

if __name__ == "__main__":
    main()
