from collections import defaultdict
from datetime import datetime
import Settings
import os
from urllib.request import urlopen  # I don't understand why this is required. But the query wouldn't work without it.
# It would work for a simple non-hourly query. Seems like it needs this as part of
# the time-out
from pprint import pprint
import json
import ssl


class NrelQuery:
    url = "https://developer.nrel.gov/api/pvwatts/"
    version = "v6"
    format = "json"  # json or xml
    api_key = Settings.nrel_api_key
    system_capacity = 1
    array_type = 1
    module_type = 1
    losses = 15

    def __init__(self, lat=-37.8978, long=145.0709, azimuth=0, tilt=0, hourly=True):
        # This class should have initialization attributes for the _range_ of azimuth/tilt
        # or there should be a wrapping class

        self.lat = lat
        self.long = long
        self.azimuth = azimuth
        self.tilt = tilt
        self.hourly = hourly
        self.ac = {}

    @property
    def timeframe(self):
        if self.hourly:
            return "&timeframe=hourly"
        else:
            return ""

    def request(self):
        requesturl = f"{self.url}{self.version}.{self.format}?api_key={self.api_key}&lat={self.lat}&lon={self.long}" \
                     f"&system_capacity={self.system_capacity}&azimuth={self.azimuth}&tilt={self.tilt}" \
                     f"&array_type={self.array_type}&module_type={self.module_type}" \
                     f"&losses={self.losses}{self.timeframe}"
        return requesturl


class NrelACOutput:
    #  This class should be folded into the main NRELQuery

    def __init__(self, lat, long):
        self.lat = lat
        self.long = long
        self.hours = defaultdict(dict)

    def write_sequential_file(self, ac, azimuth, tilt, write_header):
        # add hour = 0, 1, 2 ... 8760. azimuth, tilt, ac = output

        output_file_path = os.path.join(Settings.output_folder, f"lat{self.lat}_long{self.long}.txt")

        if write_header:
            with open(output_file_path, 'w') as fl:
                fl.write("Date\tHour\tAzimuth\tTilt\tACWattHours\n")

        hr = 0

        with open(output_file_path, 'a') as fl:
            for wattHours in ac:
                date_string = self.dateFromHour(hr)
                hour = hr % 24
                fl.write(f"{date_string}\t{hour}\t{azimuth}\t{tilt}\t{wattHours}\n")
                hr += 1

    # def writeTabularFile(self, hr, azimuth, tilt, wattHours):
    #     #Write in tabular form: each tilt/az is a different column. 8760 rows
    #     #Check if this is the first time writing. If so write headers
    #     table = []

    def dateFromHour(self, hr):
        day_num = int(hr / 24) + 1
        date_string = datetime.strptime("2022-" + str(day_num).zfill(3), "%Y-%j").strftime("%d-%m")
        return date_string


class NrelMaster:
    #  takes the main parameters lat, long, azimuth and tilt range
    #  manages the looping through the NrelQuery
    def __init__(self, lat: float, long: float, azimuth_granularity=15, tilt_min=10, tilt_max=30,
                 tilt_granularity=10):
        self.lat = lat
        self.long = long
        self.azimuth_granularity = azimuth_granularity
        self.tilt_min = tilt_min
        self.tilt_max = tilt_max
        self.tilt_granularity = tilt_granularity

    nrel_hourly_results = defaultdict(dict)

    def query_array(self):
        context = ssl._create_unverified_context
        ssl._create_default_https_context = context

        ac_output = NrelACOutput(self.lat, self.long)
        iteration_count = 0
        for azimuth in range(0, 360, self.azimuth_granularity):
            for tilt in range(self.tilt_min, self.tilt_max + 1, self.tilt_granularity):
                iteration_count += 1
                print(f"{iteration_count}:\taz:{azimuth}\ttilt:{tilt}")

                nrel = NrelQuery(self.lat, self.long, azimuth=azimuth, tilt=tilt, hourly=True)

                with urlopen(nrel.request(), timeout=2) as response:
                    json_out = json.loads(response.read())
                    if len(json_out) > 0:
                        nrel.ac = json_out['outputs']['ac']

                self.nrel_hourly_results[azimuth][tilt] = nrel.ac  # add the ac output to a results dictionary

    def aggregate_hourly_results(self):
        for azimuth in range(0, 360, self.azimuth_granularity):
            for tilt in range(self.tilt_min, self.tilt_max+1, self.tilt_granularity):
                hrly = self.nrel_hourly_results[azimuth][tilt]
                #  this is 8760 hourly results

