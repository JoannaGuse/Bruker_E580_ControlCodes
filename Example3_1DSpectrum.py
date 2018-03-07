# -*- coding: utf-8 -*-
"""
Created on Thu May 18 18:57:58 2017

@author:Joanna
"""


import os,sys; sys.path.insert(0, os.popen("Xepr --apipath").read())  # this locates the XeprAPI module
import XeprAPI              # load the Xepr API module
import numpy as NP
os.chdir('/home/xuser/Dropbox (UNSW ESR Lab)/TEST_EPR_IQ_SETUP/ExpCodes')
import XEPR_moduleJo as Jo
import time
import pylab

todaydate=(str(time.gmtime()[2])+'_'+str(time.gmtime()[1])+ '_'+ str(time.gmtime()[0]))
pathname='/home/xuser/Dropbox (UNSW ESR Lab)/TEST_EPR_IQ_SETUP/ExpCodes/Data/'
if not os.path.exists(pathname + todaydate):
    os.mkdir(pathname + todaydate)

savedir=pathname +todaydate+'/'


#%%______________my parameters_______________________

VideoGain=48
VideoBW=200
TL=16

mwAtten=7 # optimize in setup
Bcenter=3445 # will optimize
Bsweep=100

SRT=1000
ShotPerPoint=200
Nscans=1
Navgs=500
sizeX=2048
sizeB=201


d0=1370
pg=100
hahnecho=((0,84), (500, 78))
EVENT=((0,50), (0,0))

setup=True
    
samplename='TEMPO' #for notes
Temp=297

#invBW='69MHz' 
#p1='Square'
#p2='Square'
#pulses='Echo1_SqSq'

invBW='60MHz' 
p1='EBURP2'
p2='REBURP'
pulses='UnscaledEcho2_ERE'



#%%______________connect___________________ 
[Xepr, ID]=Jo.ConnectXEPR(globals())

if setup:
    pulse_exp=Jo.createPulseExp(Xepr, Expname='setup')
    time.sleep(1)
    config = Xepr.XeprExperiment("AcqHidden");
    pulse_exp=Jo.configureTimeout(pulse_exp, timeout=600)
    pulse_exp=Jo.configureRecieverUnit(pulse_exp,config, VideoGain, VideoBW, mwAtten, TL)
    Xepr.XeprCmds.aqParOpen()
    
    pulse_exp=Jo.configureShot(pulse_exp, SRT, ShotPerPoint)
    time.sleep(1)
    pulse_exp=Jo.configureField(pulse_exp, int(Bcenter), Bsweep=100, startPos='Center')   
    
    pulse_exp=Jo.configureAcqTrigger(pulse_exp, d0, pg, displacement=0, increment=0, timebase='Single Point') 
    pulse_exp=Jo.configurePattern2(pulse_exp, Xepr, 'U2', EVENT)   
    pulse_exp=Jo.configurePattern2(pulse_exp,  Xepr, '+x', hahnecho)
    pulse_exp=Jo.configurePattern2(pulse_exp,  Xepr, 'U1', hahnecho)   
    

    pulse_exp=Jo.configureAcqFromTables(pulse_exp, dim=(2048,1), Xaxis='Transient', Yaxis='Magnetic Field', Nscans=Nscans)
    config=Jo.configureSpecjet(config, Npts=2048, Navgs=Navgs, timebase=1)
    time.sleep(2)
    pulse_exp.aqExpRunAndWait()

    ff=raw_input('adjust phase, B0 and HPP to optimize echo and then enter')
    pg=raw_input('enter width of echo for integration:')
    start=raw_input('enter start of echo:')
    
    d0=d0+int(start)
    pg=int(pg)
    Bcenter=float(pulse_exp["CenterField"].value) 
    mwAtten=pulse_exp["Attenuation"].value 



#%%_____________configure_______________________-
pulse_exp=Jo.createPulseExp(Xepr, Expname='1D_ESE_spectrum')
config = Xepr.XeprExperiment("AcqHidden");
pulse_exp=Jo.configureTimeout(pulse_exp, timeout=600)
pulse_exp=Jo.configureRecieverUnit(pulse_exp,config, VideoGain, VideoBW, mwAtten, TL)
Xepr.XeprCmds.aqParOpen()

pulse_exp=Jo.configureAcqTrigger(pulse_exp, d0, pg, displacement=0, increment=0, timebase='1.0') 
pulse_exp=Jo.configurePattern(pulse_exp, '+x', hahnecho)
pulse_exp=Jo.configurePattern(pulse_exp, 'U1', hahnecho)
pulse_exp=Jo.configurePattern(pulse_exp, 'U2', EVENT)


pulse_exp=Jo.configureShot(pulse_exp, SRT, ShotPerPoint)
pulse_exp=Jo.configureAcqFromTables(pulse_exp, dim=(sizeB, 1), Xaxis='Magnetic Field', Yaxis='Magnetic Field', Nscans=Nscans)
config=Jo.configureSpecjet(config, Npts=sizeX, Navgs=Navgs, timebase=1)
pulse_exp=Jo.configureField(pulse_exp, int(Bcenter), Bsweep, startPos='Left')

#%% perform Experiment
pulse_exp.aqExpRunAndWait()
dataset = Xepr.XeprDataset(xeprset = "primary", iscomplex=True)
x=dataset.X
y=dataset.O
B=NP.linspace(Bcenter-Bsweep/2, Bcenter+Bsweep/2, sizeB)
Xepr=Jo.DefineExpConditions(Xepr, samplename, Temp, other=[])


#%% save data

savetitle =samplename+'_1DSPEC_'+pulses+invBW+'_'+str(Bsweep)+'G_HPP'+str(mwAtten) 

savefile = "'" + savedir + savetitle + "'"
Xepr.XeprCmds.vpSave('Current', 'Primary', savetitle, savefile)
Xepr.XeprCmds.vpSaveAsc('Primary', savefile)


Jo.savetoMATLAB(savedir+savetitle, globals())


print '___FINISHED experiment__'
#pulse_exp=Jo.EndSession(pulse_exp, config)
