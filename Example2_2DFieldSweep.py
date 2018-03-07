#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 19:09:58 2017

@author: Joanna 
"""
def main():
        
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
    
    scriptname=sys.argv[0]
    with open (scriptname, "r") as myfile:
        scriptext=myfile.readlines()
                  
    #%%______________my parameters_______________________
    
    VideoGain=33
    VideoBW=20
    TL=16
    
    mwAtten=5 # optimize in setup
    Bcenter=3481# will optimize
    Bsweep=120
    
    SRT=200
    ShotPerPoint=1
    Nscans=1
    Navgs=500
    sizeX=1024
    sizeY=121
    
    
    d0=400
    pg=20
    pulsepattern=((0,38), (400,38))
    EVENT=((800,50), (0,0))
    
    setup=True
        
    samplename='TEMPO' #for notes
    Temp=80
    
    
    #invBW='69MHz' 
    #p1='Square'
    #p2='Square'
    #pulses='Exp1SqSq'
    
    invBW='60MHz' 
    p1='Gauss'
    p2='Gauss'
    pulses='Exp2GG'
    
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
        pulse_exp=Jo.configurePattern2(pulse_exp,  Xepr, '+x', pulsepattern)
        pulse_exp=Jo.configurePattern2(pulse_exp,  Xepr, 'U1', pulsepattern)
        pulse_exp=Jo.configurePattern2(pulse_exp, Xepr, 'U2', EVENT)
    
        pulse_exp=Jo.configureAcqFromTables(pulse_exp, dim=(sizeX,1), Xaxis='Transient', Yaxis='Magnetic Field', Nscans=Nscans)
        config=Jo.configureSpecjet(config, Npts=sizeX, Navgs=Navgs, timebase=1)
        time.sleep(2)
        pulse_exp.aqExpRunAndWait()
    
        ff=raw_input('adjust phase, B0 and HPP to optimize echo and then enter')
        
        Bcenter=float(pulse_exp["CenterField"].value) 
        mwAtten=pulse_exp["Attenuation"].value 
        fuw=pulse_exp["FrequencyMon"].value 
                     
            
    #%%_____________configure_______________________-
    pulse_exp=Jo.createPulseExp(Xepr, Expname='Trans_vs_B')
    config = Xepr.XeprExperiment("AcqHidden")
    pulse_exp=Jo.configureTimeout(pulse_exp, timeout=600)
    pulse_exp=Jo.configureRecieverUnit(pulse_exp,config, VideoGain, VideoBW, mwAtten, TL)
    Xepr.XeprCmds.aqParOpen()
    
    pulse_exp=Jo.configureAcqTrigger(pulse_exp, d0, pg, displacement=0, increment=0, timebase='Single Point') 
    pulse_exp=Jo.configurePattern(pulse_exp, '+x', pulsepattern)
    pulse_exp=Jo.configurePattern(pulse_exp, 'U1', pulsepattern)
    pulse_exp=Jo.configurePattern(pulse_exp, 'U2', EVENT)
    
    
    pulse_exp=Jo.configureShot(pulse_exp, SRT, ShotPerPoint)
    pulse_exp=Jo.configureAcqFromTables(pulse_exp, dim=(sizeX,sizeY), Xaxis='Transient', Yaxis='Magnetic Field', Nscans=Nscans)
    config=Jo.configureSpecjet(config, Npts=sizeX, Navgs=Navgs, timebase=1)
    pulse_exp=Jo.configureField(pulse_exp, int(Bcenter), Bsweep, startPos='Left')
    
    #%% perform Experiment
    pulse_exp.aqExpRunAndWait()
    dataset = Xepr.XeprDataset(xeprset = "primary", iscomplex=True)
    x=dataset.X
    y=dataset.O
    B=NP.linspace(Bcenter-Bsweep/2, Bcenter+Bsweep/2, sizeY)
    Xepr=Jo.DefineExpConditions(Xepr, samplename, Temp, other=[])
    
    
    #%% save 
    
    savetitle =samplename+'_2DSPEC_'+pulses+invBW+'_'+str(Bsweep)+'G_HPP'+str(int(mwAtten))+'_'+str(Temp)+'K'
    
    
    savefile = "'" + savedir + savetitle + "'"
    Xepr.XeprCmds.vpSave('Current', 'Primary', savetitle, savefile)
    Xepr.XeprCmds.vpSaveAsc('Primary', savefile)
    
    
    Jo.savetoMATLAB(savedir+savetitle, globals())
    
    
    print '___FINISHED experiment__'
    #pulse_exp=Jo.EndSession(pulse_exp, config)
    
    
if __name__ == "__main__":main() ## with if