#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 19:04:11 2017

@author: Joanna Guse
"""

# here, I am going to create my own module containing functions to speed up
# configuring the Xepr
import time

def ConnectXEPR(globalvars):
    import os,sys; sys.path.insert(0, os.popen("Xepr --apipath").read())  # this locates the XeprAPI module
    import XeprAPI              # load the Xepr API module

    y=globalvars
    ID=y.get('ID')
    print(ID)
    if ID is None:
        print ('not ID supplied. make ID')
        pid=XeprAPI.getXeprInstances()
        keys=pid.keys()
        ID=keys[0]
        Xepr=XeprAPI.Xepr( 'True',None ,'False', ID)
        print Xepr
    else:
        print('use existing ID')
        Xepr=XeprAPI.Xepr( 'True',None ,'False', ID)
        print Xepr
    return Xepr, ID


 #____________________________________________________________

def createPulseExp(self, Expname):
    import time

    try:
         self.XeprCmds.aqExpEdit(Expname)
         self.XeprCmds.aqExpDel(Expname)
         print 'Deleting old experiment'
         pulse_exp = self.XeprExperiment(Expname,  exptype="Pulse", axs1="Field", ordaxs="Transient recorder")   # create exp
         print 'pulse Experiment created'

    except:
         pulse_exp = self.XeprExperiment(Expname,  exptype="Pulse", axs1="Field", ordaxs="Transient recorder")   # create exp
         print 'pulse Experiment created'

    time.sleep(1)
    self.XeprCmds.aqExpInstall(Expname)  # not sure what this does....
    self.XeprCmds.aqExpActivate(Expname) # send parameters to hardware
    time.sleep(1)
    pulse_exp.aqMbcOperate()     #set bridge to operate;
    config = self.XeprExperiment("AcqHidden") # access hidden experiment to change hidden
    config['ftBridge.BrPlsMode'].value =True #set  bridge to pulse mode
    return pulse_exp


#_________________________________________________

def DefineExpConditions(self, samplename, Temperature, other):
        # the self here refers to Xepr
    import time
    self.aqSetSplName(str(samplename))

    datadate=time.strftime("%d/%m/%Y")
    datatime=time.strftime("%H:%M")
    Notes='This data was taken on ' + datadate + ' at ' + datatime + '. The data was taken at '+str(Temperature) +' K.' +str(other)
    print Notes
    self.aqSetComment(Notes)
    return self
#_______________________________________________________

def configureRecieverUnit(self,config,VideoGain, VideoBW, mwAtten,TL):
         import time
# configure Reciever unit
         print 'Configuring Reciever Unit'
         config['TMLevel'].value=TL
         self["VideoGain"].value = VideoGain
         time.sleep(0.5)
         self["Attenuation"].value = mwAtten
         time.sleep(0.5)
         self['VideoBW'].value=str(VideoBW)   #this requires a string '200' or '20'
         time.sleep(0.5)


         return self

#__________________________________________________________-

def configureTimeout(self, timeout):

    print 'configuring Timeout'
    self["AutoTimeOut"].value = False # Required to adjust the timeout settings
    self["TrRecTrgTimeOut"].value = timeout
    self["TriggerTimeOut"].value =  timeout
    return self

#________________________________________________

def configureSpecjet(self, Npts, Navgs, timebase):
    #Note:self=config, not pulse_exp!!
    print 'Configuring Specjet'
    self["NoOfPoints"].value = Npts
    self["NoOfAverages"].value =Navgs
    self["TimeBase"].value = timebase
    return self

#________________________________________________
def configureField(self, Bcenter, Bsweep, startPos):
    #configure field
    print 'Configuring Field'
    self["CenterField"].value = Bcenter
    self["SweepWidth"].value=Bsweep

    if startPos is 'Left':
     self["AtLeftBorder"].value = True
    elif startPos is 'Right':
     self["AtRightBorder"].value = True
    elif startPos is 'Center':
     self["AtCenter"].value = True
    else:
     self["AtCenter"].value = True

    return self

#_____________________________________________
def configurePattern(self, channel, pulsepattern):
    import time
    pattEdit = self["*ftEpr.PatternEdit"]        # object for pulse table access
    self['*ftEpr.ChannelSlct'].value = channel
    for ii,(pulsepos,pulselen) in enumerate(pulsepattern):
        pattEdit[ii, 0] = int(pulsepos)             # set pulse position (1st row of the table)
        pattEdit[ii, 1] = int(pulselen)             # set corresponding pulse length (2nd row)
    time.sleep(1)
    return self

##_____________________________________________
def configureFullPattern(self, channel, pulsepattern):
    import time
    pattEdit = self["*ftEpr.PatternEdit"]        # object for pulse table access
    self['*ftEpr.ChannelSlct'].value = channel
    if len(pulsepattern)==1:
           pattEdit[0, 0] = int(pulsepattern[0][0])
           pattEdit[0, 1] = int(pulsepattern[0][1])
           pattEdit[0, 2] = int(pulsepattern[0][2])
           pattEdit[0, 3] = int(pulsepattern[0][3])
    else:
     for ii,(pulsepos,pulselen, disp, incr) in enumerate(pulsepattern):
        pattEdit[ii, 0] = int(pulsepos)             # set pulse position (1st row of the table)
        pattEdit[ii, 1] = int(pulselen)             # set corresponding pulse length (2nd row)
        pattEdit[ii, 2] = int(disp)
        pattEdit[ii, 3] = int(incr)

    time.sleep(2)
    return self

##_____________________________________________

def clear_channel(self, Xepr, channel):
    Expname=self.aqGetExpName()
    Xepr.execCmd('aqParSet', Expname, 'ChannelSlct', channel)
    time.sleep(0.5)
    Xepr.execCmd('aqParCut', Expname, 'PatternEdit')
    return self


##_____________________________________________
def configurePattern2(self,Xepr, channel, pulsepattern):
    import time
    pattEdit = self["*ftEpr.PatternEdit"]        # object for pulse table access

    expname=self.aqGetExpName()
    Xepr.execCmd('aqParSet', expname, 'ChannelSlct', channel)
    time.sleep(0.5)
    Xepr.execCmd('aqParCut', expname, 'PatternEdit')
    time.sleep(0.5)


    N=len(pulsepattern)
    nelements=len(pulsepattern[0])

    for ii in range(N):
        for jj in range(nelements):
            pattEdit[ii,jj]=int(pulsepattern[ii][jj])
            time.sleep(0.2)

    return self


#_________________________________
def configureAcqTrigger(self, d0, pg, displacement, increment, timebase):
    import time
    pattEdit = self["*ftEpr.PatternEdit"]        # object for pulse table access
    self['ChannelSlct'].value = 'Acquisition Trigger'
    pattEdit[0, 0] =d0            # set pulse position (1st row of the table)
    pattEdit[0, 1] =pg            # set corresponding pulse length (2nd row)
    pattEdit[0, 2] =displacement    # set pulse position displacement (3rd row)
    pattEdit[0, 3] =increment           # set length increment (4nd row)

    pattEdit[1, 0] =0
    pattEdit[1, 1] =0
    pattEdit[1, 2] =0
    pattEdit[1, 3] =0

    pattEdit[2, 0] =0
    pattEdit[2, 1] =0
    pattEdit[2, 2] =0
    pattEdit[2, 3] =0

    time.sleep(1)
    self["IntgTimeBase"].value =timebase

    return self


#__________________________________________

def configureShot(self, SRT, ShotPerPoint):
    self["ShotRepTime"].value = SRT
    self["ShotsPLoop"].value =ShotPerPoint
    return self

def configureAcqFromTables(self, dim, Xaxis, Yaxis, Nscans):
    import time
    print 'Configuring Acquisition from Tables'

    self["FTAcqModeSlct"].value = 'Run from Tables'

    self["XSpecRes"].value = dim[0]  # sets x-axis size when X-axis quantity is anything except 'Transient'
    self["YSpecRes"].value = dim[1] # sets y-axis size

    self["XAxisQuant"].value = Xaxis # valid inputs: Time, Transient, Magnetic Field, ELDOR and some other randoms
    self["YAxisQuant"].value = Yaxis # valid inputs: Magnetic Field, ELDOR etc.

    self["SweepsPExp"].value=Nscans #number of scans/averages

    time.sleep(2)
    return self


##______________________________________________-
def configureAcqFrompulseSPEL(self, config, deffile, prgfile, plsSPELexp):
    import time
    print 'configuring pulseSPEL experiment'

    config["NoOfPoints"].value = self["XSpecRes"].value
    time.sleep(1)
    prgtext=open(prgfile).read()
    deftext=open(deffile).read()

    self["FTAcqModeSlct"].value = 'Run from PulseSPEL'
    self["PlsSPELGlbTxt"].value = deftext
    self["PlsSPELPrgTxt"].value = prgtext
    self.aqExpPause()
    self.aqExpStop()
    time.sleep(5)
    self["PlsSPELEXPSlct"].value = plsSPELexp
    time.sleep(2)
    return self


#___________________________________________

def configureELDOR(self, ELDORatten, ELDORfreq):
    print 'configuring ELDOR'

    self['ELDORAtt'].value=ELDORatten
    self['FrequencyA'].value=float(ELDORfreq)

    return self

#___________________________________________

def configureELDORSweep(self, ELDORatten, Startfreq, SweepWidth):
    print 'configuring ELDOR'

    self['ELDORAtt'].value=ELDORatten
    self['ELDORFreqStart'].value=Startfreq
    self['ELDORFreqWidth'].value=SweepWidth
    return self


#____________________________________________________-
def LoopOverELDORAtten(self,Xepr,atten):
    import time
    import pylab
    Xepr.XeprCmds.vpCurrent(-1, "Secondary", 0)
    NUMBER_OF_RUNS=len(atten)

    #__________pre-initialize 2D array__________
    dset2D = Xepr.XeprDataset(size=(int(self["XSpecRes"].value), NUMBER_OF_RUNS), iscomplex=True)
    dset2D.Y = range(NUMBER_OF_RUNS)    # and use the run number indices as the 2nd abscissa
    print 'Starting acquisition loop over ELDOR Attenuation'
    for run_no in range(NUMBER_OF_RUNS):
        print "Run %u in progress..." % run_no
        print "ELDORAtten " +str(atten[run_no])
        self["ELDORAtt"].value = atten[run_no]
        time.sleep(0.5)
        self.aqExpRunAndWait()
        time.sleep(1)
        dset1D = Xepr.XeprDataset(xeprset="Primary")
        time.sleep(1)
        dset2D.X = dset1D.X         # copy the 1D abscissa into the 2D dataset
        dset2D.O[run_no][:] = dset1D.O[:]    # insemydict=rt the 1D ordinate data into the 2D dataset
        pylab.plot(dset2D.X , dset2D.O[run_no][:] )      # show only the real part (for complex data)
        time.sleep(0.5)
        dset2D.update(refresh=True, xeprset="Secondary")     # (and refresh the GUI)
        time.sleep(0.5)
        Xepr.XeprCmds.vpFulsc('Secondary') #full scale

    pylab.show()
    # transfer the 2D dataset to Xepr's secondary dataset
    dset2D.update(refresh=True, xeprset="Secondary")     # (and refresh the GUI)
    dset2D.update(refresh=True, xeprset="Primary")     # move intor primary port
    time.sleep(0.5)
    return self, dset2D



#____________________________________________________-
def LoopOverVarXAtten(self,config, Xepr,atten):
    import time
    import pylab
    Xepr.XeprCmds.vpCurrent(-1, "Secondary", 0)
    NUMBER_OF_RUNS=len(atten)

    #__________pre-initialize 2D array__________
    dset2D = Xepr.XeprDataset(size=(int(self["XSpecRes"].value), NUMBER_OF_RUNS), iscomplex=True)
    dset2D.Y = range(NUMBER_OF_RUNS)    # and use the run number indices as the 2nd abscissa
    print 'Starting acquisition loop over ELDOR Attenuation'
    for run_no in range(NUMBER_OF_RUNS):
        print "Run %u in progress..." % run_no
        print "<x> Atten " +str(atten[run_no])
        config['BrXAmp'].value= atten[run_no]
        time.sleep(0.5)
        self.aqExpRunAndWait()
        time.sleep(1)
        dset1D = Xepr.XeprDataset(xeprset="Primary")
        time.sleep(1)
        dset2D.X = dset1D.X         # copy the 1D abscissa into the 2D dataset
        dset2D.O[run_no][:] = dset1D.O[:]    # insemydict=rt the 1D ordinate data into the 2D dataset
        pylab.plot(dset2D.X , dset2D.O[run_no][:] )      # show only the real part (for complex data)
        time.sleep(0.5)
        dset2D.update(refresh=True, xeprset="Secondary")     # (and refresh the GUI)
        time.sleep(0.5)
        Xepr.XeprCmds.vpFulsc('Secondary') #full scale

    pylab.show()
    # transfer the 2D dataset to Xepr's secondary dataset
    dset2D.update(refresh=True, xeprset="Secondary")     # (and refresh the GUI)
    dset2D.update(refresh=True, xeprset="Primary")     # move intor primary port
    time.sleep(0.5)
    return self, dset2D



#____________________________________________________-
def LoopOverHPPAtten(self,Xepr,atten):
    import time
    import pylab
    Xepr.XeprCmds.vpCurrent(-1, "Secondary", 0)
    NUMBER_OF_RUNS=len(atten)

    #__________pre-initialize 2D array__________
    dset2D = Xepr.XeprDataset(size=(int(self["XSpecRes"].value), NUMBER_OF_RUNS), iscomplex=True)
    dset2D.Y = range(NUMBER_OF_RUNS)    # and use the run number indices as the 2nd abscissa
    print 'Starting acquisition loop over HPP Attenuation'
    for run_no in range(NUMBER_OF_RUNS):
        print "Run %u in progress..." % run_no
        print "Atten " +str(atten[run_no])
        self["Attenuation"].value = atten[run_no]
        time.sleep(0.5)
        self.aqExpRunAndWait()
        time.sleep(1)
        dset1D = Xepr.XeprDataset(xeprset="Primary")
        time.sleep(1)
        dset2D.X = dset1D.X         # copy the 1D abscissa into the 2D dataset
        dset2D.O[run_no][:] = dset1D.O[:]    # insemydict=rt the 1D ordinate data into the 2D dataset
        pylab.plot(dset2D.X , dset2D.O[run_no][:] )      # show only the real part (for complex data)
        time.sleep(0.5)
        dset2D.update(refresh=True, xeprset="Secondary")     # (and refresh the GUI)
        time.sleep(1)
        Xepr.XeprCmds.vpFulsc('Secondary') #full scale

    pylab.show()
    # transfer the 2D dataset to Xepr's secondary dataset
     # move intor primary port
    time.sleep(0.5)
    return self, dset2D

#___________________________________________
def Acquire_PhaseCycled_Data2(self, Xepr, phase_seq, sum_seq, pattern):
    import numpy as NP
    import time
    Nphases=len(phase_seq)
    Npulses=len(phase_seq[0])
    data=[]
    for jj in range(Nphases):
        print ('phase cycle ' +str(jj+1) +' of ' +str(Nphases))
        clear_channel(self, Xepr, '+x')
        clear_channel(self, Xepr, '-x')
        clear_channel(self, Xepr, '+y')
        clear_channel(self, Xepr, '-y')
        time.sleep(1)
        temp1=[]
        temp2=[]
        temp3=[]
        temp4=[]
        for ii in range(Npulses):
            if phase_seq[jj][ii]=='+x':
              temp1.append(pattern[ii])
              time.sleep(0.2)
            elif phase_seq[jj][ii] =='-x':
              temp2.append(pattern[ii])
              time.sleep(0.2)
            elif phase_seq[jj][ii] == '+y':
              temp3.append(pattern[ii])
              time.sleep(0.2)
            elif phase_seq[jj][ii] == '-y':
              temp4.append(pattern[ii])
              time.sleep(0.2)
        try:
            configurePattern2(self, Xepr,'+x', temp1)
        except:
            pass

        try:
            configurePattern2(self,Xepr,'-x', temp2)
        except:
            pass
        try:
            configurePattern2(self,Xepr,'+y', temp3)
        except:
            pass

        try:
            configurePattern2(self, Xepr,'-y', temp4)
        except:
            pass
        time.sleep(1)
        #get data
        self.aqExpRunAndWait()
        dataset = Xepr.XeprDataset(xeprset = "primary", iscomplex=True)
        x=dataset.X
        y=dataset.O
        data.append(y)

        if jj is 0:
            Xepr.XeprCmds.vpCurrent(-1, "Secondary", 0)
            dset2 = Xepr.XeprDataset(size=(int(self["XSpecRes"].value),int(self["YSpecRes"].value)), iscomplex=True)
            dset2.X=x
            dtotR=sum_seq[jj]*NP.real(y)
            dtotI=sum_seq[jj]*NP.imag(y)
        else:
            dtotR=dtotR+sum_seq[jj]*NP.real(y)
            dtotI=dtotI+sum_seq[jj]*NP.imag(y)
            dset2.O.real=dtotR
            dset2.O.imag=dtotI
            dset2.update(refresh=True, xeprset="Secondary")
            time.sleep(1)
            Xepr.XeprCmds.vpFulsc('Secondary') #full scale

    dset2.update(refresh=True, xeprset="Primary")
    time.sleep(1)
    Xepr.XeprCmds.vpFulsc('Primary') #full scale
    Xepr.XeprCmds.vpCurrent(-1, "Secondary", 0)


    Data1=NP.asarray(data)
    print('finished data collection')

    return self,x,dtotR, dtotI, Data1


#________________________________________________________-

def Acquire_PhaseCycled_Data(self, Xepr, phase_seq, pattern):
    import numpy as NP
    import time
    Nphases=len(phase_seq)
    Npulses=len(phase_seq[0])
    data=[]
    for jj in range(Nphases):
        print ('phase cycle ' +str(jj+1) +' of ' +str(Nphases))
        clear_channel(self, Xepr, '+x')
        clear_channel(self, Xepr, '-x')
        clear_channel(self, Xepr, '+y')
        clear_channel(self, Xepr, '-y')
        time.sleep(1)
        temp1=[]
        temp2=[]
        temp3=[]
        temp4=[]
        for ii in range(Npulses):
            if phase_seq[jj][ii]=='+x':
              temp1.append(pattern[ii])
              time.sleep(0.2)
            elif phase_seq[jj][ii] =='-x':
              temp2.append(pattern[ii])
              time.sleep(0.2)
            elif phase_seq[jj][ii] == '+y':
              temp3.append(pattern[ii])
              time.sleep(0.2)
            elif phase_seq[jj][ii] == '-y':
              temp4.append(pattern[ii])
              time.sleep(0.2)
        try:
            configurePattern2(self, Xepr,'+x', temp1)
        except:
            pass

        try:
            configurePattern2(self,Xepr,'-x', temp2)
        except:
            pass
        try:
            configurePattern2(self,Xepr,'+y', temp3)
        except:
            pass

        try:
            configurePattern2(self, Xepr,'-y', temp4)
        except:
            pass
        time.sleep(1)
        #get data
        self.aqExpRunAndWait()
        dataset = Xepr.XeprDataset(xeprset = "primary", iscomplex=True)
        x=dataset.X
        y=dataset.O
        data.append(y)

        Xepr.execCmd('vpCurrent', 1, 'Secondary', 1)


    Data1=NP.asarray(data)

    return self,x, Data1

#_______________________________________________
def EndSession(self, config):

    print 'Ramping down magnet and setting bridge to stand-by'
    self["CenterField"].value = 0
    self["Attenuation"].value = 60
    config["OpMode"].value = 'Stand By' # Put cw-bridge in stand-by mode
    return self


#___________________________________________________________

def savetoMATLAB(savename, data):
    'data should be globals()'
    import sys
    import scipy.io as sio
    from spyder.config.base import get_conf_path, get_supported_types
    from spyder.widgets.variableexplorer import utils as U

    try:
         del(mydict)
    except:
         pass


    mydict=U.globalsfilter(data, check_all=True,
                filters=tuple(get_supported_types()['picklable']),
                exclude_private=True,
                exclude_capitalized=False,
                exclude_uppercase=True,
                exclude_unsupported=True,
                excluded_names={'os', 'sys', 'In', 'Out'})

    sio.savemat(savename, mydict)
    return mydict


#___________________________________________________________
def savetoMATLAB2(savename, mydict):
    import scipy.io as sio
    sio.savemat(savename, mydict)
    return mydict
