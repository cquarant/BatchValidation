## ROOT stuff
import ROOT as R
R.gROOT.SetBatch(1)
## set the tdr style
import tdrstyle
tdrstyle.setTDRStyle()

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
file_SINGLEBARS = "data_SINGLEBARS.csv"
file_ARRAYS = "data_ARRAYS.csv"
file_TOFPET = "data_TOFPET.csv"
file_PMT = "data_PMT.csv"
file_GALAXY = "data_GALAXY.csv"

tofpetNameId = "Run"
pmtNameId = "BAR"
singleBarGalaxyNameId = "Run"
arrayGalaxyNameId = "Run"
barInArrayGalaxyNameId = "Run"

singleBarId = "FK00002"
arrayId = "FK00001"
barInArrayId = "-"

eff_PMT = 0.25
pe_peak = 0.511 #MeV

#--- Output dir
plotdir = "plot"
os.system(f"mkdir {plotdir}")

#--- Options
parser = argparse.ArgumentParser(usage="python3 Validate.py --user mtdloacsv")
parser.add_argument('--user',dest='user',required=True)
parser.add_argument('--noDumpDB',dest='noDumpDB',action='store_true')
args = parser.parse_args()

#--- Dump from database
if(args.noDumpDB==False):
    print ("Please type lxplus.cern.ch password for user "+args.user)
    os.system("ssh -f -N -L 8113:dbloader-mtd.cern.ch:8113 "+args.user+"@lxplus.cern.ch")
    print ("Tunnel for dbloader-mtd.cern.ch OPEN")

    #PID = subprocess.check_output("pgrep -u "+args.user+" -n 'ssh*'", shell=True).decode()
    PID = subprocess.check_output("pgrep -f 'ssh.*8113'", shell=True).decode()

    os.system("rm -f "+file_TOFPET)
    os.system("rm -f "+file_PMT)
    os.system("rm -f "+file_GALAXY)

    # Parts

    QUERYSINGLEBARS = (
        "select p.BARCODE,p.KIND_OF_PART "
        "from mtd_cmsr.parts p "
        "where p.LOCATION_ID = 3000 and p.KIND_OF_PART like 'singleCrystal%'"
    )
    print ("\nQUERYSINGLEBARS: " + QUERYSINGLEBARS)

    QUERYARRAYS = (
        "select p.BARCODE,p.KIND_OF_PART "
        "from mtd_cmsr.parts p "
        "where p.LOCATION_ID = 3000 and p.KIND_OF_PART like 'LYSOMatrix%'"
    )
    print ("\nQUERYARRAYS: " + QUERYARRAYS)

    print ("")

    os.system("python3 rhapi.py --all -f csv --url=http://localhost:8113 \""+QUERYSINGLEBARS+"\" > "+file_SINGLEBARS)
    os.system("python3 rhapi.py --all -f csv --url=http://localhost:8113 \""+QUERYARRAYS+"\" > "+file_ARRAYS)
    
    # Measurements
    
    QUERYTOFPET = (
    "select c1.PART_BARCODE, r.NAME, r.BEGIN_DATE, c1.CTR, c1.CTR_NORM, "
    "c1.TEMPERATURE, c1.XTLEFT, c1.XTRIGHT, c1.LY, c1.LY_NORM, c1.SIGMA_T, c1.SIGMA_T_NORM "
    "from mtd_cmsr.parts p "
    "left join mtd_cmsr.c1400 c1 on c1.PART_BARCODE = p.BARCODE "
    "left join mtd_cmsr.datasets ds on (ds.ID = c1.CONDITION_DATA_SET_ID) "
    "left join mtd_cmsr.runs r on (r.ID = ds.RUN_ID) "
    "where p.LOCATION_ID = 3000"
    )
    print ("\nQUERYTOFPET: " + QUERYTOFPET)
    
    QUERYPMT = (
    "select c2.PART_BARCODE, r.NAME, r.BEGIN_DATE, c2.B_RMS, "
    "c2.B_3S_ASYM, c2.B_2S_ASYM, c2.LY_ABS, c2.LY_NORM as LY_NORMAL, c2.DECAY_TIME "
    "from mtd_cmsr.parts p "
    "left join mtd_cmsr.c1420 c2 on c2.PART_BARCODE = p.BARCODE "
    "left join mtd_cmsr.datasets ds on (ds.ID = c2.CONDITION_DATA_SET_ID) "
    "left join mtd_cmsr.runs r on (r.ID = ds.RUN_ID) "
    "where p.LOCATION_ID = 3000"
    )
    print ("\nQUERYPMT: " + QUERYPMT)

    QUERYGALAXY = (
    "select c3.PART_BARCODE, r.NAME, r.BEGIN_DATE, c3.BARLENGTH, "
    "c3.BARLENGTH_STD, c3.LMAXVAR_LS, c3.LMAXVAR_LN, c3.L_MAX, c3.L_MEAN, c3.L_MEAN_STD, c3.WMAXVAR_LO, "
    "c3.WMAXVAR_LE, c3.W_MAX, c3.W_MEAN, c3.W_MEAN_STD, c3.TMAXVAR_FS, c3.TMAXVAR_FS_STD, c3.T_MAX, c3.T_MEAN, "
    "c3.T_MEAN_STD, c3.L_MEAN_MITU, c3.L_STD_MITU, c3.W_MEAN_MITU, c3.W_STD_MITU, c3.T_MEAN_MITU, "
    "c3.T_STD_MITU, c3.LMAXVAR_LS_STD, c3.LMAXVAR_LN_STD, c3.WMAXVAR_LO_STD, c3.WMAXVAR_LE_STD "
    "from mtd_cmsr.parts p "
    "left join mtd_cmsr.c3400 c3 on c3.PART_BARCODE = p.BARCODE "
    "left join mtd_cmsr.datasets ds on (ds.ID = c3.CONDITION_DATA_SET_ID) "
    "left join mtd_cmsr.runs r on (r.ID = ds.RUN_ID) "
    "where p.LOCATION_ID = 3000"
    )
    print ("\nQUERYGALAXY: " + QUERYGALAXY)

    print ("")

    os.system("python3 rhapi.py --all -f csv --url=http://localhost:8113 \""+QUERYTOFPET+"\" > "+file_TOFPET)
    os.system("python3 rhapi.py --all -f csv --url=http://localhost:8113 \""+QUERYPMT+"\" > "+file_PMT)
    os.system("python3 rhapi.py --all -f csv --url=http://localhost:8113 \""+QUERYGALAXY+"\" > "+file_GALAXY)

    os.system("kill -9 "+PID)
    print ("Tunnel for csvloader-mtd.cern.ch CLOSED")

