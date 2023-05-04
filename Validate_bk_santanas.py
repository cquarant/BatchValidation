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
import matplotlib

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

# Tender thresholds

thr_LOsinglebar = 4000 #photons/MeV
thr_DTsinglebar = 45 #ns
thr_LOoverDTsinglebar = 105 #photons/(MeV ns)
thr_sigma_LOsinglebar = 0.1 #relative
thr_sigma_DTsinglebar = 0.05 #relative
thr_sigma_LOoverDTsinglebar = 0.05 #relative

tolerance = 0.03 #mm
thr_Lsinglebar_min = 55.00 - tolerance #mm
thr_Lsinglebar_max = 55.00 + tolerance #mm
thr_Wsinglebar_min = 3.12 - tolerance #mm
thr_Wsinglebar_max = 3.12 + tolerance #mm
thr_Tsinglebar_type1_min = 3.75 - tolerance #mm
thr_Tsinglebar_type1_max = 3.75 + tolerance #mm
thr_Tsinglebar_type2_min = 3.00 - tolerance #mm
thr_Tsinglebar_type2_max = 3.00 + tolerance #mm
thr_Tsinglebar_type3_min = 2.40 - tolerance #mm
thr_Tsinglebar_type3_max = 2.40 + tolerance #mm

thr_LmaxArray_min = 54.70 - 0.05 #mm
thr_LmaxArray_max = 54.70 + 0.05 #mm
thr_WmaxArray_min = 51.48 - 0.10 #mm
thr_WmaxArray_max = 51.48 + 0.10 #mm
#1
thr_TmaxArray_type1_min = 4.11 - 0.10 #mm
thr_TmaxArray_type1_max = 4.11 + 0.10 #mm
#2
thr_TmaxArray_type2_min = 3.36 - 0.10 #mm
thr_TmaxArray_type2_max = 3.36 + 0.10 #mm
#3
thr_TmaxArray_type3_min = 2.76 - 0.10 #mm
thr_TmaxArray_type3_max = 2.76 + 0.10 #mm

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
    "c3.BARLENGTH_RSTD, c3.LMAXVAR_LS, c3.LMAXVAR_LN, c3.L_MAX, c3.L_MEAN, c3.L_MEAN_RSTD, c3.WMAXVAR_LO, "
    "c3.WMAXVAR_LE, c3.W_MAX, c3.W_MEAN, c3.W_MEAN_RSTD, c3.TMAXVAR_FS, c3.TMAXVAR_FS_RSTD, c3.T_MAX, c3.T_MEAN, "
    "c3.T_MEAN_RSTD, c3.L_MEAN_MITU, c3.L_RSTD_MITU, c3.W_MEAN_MITU, c3.W_RSTD_MITU, c3.T_MEAN_MITU, "
    "c3.T_RSTD_MITU, c3.LMAXVAR_LS_RSTD, c3.LMAXVAR_LN_RSTD, c3.WMAXVAR_LO_RSTD, c3.WMAXVAR_LE_RSTD "
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

#--- Create dataframes

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

df_GALAXY_SINGLEBAR = df_GALAXY[df_GALAXY['PART_BARCODE'].str.match(singleBarId)]

df_GALAXY_ARRAY_ALL = ( df_GALAXY[df_GALAXY['PART_BARCODE'].str.match(arrayId)] )
df_GALAXY_ARRAY = ( df_GALAXY_ARRAY_ALL[df_GALAXY_ARRAY_ALL['PART_BARCODE'].str.contains(barInArrayId)==False] )
df_GALAXY_BARINARRAY = ( df_GALAXY_ARRAY_ALL[df_GALAXY_ARRAY_ALL['PART_BARCODE'].str.contains(barInArrayId)] )

#- GALAXY cleaning

df_GALAXY_SINGLEBAR = df_GALAXY_SINGLEBAR[df_GALAXY_SINGLEBAR['NAME'].str.match(singleBarGalaxyNameId)]
#print ( len(df_GALAXY_SINGLEBAR.index) )
#print (df_GALAXY_SINGLEBAR)

df_GALAXY_ARRAY = ( df_GALAXY_ARRAY[df_GALAXY_ARRAY['NAME'].str.match(arrayGalaxyNameId)] )
#print ( len(df_GALAXY_ARRAY.index) )
#print (df_GALAXY_ARRAY)

df_GALAXY_BARINARRAY = ( df_GALAXY_BARINARRAY[df_GALAXY_BARINARRAY['NAME'].str.match(barInArrayGalaxyNameId)] )
#print ( len(df_GALAXY_BARINARRAY.index) )
#print (df_GALAXY_BARINARRAY)

