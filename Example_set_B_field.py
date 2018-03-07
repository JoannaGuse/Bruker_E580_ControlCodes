
# this script has not been tested on an EPR spectrometer...

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

#%%___________parameters_______________
Bcenter=3440;
Bsweep=100;

#%%______________connect___________________ 
[Xepr, ID]=Jo.ConnectXEPR(globals())

pulse_exp=Jo.createPulseExp(Xepr, Expname='setup')
time.sleep(1)
pulse_exp=Jo.configureField(pulse_exp, int(Bcenter), int(Bsweep), startPos='Center')   

    