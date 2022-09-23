import Settings
import solarvic.DailyWACOutput as dwaco
import solarvic.consumption as consumption
import numpy as np
import os
import matplotlib.pyplot as plt


def main():
    calc_supply = False
    do_plotting = False
    verbose = False
    price_per_kwh = 0.226
    ########################################
    #
    # SUPPLY CALCULATION:
    #
    ########################################
    if calc_supply:
        # Import PV configuration
        pv_config = os.path.join(os.path.curdir, 'input', 'pv_config.csv')
        data = np.loadtxt(pv_config, skiprows=1)
        long = data[0, 0]
        lat = data[0, 1]
        azimuth_tilts = data[:, 2:4]
        areas = data[:, 4]
        # Write summary of inputs
        print('Inputs:\n')
        print('Lat:', lat, 'Long:', long)
        print('Azimuths and tilts:\n', azimuth_tilts)
        print('Areas:\n', areas)

        dailywacouput = dwaco.DailyWACOutput(
            lat, long,
            Settings.nrel_api_key, azimuth_tilts)
        # Calculation -
        # Scan azimuth and tilt settings and calculate power output
        print('\nScan azimuth and tilt settings ...')
        dwaco.scan_azimuths_tilts(dailywacouput)
        pout_hourly = dwaco.calculate_power_output_hourly(dailywacouput, areas)
        np.save('./output/pout_hourly.npy', pout_hourly)
        pout_daily = dwaco.calculate_power_output_daily(pout_hourly)
        pout_monthly = dwaco.calculate_power_output_monthly(pout_daily)

        # Output - Write hourly average powert output to stdout
        # outfile = os.path.join(os.path.curdir, 'output',
        #                        'out_lat{}_long{}.csv'.format(lat, long))
        # dwaco.write_average_ac_to_csv( dailywacouput, outfile )
        if verbose:
            pp(np.arange(12) + 1, 'Hourly power production per month:',
               format='{}')
            print_table(pout_hourly)
        pp(pout_daily, 'Daily power production (kWh):')
        pp(pout_monthly, 'Monthly power production (kWh):', format='{:.0f}')
        if do_plotting:
            outfile = os.path.join(os.path.curdir, 'output',
                                   'typical_day_power.pdf')
            plot(pout_hourly, 'Hour',
                 'A/C Power Output (kW)',
                 'Typical day power output', outfile=outfile)
    else:
        pout_hourly = np.load('./output/pout_hourly.npy')

    ########################################
    #
    # SAVINGS CALCULATION:
    #
    ########################################
    # Import holidays and actual consumption
    holidays_file = os.path.join(os.path.curdir, 'input', 'holidays.csv')
    holidays = consumption.import_holidays(holidays_file)
    consumption_file = os.path.join(os.path.curdir, 'input', 'consumption.csv')
    consump = consumption.import_consumption(consumption_file)
    [consump_parsed, days] =\
        consumption.split_consumption_according_daytype(consump,
                                                        holidays)
    ndays = consumption.calc_total_days(days)
    # Calculate demand
    print('Calculate demands ...')
    demands = consumption.calc_demands(consump_parsed, ndays)
    if verbose:
        print_consumption(demands)
    if do_plotting:
        for dt in demands:
            outfile = os.path.join(os.path.curdir, 'output',
                                   'demands_{}.pdf'.format(dt))
            plot(demands[dt], 'Hour',
                 'Demand (kWh)',
                 'Typical demand', outfile=outfile)
    # Calculate self-use of power supply
    print('Calculate self-use ...')
    selfuse = consumption.calc_selfuse(demands, pout_hourly)
    if verbose:
        print_consumption(selfuse)
    # Calculate net demand
    print('Calculate net demand ...')
    netdemand = consumption.calc_netdemand(demands, pout_hourly)
    if verbose:
        print_consumption(netdemand)
    # Calculate feed-in
    print('Calculate feed-in ...')
    feedin = consumption.calc_feedin(demands, pout_hourly)
    if verbose:
        print_consumption(feedin)
    # Calculate total feed-in and self-use
    selfuse_tot = consumption.calc_total_kwh(selfuse, ndays)
    feedin_tot = consumption.calc_total_kwh(feedin, ndays)
    # Print results
    for dt in ndays:
        print('Number of ', dt)
        pp(ndays[dt], '', '{:.0f}')
    pp(selfuse_tot, 'Selfuse total (kWh):', '{:.0f}')
    pp(feedin_tot, 'Feedin total (kWh):', '{:.0f}')
    pp(selfuse_tot + feedin_tot, 'PV power output (kWh):', '{:.0f}')
    pp(selfuse_tot * price_per_kwh, 'Self use savings (AUD):', '{:.0f}')
    print('\nTotal self-use savaings (AUD):\t {:.2f}'.format(
            np.sum(selfuse_tot * price_per_kwh)))
    return 0


def pp(outputs, title='', format='{:.2f}'):
    """
    Write tables to output
    """
    if title:
        print(title)
    print('\t', '\t'.join(format.format(o) for o in outputs))
    return None


def print_table(table):
    """
    Wrapper around pp function
    """
    for idx in range(len(table)):
        pp(table[idx, :])
    return None


def print_consumption(consumption):
    """
    Wrapper around print_table function
    """
    for dt in consumption:
        print(dt)
        print_table(consumption[dt])
    return None


def plot(out, xl, yl, ti, outfile=''):
    """
    Plot typical day power output
    """
    plt.figure()
    plt.plot(out)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.xticks(np.arange(24))
    plt.legend(np.arange(12) + 1)
    plt.title(ti)
    plt.grid(visible=True, axis='y')
    if outfile:
        plt.savefig(outfile)
    else:
        plt.show()
    return None


if __name__ == "__main__":
    main()