#--- Print number of parts and measurements for each dataframe

num_singlebars = len(df_SINGLEBARS.index)
num_arrays = len(df_ARRAYS.index)

num_exp_tofpet = num_arrays*16
num_exp_pmt = num_singlebars
num_exp_galaxy_barsInArray = num_arrays*16

print ("")
print ("Number of single bar parts: ", num_singlebars )
print ("Number of array parts: ", num_arrays )
print ("")
        
# #-------------------------------------------------------------
#     #    #     #    #    #       #     #  #####  ###  #####  
#    # #   ##    #   # #   #        #   #  #     #  #  #     # 
#   #   #  # #   #  #   #  #         # #   #        #  #       
#  #     # #  #  # #     # #          #     #####   #   #####  
#  ####### #   # # ####### #          #          #  #        # 
#  #     # #    ## #     # #          #    #     #  #  #     # 
#  #     # #     # #     # #######    #     #####  ###  #####  
# #-------------------------------------------------------------

outputfile = open("results.txt", "w")
c = R.TCanvas()

latex = R.TLatex()
latex.SetTextSize(0.025)
latex.SetTextAlign(13) 

#--- Check for missing measurements

for index, row in df_SINGLEBARS.iterrows():

    func.GetDataframe(str(row['BARCODE']),df_PMT,"PREIRR","PMT",1)
    func.GetDataframe(str(row['BARCODE']),df_GALAXY_SINGLEBAR,"PREIRR","GALAXY_SINGLEBAR",1)
    
for index, row in df_ARRAYS.iterrows():

    func.GetDataframe(str(row['BARCODE']),df_GALAXY_ARRAY,"PREIRR","GALAXY_ARRAY",1)
    func.GetDataframeArray(str(row['BARCODE']),df_GALAXY_BARINARRAY,"PREIRR","GALAXY_BARINARRAY",1)
    func.GetDataframeArray(str(row['BARCODE']),df_TOFPET,"PREIRR","TOFPET",1)

#-------------------------
#--- Single bars analysis
#-------------------------

#-- PMT analysis

df_PMT_summary = pd.DataFrame(columns=['BARCODE','measured_PMT','pass_LO','pass_DT','pass_LOoverDT'])
    
df_PMT['LO'] = [ly/(eff_PMT*pe_peak)  for ly in df_PMT['LY_ABS']] ## photons / MeV
df_PMT['pass_LO'] = [1 if ly>thr_LOsinglebar else 0 for ly in df_PMT['LO']] 

df_PMT['pass_DT'] = [1 if dt<thr_DTsinglebar else 0 for dt in df_PMT['DECAY_TIME']] ## ns

df_PMT['LOoverDT'] = df_PMT['LO']/df_PMT['DECAY_TIME'] 
df_PMT['pass_LOoverDT'] = [1 if ratio>thr_LOoverDTsinglebar else 0 for ratio in df_PMT['LOoverDT']] 

#-- GALAXY_SINGLEBAR analysis

df_GALAXY_SINGLEBAR_summary = pd.DataFrame(columns=['BARCODE','measured_GALAXY','pass_L','pass_W','pass_T'])

#-- Histograms
h1_PMT_LO_PREIRR = R.TH1F("h1_PMT_LO_PREIRR","h1_PMT_LO_PREIRR",100,3000,8000)
h1_PMT_LO_PREIRR.GetXaxis().SetTitle("Light Output [photons/MeV]")
h1_PMT_LO_PREIRR.GetYaxis().SetTitle("Number of single bars")

h1_PMT_DT_PREIRR = R.TH1F("h1_PMT_DT_PREIRR","h1_PMT_DT_PREIRR",100,34,46)
h1_PMT_DT_PREIRR.GetXaxis().SetTitle("Decay Time, DT [ns]")
h1_PMT_DT_PREIRR.GetYaxis().SetTitle("Number of single bars")

h1_PMT_LOoverDT_PREIRR = R.TH1F("h1_PMT_LOoverDT_PREIRR","h1_PMT_LOoverDT_PREIRR",100,50,200)
h1_PMT_LOoverDT_PREIRR.GetXaxis().SetTitle("LO/DT [photons/(MeV ns)]")
h1_PMT_LOoverDT_PREIRR.GetYaxis().SetTitle("Number of single bars")

h1_PMT_BRMS_PREIRR = R.TH1F("h1_PMT_BRMS_PREIRR","h1_PMT_BRMS_PREIRR",100,0,1)
h1_PMT_BRMS_PREIRR.GetXaxis().SetTitle("Baseline RMS [a.u.]")
h1_PMT_BRMS_PREIRR.GetYaxis().SetTitle("Number of single bars")

