import os
from bokeh.plotting import figure, output_file, show
import datetime
import time
import csv
import numpy as np
from math import pi
from bokeh.models import *

def OpenCsvAndCreateGraph(filename,path):
	if filename.endswith("csv"):
		with open(os.path.join(path, filename), 'r') as csv_file:
			reader = csv.reader(csv_file, delimiter=',')
			x=[]
			y=[]
			z=[]
			xhh=[]
			i=0
			for riga in reader:
				x.append(riga[0])
				y.append(float(riga[1]))
				i=i+1
				xhh.append(time.strftime("%d/%m/%Y %H:%M:%S",time.localtime(float(riga[0])-7200)))
		print (xhh,y)		
			# ~ print("") #fine riga
	
		p = figure(title=filename,x_range=xhh,sizing_mode="stretch_width",width=600, height=400)
		p.line(xhh,y,legend_label=filename ,line_width=2,color="navy", alpha=0.5)
		p.xaxis.major_label_orientation=pi/4
		p.legend.location = "top_right"
		p.legend.click_policy="mute"
		outputname=filename[:-4]
		outputname=outputname+".html"
		#print(outputname)
		output_file(path+"/"+ outputname)
		show(p)

	


if __name__ == '__main__':
	os.chdir("../Simulations")
	initialpath=os.getcwd()
	for directory in os.listdir(initialpath):
		# ~ print(directory)
		os.chdir(directory+ "/output") #entro nelle singole cartelle di output
		# ~ print(os.getcwd())
		outputpath=os.getcwd()
		for directory2 in os.listdir("."): #scorro le sottocartelle di output
			#print(directory2)
			os.chdir(directory2)
			for filename in os.listdir("."):
				OpenCsvAndCreateGraph(filename,os.getcwd())
			os.chdir(outputpath)
			
		
		os.chdir(initialpath) #mi risposto in simulations
	
		
