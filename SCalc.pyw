# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 21:18:06 2017

@author: Corey
"""
import math
import Tkinter as tk
import csv
import os
import os.path
ScriptDir = os.path.dirname(__file__)

def kelvin(Temp):
    '''
    Convert the temperatures to kelvin
    '''
    Tkelvin = Temp + 273.15
    return Tkelvin

def spwater(Temp):
    '''
    This calculates the saturation pressure over water for a given temperature.
    '''
    SPwater = math.exp(54.842763-6763.22/Temp-4.21*math.log(Temp)+0.000367*Temp
          +math.tanh(0.0415*(Temp-218.8))*(53.878-1331.22/Temp-9.44523*math.log(Temp)
          +0.014025*Temp))
    return SPwater

def spice(Temp):
    '''
    While it may sound spicy, this actually is meant to calcuate the saturation
    pressure over ice.  It isn't used but I liked the variable name
    '''
    SPice=math.exp(9.550426-5723.265/Temp+3.53068*math.log(Temp)-0.00728332*Temp)
    return SPice


def avgpinf(Tmin,Tmax,RH):
    '''
    Calculate the average ambient pressure
    '''
    Tmax = kelvin(Tmax)
    Tmin = kelvin(Tmin)
    spMax = spwater(Tmax)
    spMin = spwater(Tmin)
    
    pinfMax = (spMax*RH)/100
    pinfMin = (spMin*RH)/100
    
    pinf = (pinfMax+pinfMin)/2
    return pinf
    
def avgspwater(Tmin,Tmax):
    '''
    Calculate the average ambient saturation pressure over water
    '''
    Tmax = kelvin(Tmax)
    Tmin = kelvin(Tmin)
    spMin = spwater(Tmin)
    spMax = spwater(Tmax)
    avg = (spMin+spMax)/2
    return avg
    
def avgspice(Tmin,Tmax):
    '''
    Calculate the average ambient saturation pressure over ice
    '''
    Tmax = kelvin(Tmax)
    Tmin = kelvin(Tmin)
    spMin = spice(Tmin)
    spMax = spice(Tmax)
    avg = (spMin+spMax)/2
    return avg

def sscalc(Tmin,Tmax,Tsub,RH):
    '''
    This will calculate the average supersaturation given the following variables
    Tmin is the lower bound of the ambient temperature
    Tmax is the upper bound of the ambient temperature
    Tsub is the temperature of the substrate
    RH is the relative humidity of the environment, aka the humidity chamber
    '''
    
    def pinf(SP,RH):
        '''
        This calculates the pressure of the ambient using the saturation pressure
        over water and relative humidity
        '''
        Pinf = (SP*RH)/100
        return Pinf
    
    def supersaturation(pinf, SP):
        '''
        This calculates the supersaturation from a given Pinf and the substrate's
        saturation pressure over water
        '''
        S = pinf / SP
        return S
    
    Tmax = kelvin(Tmax)
    Tmin = kelvin(Tmin)
    Tsub = kelvin(Tsub)
    
    spMax = spwater(Tmax)
    spMin = spwater(Tmin)
    spSub = spwater(Tsub)
    
    pinfMax = pinf(spMax,RH)
    pinfMin = pinf(spMin,RH)
    
    sMax = pinfMax/spSub
    sMin = pinfMin/spSub
    
    SS = (sMax + sMin)/2
    return SS

def rhcalc(Tmin,Tmax,Tsub,SS):
    '''
    This will calculate the necessary RH given the following variables
    Tmin is the lower bound of the ambient temperature
    Tmax is the upper bound of the ambient temperature
    Tsub is the temperature of the substrate
    SS is the supersaturation
    '''
    
    def pinf(SP, SS):
        '''
        This calculates the ambient pressure from the substrate's
        saturation pressure over water and desired supersaturation
        '''
        pinf = SP * SS
        return pinf
    
    def rh(SP,Pinf):
        '''
        This calculates the pressure of the ambient using the saturation pressure
        over water and relative humidity
        '''
        RH = (Pinf*100)/SP
        return RH
    
    Tmax = kelvin(Tmax)
    Tmin = kelvin(Tmin)
    Tsub = kelvin(Tsub)
    
    spMax = spwater(Tmax)
    spMin = spwater(Tmin)
    spSub = spwater(Tsub)
    
    pinf = pinf(spSub,SS)
    
    RHMax = rh(spMax,pinf)
    RHMin = rh(spMin,pinf)
    
    RH = (RHMax + RHMin)/2
    
    return RH

def tsubcalc(Tmin,Tmax,RH,SS):
    '''
    This will calculate the necessary RH given the following variables
    Tmin is the lower bound of the ambient temperature
    Tmax is the upper bound of the ambient temperature
    RH is the relative humidity
    SS is the supersaturation
    '''
    # These are the initial guesses, it's not very pretty
    # SSguess is overwritten immediately when the loop starts
    # basically increment temperature from -50 by 0.001 until the
    # difference between the guess and the given Supersaturation is less than 0.001
    Tguess = -50.0
    SSguess = -100
    while(abs(SSguess-SS) > 0.001):
        SSguess = sscalc(Tmin, Tmax, Tguess, RH)
        Tguess = Tguess + 0.001
        if(Tguess > 60):
            break
    return Tguess

class MainWindow:
    def __init__(self, master):        
        
        ################################################################
        # Variable declarations and setting intial values
        ################################################################
        self.RHbox = tk.IntVar()
        self.SSbox = tk.IntVar()
        self.Tsubbox = tk.IntVar()
        self.Tmax = tk.DoubleVar()
        self.Tmin = tk.DoubleVar()
        self.Tsub = tk.DoubleVar()
        self.RH = tk.DoubleVar()
        self.SS = tk.DoubleVar()
        self.RHResult = tk.DoubleVar()
        self.SSResult = tk.DoubleVar()
        self.TsubResult = tk.DoubleVar()
        self.nDecimals = tk.IntVar()
        self.spwbox = tk.IntVar()
        self.spibox = tk.IntVar()
        self.pinfbox = tk.IntVar()
        self.spwAVal = tk.DoubleVar() # Ambient SP over water
        self.spwSVal = tk.DoubleVar() # Substrate SP over water
        self.spiAVal = tk.DoubleVar()
        self.spiSVal = tk.DoubleVar()
        self.pinfVal = tk.DoubleVar()
        
        # This gets the values that were 
        PreviousSettingsPath = 'Files/PreviousSettings.csv'
        PreviousSettingsPath = os.path.join(ScriptDir, PreviousSettingsPath)
        PreviousSettings = []
        with open(PreviousSettingsPath) as f:
            reader = csv.reader(f)
            PreviousSettings = next(reader)
        self.RHbox.set(PreviousSettings[0])
        self.SSbox.set(PreviousSettings[1])
        self.Tsubbox.set(PreviousSettings[2])
        self.Tmax.set(PreviousSettings[3])
        self.Tmin.set(PreviousSettings[4])
        self.Tsub.set(PreviousSettings[5])
        self.RH.set(PreviousSettings[6])
        self.SS.set(PreviousSettings[7])
        self.RHResult.set(PreviousSettings[8])
        self.SSResult.set(PreviousSettings[9])
        self.TsubResult.set(PreviousSettings[10])
        self.nDecimals.set(PreviousSettings[11])
        self.spwbox.set(PreviousSettings[12])
        self.spibox.set(PreviousSettings[13])
        self.pinfbox.set(PreviousSettings[14])
        self.spwAVal.set(PreviousSettings[15])
        self.spwSVal.set(PreviousSettings[16])
        self.spiAVal.set(PreviousSettings[17])
        self.spiSVal.set(PreviousSettings[18])
        self.pinfVal.set(PreviousSettings[19])
        
        ################################################################
        # Creating the GUI widgets
        ################################################################
        
        # Create a top menu bar
        self.menubar = tk.Menu(master)
        self.menubar.add_command(label='Settings', command=self.settingsMenu)
        master.config(menu=self.menubar)
        
        # Create the checkboxes to decide what to compute
        self.RHcalcButton = tk.Checkbutton(master, text='Solve for RH', width=10,
                                           variable = self.RHbox, command=self.rhUpdate)
        self.SScalcButton = tk.Checkbutton(master, text='Solve for SS', width=10,
                                           variable = self.SSbox, command=self.ssUpdate)
        self.TsubcalcButton = tk.Checkbutton(master, text='Solve for Tsub', width=10,
                                           variable = self.Tsubbox, command=self.tsubUpdate)
        
        self.preset1Button = tk.Button(master, text='Frost Growth', width=10, command=self.setPreset1)
        self.preset2Button = tk.Button(master, text='Experiment', width=10, command=self.setPreset2)
        self.preset3Button = tk.Button(master, text='Preset 3', width=10, command=self.setPreset3)

        
        # Create the 'labels', aka the text
        self.TmaxLabel = tk.Label(master, text='Max ambient temperature',anchor=tk.E,width=20)
        self.TminLabel = tk.Label(master, text='Min ambient temperature',anchor=tk.E,width=20)
        self.TsubLabel = tk.Label(master, text='Substrate temperature',anchor=tk.E,width=20)
        self.RHLabel = tk.Label(master, text='Relative humidity',anchor=tk.E,width=20)
        self.SSLabel = tk.Label(master, text='Supersaturation',anchor=tk.E,width=20)

        # Create the entry boxes
        self.TmaxEntry = tk.Entry(master, textvariable=self.Tmax,width=20)
        self.TminEntry = tk.Entry(master, textvariable=self.Tmin,width=20)
        self.TsubEntry = tk.Entry(master, textvariable=self.Tsub,width=20)
        self.RHEntry = tk.Entry(master, textvariable=self.RH,width=20)
        self.SSEntry = tk.Entry(master, textvariable=self.SS,width=20)
        
        # Create the calculation button and resulting values
        self.ComputeButton = tk.Button(master, text='Calculate',
                                       command = self.calculate, width=50)
        self.ResultLabel = tk.Label(master, text='')
        self.ResultNumLabel = tk.Label(master, text='')
        self.ResultLabel.configure(font=('Segoe UI', 11))
        self.ResultNumLabel.configure(font=('Segoe UI', 15))
        
        #Create the extra information labels
        self.spwALabel = tk.Label(master, text='Ambient saturation pressure over water',width=30,anchor=tk.E)
        self.spwAValLabel = tk.Label(master, textvariable=self.spwAVal,anchor=tk.W)
        self.spwSLabel = tk.Label(master, text='Substrate saturation pressure over water',width=30,anchor=tk.E)
        self.spwSValLabel = tk.Label(master, textvariable=self.spwSVal,anchor=tk.W)
        
        self.spiALabel = tk.Label(master, text='Ambient saturation pressure over ice',width=30,anchor=tk.E)
        self.spiAValLabel = tk.Label(master, textvariable=self.spiAVal,anchor=tk.W)
        self.spiSLabel = tk.Label(master, text='Substrate saturation pressure over ice',width=30,anchor=tk.E)
        self.spiSValLabel = tk.Label(master, textvariable=self.spiSVal,anchor=tk.W)
        
        self.pinfLabel = tk.Label(master, text='Ambient pressure',width=30,anchor=tk.E)
        self.pinfValLabel = tk.Label(master, textvariable=self.pinfVal,anchor=tk.W)
        
        
        ################################################################
        # Set locations for the widgets
        ################################################################
        
        # Place the checkboxes
        self.RHcalcButton.grid(row=0, column=0)
        self.SScalcButton.grid(row=0, column=1)
        self.TsubcalcButton.grid(row=0, column=2)
        
        # These place the labels in the GUI
        self.TmaxLabel.grid(row=1, column=0, columnspan=2)
        self.TminLabel.grid(row=2, column=0, columnspan=2)
        self.TsubLabel.grid(row=3, column=0, columnspan=2)

        # These place the entries in the GUI
        self.TmaxEntry.grid(row=1, column=2)
        self.TminEntry.grid(row=2, column=2)
        self.TsubEntry.grid(row=3, column=2)
        
        # Place the bottom rows
        self.ComputeButton.grid(row=6, columnspan=3)
        self.ResultLabel.grid(row=7,column=0, columnspan=2)
        self.ResultNumLabel.grid(row=7,column=2)
        
        # Use previous session's values to determine the initial layout
        if(self.RHbox.get()==1 and self.SSbox.get()==0 and self.Tsubbox.get()==0):
            self.rhUpdate()
        elif(self.RHbox.get()==0 and self.SSbox.get()==1 and self.Tsubbox.get()==0):
            self.ssUpdate()
        elif(self.RHbox.get()==0 and self.SSbox.get()==0 and self.Tsubbox.get()==1):
            self.tsubUpdate()
        
        if(self.spwbox.get()==1):
            self.spwALabel.grid(row=8,columnspan=2)
            self.spwAValLabel.grid(row=8,column=2)
            self.spwSLabel.grid(row=9,columnspan=2)
            self.spwSValLabel.grid(row=9,column=2)
            
        if(self.spibox.get()==1):
            self.spiALabel.grid(row=10,columnspan=2)
            self.spiAValLabel.grid(row=10,column=2)
            self.spiSLabel.grid(row=11,columnspan=2)
            self.spiSValLabel.grid(row=11,column=2)
            
        if(self.pinfbox.get()==1):
            self.pinfLabel.grid(row=12,columnspan=2)
            self.pinfValLabel.grid(row=12,column=2)
            
        self.preset1Button.grid(row=13, column=0)
        self.preset2Button.grid(row=13, column=1)
        self.preset3Button.grid(row=13, column=2)
        
        root.wm_title('Humidity Chamber Calculator')
        # This rebinds the window close red X to a function that will save the 
        # entered values and then close the window
        master.protocol("WM_DELETE_WINDOW",self.saveValues)
        
    ################################################################
    # Functions defined in the MainWindow class but not __init__
    ################################################################    
    
    def settingsMenu(self):
        '''
        This is the box that pops up when the settings button is pressed
        '''
        # Create a frame called top that everything is placed in
        top = tk.Toplevel()
        
        # Create the widgets
        spwBox = tk.Checkbutton(top, text='Display saturation pressure over water',
                                variable=self.spwbox, anchor=tk.W, width=30,
                                command=self.spwUpdate)
        spiBox = tk.Checkbutton(top, text='Display saturation pressure over ice',
                                variable=self.spibox, anchor=tk.W, width=30,
                                command=self.spiUpdate)
        pinfBox = tk.Checkbutton(top, text='Display P_infinity',
                                 variable=self.pinfbox, anchor=tk.W, width=30,
                                 command=self.pinfUpdate)
        nDecimalsLabel = tk.Label(top, text='Result decimal places', anchor=tk.W, width=20)
        nDecimalsEntry = tk.Entry(top, textvariable=self.nDecimals, width=10)
        
        # Place the widgets into the window

        spwBox.grid(row=0,columnspan=2)
        spiBox.grid(row=1,columnspan=2)
        pinfBox.grid(row=2,columnspan=2)
        nDecimalsLabel.grid(row=3,column=0)
        nDecimalsEntry.grid(row=3,column=1)
        
        # Set the location that the window appears to be the same as the main window
        x = root.winfo_x()
        y = root.winfo_y()
        top.geometry("+%d+%d" % (x, y))
    
    def setPreset1(self):
        self.Tsub.set(-20)
        self.SS.set(4)
    
    def setPreset2(self):
        self.Tsub.set(-10)
        self.SS.set(1.1)
    
    def setPreset3(self):
        self.Tsub.set(-20)
        self.SS.set(4)
        
        
    def calculate(self):
        '''
        Calculates the values desired when the compute button is pressed
        '''
        # Check to see which box is selected and then calculate it
        if(self.RHbox.get() == 1):
            RH = round(rhcalc(self.Tmin.get(), self.Tmax.get(), self.Tsub.get(), self.SS.get()),self.nDecimals.get())
            Result = RH
            self.RHResult.set(Result)
        elif(self.SSbox.get() == 1):
            SS = round(sscalc(self.Tmin.get(),self.Tmax.get(),self.Tsub.get(),self.RH.get()),self.nDecimals.get())
            Result = SS
            self.SSResult.set(Result)
        elif(self.Tsubbox.get() == 1):
            Tsub = round(tsubcalc(self.Tmin.get(),self.Tmax.get(),self.RH.get(), self.SS.get()),self.nDecimals.get())
            Result = Tsub
            self.TsubResult.set(Result)
        else: # If nothing is selected the user is insulted, as it should be
            top = tk.Toplevel()
            topLabel = tk.Label(top, text='Nothing is selected dummy.')
            topLabel.pack()
            x = root.winfo_x()
            y = root.winfo_y()
            top.geometry("+%d+%d" % (x, y))
        self.ResultNumLabel.configure(text=Result)
        
        # Saturation pressure over water calculations
        if(self.spwbox.get() == 1):
            spwA = avgspwater(self.Tmin.get(),self.Tmax.get())
            self.spwAVal.set(round(spwA,self.nDecimals.get()))
            spwS = spwater(kelvin(self.Tsub.get()))
            self.spwSVal.set(round(spwS,self.nDecimals.get()))
        
        # Saturation pressure over ice calculations
        if(self.spibox.get() == 1):
            spiA = avgspice(self.Tmin.get(),self.Tmax.get())
            self.spiAVal.set(round(spiA,self.nDecimals.get()))
            spiS = spice(kelvin(self.Tsub.get()))
            self.spiSVal.set(round(spiS,self.nDecimals.get()))
        
        # Ambient pressure calculations
        if(self.pinfbox.get() == 1):
            pinf = avgpinf(self.Tmin.get(),self.Tmax.get(),self.RH.get())
            self.pinfVal.set(round(pinf,self.nDecimals.get()))
            
        
    def rhUpdate(self):
        '''
        Show the proper fields when solving for RH
        '''
        self.SSLabel.grid(row=5, column=0, columnspan=2)
        self.SSEntry.grid(row=5, column=2)
        self.TsubLabel.grid(row=3, column=0, columnspan=2)
        self.TsubEntry.grid(row=3, column=2)
        self.RHLabel.grid_forget()
        self.RHEntry.grid_forget()
        self.SSbox.set(0)
        self.Tsubbox.set(0)
        self.ComputeButton.config(text='Calculate relative humidity')
        self.ResultLabel.config(text='The relative humidity is')
        self.ResultNumLabel.configure(text=str(self.RHResult.get()))
        
    def ssUpdate(self):
        '''
        Show the proper fields when solving for SS
        '''
        self.RHLabel.grid(row=4, column=0, columnspan=2)
        self.RHEntry.grid(row=4, column=2)
        self.TsubLabel.grid(row=3, column=0, columnspan=2)
        self.TsubEntry.grid(row=3, column=2)
        self.SSLabel.grid_forget()
        self.SSEntry.grid_forget()
        self.RHbox.set(0)
        self.Tsubbox.set(0)
        self.ComputeButton.config(text='Calculate supersaturation')
        self.ResultLabel.config(text='The supersaturation is')
        self.ResultNumLabel.configure(text=str(self.SSResult.get()))
        
    def tsubUpdate(self):
        '''
        Show the proper fields when solving for SS
        '''
        self.RHLabel.grid(row=4, column=0, columnspan=2)
        self.RHEntry.grid(row=4, column=2)
        self.SSLabel.grid(row=5, column=0, columnspan=2)
        self.SSEntry.grid(row=5, column=2)
        self.TsubLabel.grid_forget()
        self.TsubEntry.grid_forget()
        self.RHbox.set(0)
        self.SSbox.set(0)
        self.ComputeButton.config(text='Calculate substrate temperature')
        self.ResultLabel.config(text='The substrate temperature is')
        self.ResultNumLabel.configure(text=str(self.TsubResult.get()))
    
    def spwUpdate(self):
        '''
        Show the saturation pressure of water when the box is clicked
        '''
        if(self.spwbox.get()==1):
            self.spwALabel.grid(row=8,columnspan=2)
            self.spwAValLabel.grid(row=8,column=2)
            self.spwSLabel.grid(row=9,columnspan=2)
            self.spwSValLabel.grid(row=9,column=2)
        else:
            self.spwALabel.grid_forget()
            self.spwAValLabel.grid_forget()
            self.spwSLabel.grid_forget()
            self.spwSValLabel.grid_forget()
    
    def spiUpdate(self):
        '''
        Show the saturation pressure of ice when the box is clicked
        '''
        if(self.spibox.get()==1):
            self.spiALabel.grid(row=10,columnspan=2)
            self.spiAValLabel.grid(row=10,column=2)
            self.spiSLabel.grid(row=11,columnspan=2)
            self.spiSValLabel.grid(row=11,column=2)
        else:
            self.spiALabel.grid_forget()
            self.spiAValLabel.grid_forget()
            self.spiSLabel.grid_forget()
            self.spiSValLabel.grid_forget()
    
    def pinfUpdate(self):
        '''
        Show the saturation pressure of water when the box is clicked
        '''
        if(self.pinfbox.get()==1):
            self.pinfLabel.grid(row=12,columnspan=2)
            self.pinfValLabel.grid(row=12,column=2)
        else:
            self.pinfLabel.grid_forget()
            self.pinfValLabel.grid_forget()
    
    def quitWindow(self):
        '''
        I feel like there's an easier way to do this, but it's working so...
        '''
        root.destroy()
    
    def saveValues(self):
        '''
        Here I save a csv file with the values that are in the window when it's
        closed.  Then they are read when the program is next loaded so that things
        are pretty and stuff
        '''
        # Create the path going to the csv
        SavePath = 'Files/PreviousSettings.csv'
        SavePath = os.path.join(ScriptDir, SavePath)
        # Get all of the entered values into a list called Settings
        Settings = [self.RHbox.get(),self.SSbox.get(),self.Tsubbox.get(),
                    self.Tmax.get(),self.Tmin.get(),self.Tsub.get(),
                    self.RH.get(),self.SS.get(),self.RHResult.get(),
                    self.SSResult.get(),self.TsubResult.get(),
                    self.nDecimals.get(),self.spwbox.get(),
                    self.spibox.get(), self.pinfbox.get(),
                    self.spwAVal.get(), self.spwSVal.get(),
                    self.spiAVal.get(), self.spiSVal.get(),
                    self.pinfVal.get()]
        # Write Settings into the csv file
        with open(SavePath, "w") as f:
            writer = csv.writer(f)
            writer.writerow(Settings)
        # Close the window by calling the quitWindow function
        self.quitWindow()
    
root = tk.Tk()
gui = MainWindow(root)
root.mainloop()