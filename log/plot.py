#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import click
import numpy as np
import matplotlib.pyplot as plt

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
     
    lastTemp=-1
    pos = 0
    for actTemp in data['Input']:
        if actTemp >= 180.0 and lastTemp < 180.0:
            # print 'pos rising:', pos
            rising = data['Time'][pos]
            rising_pos = pos
            print 'rising: ', rising
        elif actTemp <= 180.0 and lastTemp > 180.0:
            falling = data['Time'][pos]
            falling_pos = pos
            print 'falling: ', falling
        lastTemp = actTemp
        pos += 1
     
    print 'diff:', falling-rising
        
    plt.plot(data['Time'], data['Setpoint'], label='Setpoint')
    plt.plot(data['Time'], data['Input'], label='Input')
    plt.plot(sollTime, sollTemp, label='soll')
    plt.legend()
    plt.grid(True)
    plt.ylim((-10,300))
    plt.xlabel('time [s]')
    plt.ylabel(u'temperature [°C]')
     
    plt.annotate('rising', xy=(data['Time'][rising_pos], data['Input'][rising_pos]),
                     xytext=(data['Time'][rising_pos]+10, data['Input'][rising_pos]+10),
                     arrowprops=dict(facecolor='black', shrink=0.05))
    plt.annotate('falling', xy=(data['Time'][falling_pos], data['Input'][falling_pos]),
                     xytext=(data['Time'][falling_pos]+10, data['Input'][falling_pos]+10),
                     arrowprops=dict(facecolor='black', shrink=0.05))
    plt.show()

if __name__ == '__main__':
    plot()
