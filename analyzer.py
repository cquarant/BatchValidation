## Python stuff
import os
import re
import numpy as np
import pandas as pd

import Functions as func
from configs import config

#--- DEFAULTS
DIRIN  = 'data'
DIROUT = 'analyzed_data'
DIRCONFIG = 'configs'

CF = {
        'LY_au_to_phMev'   : 1, # LY conversion factor from arbitrary units to ph/Mev (needs PMT input)
        'LY_T1_to_T2'      : 1, # LY conversion factor from type 1 to type 2 arrays
        'LY_T3_to_T2'      : 1, # LY conversion factor from type 3 to type 2 arrays
        'SIGMA_T_T1_to_T2' : 1, # SIGMA_T conversion factor from type 1 to type 2 arrays
        'SIGMA_T_T3_to_T2' : 1, # SIGMA_T conversion factor from type 3 to type 2 arrays
        'XT_T1_to_T2'      : 1, # XT conversion factor from type 1 to type 2 arrays
        'XT_T3_to_T2'      : 1, # XT conversion factor from type 3 to type 2 arrays
    }
    
#--- Set constants
eff_PMT = 0.25
pe_peak = 0.511 #MeV

def evaluateConversionFactors(df_PMT, df_TOFPET_ARRAY, dirout=DIRCONFIG):

    # array LY conversion factor (a.u. --> ph/MeV)
    ly_mean_singleCrystal = df_PMT[ df_PMT['NAME'].str.contains('STP')==False ]['LO'].mean()
    ly_mean_array = df_TOFPET_ARRAY[ df_TOFPET_ARRAY['KIND_OF_PART'].str.contains('2') ]['LY'].mean()
    CF['LY_au_to_phMev'] = ly_mean_singleCrystal / ly_mean_array

    # LY, SIGMA_T conversion factors from type 1,3 to type 2 arrays
    df_TOFPET_ARRAY_COPY = df_TOFPET_ARRAY.copy()
    df_TOFPET_ARRAY_COPY = df_TOFPET_ARRAY_COPY[df_TOFPET_ARRAY_COPY[ 'tag'].str.match("^PREIRR$") ]
    df_TOFPET_ARRAY_MEAN_OVER_TYPE = df_TOFPET_ARRAY_COPY.groupby(['KIND_OF_PART'], as_index=False).mean(numeric_only=True)
    
    for var in ['LY', 'SIGMA_T']:#, 'XT']:
        type2_avg = df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains('2') ].iloc[0][var]
        for arraytype in ['1','3']:            
            array_avg = df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains(arraytype) ].iloc[0][var]
            CF[f'{var}_T{arraytype}_to_T2'] = type2_avg / array_avg

    saveConversionFactors(dirout_=dirout)


def saveConversionFactors(dirout_=DIRCONFIG):
    cfFile = open(f'{dirout_}/conversionFactors.txt','w')
    print(f'Opening file: {dirout_}/conversionFactors.txt')
    for cfName in CF:
        factor = CF[cfName]
        cfFile.write(f"{cfName} {factor}"+"\n")
    cfFile.close()


def loadConversionFactors(dirconfig=DIRCONFIG):

    cfFileName = f'{dirconfig}/conversionFactors.txt'
    if not os.path.isfile(cfFileName):
        print(f'File {cfFileName} not found')
        print(f'Use default factors:')
        print(CF)
        return 0

    cfFile = open(cfFileName, 'r')
    for line in cfFile.readlines():
        splitline = line.split()
        CF[splitline[0]] = float(splitline[1])


def applyConversionFactors(df_TOFPET_ARRAY):

    df_TOFPET_ARRAY['LY'] = df_TOFPET_ARRAY['LY'] * CF['LY_au_to_phMev']
                            
    for var in ['LY', 'SIGMA_T','XT']:
        for arraytype in ['1','3']:
            df_TOFPET_ARRAY[var] = np.where(df_TOFPET_ARRAY['KIND_OF_PART'].str.contains(arraytype),
                               df_TOFPET_ARRAY[var] * CF[f'{var}_T{arraytype}_to_T2'],
                               df_TOFPET_ARRAY[var])


#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#
#  _  _ ____ _ _  _    ____ _  _ ____ _    _   _ ___  ____ ____  #
#  |\/| |__| | |\ |    |__| |\ | |__| |     \_/    /  |___ |__/  #
#  |  | |  | | | \|    |  | | \| |  | |___   |    /__ |___ |  \  #
#                                                                #
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#                                                             


