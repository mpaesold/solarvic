import numpy as np
from urllib.request import urlopen
import json


# Class definitions

class DailyWACOutput:
    url = "https://developer.nrel.gov/api/pvwatts/"
    version = "v6"
    format = "json"  # json or xml
    system_capacity = 1
    array_type = 1
    module_type = 1
    losses = 15
    months = np.arange(12)  # 0 .. 23
    hours = np.arange(24)  # 0 .. 23
    daysPerMonth = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

    def __init__(self,
                 lat, long, api_key,
                 azimuth_granularity=15,
                 tilt_min=10, tilt_max=30, tilt_granularity=10):
        """
        Creator for class DailyWACOutput.
        """
        self.lat = lat
        self.long = long
        self.api_key = api_key
        self.azimuths = np.arange(0, 360, azimuth_granularity)  # 0, 15 .. 345
        self.tilts = np.arange(tilt_min, tilt_max, tilt_granularity)  # 10, 20, 30
        self.daily_average_acout = np.zeros((len(self.months),
                                             len(self.hours),
                                             len(self.azimuths),
                                             len(self.tilts)))
        self.monthindex = np.array([[np.sum(self.daysPerMonth[:m]), np.sum(self.daysPerMonth[:m + 1])]
                                    for m in self.months])
        return None

    def azimuths_tilts(self):
        """
        Generator that yields all possible combinations of azimuth and tilt
        settings.
        """
        for t in self.tilts:
            for az in self.azimuths:
                yield (t, az)

    def generate_request_url(self, azimuth, tilt):
        """
        Returns a string for the request URL that can be sent to NREL.
        """
        requesturl = self.url + self.version + '.' + self.format \
                     + '?api_key=' + self.api_key \
                     + '&lat=' + str(self.lat) + '&lon=' + str(self.long) \
                     + '&system_capacity=' + str(self.system_capacity) \
                     + '&azimuth=' + str(azimuth) + '&tilt=' + str(tilt) \
                     + '&array_type=' + str(self.array_type) \
                     + '&module_type=' + str(self.module_type) \
                     + '&losses=' + str(self.losses) \
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
        Calculate average Wac output for each month and a fixed seting of
        azimuth and tilt.
        """
        wac = wac.reshape((365, 24))
        for m in self.months:
            # Average over hours for each month and
            m0 = self.monthindex[m, 0]  # First day in year of month m
            m1 = self.monthindex[m, 1]  # Last day in year of month m
            self.daily_average_acout[m, :,
            self.azimuths == az,
            self.tilts == tilt] = np.average(wac[m0:m1, :], axis=0)
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
    for (tilt, az) in dwaco.azimuths_tilts():
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
                 SEP.join([HEADER.format(a, t) for t in dwaco.tilts for a in dwaco.azimuths])
        f.write(header + '\n')
        for month in dwaco.months:
            for h in dwaco.hours:
                line = DATE.format(month + 1, h) + SEP
                line += SEP.join([WACFORMAT.format(ac)
                                  for t in dwaco.tilts for ac in
                                  dwaco.daily_average_acout[month, h, :,
                                  np.where(dwaco.tilts == t)[0][0]]])
                f.write(line + '\n')
    return None