h1_PMT_B2SASYM_PREIRR = R.TH1F("h1_PMT_B2SASYM_PREIRR","h1_PMT_B2SASYM_PREIRR",100,0,2)
h1_PMT_B2SASYM_PREIRR.GetXaxis().SetTitle("Baseline Asymmetry @2#sigma")
h1_PMT_B2SASYM_PREIRR.GetYaxis().SetTitle("Number of single bars")

h1_PMT_B3SASYM_PREIRR = R.TH1F("h1_PMT_B3SASYM_PREIRR","h1_PMT_B3SASYM_PREIRR",500,0,20)
h1_PMT_B3SASYM_PREIRR.GetXaxis().SetTitle("Baseline Asymmetry @3#sigma")
h1_PMT_B3SASYM_PREIRR.GetYaxis().SetTitle("Number of single bars")

h1_GALAXY_SINGLEBAR_L_PREIRR = R.TH1F("h1_GALAXY_SINGLEBAR_L_PREIRR","h1_GALAXY_SINGLEBAR_L_PREIRR",100,thr_Lsinglebar_min-tolerance,thr_Lsinglebar_max+tolerance)
h1_GALAXY_SINGLEBAR_L_PREIRR.GetXaxis().SetTitle("Length [mm]")
h1_GALAXY_SINGLEBAR_L_PREIRR.GetYaxis().SetTitle("Number of single bars")
h1_GALAXY_SINGLEBAR_L_PREIRR.GetXaxis().SetNdivisions(6,10,0, R.kTRUE)

h1_GALAXY_SINGLEBAR_W_PREIRR = R.TH1F("h1_GALAXY_SINGLEBAR_W_PREIRR","h1_GALAXY_SINGLEBAR_W_PREIRR",100,thr_Wsinglebar_min-tolerance,thr_Wsinglebar_max+tolerance)
h1_GALAXY_SINGLEBAR_W_PREIRR.GetXaxis().SetTitle("Width [mm]")
h1_GALAXY_SINGLEBAR_W_PREIRR.GetYaxis().SetTitle("Number of single bars")

h1_GALAXY_SINGLEBAR_T_PREIRR = R.TH1F("h1_GALAXY_SINGLEBAR_T_PREIRR","h1_GALAXY_SINGLEBAR_T_PREIRR",100,thr_Tsinglebar_type2_min-tolerance,thr_Tsinglebar_type2_max+tolerance)
h1_GALAXY_SINGLEBAR_T_PREIRR.GetXaxis().SetTitle("Thickness [mm]")
h1_GALAXY_SINGLEBAR_T_PREIRR.GetYaxis().SetTitle("Number of single bars")

#-- Results

#-----------------
df_PMT_PREIRR = func.GetDataframe("all",df_PMT,"PREIRR","PMT",0)
df_GALAXY_SINGLEBAR_PREIRR = func.GetDataframe("all",df_GALAXY_SINGLEBAR,"PREIRR","GALAXY_SINGLEBAR",0)
#-----------------

