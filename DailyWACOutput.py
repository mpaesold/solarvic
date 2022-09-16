import numpy as np
import Settings
from urllib.request import urlopen
import json
import os

class DailyWACOutput:
    url = "https://developer.nrel.gov/api/pvwatts/"
    version = "v6"
    format = "json"  # json or xml
    api_key = Settings.nrel_api_key
    system_capacity = 1
    array_type = 1
    module_type = 1
    losses = 15
    months = np.arange(12) + 1 # 1 .. 24
    hours = np.arange(24) # 0 .. 23
    daysPerMonth = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    
    def __init__(self,
            lat, long,
            azimuth_granularity=15,
            tilt_min=10, tilt_max=30, tilt_granularity=10):
        self.lat = lat
        self.long = long
        self.azimuths = np.arange(0,360,azimuth_granularity) # 0, 15 .. 345
        self.tilts = np.arange(tilt_min,tilt_max,tilt_granularity) # 10, 20, 30
        self.SEP = '\t'
        self.acOut_date_hours_azimuth_tilt = self.__ac_output_azimuth_tilt()
        return None
    
    def __dates_hours( self ):
        datesHours = np.zeros((len(self.hours) * np.sum(self.daysPerMonth), 3))
        idx = 0
        for month in self.months:
            m = np.where(self.months == month)[0][0]
            days = np.arange(self.daysPerMonth[m])+1
            for day in days:
                datesHours[idx : idx + len(self.hours),0] = month
                datesHours[idx : idx + len(self.hours),1] = day
                datesHours[idx : idx + len(self.hours),2] = self.hours
                idx += len(self.hours)
        return datesHours
    
    def __ac_output_azimuth_tilt( self ):
        datesHours = self.__dates_hours()
        ac_output_azimuth_tilt = np.zeros((len(self.hours)
                                        * np.sum(self.daysPerMonth)
                                        * len(self.azimuths)
                                        * len(self.tilts), 6))
        idx = 0
        for az in self.azimuths:
            for tilt in self.tilts:
                ac_output_azimuth_tilt[idx :
                    idx + len(self.hours) * np.sum(self.daysPerMonth), 0:3] = datesHours
                ac_output_azimuth_tilt[idx :
                    idx + len(self.hours) * np.sum(self.daysPerMonth), 3] = az
                ac_output_azimuth_tilt[idx :
                    idx + len(self.hours) * np.sum(self.daysPerMonth), 4] = tilt
                idx += len(self.hours) * np.sum(self.daysPerMonth)
        return ac_output_azimuth_tilt
    
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
        return out['outputs']['ac']
    
    def scan_azimuths_tilts( self ):
    # Iterate over all settings of Azimuth and Tilt at lat/long coordignates
    # and query AC Power output
        for (tilt, az) in self.azimuths_tilts():
            print(az, tilt)
            rurl = self.generate_request_url( az, tilt )
            ac_out = self.query_acoutput_from_nrel( rurl )
            # Write AC Power output to list
            self.acOut_date_hours_azimuth_tilt[
                (self.acOut_date_hours_azimuth_tilt[:, 3] == az)
                * (self.acOut_date_hours_azimuth_tilt[:, 4] == tilt),
                -1] = ac_out
        return None
    
    def calculate_daily_ac_average( self ):
        res = np.zeros( (len(self.months),
            len(self.hours),
            len(self.azimuths),
            len(self.tilts)) )
        data = self.acOut_date_hours_azimuth_tilt
        for month in self.months:
            data_for_month = data[ data[:,0] == month ][:,2:] # remove Day and Month column
            for hour in self.hours:
                data_for_hour = data_for_month[ data_for_month[:,0] == hour][:,1:] # remove Hour column
                for azimuth in self.azimuths:
                    data_for_azimuth = data_for_hour[ data_for_hour[:,0] == azimuth][:,1:] # remove Azimuth column
                    for tilt in self.tilts:
                        data_for_tilt = data_for_azimuth[ data_for_azimuth[:,0] == tilt ]
                        res[self.months == month,
                                self.hours == hour,
                                self.azimuths == azimuth,
                                self.tilts == tilt] = np.average(data_for_tilt, axis=0)[1]
        self.daily_average_acout = res
        return None
    
    def write_average_ac_to_csv( self ):
    # Pivot list to months/days and azimuth/tilt
        with open('./output/ac_out_writeline.csv', 'w') as f:
            header = 'Date' + self.SEP + \
                self.SEP.join(['A:{}-T:{}'.format(a,t) for t in self.tilts for a in self.azimuths])
            f.write(header + '\n')
            for month in self.months:
                m = np.where(self.months == month)[0][0]
                for h in self.hours:
                    line = 'M:{:02d}-H:{:02d}'.format(month, h) + self.SEP
                    line += self.SEP.join( ['{:.4f}'.format(ac)
                        for t in self.tilts for ac in self.daily_average_acout[m, h, :, np.where(self.tilts == t)[0][0]] ])
                    f.write(line + '\n')
        return None