#--- Create basic dataframes

# Parts
    
#---------
#-- SINGLEBARS
#---------

df_SINGLEBARS = pd.read_csv(file_SINGLEBARS)
df_SINGLEBARS = df_SINGLEBARS.sort_values(by=['BARCODE'])
df_SINGLEBARS.dropna(
    axis=0,
    how='all',
    subset=None,
    inplace=True
)
#print ( len(df_SINGLEBARS.index) )
#print ( df_SINGLEBARS )
    
#---------
#-- ARRAYS
#---------

df_ARRAYS = pd.read_csv(file_ARRAYS)
df_ARRAYS = df_ARRAYS.sort_values(by=['BARCODE'])
df_ARRAYS.dropna(
    axis=0,
    how='all',
    subset=None,
    inplace=True
)
#print ( len(df_ARRAYS.index) )
#print ( df_ARRAYS )


# Measurements
    
#---------
#-- TOFPET
#---------
df_TOFPET = pd.read_csv(file_TOFPET)
df_TOFPET = df_TOFPET.sort_values(by=['PART_BARCODE'])
df_TOFPET.dropna(
    axis=0,
    how='all',
    subset=None,
    inplace=True
)

#- TOFPET cleaning
df_TOFPET = df_TOFPET[df_TOFPET['NAME'].str.match(tofpetNameId)]
#print ( len(df_TOFPET.index) )
#print ( df_TOFPET )