for index, row in df_SINGLEBARS.iterrows():

    mybarPMT = func.GetDataframe(str(row['BARCODE']),df_PMT,"PREIRR","PMT",0)
    #print (mybarPMT)
    if mybarPMT.empty:
        df_PMT_summary = df_PMT_summary.append({'BARCODE':str(row['BARCODE'])
                                                ,'measured_PMT':0
                                                ,'pass_LO':0
                                                , 'pass_DT':0
                                                , 'pass_LOoverDT':0
                                                }
                                                , ignore_index=True)
        continue
    else:
        df_PMT_summary = df_PMT_summary.append({'BARCODE':str(row['BARCODE'])
                                                ,'measured_PMT':1
                                                ,'pass_LO': int(mybarPMT['pass_LO'])
                                                , 'pass_DT':  int(mybarPMT['pass_DT'])
                                                , 'pass_LOoverDT': int(mybarPMT['pass_LOoverDT'])
                                                }
                                                , ignore_index=True)
        
    mybarGALAXY_SINGLEBAR = func.GetDataframe(str(row['BARCODE']),df_GALAXY_SINGLEBAR,"PREIRR","GALAXY_SINGLEBAR",0)
    #print (mybarGALAXY_SINGLEBAR)        
    if mybarGALAXY_SINGLEBAR.empty:
        df_GALAXY_SINGLEBAR_summary = df_GALAXY_SINGLEBAR_summary.append({'BARCODE':str(row['BARCODE'])
                                                    ,'measured_GALAXY':0
                                                    ,'pass_L':0
                                                    , 'pass_W':0
                                                    , 'pass_T':0
                                                    }
                                                    , ignore_index=True)
        continue
    else:
        pass_L = 0
        pass_W = 0
        pass_T = 0
        if (float(mybarGALAXY_SINGLEBAR['L_MEAN'])>thr_Lsinglebar_min and float(mybarGALAXY_SINGLEBAR['L_MEAN'])<thr_Lsinglebar_max):
            pass_L = 1
        if (float(mybarGALAXY_SINGLEBAR['W_MEAN'])>thr_Wsinglebar_min and float(mybarGALAXY_SINGLEBAR['W_MEAN'])<thr_Wsinglebar_max):
            pass_W = 1        
        if(row['KIND_OF_PART']=="singleCrystal #1"):
            if (float(mybarGALAXY_SINGLEBAR['T_MEAN'])>thr_Tsinglebar_type1_min and float(mybarGALAXY_SINGLEBAR['T_MEAN'])<thr_Tsinglebar_type1_max):
                pass_T = 1        
        if(row['KIND_OF_PART']=="singleCrystal #2"):
            if (float(mybarGALAXY_SINGLEBAR['T_MEAN'])>thr_Tsinglebar_type2_min and float(mybarGALAXY_SINGLEBAR['T_MEAN'])<thr_Tsinglebar_type2_max):
                pass_T = 1        
        if(row['KIND_OF_PART']=="singleCrystal #3"):
            if (float(mybarGALAXY_SINGLEBAR['T_MEAN'])>thr_Tsinglebar_type3_min and float(mybarGALAXY_SINGLEBAR['T_MEAN'])<thr_Tsinglebar_type3_max):
                pass_T = 1        
            
        df_GALAXY_SINGLEBAR_summary = df_GALAXY_SINGLEBAR_summary.append({'BARCODE':str(row['BARCODE'])
                                                    ,'measured_GALAXY': 1
                                                    ,'pass_L': pass_L
                                                    , 'pass_W':  pass_W
                                                    , 'pass_T': pass_T
                                                    }
                                                    , ignore_index=True)
        
    h1_PMT_LO_PREIRR.Fill( float(mybarPMT['LO']) )
    h1_PMT_DT_PREIRR.Fill( float(mybarPMT['DECAY_TIME']) )
    h1_PMT_LOoverDT_PREIRR.Fill( float(mybarPMT['LOoverDT']) )
    h1_PMT_BRMS_PREIRR.Fill( float(mybarPMT['B_RMS']) )
    h1_PMT_B2SASYM_PREIRR.Fill( float(mybarPMT['B_2S_ASYM']) )
    h1_PMT_B3SASYM_PREIRR.Fill( float(mybarPMT['B_3S_ASYM']) )

    h1_GALAXY_SINGLEBAR_L_PREIRR.Fill( float(mybarGALAXY_SINGLEBAR['L_MEAN']) )
    h1_GALAXY_SINGLEBAR_W_PREIRR.Fill( float(mybarGALAXY_SINGLEBAR['W_MEAN']) )
    h1_GALAXY_SINGLEBAR_T_PREIRR.Fill( float(mybarGALAXY_SINGLEBAR['T_MEAN']) )

df_singlebar_summary = pd.merge(df_PMT_summary,df_GALAXY_SINGLEBAR_summary, on='BARCODE')
df_singlebar_summary['pass_all'] = (df_singlebar_summary['pass_LO']*df_singlebar_summary['pass_DT']*df_singlebar_summary['pass_LOoverDT']
                                    *df_singlebar_summary['pass_L']*df_singlebar_summary['pass_W']*df_singlebar_summary['pass_T']
                                    )

stddev_LO_singlebars = h1_PMT_LO_PREIRR.GetRMS()/h1_PMT_LO_PREIRR.GetMean()
stddev_DT_singlebars = h1_PMT_DT_PREIRR.GetRMS()/h1_PMT_DT_PREIRR.GetMean()
stddev_LOoverDT_singlebars = h1_PMT_LOoverDT_PREIRR.GetRMS()/h1_PMT_LOoverDT_PREIRR.GetMean()

pass_LO_singlebars = 0
pass_DT_singlebars = 0
pass_LOoverDT_singlebars = 0

pass_stddev_LO_singlebars = 0
pass_stddev_DT_singlebars = 0
pass_stddev_LOoverDT_singlebars = 0

pass_L_singlebars = 0
pass_W_singlebars = 0
pass_T_singlebars = 0

if len( df_singlebar_summary[ df_singlebar_summary['pass_LO']==1 ] ) == num_singlebars:
    pass_LO_singlebars = 1
