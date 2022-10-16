import Settings
import solarvic.DailyWACOutput as dwaco
import solarvic.utilities as util
import solarvic.consumption as consumption
import numpy as np
import sqlite3
import os

INPUTFOLDER = os.path.join(os.path.curdir, 'input')
OUTPUTFOLDER = os.path.join(os.path.curdir, 'output')


def main():
    # calc_supply = True
    do_plotting = False
    verbose = False
    price_per_kwh = 0.226
    dbfile = os.path.join(OUTPUTFOLDER, 'solarvic.db')
    dbcon = sqlite3.connect(dbfile)
    # Query lon & lat
    # lat = float(input("Provide latitude: "))
    # long = float(input("Provide longitude: "))
    lat = -37.8979
    long = 145.0709
    # Import holidays and actual consumption
    holidays_file = os.path.join(INPUTFOLDER, 'holidays.csv')
    holidays = consumption.import_holidays(holidays_file)
    consumption_file = os.path.join(INPUTFOLDER, 'consumption.csv')
    consump = consumption.import_consumption(consumption_file)

    def is_schoolday(day, holidays):
        """
        Define which day is a school day and which is not.
        """
        cat = 'schoolday'
        if day in holidays or not np.is_busday(day):
            cat = 'nonschoolday'
        return cat

    def daytype(day):
        return is_schoolday(day, holidays)
    [consump_parsed, days] =\
        consumption.split_consumption_according_daytype(consump,
                                                        holidays,
                                                        daytype)
    ndays = consumption.calc_total_days(days)

    while True:
        # Query user for PV configuration: Azimuth, Tilt and Area
        azimuths, tilts, areas = query_input()
        # Write summary of inputs
        print('\n\n ***  Your inputs are:\n')
        print('Lat:', lat, 'Long:', long)
        print('Azimuths:\n', azimuths)
        print('Tilts:\n', tilts)
        print('Areas:\n', areas)
        dbcur = dbcon.cursor()
        pout_hourly = np.zeros((24, 12))
        # CALCULATE SUPPLY
        print('Calculate supply ...')
        for idx in range(len(areas)):
            area = areas[idx]
            az = azimuths[idx]
            t = tilts[idx]
            pvsetting = dwaco.DailyWACOutput(
                    lat, long, Settings.nrel_api_key)
            query = "SELECT EXISTS(SELECT 1 FROM acout WHERE azimuth = "\
                    + "{} AND tilt = {})".format(az, t)
            check = dbcur.execute(query).fetchone()[0]
            # Check whether entry exists in DB
            if check == 0:
                rurl = pvsetting.generate_request_url(az, t)
                ac_hourly = dwaco.query_acoutput_from_nrel(rurl)
                ac_avg = dwaco.calculate_daily_ac_average(pvsetting, ac_hourly)
                dwaco.write_daily_average_to_db(dbcon, pvsetting, ac_avg,
                                                az, t)
            else:
                query = "SELECT acout FROM acout WHERE azimuth = "\
                        + "{} AND tilt = {}".format(az, t)
                ac_avg = np.array(dbcur.execute(query).fetchall())
                ac_avg = ac_avg.reshape((12, 24)).T
            pout_hourly += ac_avg * area / 1000.0
        if verbose:
            util.print_table(pout_hourly)
        # CALCULATE DEMANDS
        print('Calculate demands ...')
        demands = consumption.calc_demands(consump_parsed, ndays)
        if verbose:
            util.print_consumption(demands)
        if do_plotting:
            for dt in demands:
                outfile = os.path.join(os.path.curdir, 'output',
                                       'demands_{}.pdf'.format(dt))
                util.plot(demands[dt], 'Hour',
                          'Demand (kWh)',
                          'Typical demand', outfile=outfile)
        # Calculate self-use of power supply
        print('Calculate self-use ...')
        selfuse = consumption.calc_selfuse(demands, pout_hourly)
        if verbose:
            util.print_consumption(selfuse)
        # Calculate net demand
        print('Calculate net demand ...')
        netdemand = consumption.calc_netdemand(demands, pout_hourly)
        if verbose:
            util.print_consumption(netdemand)
        # Calculate feed-in
        print('Calculate feed-in ...')
        feedin = consumption.calc_feedin(demands, pout_hourly)
        if verbose:
            util.print_consumption(feedin)
        # Calculate total feed-in and self-use
        selfuse_tot = consumption.calc_total_kwh(selfuse, ndays)
        feedin_tot = consumption.calc_total_kwh(feedin, ndays)
        # Print results
        for dt in ndays:
            print('Number of ', dt)
            util.pp(ndays[dt], '', '{:.0f}')
        util.pp(selfuse_tot, 'Selfuse total (kWh):', '{:.0f}')
        util.pp(feedin_tot, 'Feedin total (kWh):', '{:.0f}')
        util.pp(selfuse_tot + feedin_tot, 'PV power output (kWh):', '{:.0f}')
        util.pp(selfuse_tot * price_per_kwh, 'Self use savings (AUD):', '{:.0f}')
        print('\nTotal self-use savaings (AUD):\t {:.2f}'.format(
                np.sum(selfuse_tot * price_per_kwh)))
        # END OF CALCULATION
        res = input("Check other configuration? [y/n]: ")
        if res == 'y':
            continue
        else:
            break
    print("Finished!")
    return None


def query_input():
    """
    Query user for input of azimuth, tilt and peak kW settings of PV
    configuration.
    """
    print("Please provide azimuth, tilts and peak power of PV panels.")
    azimuths_raw = input("\tAzimuth settings [comma separated list]:\n\t")
    tilts_raw = input("\tTilt settings [comma separated list]:\n\t")
    area_raw = input("\tPeak power in W [comma separated list]:\n\t")
    azimuths = list(map(int, azimuths_raw.split(',')))
    tilts = list(map(int, tilts_raw.split(',')))
    areas = list(map(float, area_raw.split(',')))
    return azimuths, tilts, areas


if __name__ == "__main__":
    main()