#---------
#-- PMT
#---------
df_PMT = pd.read_csv(file_PMT)
df_PMT = df_PMT.sort_values(by=['PART_BARCODE'])
df_PMT.dropna(
    axis=0,
    how='all',
    subset=None,
    inplace=True
)
#- PMT cleaning
df_PMT = df_PMT[df_PMT['NAME'].str.match(pmtNameId)]
#print ( len(df_PMT.index) )
#print ( df_PMT )

#---------
#-- GALAXY
#---------
df_GALAXY = pd.read_csv(file_GALAXY)
df_GALAXY = df_GALAXY.sort_values(by=['PART_BARCODE'])
df_GALAXY.dropna(
    axis=0,
    how='all',
    subset=None,
    inplace=True
)

#--- Print number of parts and measurements for each dataframe

num_singlebars = len(df_SINGLEBARS.index)
num_arrays = len(df_ARRAYS.index)

num_exp_tofpet = num_arrays*16
num_exp_pmt = num_singlebars
num_exp_galaxy_barsInArray = num_arrays*16

outputfile = open("results.txt", "w")
c = R.TCanvas()

latex = R.TLatex()
latex.SetTextSize(0.025)
latex.SetTextAlign(13) 

# #-------------------------------------------------------------
#     #    #     #    #    #       #     #  #####  ###  #####  
#    # #   ##    #   # #   #        #   #  #     #  #  #     # 
#   #   #  # #   #  #   #  #         # #   #        #  #       
#  #     # #  #  # #     # #          #     #####   #   #####  
#  ####### #   # # ####### #          #          #  #        # 
#  #     # #    ## #     # #          #    #     #  #  #     # 
#  #     # #     # #     # #######    #     #####  ###  #####  
# #-------------------------------------------------------------

#---------------------------------------------------------
#-----------  Dataframes for single bars validation
#---------------------------------------------------------

# GALAXY for single bars
df_GALAXY_SINGLEBAR = pd.merge( df_SINGLEBARS, df_GALAXY, how='inner', left_on='BARCODE', right_on='PART_BARCODE')
df_GALAXY_SINGLEBAR = df_GALAXY_SINGLEBAR[df_GALAXY_SINGLEBAR['NAME'].str.match(singleBarGalaxyNameId)] # cleaning
 
# PMT for single bars
df_PMT = pd.merge( df_SINGLEBARS, df_PMT, how='inner', left_on='BARCODE', right_on='PART_BARCODE')
df_PMT['LO'] = [ly/(eff_PMT*pe_peak)  for ly in df_PMT['LY_ABS']] ## photons / MeV
df_PMT['LOoverDT'] = df_PMT['LO']/df_PMT['DECAY_TIME'] 
df_PMT['LO_RSTD']  = df_PMT['LO'].std()/df_PMT['LO'].mean()*100
df_PMT['DT_RSTD']  = df_PMT['DECAY_TIME'].std()/df_PMT['DECAY_TIME'].mean()*100
df_PMT['LOoverDT_RSTD']  = df_PMT['LOoverDT'].std()/df_PMT['LOoverDT'].mean()*100

#---------------------------------------------------------
#-----------  Dataframes for array validation
#---------------------------------------------------------

# Dataframe with array types + galaxy measurements for whole array
df_GALAXY_ARRAY = pd.merge( df_ARRAYS, df_GALAXY, how='inner', left_on='BARCODE', right_on='PART_BARCODE')
df_GALAXY_ARRAY['LMAXVAR'] = df_GALAXY_ARRAY[['LMAXVAR_LS','LMAXVAR_LN']].max(axis=1)