if len( df_singlebar_summary[ df_singlebar_summary['pass_DT']==1 ] ) == num_singlebars:
    pass_DT_singlebars = 1
if len( df_singlebar_summary[ df_singlebar_summary['pass_LOoverDT']==1 ] ) == num_singlebars:
    pass_LOoverDT_singlebars = 1
    
if stddev_LO_singlebars < thr_sigma_LOsinglebar:
    pass_stddev_LO_singlebars = 1
if stddev_DT_singlebars < thr_sigma_DTsinglebar:
    pass_stddev_DT_singlebars = 1
if stddev_LOoverDT_singlebars < thr_sigma_LOoverDTsinglebar:
    pass_stddev_LOoverDT_singlebars = 1

if len( df_singlebar_summary[ df_singlebar_summary['pass_L']==1 ] ) == num_singlebars:
    pass_L_singlebars = 1
if len( df_singlebar_summary[ df_singlebar_summary['pass_W']==1 ] ) == num_singlebars:
    pass_W_singlebars = 1
if len( df_singlebar_summary[ df_singlebar_summary['pass_T']==1 ] ) == num_singlebars:
    pass_T_singlebars = 1

#-- Save summary

outputfile.write("---------------"+"\n")
outputfile.write("PMT Single bars"+"\n")
outputfile.write("---------------"+"\n")
outputfile.write("Number of single bar parts: "+str( len(df_singlebar_summary) )+"\n" )
outputfile.write("Number of single bar parts with measurements: "+str( len(df_singlebar_summary[ df_singlebar_summary['measured_PMT']==1 ]) )+"\n" )
outputfile.write("\n")
outputfile.write("LO [photons/MeV]: min="+str(df_PMT_PREIRR['LO'].min().round(1))
                     +" max="+str(df_PMT_PREIRR['LO'].max().round(1))+" ==> Pass = "+str(pass_LO_singlebars)+"\n" )
outputfile.write("LO: relative std.dev.="+str(round(stddev_LO_singlebars,3))+" ==> Pass = "+str(pass_stddev_LO_singlebars)+"\n" )
outputfile.write("\n")
outputfile.write("DT [ns]: min="+str(df_PMT_PREIRR['DECAY_TIME'].min().round(1))
                     +" max="+str(df_PMT_PREIRR['DECAY_TIME'].max().round(1))+" ==> Pass = "+str(pass_DT_singlebars)+"\n" )
outputfile.write("DT: relative std.dev.="+str(round(stddev_DT_singlebars,3))+" ==> Pass = "+str(pass_stddev_DT_singlebars)+"\n" )
outputfile.write("\n")
outputfile.write("LO/DT [photons/(MeV ns)]: min="+str(df_PMT_PREIRR['LOoverDT'].min().round(1))
                     +" max="+str(df_PMT_PREIRR['LOoverDT'].max().round(1))+" ==> Pass = "+str(pass_LOoverDT_singlebars)+"\n" )
outputfile.write("LO/DT: relative std.dev.="+str(round(stddev_LOoverDT_singlebars,3))+" ==> Pass = "+str(pass_stddev_LOoverDT_singlebars)+"\n" )
outputfile.write("---------------"+"\n")

outputfile.write("\n")

outputfile.write("---------------"+"\n")
outputfile.write("GALAXY Single bars"+"\n")
outputfile.write("---------------"+"\n")
outputfile.write("Number of single bar parts: "+str( len(df_singlebar_summary) )+"\n" )
outputfile.write("Number of single bar parts with measurements: "+str( len(df_singlebar_summary[ df_singlebar_summary['measured_GALAXY']==1 ]) )+"\n" )
outputfile.write("\n")
outputfile.write("Length [mm]: min="+str(df_GALAXY_SINGLEBAR_PREIRR['L_MEAN'].min().round(3))
                     +" max="+str(df_GALAXY_SINGLEBAR_PREIRR['L_MEAN'].max().round(3))+" ==> Pass = "+str(pass_L_singlebars)+"\n" )
outputfile.write("\n")
outputfile.write("Width [mm]: min="+str(df_GALAXY_SINGLEBAR_PREIRR['W_MEAN'].min().round(3))
                     +" max="+str(df_GALAXY_SINGLEBAR_PREIRR['W_MEAN'].max().round(3))+" ==> Pass = "+str(pass_W_singlebars)+"\n" )
outputfile.write("\n")
outputfile.write("Thickness [mm]: min="+str(df_GALAXY_SINGLEBAR_PREIRR['T_MEAN'].min().round(3))
                     +" max="+str(df_GALAXY_SINGLEBAR_PREIRR['T_MEAN'].max().round(3))+" ==> Pass = "+str(pass_T_singlebars)+"\n" )
