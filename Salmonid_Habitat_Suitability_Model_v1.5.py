# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 08:43:37 2019

@author: lurussell
"""

#Version 1.5 updated Dec 22nd 2021
# Switched from GDAL to rasterio
# Dropped scipy.interp1d for numpy.interp to reduce exe size

#Version 1.4 updated June 5th 2020
#Added try/except clause to print out error statement if export fails for some reason
#Added version number to the tool and added source for the preference curves

#Version 1.3 updated Feb 2020
#Added pref curve for spring chinook holding an O.mykiss juvenile
#No change to the code, but executable is compiled in python console using pyinstaller (not using anaconda) for much smaller file size

#Version 1.2 updated January 2020
#Put entire code into a class to do away with global variables
#changed depth/velocity inputs from labels to entry boxes to allow for easy copy/paste of raster file locations

#Version 1.1 updated January 2020
#Added preference curves for Juvenile Coho Rearing and Juvenile/Adult Rainbow Trout RearingYoo

from tkinter import Label, Button, Frame, Entry
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from numpy import where, shape, interp
from numpy.ma import masked_where
import rasterio

###############################################################################

class Application(Frame):
    
    def __init__(self, master=None, Frame=None):
        Frame.__init__(self, master)
        super(Application,self).__init__()
        self.grid(column = 8,row = 8)
        self.createWidgets()
        self.createCurves()

###############################################################################
    def createWidgets(self):
        #define tkinter buttons, labels, etc...
        title = Label(text = 'Salmonid Habitat Suitability Index')
        title.config(font=('Calibri',18))
        self.values = ['Adult Chinook Spawning Large River',
                  'Adult Chinook Spawning Small River',
                  'Juvenile Chinook Rearing',
                  'Adult Coho Spawning',
                  'Juvenile Coho Rearing',
                  'Adult Sockeye Spawning',
                  'Juvenile/Adult Rainbow Trout Rearing',
                  'Spring Chinook Holding',
                  'O. mykiss Juvenile']
        self.dropdown = Combobox(values=self.values)
        dropdownLabel = Label(text='Salmonid species/lifestage: ')
        self.inputfileDep = Entry()
        self.inputfileVel = Entry()
        self.exportCompleteRaster = Label(text = '')
        devLabel = Label(text='Developed in Python 3.7 by Luke Russell, Version 1.5, last update Dec 2021')
        devLabel.config(font=('Calibri',7))
        citeLabel = Label(text='Habitat suitability curves taken from: \nWashington Dept. of Fish and Wildlife Instream Flow Study Guidelines (2004 & 2016)')
        citeLabel.config(font=('Calibri',7))
        
        #place tkinter objects onto grid
        self.inputfileDep.grid(column=1, row=1, sticky="ew",columnspan= 2,padx=10,pady=5)
        self.inputfileVel.grid(column=1, row=2, sticky="ew",columnspan= 2,padx=10,pady=5)
        title.grid(column=0, row=[0], columnspan = 3, sticky="ew")
        dropdownLabel.grid(column=0,row=3,sticky='ew',columnspan=2,padx=10,pady=10)
        self.dropdown.grid(column=2,row=3,sticky='ew',padx=10,pady=10) 
        self.exportCompleteRaster.grid(column=2,row=7,sticky='ew',columnspan=2)
        devLabel.grid(column=0,row=9,columnspan=3,sticky='ew')
        citeLabel.grid(column=0,row=8,columnspan=3,sticky='ew')
        
        #place tkinter buttons
        openDepth = Button(text = 'Open Depth Raster', command = self.openDep)
        openDepth.grid(column=0, row=1, sticky="ew",padx=10,pady=5)
        
        openVelocity = Button(text = 'Open Velocity Raster', command = self.openVel)
        openVelocity.grid(column=0, row=2, sticky="ew",padx=10,pady=5)
        
        exportShp = Button(text = 'Export As Raster', command = self.exportRaster)
        exportShp.grid(column=0, row=7, sticky="ew",columnspan=2,padx=10,pady=5)

###############################################################################
    def createCurves(self):
        #time to define the preference curves for each salmon species and lifestage
        #all lists are indexed the same 0=depth, 1=depth preference value, 2=velocity, 3=velocity preference value
        ChnSpwnLR = [[0,0.55,1.05,1.55,5.05,10,30,35,99], #depth
                        [0,0,0.75,1,1,0,0,0,0], #depth pref
                        [0,0.55,0.75,1.55,3.55,4.95,6.55,7,99], #velocity
                        [0,0,0.79,1,1,0,0,0,0]] #velocity pref
        
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
        
        SpringChnHold = [[0,0.8,2,6.5,99],
                        [0,0,0.1,1,1],
                        [0,2.4,3.8,4.8,6,99],
                        [1,1,0.8,0.2,0,0]]
        
        OmykissJuv = [[0,0.15,0.65,1.35,2.65,99],
                      [0,0,0.1,0.63,1,1],
                      [0,0.75,0.95,1.15,1.55,1.85,3.15,3.85,5,99],
                      [0.55,1,1,0.87,0.78,0.54,0.3,0.07,0,0]]
        
        #put all the preference curves into  a single list
        prefcurves = [ChnSpwnLR,ChnSpwnSR,ChnJuv,CohoSpwn,CohoJuv,SockSpwn,RainbowTrout,SpringChnHold,OmykissJuv]
        #create a dict object to make it easy to call
        self.salmonDict = dict(zip(self.values,prefcurves))

###############################################################################

    #define func and button for opening file directory to load depth raster
    def openDep(self):
        self.inputfileDep.delete(0,'end')
        self.inputfileDep.insert(0,'Working...')
        
        filename = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Rasters",["*.img","*.tif","*.jpg",".jpeg",".jp2",".png",".dat","*.bmp","*.vrt"]),("all files","*.*")))
        self.inputfileDep.delete(0,'end')
        self.inputfileDep.insert(0,filename)
###############################################################################

    #define func and button for opening file directory to load velocity raster
    def openVel(self):
        self.inputfileVel.delete(0,'end')
        self.inputfileVel.insert(0,'Working...')
        
        filename = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("Rasters",["*.img","*.tif","*.jpg",".jpeg",".jp2",".png",".dat","*.bmp","*.vrt"]),("all files","*.*")))
        self.inputfileVel.delete(0,'end')
        self.inputfileVel.insert(0,filename)
###############################################################################

    def exportRaster(self):  
        #make sure input file is selected
        if self.inputfileVel.get() != '' and self.inputfileVel.get() != 'Please select input file!' and self.inputfileDep.get() != '' and self.inputfileDep.get() != 'Please select input file!':
            while self.dropdown.get() not in self.values:
                    self.dropdown.set('Please select variable!')
                    return
            
            self.exportCompleteRaster['text'] = 'Working...'
            #get file export location
            filename = asksaveasfilename(initialdir = "/",title = "Select folder",filetypes = (("GeoTiff","*.tif"),("all files","*.*")))
            if filename:
                try:
                    ###################################################################
                    #open dep raster and read as array, remove no data value (no data = no water)
                    with rasterio.open(self.inputfileDep.get()) as raster:
                        self.nodata = raster.nodata
                        self.dep_array = raster.read(1)
                        self.mask = masked_where(self.dep_array==self.nodata,self.dep_array)
                        self.mask = self.dep_array
                        self.dep_array = where(self.dep_array==self.nodata,0,self.dep_array)
                        
                        #grab the geospatial info of the raster to make sure the output has the same units/size/resolution
                        profile = raster.profile
                    
                    ###################################################################
                    #open vel raster and read as array, remove no data value (no data = no water)
                    with rasterio.open(self.inputfileVel.get()) as raster:
                        nodata = raster.nodata
                        self.vel_array = raster.read(1)
                        self.vel_array = where(self.vel_array==nodata,0,self.vel_array)
                        
                    # no need to grab the geotransform info because we already grabbed it from the depth raster
                    
                    ###################################################################
                    #replace all values in array with corresponding value on preference curve
                    dep_array_norm = interp(self.dep_array,self.salmonDict[self.dropdown.get()][0],self.salmonDict[self.dropdown.get()][1])
                    vel_array_norm = interp(self.vel_array,self.salmonDict[self.dropdown.get()][2],self.salmonDict[self.dropdown.get()][3])
                        
                    #combine dep and vel to final habitat suitibility (set no dat/no water value to -9999)
                    final = dep_array_norm * vel_array_norm
                    final = where(self.mask==self.nodata,-9999,final)
                    
                    #create geotiff object at filename location
                    output_path = filename+'.tif'
                    profile['driver'] = 'GTIFF'
                    with rasterio.open(output_path, 'w', **profile) as output:
                        #write habitat suitability to band 1 of geotiff file
                        output.write(final,indexes=1)
                        output.nodata = -9999
                
                    self.exportCompleteRaster['text'] = 'Export complete!'
                except Exception as e:
                    print(e)
                    self.exportCompleteRaster['text'] = 'Failed to export.'
            else:
                self.exportCompleteRaster['text'] = 'Please select output file location!'
###############################################################################

app = Application()
app.master.title('HSI Tool')
app.mainloop()