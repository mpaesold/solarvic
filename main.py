import Settings
import solarvic.DailyWACOutput as dwaco
import solarvic.consumption as consumption
import numpy as np
import os
import matplotlib.pyplot as plt


def main():
    calc_supply = False
    do_plotting = False
    ########################################
    #
    # SUPPLY CALCULATION: 
    #
    ########################################
    # Import PV configuration
    if calc_supply:
        pv_config = os.path.join(os.path.curdir, 'input', 'pv_config.csv')
        data = np.loadtxt(pv_config, skiprows=1)
        long = data[0, 0]
        lat = data[0, 1]
        azimuth_tilts = data[:, 2:4]
        areas = data[:, 4]
        # Write summary of inputs
        print('Lat:', lat, 'Long:', long)
        print('Azimuths and tilts:\n', azimuth_tilts)
        print('Areas:\n', areas)

        dailywacouput = dwaco.DailyWACOutput(
            lat, long,
            Settings.nrel_api_key, azimuth_tilts)
        # Calculation - Scan azimuth and tilt settings and calculate power output
        print('Scan azimuth and tilt settings:')
        dwaco.scan_azimuths_tilts(dailywacouput)
        pout_hourly = dwaco.calculate_power_output_hourly(dailywacouput, areas)
        pout_daily = dwaco.calculate_power_output_daily(pout_hourly)
        pout_monthly = dwaco.calculate_power_output_monthly(pout_daily)

        # Output - Write hourly average powert output to stdout
        #outfile = os.path.join(os.path.curdir, 'output',
        #                       'out_lat{}_long{}.csv'.format(lat, long))
        #dwaco.write_average_ac_to_csv( dailywacouput, outfile )
        pp(np.arange(12) + 1, 'Hourly power production per month:', format='{}')
        for idx in range(24):
            pp(pout_hourly[idx, :])
        pp(pout_daily, 'Daily power production:')
        pp(pout_monthly, 'Monthly power production:', format='{:.0f}')
        if do_plotting:
            outfile = os.path.join(os.path.curdir, 'output',
                                       'typical_day_power.pdf')
            plot(pout_hourly, 'Hour', 
                 'A/C Power Output (kW)',
                 'Typical day power output', outfile=outfile)

    ########################################
    #
    # Demand calculation: 
    #
    ########################################
    # Import holidays and actual consumption
    holidays_file = os.path.join(os.path.curdir, 'input', 'holidays.csv')
    holidays = consumption.import_holidays(holidays_file)
    consumption_file = os.path.join(os.path.curdir, 'input', 'consumption.csv')
    consump = consumption.import_consumption(consumption_file)

    demands = consumption.calc_demands(consump, holidays)
    for dt in demands:
        print(dt)
        for idx in range(len(demands[dt])):
            pp(demands[dt][idx, :])
        if do_plotting:
            outfile = os.path.join(os.path.curdir, 'output',
                                   'demands_{}.pdf'.format(dt))
            plot(demands[dt], 'Hour', 
                 'Demand (kWh)',
                 'Typical demand', outfile=outfile)
        
    return 0

def pp(outputs, title='', format='{:.2f}'):
    """
    Write tables to output
    """
    if title:
        print(title)
    print('\t', '\t'.join(format.format(o) for o in outputs))
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
