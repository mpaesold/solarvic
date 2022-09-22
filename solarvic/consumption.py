#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compute power consumption
"""
import numpy as np
from datetime import date

def import_holidays(holidays_file):
    """
    Import holidays from file.
    """
    return np.genfromtxt(holidays_file, usecols=(0), dtype='datetime64[D]',
                             skip_header=1, delimiter=',')

def import_consumption(consumption_file):
    """
    Import consumption from file.
    """
    return np.genfromtxt(consumption_file, usecols=(1, 2, 6, 7),
                                dtype=('datetime64[m]', int, float, 'U4'),
                                skip_header=1, delimiter=',')

def calc_average_consumption(consump_raw, holidays):
    """
    Input: Raw consumption in 15 min intervals.
    Output: Average consumption per month and hour for school and non-school
    days.
    """
    consumption_avg = {'schoolday': {}, 'nonschoolday':{}}
    for con in consump_raw:
        day = np.datetime64(con[0], 'D')
        daytype = 'schoolday'
        if day in holidays or not np.is_busday(day):
            daytype = 'nonschoolday'
        time = con[0].astype(date)

        if consumption_avg[daytype].get(time.month):
            dic = consumption_avg[daytype][time.month]
            dic['consumption'][con[1]-1] += con[2]
            dic['days'][time.day-1] = 1
        else:
            intervals = np.zeros((96)) # TODO: Hardcoded number of intervals!
            intervals[con[1]-1] = con[2]
            days = np.zeros((31)) # TODO: Hardcoded number of days!
            days[time.day-1] = 1
            consumption_avg[daytype][time.month] = {'consumption': intervals,
                                                    'days': days}
    return consumption_avg

def main():
    holidays_file = './input/holidays.csv'
    holidays = import_holidays(holidays_file)
    consumption_file = './input/consumption.csv'
    consump = import_consumption(consumption_file)
    #print(holidays)
    #print(consump)

    consump_avg = calc_average_consumption(consump, holidays)
    for m in consump_avg['nonschoolday'].keys():
        print('Month: ', m)
        print(consump_avg['nonschoolday'][m]['consumption'])
        print(consump_avg['nonschoolday'][m]['days'])
    return 0

if __name__ == "__main__":
    main()