outputfile.write("---------------"+"\n")

with open('singlebar_summary.txt', 'w') as fo:
    fo.write(df_singlebar_summary.__repr__())

#-- Save histograms

func.SaveHisto(h1_PMT_LO_PREIRR,thr_LOsinglebar,"none")
func.SaveHisto(h1_PMT_DT_PREIRR,thr_DTsinglebar,"none")
func.SaveHisto(h1_PMT_LOoverDT_PREIRR,thr_LOoverDTsinglebar,"none")
func.SaveHisto(h1_PMT_BRMS_PREIRR,"none","none")
func.SaveHisto(h1_PMT_B2SASYM_PREIRR,"none","none")
func.SaveHisto(h1_PMT_B3SASYM_PREIRR,"none","none")
func.SaveHisto(h1_GALAXY_SINGLEBAR_L_PREIRR,thr_Lsinglebar_min,thr_Lsinglebar_max)
func.SaveHisto(h1_GALAXY_SINGLEBAR_W_PREIRR,thr_Wsinglebar_min,thr_Wsinglebar_max)
func.SaveHisto(h1_GALAXY_SINGLEBAR_T_PREIRR,thr_Tsinglebar_type2_min,thr_Tsinglebar_type2_max)


#########################################################################

#---------------------------------------------------------
#-----------  Dataframes for array validation
#---------------------------------------------------------

# Dataframe with array types + galaxy measurements for whole array
df_GALAXY_ARRAY = pd.merge( df_ARRAYS, df_GALAXY, how='inner', left_on='BARCODE', right_on='PART_BARCODE')
df_GALAXY_ARRAY['LMAXVAR'] = df_GALAXY_ARRAY[['LMAXVAR_LS','LMAXVAR_LN']].max(axis=1)
# Dataframe with galaxy measurements for bars in arrays
df_GALAXY_BARINARRAY = df_GALAXY[df_GALAXY['PART_BARCODE'].str.contains(barInArrayId)]

#Dataframe for Optical measurements of Bar in Arrays
df_TOFPET_BARINARRAY = df_TOFPET.copy()
df_TOFPET_BARINARRAY = df_TOFPET_BARINARRAY.loc[ ~df_TOFPET_BARINARRAY['PART_BARCODE'].str.contains('-15') & ~df_TOFPET_BARINARRAY['PART_BARCODE'].str.contains('-0')]
df_TOFPET_BARINARRAY['XT'] = (df_TOFPET_BARINARRAY['XTLEFT'] + df_TOFPET_BARINARRAY['XTRIGHT'])/2.

# Dataframe with optical properties of array (average and std. dev. for bars 1-14 for each array)
df_TOFPET_ARRAY = df_TOFPET_BARINARRAY.copy()
df_TOFPET_ARRAY['PARENT_ARRAY'] = list(list(zip(*df_TOFPET_ARRAY['PART_BARCODE'].str.split("-")))[0])

df_TOFPET_ARRAY_RUN  = df_TOFPET_ARRAY[['PARENT_ARRAY','NAME']].drop_duplicates()
df_TOFPET_ARRAY_MEAN = df_TOFPET_ARRAY.groupby(['PARENT_ARRAY'], as_index=False).mean(numeric_only=True)
df_TOFPET_ARRAY_MEAN = df_TOFPET_ARRAY_MEAN.add_suffix('_MEAN')
df_TOFPET_ARRAY_RSTD = df_TOFPET_ARRAY.groupby(['PARENT_ARRAY'], as_index=False).apply(lambda x: np.std(x) / np.mean(x))
df_TOFPET_ARRAY_RSTD = df_TOFPET_ARRAY_RSTD.add_suffix('_RSTD')

df_TOFPET_ARRAY = df_TOFPET_ARRAY_MEAN.merge( df_TOFPET_ARRAY_RSTD, how='inner', left_on='PARENT_ARRAY_MEAN', right_on='PARENT_ARRAY_RSTD')
df_TOFPET_ARRAY = df_TOFPET_ARRAY.merge(df_TOFPET_ARRAY_RUN, left_on='PARENT_ARRAY_MEAN', right_on='PARENT_ARRAY')
df_TOFPET_ARRAY['LY_MEAN'] = df_TOFPET_ARRAY['LY_MEAN'].apply(lambda x: x*3950/48.8)
df_TOFPET_ARRAY[['LY_RSTD','SIGMA_T_RSTD','XT_RSTD']] = df_TOFPET_ARRAY[['LY_RSTD','SIGMA_T_RSTD','XT_RSTD']].apply(lambda x: x*100)

