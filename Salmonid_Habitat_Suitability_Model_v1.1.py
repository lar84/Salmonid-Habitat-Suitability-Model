# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 08:43:37 2019

@author: lurussell
"""

#Version 1.1 updated January 2020
#Added preference curves for Juvenile Coho Rearing and Juvenile/Adult Rainbow Trout Rearing

from tkinter import Tk, Label, Button
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from numpy import where, shape
from numpy.ma import masked_where
from scipy.interpolate import interp1d
from osgeo.gdal import Open, GetDriverByName, GDT_Float32

###############################################################################

root = Tk()

###############################################################################

#define tkinter buttons, labels, etc...
title = Label(root, text = 'Salmonid Habitat Suitability Model')
title.config(font=('Calibri',18))
values = ['Adult Chinook Spawning Large River',
          'Adult Chinook Spawning Small River',
          'Juvenile Chinook Rearing',
          'Adult Coho Spawning',
          'Juvenile Coho Rearing',
          'Adult Sockeye Spawning',
          'Juvenile/Adult Rainbow Trout Rearing']
dropdown = Combobox(root,values=values)
dropdownLabel = Label(root,text='Salmonid species/lifestage: ')
inputfileDep = Label(root, text = '')
inputfileVel = Label(root, text = '')
exportCompleteRaster = Label(root, text = '')
devLabel = Label(root,text='Developed in Python 3.7 by Luke Russell, last update Jan 2020')
devLabel.config(font=('Calibri',8))

###############################################################################

#place tkinter objects onto grid
inputfileDep.grid(column=1, row=1, sticky="ew",columnspan= 2)
inputfileVel.grid(column=1, row=2, sticky="ew",columnspan= 2)
title.grid(column=0, row=[0], columnspan = 3, sticky="ew")
dropdownLabel.grid(column=0,row=3,sticky='ew',columnspan=2)
dropdown.grid(column=2,row=3,sticky='ew') 
exportCompleteRaster.grid(column=2,row=7,sticky='ew',columnspan=2)
devLabel.grid(column=0,row=8,columnspan=3,sticky='w')

###############################################################################

#time to define the preference curves for each salmon species and lifestage
#all lists are indexed the same 0=depth, 1=depth preference value, 2=velocity, 3=velocity preference value
ChnSpwnLR = [[0,0.55,1.05,1.55,5.05,10,30,35,99],
                [0,0,0.75,1,1,0,0,0,0],
                [0,0.55,0.75,1.55,3.55,4.95,6.55,7,99],
                [0,0,0.79,1,1,0,0,0,0]]

ChnSpwnSR = [[0,0.35,0.95,1.25,1.75,2.75,99],
                [0,0,0.8,0.94,1,0.4,0.4],
                [0,0.55,0.65,1.15,2.25,2.35,3.75,3.85,5,99],
                [0,0,0.1,0.2,1,1,0.5,0.2,0,0]]

ChnJuv = [[0,0.45,1.05,1.65,2.05,2.45,99],
             [0,0,0.3,0.85,0.95,1,1],
             [0,0.15,0.55,0.95,1.05,1.85,3.65,99],
             [0.24,0.3,0.85,1,1,0.45,0,0]]

CohoSpwn = [[0,0.15,0.55,0.85,1.15,1.55,1.95,2.75,99],
               [0,0,0.65,1,1,0.9,0.53,0.35,0.35],
               [0,0.45,1.25,1.45,4.25,5,99],
               [0,0.53,1,1,0.62,0,0]]

CohoJuv = [[0,0.1,0.25,1.55,2.5,3.25,3.9,4,99],
           [0,0,0.25,0.9,1,1,0.9,0.27,0.27],
           [0,0.15,0.3,0.45,0.6,1.2,2,99],
           [0.78,1,0.96,0.31,0.2,0.16,0,0]]

SockSpwn = [[0,0.15,0.55,1.15,1.25,1.55,99],
                [0,0,0.6,1,1,0.45,0.45],
                [0,0.05,0.25,0.85,1.25,2.35,3.95,99],
                [0,0,0.5,1,1,0.26,0,0]]

RainbowTrout = [[0,0.55,1.55,2.25,2.6,2.75,3.4,4.75,99],
           [0,0,0.45,0.5,0.65,1,1,0.66,0.66],
           [0,0.85,1.75,2.65,3.7,5.25,99],
           [0.25,1,0.45,0.4,0.1,0,0]]

#put all the preference curves into  a single list
prefcurves = [ChnSpwnLR,ChnSpwnSR,ChnJuv,CohoSpwn,CohoJuv,SockSpwn,RainbowTrout]
#create a dict object to make it easy to call
salmonDict = dict(zip(values,prefcurves))

###############################################################################

#define func and button for opening file directory to load depth raster
def openDep():
    inputfileDep['text'] = 'Working...'
    
    filename = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Rasters",["*.img","*.tif","*.jpg",".jpeg",".jp2",".png",".dat","*.bmp"]),("all files","*.*")))

    global dep_array
    global mask
    global nodata
    global geotransform
    
    #open dep raster and read as array, remove no data value (no data = no water)
    raster = Open(filename)
    nodata = raster.GetRasterBand(1).GetNoDataValue()
    dep_array = raster.GetRasterBand(1).ReadAsArray()
    mask = masked_where(dep_array==nodata,dep_array)
    mask = dep_array
    dep_array = where(dep_array==nodata,0,dep_array)
    
    #grab the geospatial info of the raster to make sure the output has the same units/size/resolution
    geotransform = raster.GetGeoTransform()
    
    #close file to save on local memory
    raster = None

    if filename: 
            inputfileDep['text']=filename
    
openDepth = Button(root, text = 'Open Depth Raster', command = openDep)
openDepth.grid(column=0, row=1, sticky="ew")

###############################################################################

#define func and button for opening file directory to load velocity raster
def openVel():
    inputfileVel['text'] = 'Working...'
    
    filename = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Rasters",["*.img","*.tif","*.jpg",".jpeg",".jp2",".png",".dat","*.bmp"]),("all files","*.*")))

    #open vel raster and read as array, remove no data value (no data = no water)
    global vel_array
    raster = Open(filename)
    nodata = raster.GetRasterBand(1).GetNoDataValue()
    vel_array = raster.GetRasterBand(1).ReadAsArray()
    vel_array = where(dep_array==nodata,0,dep_array)
    
    # no need to grab the geotransform info because we already grabbed it from the depth raster
    
    #close file to save on local memory
    raster = None
    
    if filename: 
            inputfileVel['text']=filename
    
openVelocity = Button(root, text = 'Open Velocity Raster', command = openVel)
openVelocity.grid(column=0, row=2, sticky="ew")

###############################################################################

def exportRaster():
    
    #make sure input file is selected
    if inputfileVel['text'] != '' and inputfileVel['text'] != 'Please select input file!' and inputfileDep['text'] != '' and inputfileDep['text'] != 'Please select input file!':
        while dropdown.get() not in values:
                dropdown.set('Please select variable!')
                return
        
        exportCompleteRaster['text'] = 'Working...'
        
        #get file export location
        filename = asksaveasfilename(initialdir = "/",title = "Select folder",filetypes = (("GeoTiff","*.tif"),("all files","*.*"))) 
        
        #select pref curve by whatever species/lifestage was chosen from dropdown menu
        depPref = interp1d(salmonDict[dropdown.get()][0],salmonDict[dropdown.get()][1])
        velPref = interp1d(salmonDict[dropdown.get()][2],salmonDict[dropdown.get()][3])
        
        #replace all values in array with corresponding value on preference curve
        dep_array_norm = depPref(dep_array)
        vel_array_norm = velPref(vel_array)
            
        #combine dep and vel to final habitat suitibility (set no dat/no water value to -9999)
        final = (dep_array_norm * vel_array_norm)
        final = where(mask==nodata,-9999,final)
        
        #create geotiff object at filename location
        driver = GetDriverByName('GTiff')
        output = driver.Create(filename+'.tif',shape(final)[1],shape(final)[0],1,GDT_Float32)
        
        #write habitat suitability to band 1 of geotiff file
        output.GetRasterBand(1).WriteArray(final)
        output.GetRasterBand(1).SetNoDataValue(-9999)
        
        #set bounds and pixel size of raster and close
        output.SetGeoTransform(geotransform)
        output = None
        
        exportCompleteRaster['text'] = 'Export complete!'

exportShp = Button(root, text = 'Export As Raster', command = exportRaster)
exportShp.grid(column=0, row=7, sticky="ew",columnspan=2)

###############################################################################

root.mainloop()