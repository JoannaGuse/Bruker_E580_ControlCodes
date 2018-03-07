#-------------------------------------------------------------------------------
# Name:       2DFieldSweep
# Purpose:
#
# Author:      Joanna Guse
#
# Created:     27/07/2017
# Copyright:   (c) z5011347 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

#%% import directories and modules
import os,sys; sys.path.insert(0, os.popen("Xepr --apipath").read())  # this locates the XeprAPI module
import XeprAPI              # load the Xepr API module
import numpy as NP
os.chdir('/home/xuser/Dropbox (UNSW ESR Lab)/TEST_EPR_IQ_SETUP/ExpCodes')
import XEPR_moduleJo as Jo
import time
import pylab
import scipy.io as sio

#%% set up saving directory
todaydate=(str(time.gmtime()[2])+'_'+str(time.gmtime()[1])+ '_'+ str(time.gmtime()[0]))
pathname='/home/xuser/Dropbox (UNSW ESR Lab)/TEST_EPR_IQ_SETUP/ExpCodes/Data/'
if not os.path.exists(pathname + todaydate):
    os.mkdir(pathname + todaydate)

savedir=pathname +todaydate+'/'

scriptname=sys.argv[0]
with open (scriptname, "r") as myfile:
    scriptext=myfile.readlines()



#%% set up parameters in dictionary v,
v={'scriptext': scriptext}
v={'scriptname': scriptname}

v['VideoGain']= 33
v[VideoBW]=20
v[TL]=16


v[mwAtten]=5 # optimize in setup
v[Bcenter]=3481# will optimize
v[Bsweep]=120

v[SRT]=200
v[ShotPerPoint]=1
v[Nscans]=1
v[Navgs]=500
v[sizeX]=1024
v[sizeY]=121


v[d0]=400
v[pg]=20
v[p1]=16
v[p2]=32
v[tau]=400

v[pulsepattern]=((0,v[p1]), (v[tau],v[p2]))
v[EVENT]=((1.2*v[tau],100), (0,0))  #Triggers AWG sequence



v[samplename]='TEMPO' #for notes
v[Temp]=80

v[pulses]='SS'
v[invBW]=34

#%% connect to EPR

[Xepr, ID]=Jo.ConnectXEPR(globals())


#%%_____________setup experiment_________________________

pulse_exp=Jo.createPulseExp(Xepr, Expname='setup')
time.sleep(1)
config = Xepr.XeprExperiment("AcqHidden");
pulse_exp=Jo.configureTimeout(pulse_exp, timeout=600)
pulse_exp=Jo.configureRecieverUnit(pulse_exp,config, v[VideoGain], v[VideoBW], v[mwAtten], v[TL])
Xepr.XeprCmds.aqParOpen()

pulse_exp=Jo.configureShot(pulse_exp, v[SRT], v[ShotPerPoint])
time.sleep(1)
pulse_exp=Jo.configureField(pulse_exp, int(v[Bcenter]), v[Bsweep], startPos='Center')

pulse_exp=Jo.configureAcqTrigger(pulse_exp, v[d0], v[pg], displacement=0, increment=0, timebase='Single Point')
pulse_exp=Jo.configurePattern2(pulse_exp,  Xepr, '+x', v[pulsepattern])
pulse_exp=Jo.configurePattern2(pulse_exp,  Xepr, 'U1', v[pulsepattern])
pulse_exp=Jo.configurePattern2(pulse_exp, Xepr, 'U2', v[EVENT])

pulse_exp=Jo.configureAcqFromTables(pulse_exp, dim=(v[sizeX],1), Xaxis='Transient', Yaxis='Magnetic Field', Nscans=Nscans)
config=Jo.configureSpecjet(config, Npts=v[sizeX], Navgs=v[Navgs], timebase=1)
time.sleep(2)
pulse_exp.aqExpRunAndWait()

ff=raw_input('adjust phase, B0 and HPP to optimize echo and then enter')

v[Bcenter]=float(pulse_exp["CenterField"].value)
v[mwAtten]=pulse_exp["Attenuation"].value
v[fuw]=pulse_exp["FrequencyMon"].value




#%% _____________configure Experiment _______________________-
pulse_exp=Jo.createPulseExp(Xepr, Expname='Trans_vs_B')
time.sleep(1)
config = Xepr.XeprExperiment("AcqHidden");
pulse_exp=Jo.configureTimeout(pulse_exp, timeout=600)
pulse_exp=Jo.configureRecieverUnit(pulse_exp,config, v[VideoGain], v[VideoBW], v[mwAtten], v[TL])
Xepr.XeprCmds.aqParOpen()

pulse_exp=Jo.configureShot(pulse_exp, v[SRT], v[ShotPerPoint])
time.sleep(1)
pulse_exp=Jo.configureField(pulse_exp, int(v[Bcenter]), v[Bsweep], startPos='Left')

pulse_exp=Jo.configureAcqTrigger(pulse_exp, v[d0], v[pg], displacement=0, increment=0, timebase='Single Point')
pulse_exp=Jo.configurePattern2(pulse_exp,  Xepr, '+x', v[pulsepattern])
pulse_exp=Jo.configurePattern2(pulse_exp,  Xepr, 'U1', v[pulsepattern])
pulse_exp=Jo.configurePattern2(pulse_exp, Xepr, 'U2', v[EVENT])

pulse_exp=Jo.configureAcqFromTables(pulse_exp, dim=(v[sizeX],1), Xaxis='Transient', Yaxis='Magnetic Field', Nscans=Nscans)
config=Jo.configureSpecjet(config, Npts=v[sizeX], Navgs=v[Navgs], timebase=1)
time.sleep(2)
pulse_exp.aqExpRunAndWait()


#%% perform Experiment
pulse_exp.aqExpRunAndWait()
dataset = Xepr.XeprDataset(xeprset = "primary", iscomplex=True)
x=float(dataset.X)
y=float(dataset.O)
B=float(NP.linspace(Bcenter-Bsweep/2, Bcenter+Bsweep/2, sizeY))

Data={'x':x}
Data[y]=y
Data[B]=B


Xepr=Jo.DefineExpConditions(Xepr, samplename, Temp, other=[])


#%% save

savetitle ='2DSPEC_'+v[samplename]+v[pulses]+v[invBW]+'_'+str(v[Bsweep])+'G_HPP'+str(int(v[mwAtten]))+'_'+str(v[Temp])+'K'


savefile = "'" + savedir + savetitle + "'"
Xepr.XeprCmds.vpSave('Current', 'Primary', savetitle, savefile)
Xepr.XeprCmds.vpSaveAsc('Primary', savefile)


sio.savemat(savedir+savetitle,v, Data )

print '___FINISHED experiment__'
#pulse_exp=Jo.EndSession(pulse_exp, config)
