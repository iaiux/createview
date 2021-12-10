import os
from bokeh.plotting import figure, output_file, save,show
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
import pandas as pd
from argparse import RawTextHelpFormatter
from scipy.interpolate import interp1d
from pathlib import Path
from scipy import interpolate
import json
from bokeh.palettes import Spectral11

logging.basicConfig(level=logging.DEBUG)

directory_list = ["EV", "PV"]

def Trova(Stringa, Carattere):
  Indice = 0
  while Indice < len(Stringa):
    if Stringa[Indice] == Carattere:
      return Indice
    Indice = Indice + 1
  return -1


def createPowerGraph(x, y, title, path, id):
    xhh = []
    for j in x:
        xhh.append(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(float(j))))
    outputname = title[:-4]
    p = figure(title=outputname + "_" + id, x_range=xhh,sizing_mode="stretch_width", width=600, height=400)
    p.line(xhh, y, legend_label=outputname + "_" + id, line_width=2, color="navy", alpha=0.5)

    dicaxis = {i: xhh[i] for i in range(0, len(xhh))}
    paxis = int(len(xhh) / 50)
    select_axis_key = list(range(0, len(xhh), paxis))
    select_axis = {k: v for (k, v) in dicaxis.items() if k in select_axis_key}
    mapp = """ var mapping = {};
           return mapping[tick]; """
    p.xaxis.ticker = FixedTicker(ticks=select_axis_key)
    p.xaxis.formatter = FuncTickFormatter(code=mapp.format(json.dumps(select_axis)))

    p.xaxis.major_label_orientation = pi / 4
    p.legend.location = "top_right"
    p.legend.click_policy = "mute"
    outputname = outputname + "_" + id + ".html"
    # ~ logging.debug("saving: " + path+"/" + outputname)
    output_file(path + "/" + outputname)

    save(p)


def OpenCsvAndCreateEnergyGraph(filename, path):
    with open(os.path.join(path, filename), 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        x = []
        y = []
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

def createGraphWithAllDevicesPowers(listoflistx,listoflisty,nameOfFileWithAllPowers,id):
    mypalette=Spectral11[0:len(listoflistx)]
    legend_list.append(nameOfFileWithAllPowers+"_"+id+"_power")
    data = {'xs': listoflistx,'ys': listoflisty,'labels': legend_list, 'color': mypalette}
    source = ColumnDataSource(data)

    p = figure(title=nameOfFileWithAllPowers + "_powers", x_range=xhh,sizing_mode="stretch_width", width=600, height=400)
    p.multi_line('xs' ,'ys',line_width=2, line_color='color',legend_group='labels', source = source)
    dicaxis = {i: xhh[i] for i in range(0, len(xhh))}
    paxis = int(len(xhh) / 30)
    select_axis_key = list(range(0, len(xhh), paxis))
    select_axis = {k: v for (k, v) in dicaxis.items() if k in select_axis_key}
    mapp = """ var mapping = {}; return mapping[tick]; """
    p.xaxis.ticker = FixedTicker(ticks=select_axis_key)
    p.xaxis.formatter = FuncTickFormatter(code=mapp.format(json.dumps(select_axis)))
    p.xaxis.major_label_orientation = pi / 4
    output_file(os.getcwd() + "/" + nameOfFileWithAllPowers+'_powers.html')
    return p
	
def OpenCsvAndCreateConsAndProdGraph(filename,path,Day):
    with open(os.path.join(path, filename), 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        x = []
        y = []
        xhh = []
        for riga in reader:
            try:
                x.append(riga[0])
                y.append(float(riga[1]))
            except:
                None
        for i in range(0,len(x)):
            xf=Day+" "+ x[i]
            xhh.append(datetime.datetime.strptime(xf, "%m-%d-%y %H:%M").strftime("%d/%m/%Y %H:%M"))
        outputname=filename[:-4]
        p = figure(title=outputname + " "+ Day,x_range=xhh,sizing_mode="stretch_width", width=600, height=400)
        p.line(xhh, y, legend_label=outputname + " " + Day, line_width=2, color="navy", alpha=0.5)
        dicaxis = {i: xhh[i] for i in range(0, len(xhh))}
        paxis = int(len(xhh) / 50)
        select_axis_key = list(range(0, len(xhh), paxis))
        select_axis = {k: v for (k, v) in dicaxis.items() if k in select_axis_key}
        mapp = """ var mapping = {};
           return mapping[tick]; """
        p.xaxis.ticker = FixedTicker(ticks=select_axis_key)
        p.xaxis.formatter = FuncTickFormatter(code=mapp.format(json.dumps(select_axis)))
        p.xaxis.major_label_orientation = pi / 4
        p.legend.location = "top_right"
        p.legend.click_policy = "mute"
        outputname = outputname + " " + Day + ".html"
    # ~ logging.debug("saving: " + path+"/" + outputname)
        output_file(path + "/" + outputname)

        save(p)
		

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
        # ~ print("Stampo startTime "+ startTime)
        Day=startTime.replace("_","-")
        startTime=datetime.datetime.strptime( Day, "%m-%d-%y").timestamp() #converto la data in timeseries
        # ~ print("Stampo startTime "+ str(startTime))
        # entro nelle singole cartelle di output
        os.chdir("output")
        outputpath = os.getcwd()
        # scorro le sottocartelle di output
        p=figure()
        listoflistx=[]
        listoflisty=[]
        legend_list=[]
        for device_type in directory_list:
             if os.path.isdir(device_type):
                os.chdir(device_type)
                for filename in glob.glob("*.csv"):
                    logging.debug("processing " + device_type + "/" + filename)
                    OpenCsvAndCreateEnergyGraph(filename, os.getcwd())
                    y=[]
                    x=[]
                    index=Trova(filename,"_")
                    nameOfFileWithAllPowers=filename[:index]
                    id=filename[index+1:-4]
                    # ~ print("Stampo nome file:" + nameOfFileWithAllPowers)
                    # ~ print("Stampo id:" + str(id))
                    x,y=generatePowerTimeSeries(filename, startTime)
                    createPowerGraph(x,y,filename,os.getcwd(),"power")  
                    listoflisty.append(y)
                    xhh = []
                    for j in x:
                        xhh.append(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(float(j))))
                    listoflistx.append(xhh)
                    p=createGraphWithAllDevicesPowers(listoflistx,listoflisty,nameOfFileWithAllPowers,id)
 

        save(p)                    
    os.chdir(outputpath)
    print("Sto in: "+ os.getcwd())
    for filename in glob.glob("*.csv"):
        # ~ print("Nome file: "+filename)
        # ~ logging.debug("processing " + "/" + filename)
        OpenCsvAndCreateConsAndProdGraph(filename,os.getcwd(),Day)