# Dataframe with galaxy measurements for bars in arrays
df_GALAXY_BARINARRAY = df_GALAXY[df_GALAXY['PART_BARCODE'].str.contains(barInArrayId)]
df_GALAXY_BARINARRAY['PARENT_ARRAY'] = list(list(zip(*df_GALAXY_BARINARRAY['PART_BARCODE'].str.split("-")))[0])
df_GALAXY_BARINARRAY = df_GALAXY_BARINARRAY.merge( df_ARRAYS, how='left', left_on='PARENT_ARRAY', right_on='BARCODE')

# Dataframe with optical properties of array (average and std. dev. for bars 1-14 for each array)
df_TOFPET_ARRAY = df_TOFPET.copy()
df_TOFPET_ARRAY['PARENT_ARRAY'] = list(list(zip(*df_TOFPET_ARRAY['PART_BARCODE'].str.split("-")))[0])
df_TOFPET_ARRAY = df_TOFPET_ARRAY.loc[ ~df_TOFPET_ARRAY['PART_BARCODE'].str.contains('-15') & ~df_TOFPET_ARRAY['PART_BARCODE'].str.contains('-0')] # remove first and last bar of each array
df_TOFPET_ARRAY['XT'] = (df_TOFPET_ARRAY['XTLEFT'] + df_TOFPET_ARRAY['XTRIGHT'])/2.

df_TOFPET_ARRAY_RUN  = df_TOFPET_ARRAY[['PARENT_ARRAY','NAME']].drop_duplicates()
df_TOFPET_ARRAY_MEAN = df_TOFPET_ARRAY.groupby(['PARENT_ARRAY'], as_index=False).mean(numeric_only=True)
df_TOFPET_ARRAY_MEAN = df_TOFPET_ARRAY_MEAN.add_suffix('_MEAN')
df_TOFPET_ARRAY_RSTD = df_TOFPET_ARRAY.groupby(['PARENT_ARRAY'], as_index=False).apply(lambda x: np.std(x) / np.mean(x))
df_TOFPET_ARRAY_RSTD = df_TOFPET_ARRAY_RSTD.add_suffix('_RSTD')

df_TOFPET_ARRAY = df_TOFPET_ARRAY_MEAN.merge( df_TOFPET_ARRAY_RSTD, how='inner', left_on='PARENT_ARRAY_MEAN', right_on='PARENT_ARRAY_RSTD')
df_TOFPET_ARRAY = df_TOFPET_ARRAY.merge( df_TOFPET_ARRAY_RUN, left_on='PARENT_ARRAY_MEAN', right_on='PARENT_ARRAY')
df_TOFPET_ARRAY = df_TOFPET_ARRAY.merge( df_ARRAYS, how='left', left_on='PARENT_ARRAY_MEAN', right_on='BARCODE')
df_TOFPET_ARRAY['LY_MEAN'] = df_TOFPET_ARRAY['LY_MEAN'].apply(lambda x: x*3950/48.8)
df_TOFPET_ARRAY[['LY_RSTD','SIGMA_T_RSTD','XT_RSTD']] = df_TOFPET_ARRAY[['LY_RSTD','SIGMA_T_RSTD','XT_RSTD']].apply(lambda x: x*100)

#Dataframe for Optical measurements of Bar in Arrays
df_TOFPET_BARINARRAY = df_TOFPET.copy()
df_TOFPET_BARINARRAY['PARENT_ARRAY'] = list(list(zip(*df_TOFPET_BARINARRAY['PART_BARCODE'].str.split("-")))[0])
df_TOFPET_BARINARRAY = df_TOFPET_BARINARRAY.merge( df_ARRAYS, how='left', left_on='PARENT_ARRAY', right_on='BARCODE')
df_TOFPET_BARINARRAY = df_TOFPET_BARINARRAY.loc[ ~df_TOFPET_BARINARRAY['PART_BARCODE'].str.contains('-15') & ~df_TOFPET_BARINARRAY['PART_BARCODE'].str.contains('-0')]
df_TOFPET_BARINARRAY['XT'] = (df_TOFPET_BARINARRAY['XTLEFT'] + df_TOFPET_BARINARRAY['XTRIGHT'])/2.

