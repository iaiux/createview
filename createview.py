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
import matplotlib.pyplot as plt

from argparse import RawTextHelpFormatter
from scipy.interpolate import interp1d
from pathlib import Path
from scipy import interpolate



logging.basicConfig(level=logging.DEBUG)

directory_list = ["EV", "PV"]


def createGraph(x,y,title,path,name):
	xhh=[]
	for j in x:
		xhh.append(time.strftime("%d/%m/%Y %H:%M:%S",time.localtime(float(j-7200))))
	outputname = title[:-4]
	p= figure(title=outputname+"_"+name,x_range=xhh,
               sizing_mode="stretch_width", width=600, height=400)
	p.line(xhh, y, legend_label=outputname+"_"+name,line_width=2, color="navy", alpha=0.5)
	p.xaxis.major_label_orientation = pi/4
	p.legend.location = "top_right"
	p.legend.click_policy = "mute"
	#https://stackoverflow.com/questions/40638685/bokeh-select-xaxis-to-be-shown-in-plot-not-numbers
	outputname = outputname+"_"+name+".html"
	# ~ logging.debug("saving: " + path+"/" + outputname)
	output_file(path+"/" + outputname)
	save(p)
	


def OpenCsvAndCreateGraph(filename, path):
    with open(os.path.join(path, filename), 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        x = []
        y = []
        z = []
        xhh = []
        for riga in reader:
            x.append(riga[0])
            y.append(float(riga[1]))
            xhh.append(time.strftime("%d/%m/%Y %H:%M:%S",
                       time.localtime(float(riga[0])-7200)))
    print(xhh, y)
    # ~ print("") #fine riga
    title=filename[:-4]
    p = figure(title=title+"_energy", x_range=xhh,
               sizing_mode="stretch_width", width=600, height=400)
    p.line(xhh, y, legend_label=title+"_energy",
           line_width=2, color="navy", alpha=0.5)
    p.xaxis.major_label_orientation = pi/4
    p.legend.location = "top_right"
    p.legend.click_policy = "mute"

    outputname = filename[:-4]
    outputname = outputname+".html"
    logging.debug("saving: " + path+"/" + outputname)
    output_file(path+"/" + outputname)
    save(p)


def generatePowerTimeSeries(file, startTime):
    """
    Args:
        file:
        startTime:
    """
 
    endTime = startTime + 86400
    with open(file, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=",")
        count = 0
        x = []  # lista dei tempi della timeseries
        y = []  # lista dei valori della timeseries
        lastSample = 0  # Questo mi serve per tenermi in memoria il tempo precedente alla riga che sto leggendo, cosi posso farmi il delta per la trasformazione in potenza
        lastValue = 0  # Questo mi serve per tenermi in memoria il valore di energia precedente alla riga che sto leggendo, cosi posso farmi il delta per la trasformazione in potenza
        for row in csv_reader:  # per tutte le righe
            try:
                row[0] = datetime.datetime.strptime( row[0], "%Y-%m-%d %H:%M:%S").timestamp()
            except:
                None
            if (count != 0):  # salto la prima riga del
                # la ts perchÃ© devo convertire in potenza
                if(float(row[0]) != lastSample):
                    x.append(lastSample+1)  # aggiunto il tempo alla lista dei tempi
                    y.append(3600*(float(row[1]) - lastValue) / (float(row[0]) - lastSample))
                    x.append(float(row[0]))  # aggiunto il tempo alla lista dei tempi
                    y.append(3600 * (float(row[1]) - lastValue) / (float(row[0]) - lastSample))
 
            else:
                if (startTime < float(row[0])):  # faccio in modo che se il primo tempo della timeseries Ã© piÃº grande del minimo del periodo di interesse ci piazzo uno zero, cosi dopo non ho problemi quando vado a ricampionare
                    x.append(startTime)
                    y.append(0)  # aggiungo alla lista dei valori la potenza
            lastSample = float(row[0])  # aggiorno il tempo precedente
            lastValue = float(row[1])  # aggiorno l'energia precedente
            count += 1  # aggiorno il count quando ho finito la riga
    y.append(0)
    x.append(lastSample+1)
    #if endTime > lastSample:  # stesso discorso di prima, se l'ultimo tempo della timeseries Ã© piÃº piccolo del massimo tempo di interesse metto uno zero per non aver problemi dopo
    y.append(0.1)
    x.append(endTime)
    f = interpolate.interp1d(x, y, kind='previous')  # faccio l'interpolazione lineare
    xnew = np.arange(startTime, endTime, 300)  # mi creo il vettore dei tempi con un sample ogni 5 minuti (300 secondi)
    ynew = f(xnew)  # genero la nuova serie di potenze ricampionatew
    # ~ plt.plot(xnew,ynew)
    # ~ plt.show()
    return xnew,ynew

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This program converts timeseries to bokeh plots.', formatter_class=RawTextHelpFormatter)
    parser.add_argument('-dir', metavar='in_dir',
                        default='.', help='Simulation folder')
    args = parser.parse_args()
    sim_dir = args.dir
    if os.path.isdir(sim_dir):
        os.chdir(args.dir)
        startTime=os.getcwd() #prendo il percorso
        startTime=Path(startTime).stem #estrapolo solo il nome della cartella per capire di che giorno stiamo parlando
        startTime=startTime[0:8] #estraggo solo il giorno
        print("Stampo startTime "+ startTime)
        startTime=startTime.replace("_","-")
        startTime=datetime.datetime.strptime( startTime, "%m-%d-%y").timestamp() #converto la data in timeseries
        print("Stampo startTime "+ str(startTime))
        # entro nelle singole cartelle di output
        os.chdir("output")
        outputpath = os.getcwd()
        # scorro le sottocartelle di output
        for device_type in directory_list:
             if os.path.isdir(device_type):
                os.chdir(device_type)
                for filename in glob.glob("*.csv"):
                    logging.debug("processing " + device_type + "/" + filename)
                    OpenCsvAndCreateGraph(filename, os.getcwd())
                    y=[]
                    x=[]
                    x,y=generatePowerTimeSeries(filename, startTime)
                    createGraph(x,y,filename,os.getcwd(),"power")
    os.chdir(outputpath)
