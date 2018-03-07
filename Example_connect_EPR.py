#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:38:02 2017

@author: xuser
"""

import os,sys; sys.path.insert(0, os.popen("Xepr --apipath").read())  # this locates the XeprAPI module
import XeprAPI              # load the Xepr API module
import numpy as NP
os.chdir('/home/xuser/Dropbox (UNSW ESR Lab)/TEST_EPR_IQ_SETUP/ExpCodes')
import XEPR_moduleJo as Jo
import time


try:
    print(ID)
    print('use existing ID')
    Xepr=XeprAPI.Xepr( 'True',None ,'False', ID)     
    print Xepr
except:
    print ('not ID supplied. make ID')
    pid=XeprAPI.getXeprInstances()
    keys=pid.keys()
    ID=keys[0]
    Xepr=XeprAPI.Xepr( 'True',None ,'False', ID)     
    print Xepr
    