#---------------------------------------------------------
#-----------  Dataframes for single bars validation
#---------------------------------------------------------


#---------------------------------------------------------
#-------- Configuration of Validation steps
#---------------------------------------------------------

dictConfig = {
    "GALAXY_ARRAY": {
        'tag'    : 'PREIRR',
        'meas'   : ["W_MAX","L_MAX","LMAXVAR"],#,"T_MAX"], 
        'df_meas': df_GALAXY_ARRAY,
        'summary_df_col': ['BARCODE','KIND_OF_PART', 'NAME'],
    },
    "GALAXY_BARINARRAY" : {
        'tag'    : 'PREIRR',
        'meas':["BARLENGTH"],
        'df_meas': df_GALAXY_BARINARRAY,
        'summary_df_col': ['PART_BARCODE', 'NAME'],
    },
    "TOFPET_ARRAY_PREIRR" : {
        'tag' : 'PREIRR',
        'meas': ['LY_MEAN','LY_RSTD','SIGMA_T_MEAN','SIGMA_T_RSTD','XT_MEAN','XT_RSTD'],
        'df_meas': df_TOFPET_ARRAY,
        'summary_df_col' : ['PARENT_ARRAY','NAME']
    },
    "TOFPET_ARRAY_GREASE" : {
        'tag' : 'GREASE',
        'meas': ['LY_MEAN','LY_RSTD','SIGMA_T_MEAN','SIGMA_T_RSTD','XT_MEAN','XT_RSTD'],
        'df_meas': df_TOFPET_ARRAY,
        'summary_df_col' : ['PARENT_ARRAY','NAME']
    },
    "TOFPET_BARINARRAY_PREIRR" : {
        'tag' : 'PREIRR',
        'meas': ['SIGMA_T','XT'],
        'df_meas': df_TOFPET_BARINARRAY,
        'summary_df_col' : ['PART_BARCODE','NAME']
    },
    "TOFPET_BARINARRAY_GREASE" : {
        'tag' : 'GREASE',
        'meas': ['SIGMA_T','XT'],
        'df_meas': df_TOFPET_BARINARRAY,
        'summary_df_col' : ['PART_BARCODE','NAME']
    },
    
}

# Measurements to be checked
dictMeas = {
    "L_MAX"    : {'db_name': 'L_MAX'    , 'xmin':54.85, 'xmax':55.15, 'thr':[54.90, 55.10], 'label':'Length'             , 'unit':'[mm]', 'pass_check':False},
    "LMAXVAR"  : {'db_name': 'LMAXVAR'  , 'xmin': 0.00, 'xmax': 0.07, 'thr':[-1.00,  0.05], 'label':'Planarity'          , 'unit':'[mm]', 'pass_check':False},
    "W_MAX"    : {'db_name': 'W_MAX'    , 'xmin':50.88, 'xmax':52.08, 'thr':[51.38, 51.58], 'label':'Width'              , 'unit':'[mm]', 'pass_check':False},
    "T_MAX"    : {'db_name': 'T_MAX'    , 'xmin': 3.91, 'xmax': 4.31, 'thr':[ 4.01,  4.21], 'label':'Thickness (type #3)', 'unit':'[mm]', 'pass_check':False},
    "BARLENGTH": {'db_name': 'BARLENGTH', 'xmin':54.85, 'xmax':55.15, 'thr':[54.95, 55.05], 'label':'Length'             , 'unit':'[mm]', 'pass_check':False},
    "LY_MEAN"  : {'db_name': 'LY_MEAN'  , 'xmin':3750 , 'xmax':7000 , 'thr':[4000,9999999], 'label':'Light Yield'        , 'unit':'[ph/MeV]', 'pass_check':False},
    "LY_RSTD"  : {'db_name': 'LY_RSTD'  , 'xmin': 0.00, 'xmax':10.00, 'thr':[ 0.00,  7.00], 'label':'Light Yield RMS'    , 'unit':'(%)' , 'pass_check':False},
    "SIGMA_T_MEAN": {'db_name':'SIGMA_T_MEAN', 'xmin':90, 'xmax':150, 'thr':[ 0.00,140.00], 'label':'Time resolution'    , 'unit':'[ps]', 'pass_check':False},
    "SIGMA_T_RSTD": {'db_name':'SIGMA_T_RSTD', 'xmin': 0, 'xmax':10., 'thr':[ 0.00,  6.00], 'label':'Time resolution RMS', 'unit':'(%)' , 'pass_check':False},
    "XT_MEAN"  : {'db_name': 'XT_MEAN'  , 'xmin': 0.00, 'xmax': 0.30, 'thr':[ 0.00,  0.25], 'label':'Cross Talk'         , 'unit':''    , 'pass_check':False},
    "XT_RSTD"  : {'db_name': 'XT_RSTD'  , 'xmin': 0.00, 'xmax':50.00, 'thr':[ 0.00, 40.00], 'label':'Cross Talk RMS'     , 'unit':'(%)' , 'pass_check':False},
    "SIGMA_T"  : {'db_name': 'SIGMA_T'  , 'xmin':90   , 'xmax':150  , 'thr':[ 0.00,140.00], 'label':'Time resolution'    , 'unit':'[ps]', 'pass_check':False},
    "XT"       : {'db_name': 'XT'       , 'xmin': 0.00, 'xmax': 0.30, 'thr':[ 0.00,  0.25], 'label':'Cross Talk'         , 'unit':''    , 'pass_check':False},
}

