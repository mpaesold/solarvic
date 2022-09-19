import Settings
import DailyWACOutput as dwaco
import numpy as np
import os


def main():
    infile = os.path.join(os.path.curdir, 'input', 'pv_config.csv')
    data = np.loadtxt(infile, skiprows=1)
    long = data[0, 0]
    lat = data[0, 1]
    azimuth_tilts = data[:, 2:4]
    areas = data[:, 4]

    outfile = os.path.join(os.path.curdir, 'output',
                           'out_lat{}_long{}.csv'.format(lat, long))
    outfileplot = os.path.join(os.path.curdir, 'output',
                               'typical_day_power.pdf')

    print('Lat:', lat, 'Long:', long)
    print('Azimuths and tilts:\n', azimuth_tilts)
    print('Areas:\n', areas)

    dailywacouput = dwaco.DailyWACOutput(
        lat, long,
        Settings.nrel_api_key, azimuth_tilts)

    print('Scan azimuth and tilt settings:')
    dwaco.scan_azimuths_tilts(dailywacouput)
    # dwaco.write_average_ac_to_csv( dailywacouput, outfile )
    pout_hourly = dwaco.calculate_power_output_hourly(dailywacouput, areas)
    pout_daily = dwaco.calculate_power_output_daily(pout_hourly)
    pout_monthly = dwaco.calculate_power_output_monthly(pout_daily)

    print('Hourly power production per month:')
    print('Hour', ':\t', '\t'.join('{}'.format(m) for m in np.arange(12) + 1))
    for idx in range(24):
        print(idx, ':\t', '\t'.join('{:.2f}'.format(p) for p in pout_hourly[idx, :]))

    print('Daily power production:')
    print('\t', '\t'.join('{:.2f}'.format(p) for p in pout_daily))

    print('Monthly power production:')
    print('\t', '\t'.join('{:.0f}'.format(p) for p in pout_monthly))

    dwaco.plot_hourly_power_output(pout_hourly, outfileplot)
    return 0


if __name__ == "__main__":
    main()
