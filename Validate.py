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

#--- DEFAULTS
from configs.config import *

#--- Options
parser = argparse.ArgumentParser(usage="python3 Validate.py --user mtdloacsv")
parser.add_argument('--user'    , dest='user'       , default='mtdloadb')
parser.add_argument('--dumpDB'  , dest='dumpDB'     , action= 'store_true')
parser.add_argument('--batch'   , dest='batch'      , default=DEFAULTBATCH)
parser.add_argument('--dirDump' , dest='dirDump'    , default=DIRDUMP)
parser.add_argument('--analysis', dest='analysis'   , action= 'store_true')
parser.add_argument('--dirInA'  , dest='dirInA'     , default=DIRINANALYSIS)
parser.add_argument('--dirOutA' , dest='dirOutA'    , default=DIROUTANALYSIS)
parser.add_argument('--evalSF'  , dest='evalSF'     , action= 'store_true')
parser.add_argument('--applySF' , dest='applySF'    , default= 1 )
parser.add_argument('--skip'    , dest='skipRunFile', default= '')
parser.add_argument('--dirInV'  , dest='dirInV'     , default=DIRINVAL)
parser.add_argument('--dirOutV' , dest='dirOutV'    , default=DIROUTVAL)
args = parser.parse_args()

if int(args.applySF) not in [0,1]:
    print("--applySF admits only values 0 or 1. Default=1")
    exit(0)

# Dump from OMS DB
import dumper as dump
if args.dumpDB==True:

    dirout = f'{MAINDIR}/{args.dirDump}/{args.batch}'
    dump.dumpAll(dirout=dirout, batch=args.batch)


import analyzer 
if args.analysis:
    dirInA  = f'{MAINDIR}/{args.dirInA}/{args.batch}'
    dirOutA = f'{MAINDIR}/{args.dirOutA}/{args.batch}'
    analyzer.analyzeOmsData(dirin=dirInA, dirout=dirOutA, evalSF=args.evalSF, applySF=int(args.applySF), skipRunFile=args.skipRunFile)

import validator
dirInV  = f'{MAINDIR}/{args.dirInV}/{args.batch}'
dirOutV = f'{MAINDIR}/{args.dirOutV}/{args.batch}'
reportTitle = f'results_{args.batch}.txt'
validator.runValidation(dirin=dirInV, dirout=dirOutV, outputfilename=reportTitle)
