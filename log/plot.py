#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import numpy as np
import matplotlib.pyplot as plt

#https://stackoverflow.com/a/13732668
def runningMeanFast(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

# log serial output to file
# grabserial -d /dev/ttyUSB0 -b 57600 -o 2018-01-26_temp_on_ptc.log

# clean log
# cat 2018-01-26_temp_on_ptc.log | grep -v output  | grep -v "SSR off"|tail -n +3 > 2018-01-26_temp_on_ptc.log.csv

# data = np.genfromtxt('2018-01-26_3_temp_on_ptc.log.csv', delimiter=' ',names=True)
            
@click.command()
@click.option('--filename', help ='logfile to parse', required=True)
#@click.argument('filename', type=click.File('rb'))
def plot(filename):
    filtered = [ line for line in open(filename) if 'output' not in line and 'SSR off' not in line]
    #print filtered
    data = np.genfromtxt(filtered, delimiter=' ', names=True, skip_header=2)

    sollTime = [0, 120, 180, 240, 260, 350]
    sollTemp = [20, 150, 180, 230, 230, 100]

    liquid_point = 180.0

    lastTemp=-1
    pos = 0
    rising = 0
    rising_pos = 0
    falling = 0
    falling_pos = 0
    max_input = 0
    max_set = 0
    for actTemp in data['Input']:
        if actTemp >= liquid_point and lastTemp < liquid_point:
            rising = data['Time'][pos]
            rising_pos = pos
            print 'time starting liquid: {0}s'.format(rising)
        elif actTemp <= liquid_point and lastTemp > liquid_point:
            falling = data['Time'][pos]
            falling_pos = pos
            print 'time stopping liquid: {0}s'.format(falling)
        if actTemp > max_input:
            max_input = actTemp
        lastTemp = actTemp
        pos += 1

    print 'time in liquid state (above {0}°C): {1}s'.format(liquid_point,falling-rising)

    for setTemp in data['Setpoint']:
        if setTemp > max_set:
            max_set = setTemp

    print
    print 'maximum temperature set: {0}°C'.format(max_set)
    print 'maximum temperature read: {0}°C'.format(max_input)

    last = data['Input'][0]
    diff_input = list()
    for current in data['Input']:
        diff_input.append(current-last)
        last = current

    moving_aves = runningMeanFast(diff_input, 10)

    output_percent = list()
    for current in data['Output']:
        output_percent.append((current/2000.0)*100.0)

    f, axarr = plt.subplots(3, sharex=True)

    axarr[0].plot(data['Time'], data['Setpoint'], label='Setpoint')
    axarr[0].plot(data['Time'], data['Input'], label='Input')
    axarr[0].plot(sollTime, sollTemp, label='soll')
    axarr[1].plot(data['Time'], diff_input, label='diff input')
    axarr[1].plot(data['Time'], moving_aves, label='diff input average')
    # axarr[2].plot(data['Time'], data['Output'], label='Output')
    axarr[2].plot(data['Time'], output_percent, label='Output percent')

    for i in range(3):
        axarr[i].legend()
        axarr[i].grid(True)

    # axarr[0].set_ylim([-10,300])
    plt.xlabel('time [s]')
    # plt.ylabel(u'temperature [°C]')
    axarr[0].set_ylabel(u'temperature [°C]')
    axarr[1].set_ylabel(u'delta temperature [°C]')
    axarr[2].set_ylabel(u'ssr output [%]')
    # axarr[1].ylabel(u'temperature diff [°C]')

    # plt.annotate('rising', xy=(data['Time'][rising_pos], data['Input'][rising_pos]),
    if rising_pos:
        axarr[0].annotate('rising', xy=(data['Time'][rising_pos], data['Input'][rising_pos]),
                          xytext=(data['Time'][rising_pos]+10, data['Input'][rising_pos]+10),
                          arrowprops=dict(facecolor='black', shrink=0.05))
    # plt.annotate('falling', xy=(data['Time'][falling_pos], data['Input'][falling_pos]),

    if falling_pos:
        axarr[0].annotate('falling', xy=(data['Time'][falling_pos], data['Input'][falling_pos]),
                          xytext=(data['Time'][falling_pos]+10, data['Input'][falling_pos]+10),
                          arrowprops=dict(facecolor='black', shrink=0.05))
    if rising_pos:
        axarr[0].axvline(x=rising_pos, color='r')
    if falling_pos:
        axarr[0].axvline(x=falling_pos, color='r')
    axarr[0].axhline(y=liquid_point, color='r')
    plt.show()

if __name__ == '__main__':
    plot()
