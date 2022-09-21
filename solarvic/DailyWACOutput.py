import numpy as np
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt

months = np.arange(12) # 0 .. 23
hours = np.arange(24) # 0 .. 23
daysPerMonth = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])


# Class definitions

class DailyWACOutput:
    
    def __init__(self,
                 lat, long, api_key, azimuth_tilts):
        """
        Creator for class DailyWACOutput.
        """
        self.lat = lat
        self.long = long
        self.api_key = api_key
        self.azimuth_tilts = azimuth_tilts
        self.daily_average_acout = np.zeros( (len(months),
            len(hours),
            len(self.azimuth_tilts) ))
        self.monthindex = np.array( [ [ np.sum( daysPerMonth[:m] ), np.sum( daysPerMonth[:m+1] )]
                  for m in months ] )
        return None
    
    def generate_request_url( self, azimuth, tilt,
                             url = "https://developer.nrel.gov/api/pvwatts/",
                             version = "v6",
                             format = "json",  # json or xml
                             system_capacity = '1',
                             array_type = '1',
                             module_type = '1',
                             losses = '15'):
        """
        Returns a string for the request URL that can be sent to NREL.
        """
        requesturl = url + version + '.' + format \
            + '?api_key=' + self.api_key \
            + '&lat=' + str(self.lat) + '&lon=' + str(self.long) \
            + '&system_capacity=' + system_capacity \
            + '&azimuth=' + str(azimuth) + '&tilt=' + str(tilt) \
            + '&array_type=' + array_type \
            + '&module_type=' + module_type \
            + '&losses=' + losses \
            + '&timeframe=hourly'
        return requesturl

    def query_acoutput_from_nrel(self, requesturl):
        """
        Sends query to NREL and returns the AC Power as array
        """
        # TODO: Handle exception correctly.
        # Calculate average on an ongoing basis and store last
        # successful API request in order to be able to restart.
        with urlopen(requesturl, timeout=2) as response:
            out = json.loads(response.read())
        return np.array(out['outputs']['ac'])

    def calculate_daily_ac_average(self, wac, az, tilt):
        """
        Calculate average Wac output for each month and a fixed setting of
        azimuth and tilt.
        """
        wac = wac.reshape( (365, 24) )
        for m in months:
            # Average over hours for each month and
            m0 = self.monthindex[m,0] # First day in year of month m
            m1 = self.monthindex[m,1] # Last day in year of month m
            self.daily_average_acout[ m, :, 
                                     (self.azimuth_tilts[:,0] == az) *
                                     (self.azimuth_tilts[:,1] == tilt) ] = np.average( wac[ m0:m1,:], axis=0 )
        return None


# Module Functions

def scan_azimuths_tilts(dwaco):
    """
    Main function that scans all azimuth and tilt settings and sends
    queries to NREL.
    Results are stored iteratively.
    """
    # Iterate over all settings of Azimuth and Tilt at lat/long coordinates
    # and query AC Power output
    for (az, tilt) in dwaco.azimuth_tilts:
        print(az, tilt)
        rurl = dwaco.generate_request_url(az, tilt)
        ac_out = dwaco.query_acoutput_from_nrel(rurl)
        dwaco.calculate_daily_ac_average(ac_out, az, tilt)
    return None


def write_average_ac_to_csv(dwaco, outfile, SEP='\t', WACFORMAT='{:.4f}',
                            DATE='M:{:02d}-H:{:02d}', HEADER='A:{}-T:{}'):
    """
    Writes the average AC power to CSV file.
    """
    with open(outfile, 'w') as f:
        header = 'Date' + SEP + \
            SEP.join([HEADER.format(a,t) for (a, t) in dwaco.azimuth_tilts ])
        f.write(header + '\n')
        for month in months:
            for h in hours:
                line = DATE.format(month+1, h) + SEP
                line += SEP.join( [ WACFORMAT.format(
                    dwaco.daily_average_acout[ month, h, \
                        (dwaco.azimuth_tilts[:,0] == a) * \
                        (dwaco.azimuth_tilts[:,1] == t) ][0] ) \
                        for (a, t) in dwaco.azimuth_tilts ] )
                f.write(line + '\n')
    return None

def calculate_power_output_hourly( dwaco, areas ):
    """
    Calculate expected power output per hour of day by month.
    """
    pout = np.zeros((len(hours), len(months)))
    for m in months:
        for h in hours:
            pout[h, m] = np.dot(dwaco.daily_average_acout[m, h, :], areas) 
    return pout / 1000.0

def calculate_power_output_daily(pout_hr):
    """
    Sum hourly power output and return daily power output.
    """
    return np.sum(pout_hr, axis=0)

def calculate_power_output_monthly(pout_day):
    """
    Calculate expected power output for whole month.
    """
    return pout_day * daysPerMonth

def plot_hourly_power_output(pout, outfile, savefig=True):
    """
    Plot typical day power output
    """
    plt.plot(pout)
    plt.ylabel('A/C Power Output (kW)')
    plt.xlabel('Hour')
    plt.xticks( hours )
    plt.legend( months+1 )
    plt.title( 'Typical day power output' )
    plt.grid(visible=True, axis='y')
    if savefig:
        plt.savefig(outfile)
    else:
        plt.show()
    return None
