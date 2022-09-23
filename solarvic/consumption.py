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
    days = {}
    for dt in daytypes:
        consumption[dt] = {}
        days[dt] = {}
    for con in con_raw:
        day = np.datetime64(con[0], 'D')
        dt = daytypes[0]
        if day in holidays or not np.is_busday(day):
            dt = daytypes[1]

        time = con[0].astype(date)
        if time.month in consumption[dt]:
            consumption[dt][time.month][con[1]-1] += con[2]
            days[dt][time.month][time.day-1] = 1
        else:
            consumption[dt][time.month] = np.zeros((96)) # TODO: Hardcoded number of intervals!
            days[dt][time.month] = np.zeros((31))
            consumption[dt][time.month][con[1]-1] = con[2]
            days[dt][time.month][time.day-1] = 1
    return [consumption, days]

def calc_demands(consump_parsed, ndays):
    """
    Input: Raw consumption in 15 min intervals.
    Output: Average consumption per month and hour for school and non-school
    days.
    """
    demands = {}
    for dt in consump_parsed:
        demands[dt] = np.zeros((24, 12))
        for m in consump_parsed[dt]:
            nday = ndays[dt][m-1]
            con = consump_parsed[dt][m].reshape((24, 4))
            demands[dt][:, m-1] = np.sum(con, axis=1)/nday/1000
    return demands

def calc_selfuse(demands, supply):
    """
    Calculate the amount of pout that is directly consumed.
    Self-usage is calculated as minimum between demand and supply.
    """
    out = {}
    for dt in demands:
        out[dt] = np.minimum(demands[dt], supply)
    return out

def calc_netdemand(demands, supply):
    """
    Calculate the net demand. Can be less can zero.
    """
    out = {}
    for dt in demands:
        out[dt] = demands[dt] - supply
    return out

def calc_feedin(demands, supply):
    """
    Calculate the amount of power that can be supplied to the grid. 
    Feed-in is calculated as the over-supplied power.
    """
    out = {}
    for dt in demands:
        out[dt] = np.maximum(np.zeros(np.shape(supply)), supply - demands[dt])
    return out

def calc_total_days(days):
    """
    Calculate the sum total per daytype for each month.
    """
    res = {}
    for dt in days:
        res[dt] = np.zeros((12))
        for idx in range(len(res[dt])):
            res[dt][idx] = np.sum(days[dt][idx+1])
    return res

def calc_total_kwh(kwh, ndays):
    res = np.zeros((12))
    for dt in kwh:
        tot = np.sum(kwh[dt], axis=0)
        for idx in range(len(tot)):
            tot[idx] *= np.sum(ndays[dt][idx])
        res += tot
    return res

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

