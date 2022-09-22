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

def split_consumption_according_daytype(con_raw, holidays,
                                        daytypes=('schoolday', 'nonschoolday')):
    """
    Returns dictionary with daytypes as first set of key. Next level is month.
    Contains fields with consumption and day of month where consumption
    occured.
    """
    consumption = {}
    for daytype in daytypes:
        consumption[daytype] = {}
    for con in con_raw:
        day = np.datetime64(con[0], 'D')
        daytype = daytypes[0]
        if day in holidays or not np.is_busday(day):
            daytype = daytypes[1]
        time = con[0].astype(date)

        if consumption[daytype].get(time.month):
            dic = consumption[daytype][time.month]
            dic['consumption'][con[1]-1] += con[2]
            dic['days'][time.day-1] = 1
        else:
            intervals = np.zeros((96)) # TODO: Hardcoded number of intervals!
            intervals[con[1]-1] = con[2]
            days = np.zeros((31)) # TODO: Hardcoded number of days!
            days[time.day-1] = 1
            consumption[daytype][time.month] = {'consumption': intervals,
                                                'days': days}
    return consumption

def calc_demands(consump_raw, holidays):
    """
    Input: Raw consumption in 15 min intervals.
    Output: Average consumption per month and hour for school and non-school
    days.
    """
    daytypes = ('schoolday', 'nonschoolday')
    demands = {}
    consump_parsed = split_consumption_according_daytype(consump_raw, holidays,
                                                         daytypes)
    for dt in consump_parsed:
        demands[dt] = np.zeros((24, 12))
        for m in consump_parsed[dt]:
            days = np.sum(consump_parsed[dt][m]['days'])
            con = consump_parsed[dt][m]['consumption'].reshape((24, 4))
            demands[dt][:, m-1] = np.sum(con, axis=1)/days/1000
    return demands

def main():
    holidays_file = './input/holidays.csv'
    holidays = import_holidays(holidays_file)
    consumption_file = './input/consumption.csv'
    consump = import_consumption(consumption_file)
    #print(holidays)
    #print(consump)
    consump_avg = calc_average_consumption(consump, holidays)
    return 0


if __name__ == "__main__":
    main()