def analyzeOmsData(dirin=DIRIN, dirout=DIROUT, evalSF=False, applySF=True, skipRuns=''):

    omsData = config.omsData

    # Get input dataframes from file
    df = {}
    for d in omsData:
        
        set_index = omsData[d]['index']
        filename = omsData[d]['filecsv']
        inputfile = f'/home/cmsdaq/BatchValidation/{dirin}/{filename}'
        
        df[d] = func.loadDataFrame(inputfile,set_index)

    #---------------------------------------------------------
    #-----------  Dataframes for single bars validation
    #---------------------------------------------------------

    # GALAXY for single bars
    df['GALAXY_SINGLEBAR'] = pd.merge( df['SINGLEBARS'], df['GALAXY'], how='inner', left_on='BARCODE', right_on='PART_BARCODE')

    # PMT for single bars
    df['PMT'] = pd.merge( df['SINGLEBARS'], df['PMT'], how='inner', left_on='BARCODE', right_on='PART_BARCODE')
    df['PMT']['LO'] =  df['PMT']['LY_ABS'] / (eff_PMT*pe_peak)    ## photons / MeV
    df['PMT']['LOoverDT'] = df['PMT']['LO'] / df['PMT']['DECAY_TIME'] 

    # Eval relatve dev. std. grouping by tag
    df['PMT']['tag'] = df['PMT']['NAME'].str.replace('(Run_LO_)?BAR\d{3,14}_', '')
    
    df['PMT_MEAN'] = df['PMT'][['tag','LO','DECAY_TIME','LOoverDT']].groupby(['tag'], as_index=False).mean(numeric_only=True)
    df['PMT_STD']  = df['PMT'][['tag','LO','DECAY_TIME','LOoverDT']].groupby(['tag'], as_index=False).std(numeric_only=True)
    df['PMT_RSTD'] = df['PMT_STD'].select_dtypes(exclude='object').div( 
                df['PMT_MEAN'].select_dtypes(exclude='object') ).combine_first(df['PMT_STD'])
    df['PMT_RSTD'] = df['PMT_RSTD'].add_suffix('_RSTD')

    df['PMT'] = df['PMT'].merge(df['PMT_RSTD'], how='left', left_on='tag', right_on='tag_RSTD')
    df['PMT'] = df['PMT'].drop(['tag_RSTD'], axis=1)
    
    #---------------------------------------------------------
    #-----------  Dataframes for array validation
    #---------------------------------------------------------

    # Dataframe with array types + galaxy measurements for whole array
    df['GALAXY_ARRAY'] = pd.merge( df['ARRAYS'], df['GALAXY'], how='inner', left_on='BARCODE', right_on='PART_BARCODE')
    df['GALAXY_ARRAY']['LMAXVAR'] = df['GALAXY_ARRAY'][['LMAXVAR_LS','LMAXVAR_LN']].max(axis=1)

    # Dataframe with galaxy measurements for bars in arrays only
    df['GALAXY_BARINARRAY'] = df['GALAXY'][df['GALAXY']['PART_BARCODE'].str.contains("-")]
    df['GALAXY_BARINARRAY']['PARENT_ARRAY'] = list(list(zip(* df['GALAXY_BARINARRAY']['PART_BARCODE'].str.split("-")))[0])
    df['GALAXY_BARINARRAY'] = df['GALAXY_BARINARRAY'].merge( df['ARRAYS'], how='left', left_on='PARENT_ARRAY', right_on='BARCODE')

    # Dataframe with optical properties of array (average and std. dev. for bars 1-14 for each array)
    df['TOFPET_ARRAY'] = df['TOFPET'].copy()
    df['TOFPET_ARRAY']['PARENT_ARRAY'] = list(list(zip(*df['TOFPET_ARRAY']['PART_BARCODE'].str.split("-")))[0])
    df['TOFPET_ARRAY']['tag'] = df['TOFPET_ARRAY']['NAME'].str.replace('Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_', '') # create tag column

    df['TOFPET_ARRAY'] = pd.merge( df['ARRAYS'], df['TOFPET_ARRAY'], how='inner', left_on='BARCODE', right_on='PARENT_ARRAY')
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].loc[ ~df['TOFPET_ARRAY']['PART_BARCODE'].str.contains('-15') & ~df['TOFPET_ARRAY']['PART_BARCODE'].str.contains('-0')] # remove first and last bar of each array
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].loc[ ~df['TOFPET_ARRAY']['PART_BARCODE'].str.contains('-1$') | ~df['TOFPET_ARRAY']['tag'].str.match('PREIRR-GR')] # remove second bar of each array for PREIRR-GR measurements
    df['TOFPET_ARRAY']['XT'] = (df['TOFPET_ARRAY']['XTLEFT'] + df['TOFPET_ARRAY']['XTRIGHT'])

    if(evalSF==True):
        evaluateConversionFactors(df['PMT'], df['TOFPET_ARRAY'])
    else:
        loadConversionFactors()
    if(applySF==True):
        applyConversionFactors(df['TOFPET_ARRAY'])

    df['TOFPET_ARRAY_RUN']  = df['TOFPET_ARRAY'][['PARENT_ARRAY','NAME']].drop_duplicates()
    df['TOFPET_ARRAY_MEAN'] = df['TOFPET_ARRAY'].groupby(['NAME'], as_index=False).mean(numeric_only=True)
    df['TOFPET_ARRAY_STD']  = df['TOFPET_ARRAY'].groupby(['NAME'], as_index=False).std(numeric_only=True)
    
    # Relative standard deviation
    df['TOFPET_ARRAY_RSTD'] = df['TOFPET_ARRAY_STD'].select_dtypes(exclude='object').div( 
                df['TOFPET_ARRAY_MEAN'].select_dtypes(exclude='object') ).combine_first(df['TOFPET_ARRAY_STD'])

    df['TOFPET_ARRAY_MEAN'] = df['TOFPET_ARRAY_MEAN'].add_suffix('_MEAN')
    df['TOFPET_ARRAY_STD']  = df['TOFPET_ARRAY_STD'].add_suffix('_STD')
    df['TOFPET_ARRAY_RSTD'] = df['TOFPET_ARRAY_RSTD'].add_suffix('_RSTD')

    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY_MEAN'].merge( df['TOFPET_ARRAY_STD'] , how='inner', left_on='NAME_MEAN', right_on='NAME_STD' )
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY']     .merge( df['TOFPET_ARRAY_RSTD'], how='inner', left_on='NAME_MEAN', right_on='NAME_RSTD')
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].merge( df['TOFPET_ARRAY_RUN'], left_on='NAME_MEAN', right_on='NAME')
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].merge( df['ARRAYS'], how='left', left_on='PARENT_ARRAY', right_on='BARCODE')
    df['TOFPET_ARRAY'][['LY_RSTD','SIGMA_T_RSTD','XT_RSTD','XT_STD']] = df['TOFPET_ARRAY'][['LY_RSTD','SIGMA_T_RSTD','XT_RSTD','XT_STD']].apply(lambda x: x*100)

    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].drop(columns=['NAME_MEAN','NAME_STD','NAME_RSTD'])
    col = df['TOFPET_ARRAY'].pop("BARCODE")
    df['TOFPET_ARRAY'].insert(0, col.name, col)
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].sort_values(by=['BARCODE'])

    #---------------------------------------------------------
    #-----------  Dataframes for BARS IN ARRAYS validation
    #---------------------------------------------------------

    #Dataframe for Optical measurements of Bar in Arrays
    df['TOFPET_BARINARRAY'] = df['TOFPET'].copy()
    df['TOFPET_BARINARRAY']['PARENT_ARRAY'] = list(list(zip(*df['TOFPET_BARINARRAY']['PART_BARCODE'].str.split("-")))[0])
    df['TOFPET_BARINARRAY'] = df['TOFPET_BARINARRAY'].merge( df['ARRAYS'], how='left', left_on='PARENT_ARRAY', right_on='BARCODE')
    df['TOFPET_BARINARRAY']['tag'] = df['TOFPET_BARINARRAY']['NAME'].str.replace('Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_', '') # create tag column
    df['TOFPET_BARINARRAY'] = df['TOFPET_BARINARRAY'].loc[ ~df['TOFPET_BARINARRAY']['PART_BARCODE'].str.contains('-1$') | ~df['TOFPET_BARINARRAY']['tag'].str.match('PREIRR-GR')] # remove second bar of each array for PREIRR-GR measurements

    df['TOFPET_BARINARRAY'] = df['TOFPET_BARINARRAY'].loc[ ~df['TOFPET_BARINARRAY']['PART_BARCODE'].str.contains('-15') & ~df['TOFPET_BARINARRAY']['PART_BARCODE'].str.contains('-0')]
    df['TOFPET_BARINARRAY']['XT'] = (df['TOFPET_BARINARRAY']['XTLEFT'] + df['TOFPET_BARINARRAY']['XTRIGHT'])/2.

    # apply conversion
    if(applySF==True):
        applyConversionFactors(df['TOFPET_BARINARRAY'])
    
    # Save to file
    if not os.path.isdir(dirout):
        os.system(f'mkdir -p {dirout}')
    for tag in df:
        df[tag].to_csv(f'{dirout}/data_{tag}.csv')
        with open(f'{dirout}/data_{tag}.txt', 'w') as file:
            df_string = df[tag].to_string()
            file.write(df_string) 
    
