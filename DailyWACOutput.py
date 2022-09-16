import numpy as np
from urllib.request import urlopen
import json
import os

class DailyWACOutput:
    url = "https://developer.nrel.gov/api/pvwatts/"
    version = "v6"
    format = "json"  # json or xml
    system_capacity = 1
    array_type = 1
    module_type = 1
    losses = 15
    months = np.arange(12) # 0 .. 23
    hours = np.arange(24) # 0 .. 23
    daysPerMonth = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    
    def __init__(self,
            lat, long,
            azimuth_granularity=15,
            tilt_min=10, tilt_max=30, tilt_granularity=10, api_key):
        self.lat = lat
        self.long = long
        self.api_key = api_key
        self.azimuths = np.arange(0, 360, azimuth_granularity) # 0, 15 .. 345
        self.tilts = np.arange(tilt_min, tilt_max, tilt_granularity) # 10, 20, 30
        self.daily_average_acout = np.zeros( (len(self.months),
            len(self.hours),
            len(self.azimuths),
            len(self.tilts)) )
        self.monthindex = np.array( [ [ np.sum( self.daysPerMonth[:m] ), np.sum( self.daysPerMonth[:m+1] )]
                  for m in self.months ] )
        return None
    
    def azimuths_tilts( self ):
        for t in self.tilts:
            for az in self.azimuths:
                yield (t, az)

    def generate_request_url( self, azimuth, tilt ):
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
    
    def query_acoutput_from_nrel( self, requesturl ):
        # TODO: Handle exception correctly.
        # Calculate average on an ongoing basis and store last
        # successful API reuqest in order to be able to restart.
        with urlopen( requesturl, timeout=2) as response:
            out = json.loads(response.read())
        return np.array( out['outputs']['ac'] )
    
    def scan_azimuths_tilts( self ):
    # Iterate over all settings of Azimuth and Tilt at lat/long coordignates
    # and query AC Power output
        for (tilt, az) in self.azimuths_tilts():
            print(az, tilt)
            rurl = self.generate_request_url( az, tilt )
            ac_out = self.query_acoutput_from_nrel( rurl )
            self.calculate_daily_ac_average( ac_out, az, tilt)
        return None

    def calculate_daily_ac_average(self, wac, az, tilt):
        """
        Calculate average Wac output for each month and a fixed seting of
        azimuth and tilt.
        """
        wac = wac.reshape( (365, 24) )
        for m in self.months:
            # Average over hours for each month and
            m0 = self.monthindex[m,0] # First day in year of month m
            m1 = self.monthindex[m,1] # Last day in year of month m
            self.daily_average_acout[ m, :, 
                                     self.azimuths == az,
                                     self.tilts == tilt ] = np.average( wac[ m0:m1,:], axis=0 )
        return None
    
    def write_average_ac_to_csv( self, SEP='\t' ):
    # Pivot list to months/days and azimuth/tilt
        with open('./output/ac_out_writeline.csv', 'w') as f:
            header = 'Date' + SEP + \
                SEP.join(['A:{}-T:{}'.format(a,t) for t in self.tilts for a in self.azimuths])
            f.write(header + '\n')
            for month in self.months:
                for h in self.hours:
                    line = 'M:{:02d}-H:{:02d}'.format(month+1, h) + SEP
                    line += SEP.join( ['{:.4f}'.format(ac)
                        for t in self.tilts for ac in
                                            self.daily_average_acout[month, h, :, np.where(self.tilts == t)[0][0]] ])
                    f.write(line + '\n')
        return None