#---------------------------------------------------------
#-------- Configuration of Validation steps
#---------------------------------------------------------

dictConfig = {
    "GALAXY_SINGLEBAR": {
        'title'  : 'Validation of SINGLE XTAL dimensions',
        'tag'    : ['PREIRR'],
        'meas'   : ['L_MEAN', 'W_MEAN','T_MEAN'], #RSTD = relative standard deviation 
        'df_meas': df_GALAXY_SINGLEBAR,
        'summary_df_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
    },
    "PMT_SINGLEBAR": {
        'title'  : 'Validation of SINGLE XTAL optical properties',
        'tag'    : ['PREIRR'],
        'meas'   : ['LO','DT','LOoverDT','LO_RSTD','DT_RSTD','LOoverDT_RSTD'], #RSTD = relative standard deviation 
        'df_meas': df_PMT,
        'summary_df_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
    },
    "GALAXY_ARRAY": {
        'title'  : 'Validation of ARRAY dimensions',
        'tag'    : ['PREIRR'],
        'meas'   : ["L_MAX","LMAXVAR","W_MAX","T_MAX"], 
        'df_meas': df_GALAXY_ARRAY,
        'summary_df_col': ['BARCODE','KIND_OF_PART','NAME'],
    },
    "TOFPET_ARRAY" : {
        'title'  : 'Validation of ARRAY optical properties (dry coupling)',
        'tag' : ['PREIRR','GREASE'],
        'meas': ['LY_MEAN','LY_RSTD','SIGMA_T_MEAN','SIGMA_T_RSTD','XT_MEAN','XT_RSTD'],
        'df_meas': df_TOFPET_ARRAY,
        'summary_df_col' : ['PARENT_ARRAY','KIND_OF_PART','NAME']
    },
    "GALAXY_BARINARRAY" : {
        'title'  : 'Validation of XTALS IN ARRAY dimensions',
        'tag'    : ['PREIRR'],
        'meas'   : ["BARLENGTH"],
        'df_meas': df_GALAXY_BARINARRAY,
        'summary_df_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
    },    
    "TOFPET_BARINARRAY" : {
        'title'  : 'Validation of XTALS IN ARRAY optical properties (dry coupling)',
        'tag' : ['PREIRR','GREASE'],
        'meas': ['SIGMA_T','XT'],
        'df_meas': df_TOFPET_BARINARRAY,
        'summary_df_col' : ['PART_BARCODE','KIND_OF_PART','NAME']
    },
}