histos = {}

for config in dictConfig:

    # Filter by run tag (row-wise) and for relevant measurements (column-wise)
    tag       = dictConfig[config]['tag']
    meas_list = dictConfig[config]['meas']
    df_meas   = dictConfig[config]['df_meas']
    
    summary_df = df_meas[ dictConfig[config]['summary_df_col'] + meas_list]
    summary_df = summary_df[ summary_df['NAME'].str.contains(tag)==True ]
    
    if len(summary_df)==0:
        continue
    
    outputfile.write("\n")
    outputfile.write("##############################################################"+"\n")
    outputfile.write(f"                 {config} VALDATION                  "+"\n")
    outputfile.write("##############################################################"+"\n")    
    outputfile.write("\n")
    outputfile.write("Number of parts available: "+str( len(summary_df) )+"\n" )
    outputfile.write("Number of parts measured : "+str( len(summary_df.dropna()) )+"\n" )
    outputfile.write("\n")

    for m in meas_list:
    
        m_db_name = dictMeas[m]['db_name']

        # Check if part pass MTD requirements for measurement m
        thr_list = dictMeas[m]['thr']
        summary_df[f'pass_{m_db_name}'] = np.where( summary_df[m_db_name].between(thr_list[0],thr_list[-1]), True, False )
        summary_df = summary_df.dropna()
                
        # Histogram axes settings
        nbin = max( int(len(summary_df.index)/3), 10 )
        xmin = min( dictMeas[m]['xmin'], summary_df[m_db_name].min() )
        xmax = max( dictMeas[m]['xmax'], summary_df[m_db_name].max() )
        xlab = dictMeas[m]['label']+" "+dictMeas[m]['unit']

        # Filling Histogram
        histos[f'h1_{config}_{m}_{tag}'] = summary_df.plot.hist(column=m_db_name, bins=nbin, range=[xmin,xmax])

        # Draw Histogram
        histos[f'h1_{config}_{m}_{tag}'].set_xlabel(xlab)
        
        for thr in thr_list:
            if thr > dictMeas[m]['xmin'] and thr < dictMeas[m]['xmax']:
                histos[f'h1_{config}_{m}_{tag}'].axvline(thr, color='red')

        histos[f'h1_{config}_{m}_{tag}'].get_figure().savefig(f'h1_{config}_{m}_{tag}.pdf')
    
    
        outputfile.write(f"{xlab.ljust(25)}: min="+str(summary_df[m_db_name].min().round(3)).ljust(6)+" max="+str(summary_df[m_db_name].max().round(3)).ljust(6)
                         +" ==> Pass : "+str(len(summary_df[summary_df[f'pass_{m_db_name}']==False]) == 0) )
        outputfile.write("\n")
            
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
    outputfile.write("\n")

# outputfile.write("Width [mm]: min="+str(df_GALAXY_SINGLEBAR_PREIRR['W_MEAN'].min().round(3))
#                      +" max="+str(df_GALAXY_SINGLEBAR_PREIRR['W_MEAN'].max().round(3))+" ==> Pass = "+str(pass_W_singlebars)+"\n" )
# outputfile.write("Thickness [mm]: min="+str(df_GALAXY_SINGLEBAR_PREIRR['T_MEAN'].min().round(3))
#                      +" max="+str(df_GALAXY_SINGLEBAR_PREIRR['T_MEAN'].max().round(3))+" ==> Pass = "+str(pass_T_singlebars)+"\n" )
# outputfile.write("---------------"+"\n")

#-- Example printout
#print ( func.GetDataframe("FK00002000022",df_GALAXY_SINGLEBAR,"PREIRR","GALAXY_SINGLEBAR",1)[['PART_BARCODE','L_MEAN','W_MEAN','T_MEAN']],0)

#--- Close result file
outputfile.close()
