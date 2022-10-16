import numpy as np
import sqlite3
import Settings
import solarvic.DailyWACOutput as dwaco


def main():
    long = 145.0709
    lat = -37.8979
    azimuth_tilts = [[az, t] for az in np.arange(0, 360, 180)
                     for t in [10, 20]]
    dailywacouput = dwaco.DailyWACOutput(lat, long,
                                         Settings.nrel_api_key,
                                         np.array(azimuth_tilts))
    dwaco.scan_azimuths_tilts(dailywacouput)
    con = sqlite3.connect("./output/solarvic.db")
    dailywacouput.write_daily_average_to_db(con)
    # res = cur.execute("SELECT month, hour, acout FROM acout WHERE azimuth = 180 AND tilt = 10")
    return None


if __name__ == "__main__":
    main()
