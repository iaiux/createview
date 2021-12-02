import os
from bokeh.plotting import figure, output_file, save
import datetime
import time
import csv
import numpy as np
from math import pi
from bokeh.models import *
import glob
import logging
import argparse
from argparse import RawTextHelpFormatter


logging.basicConfig(level=logging.DEBUG)

directory_list = ["EV", "PV"]

def OpenCsvAndCreateGraph(filename, path):
    with open(os.path.join(path, filename), 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        x = []
        y = []
        z = []
        xhh = []
        i = 0
        for riga in reader:
            x.append(riga[0])
            y.append(float(riga[1]))
            i = i+1
            xhh.append(time.strftime("%d/%m/%Y %H:%M:%S",
                       time.localtime(float(riga[0])-7200)))
    print(xhh, y)
    # ~ print("") #fine riga

    p = figure(title=filename, x_range=xhh,
               sizing_mode="stretch_width", width=600, height=400)
    p.line(xhh, y, legend_label=filename,
           line_width=2, color="navy", alpha=0.5)
    p.xaxis.major_label_orientation = pi/4
    p.legend.location = "top_right"
    p.legend.click_policy = "mute"
    outputname = filename[:-4]
    outputname = outputname+".html"
    logging.debug("saving: " + path+"/" + outputname)
    output_file(path+"/" + outputname)
    save(p)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This program converts timeseries to bokeh plots.', formatter_class=RawTextHelpFormatter)
    parser.add_argument('-dir', metavar='in_dir',
                        default='.', help='Simulation folder')
    args = parser.parse_args()
    sim_dir = args.dir
    os.chdir(args.dir)
    if os.path.isdir(sim_dir):
        # entro nelle singole cartelle di output
        os.chdir(sim_dir + "/output")
        outputpath = os.getcwd()
        # scorro le sottocartelle di output
        for device_type in directory_list:
             if os.path.isdir(device_type):
                os.chdir(device_type)
                for filename in glob.glob("*.csv"):
                    logging.debug("processing " + device_type + "/" + filename)
                    OpenCsvAndCreateGraph(filename, os.getcwd())
        os.chdir(outputpath)
