## Python stuff
from array import array
import os
import math as mt
import numpy as np
import re
import argparse
from collections import defaultdict
import pandas as pd
import sys
import subprocess
import matplotlib as plt

pd.set_option('display.max_rows',None)

import Functions as func

#--- Input parameters
tofpetNameId = "Run"
pmtNameId = "BAR"
singleBarGalaxyNameId = "Run"
arrayGalaxyNameId = "Run"
barInArrayGalaxyNameId = "Run"

barInArrayId = "-"

eff_PMT = 0.25
pe_peak = 0.511 #MeV

#--- DEFAULTS
DIRCONFIG = 'configs'
DIRDUMP = 'data'
DIRIN   = 'data'
DIROUT  = 'analyzed_data'
PLOTDIR = 'plot'

#--- Options
parser = argparse.ArgumentParser(usage="python3 Validate.py --user mtdloacsv")
parser.add_argument('--user'    , dest='user'     , default= 'mtdloadb')
parser.add_argument('--dumpDB'  , dest='dumpDB'   , action= 'store_true')
parser.add_argument('--analysis', dest='analysis' , action= 'store_true')
parser.add_argument('--evalSF'  , dest='evalSF'   , action= 'store_true')
parser.add_argument('--applySF' , dest='applySF'  , default= 1 )
parser.add_argument('--skipRuns', dest='skipRuns' , default= '')
args = parser.parse_args()

if args.applySF not in [0,1]:
    print("--applySF admits only values 0 or 1. Default=1")
    exit(0)

# Dump from OMS DB
import dumper as dump
if args.dumpDB==True:
    dump.dumpAll()

import analyzer 
if args.analysis:
    analyzer.analyzeOmsData(evalSF=args.evalSF, applySF=args.applySF, skipRuns=args.skipRuns)

import validator

if not os.path.isdir(PLOTDIR):
    os.system(f"mkdir {PLOTDIR}")
validator.runValidation()