# Measurements to be checked
dictMeas = {
    # Single xtal dimensions 
    "L_MEAN"   : {'db_name': 'L_MEAN'   , 'xmin':54.85, 'xmax':55.15, 'thr':[[54.97,55.03]], 'label':'Single Xtal Length'       , 'unit':'[mm]'   , 'DrawHisto' :True, 'type_group':['all']},
    "W_MEAN"   : {'db_name': 'W_MEAN'   , 'xmin': 3.00, 'xmax': 3.24, 'thr':[[ 3.09, 3.15]], 'label':'Single Xtal Width'        , 'unit':'[mm]'   , 'DrawHisto' :True, 'type_group':['all']},
    "T_MEAN"   : {'db_name': 'T_MEAN'   , 'xmin': 2.85, 'xmax': 3.15, 'thr':[[ 2.97, 3.03]], 'label':'Single Xtal Thickness'    , 'unit':'[mm]'   , 'DrawHisto' :True, 'type_group':['all']},
   
    # Single xtal optical properties
    "LO"       : {'db_name': 'LO'       , 'xmin':3750 , 'xmax':7000 , 'thr':[[4000,999999]], 'label':'Single Xtal Light Output', 'unit':'[ph/MeV]'   , 'DrawHisto' :True, 'type_group':['all']},
    "DT"       : {'db_name': 'DECAY_TIME', 'xmin':30  , 'xmax':50   , 'thr':[[-1, 45]     ], 'label':'Decay Time'              , 'unit':'[ns]'       , 'DrawHisto' :True, 'type_group':['all']},
    "LOoverDT" : {'db_name': 'LOoverDT' , 'xmin':80   , 'xmax':160  , 'thr':[[105,9999999]], 'label':'LO/DT'                   , 'unit':'[ph/MeV/ns]', 'DrawHisto' :True, 'type_group':['all']},
    "LO_RSTD"  : {'db_name': 'LO_RSTD'  , 'xmin':0.00 , 'xmax':15.00, 'thr':[[-1, 10]     ], 'label':'LO relative std. dev.'   , 'unit':'(%)'        , 'DrawHisto' :False, 'type_group':['all']},
    "DT_RSTD"  : {'db_name': 'DT_RSTD'  , 'xmin':0.00 , 'xmax':15.00, 'thr':[[-1,  5]     ], 'label':'DT relative std. dev.'   , 'unit':'(%)'        , 'DrawHisto' :False, 'type_group':['all']},
    "LOoverDT_RSTD": {'db_name': 'LOoverDT_RSTD', 'xmin':0, 'xmax':15, 'thr':[[-1, 5]     ], 'label':'LO/DT relative std. dev.', 'unit':'(%)'        , 'DrawHisto' :False, 'type_group':['all']},

    # Array Dimensions
    "L_MAX"  : {'db_name': 'L_MAX'    , 'xmin':54.75, 'xmax':55.25, 'thr':[[54.95,55.05]], 'label':'Array Length'   , 'unit':'[mm]', 'DrawHisto' :True, 'type_group':['all']},
    "LMAXVAR": {'db_name': 'LMAXVAR'  , 'xmin': 0.00, 'xmax': 0.07, 'thr':[[-1.00, 0.05]], 'label':'Array Planarity', 'unit':'[mm]', 'DrawHisto' :True, 'type_group':['all']},
    "W_MAX"  : {'db_name': 'W_MAX'    , 'xmin':50.88, 'xmax':52.08, 'thr':[[51.38,51.58]], 'label':'Array Width'    , 'unit':'[mm]', 'DrawHisto' :True, 'type_group':['all']},
    "T_MAX"  : {'db_name': 'T_MAX'    , 'xmin': 3.91, 'xmax': 4.31, 'thr':[[ 4.01, 4.21],[ 3.26, 3.46],[ 2.66, 2.86]], 'label':'Array Thickness'     , 'unit':'[mm]', 'DrawHisto' :True, 'type_group':['1','2','3'] },
    # Bar in array optical properties
    "BARLENGTH": {'db_name': 'BARLENGTH', 'xmin':54.85, 'xmax':55.15, 'thr':[[54.95,55.05]], 'label':'Length of Xtals in Arrays', 'unit':'[mm]', 'DrawHisto' :True, 'type_group':['all']},

    # Array optical properties
    "LY_MEAN"  : {'db_name': 'LY_MEAN'  , 'xmin':3750 , 'xmax':7000 , 'thr':[[4000,9999999],[4000,9999999],[4000,9999999]], 'label':'Array Light Output' , 'unit':'[ph/MeV]', 'DrawHisto' :True, 'type_group':['1','2','3']},
    "LY_RSTD"  : {'db_name': 'LY_RSTD'  , 'xmin': 0.00, 'xmax':10.00, 'thr':[[ 0.00,  7.00],[ 0.00,  7.00],[ 0.00,  7.00]], 'label':'Light Yield RMS'    , 'unit':'(%)' , 'DrawHisto' :True, 'type_group':['1','2','3']},
    "SIGMA_T_MEAN": {'db_name':'SIGMA_T_MEAN', 'xmin':90, 'xmax':150, 'thr':[[ 0.00,140.00],[ 0.00,140.00],[ 0.00,140.00]], 'label':'Time resolution'    , 'unit':'[ps]', 'DrawHisto' :True, 'type_group':['1','2','3']},
    "SIGMA_T_RSTD": {'db_name':'SIGMA_T_RSTD', 'xmin': 0, 'xmax':10., 'thr':[[ 0.00,  6.00],[ 0.00,  6.00],[ 0.00,  6.00]], 'label':'Time resolution RMS', 'unit':'(%)' , 'DrawHisto' :True, 'type_group':['1','2','3']},
    "XT_MEAN"  : {'db_name': 'XT_MEAN'  , 'xmin': 0.00, 'xmax': 0.30, 'thr':[[ 0.00,  0.25],[ 0.00,  0.25],[ 0.00,  0.25]], 'label':'Cross Talk'         , 'unit':''    , 'DrawHisto' :True, 'type_group':['1','2','3']},
    "XT_RSTD"  : {'db_name': 'XT_RSTD'  , 'xmin': 0.00, 'xmax':50.00, 'thr':[[ 0.00, 40.00],[ 0.00, 40.00],[ 0.00, 40.00]], 'label':'Cross Talk RMS'     , 'unit':'(%)' , 'DrawHisto' :True, 'type_group':['1','2','3']},
    # Bar in array
    "SIGMA_T"  : {'db_name': 'SIGMA_T'  , 'xmin':90   , 'xmax':150  , 'thr':[[ 0.00,140.00],[ 0.00,140.00],[ 0.00,140.00]], 'label':'Time resolution', 'unit':'[ps]', 'DrawHisto' :True, 'type_group':['1','2','3']},
    "XT"       : {'db_name': 'XT'       , 'xmin': 0.00, 'xmax': 0.30, 'thr':[[ 0.00,  0.25],[ 0.00,  0.25],[ 0.00,  0.25]], 'label':'Cross Talk'     , 'unit':''    , 'DrawHisto' :True, 'type_group':['1','2','3']},
}

histos = {}

for config in dictConfig:

    for tag in dictConfig[config]['tag']:
        meas_list = dictConfig[config]['meas']
        df_meas   = dictConfig[config]['df_meas'].copy()
    
        # Filter by run tag (row-wise) and for relevant measurements (column-wise)
        meas_db_names = []
        for m in meas_list:
            meas_db_names.append(dictMeas[m]['db_name'])

        df_meas = df_meas[ dictConfig[config]['summary_df_col'] + list(set(meas_db_names))]
        df_meas = df_meas[ df_meas['NAME'].str.contains(tag)==True ]

        summary_df = df_meas[ dictConfig[config]['summary_df_col'] ]
        summary_df = summary_df[ summary_df['NAME'].str.contains(tag)==True ]
    
        if len(summary_df)==0:
            continue
    
        outputfile.write("\n")
        outputfile.write("##############################################################"+"\n")
        outputfile.write( str(dictConfig[config]['title']).ljust(60)+"\n")
        outputfile.write("##############################################################"+"\n")    
        outputfile.write("\n")
        outputfile.write("Number of parts available: "+str( len(summary_df) )+"\n" )
        outputfile.write("Number of parts measured : "+str( len(summary_df.dropna()) )+"\n" )
        outputfile.write("\n")

        for m in meas_list:

            meas_config = dictMeas[m]
            m_db_name = meas_config['db_name']
            xlab = meas_config['label']

            summary_df[f'pass_{m}'] = True
            for type_i,type in enumerate(dictMeas[m]['type_group']):
    
          
                # Check if part pass MTD requirements for measurement m
                # (if type_sel != None then apply only to parts of selected type)
                thr_min = meas_config['thr'][type_i][0]
                thr_max = meas_config['thr'][type_i][1]

                if type == 'all':                
                    df_meas_filtered = df_meas
                    summary_df[f'pass_{m}_{type}'] = np.where( df_meas[m_db_name].between(thr_min,thr_max), True, False )
                    outputfile.write(f"{xlab.ljust(25)}: min="+str(df_meas[m_db_name].min().round(3)).ljust(6)+" max="+str( df_meas[m_db_name].max().round(3)).ljust(6)
                                    +" ==> Pass : "+str( round(100*len(summary_df[summary_df[f'pass_{m}_{type}']==True]) / len(summary_df), 1) )+" %" )
                else:
                    df_meas_filtered = df_meas[ df_meas['KIND_OF_PART'].str.contains(type) ]
                    summary_df[f'pass_{m}_{type}'] = np.where( ~df_meas['KIND_OF_PART'].str.contains(type) | (df_meas[m_db_name].between(thr_min,thr_max)), True, False )
                    outputfile.write(f"{xlab.ljust(25)}: min="+str(df_meas[ df_meas['KIND_OF_PART'].str.contains(type) ][m_db_name].min().round(3)).ljust(6)
                                    +" max="+str( df_meas[ df_meas['KIND_OF_PART'].str.contains(type) ][m_db_name].max().round(3)).ljust(6)
                                    +" ==> Pass : "+str( round(100*len(summary_df[summary_df[f'pass_{m}_{type}']==True]) / len(summary_df), 1) )+" %" )
                outputfile.write("\n")
                
                summary_df[f'pass_{m}'] = summary_df[f'pass_{m}'] & summary_df[f'pass_{m}_{type}']
                summary_df = summary_df.drop(f'pass_{m}_{type}', axis=1)
                summary_df = summary_df.dropna()            

                # Filter by types selected
                
                # Histogram axes settings
                nbin = max( int(len(summary_df.index)/3), 10 )
                xmin = min( dictMeas[m]['xmin'], df_meas_filtered[m_db_name].min() )
                xmax = max( dictMeas[m]['xmax'], df_meas_filtered[m_db_name].max() )
                xlab = dictMeas[m]['label']+" "+dictMeas[m]['unit']
                if type != 'all':
                    xlab += " (type #"+type+")"

                # Filling Histogram
                histos[f'h1_{config}_{m}_{type}_{tag}'] = df_meas_filtered.plot.hist(column=m_db_name, bins=nbin, range=[xmin,xmax])

                # Draw Histogram
                histos[f'h1_{config}_{m}_{type}_{tag}'].set_xlabel(xlab)
                histos[f'h1_{config}_{m}_{type}_{tag}'].grid(True, linestyle='--', color='gray', linewidth=0.5)

                if thr_min > xmin:
                    histos[f'h1_{config}_{m}_{type}_{tag}'].axvline(thr_min, color='red', linestyle='--')
                if thr_min < xmax:
                    histos[f'h1_{config}_{m}_{type}_{tag}'].axvline(thr_max, color='red', linestyle='--')

                if dictMeas[m]['DrawHisto']:
                    histos[f'h1_{config}_{m}_{type}_{tag}'].get_figure().savefig(f'{plotdir}/h1_{config}_{m}_TYPE_{type}_{tag}.pdf')
                    plt.pyplot.close('all')

        summary_fail = summary_df[summary_df.isin([False]).any(axis=1)]

        if len(summary_fail)==0:
            outputfile.write("\n")
            outputfile.write("All parts match tender requirements\n")
        else:
            outputfile.write("\n")
            outputfile.write(f"{len(summary_fail)} part(s) not matching tender requirements\n")
            outputfile.write("\n")
            outputfile.write(summary_fail.to_string())
        outputfile.write("\n")
        outputfile.write("\n")

#--- Close result file
outputfile.close()
