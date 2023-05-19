## Python stuff
import os
import numpy as np
import pandas as pd

pd.set_option('display.max_rows',1)

from configs import config

#--- DEFAULTS
DIRIN  = 'data'
DIROUT = 'analyzed_df'
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

# Load one dataframe from file
def loadDataFrame(inputfile, set_index=''):

    df = pd.read_csv(inputfile)
    df.dropna(
        axis=0,
        how='all',
        subset=None,
        inplace=True
    )

    # Sort by selected column and set it as a string for further matching
    if set_index != '':
        df = df.sort_values(by=[set_index]) 
        df[set_index] = df[set_index].astype(str)
        df[set_index] = df[set_index].str.strip('.0')

    return df

def evaluateConversionFactors(df_PMT, df_TOFPET_ARRAY, dirout=DIRCONFIG):

    # array LY conversion factor (a.u. --> ph/MeV)
    ly_mean_singleCrystal = df_PMT[ df_PMT['NAME'].str.contains('STP')==False ]['LO'].mean()
    ly_mean_array = df_TOFPET_ARRAY[ df_TOFPET_ARRAY['KIND_OF_PART'].str.contains('2') ]['LY'].mean()
    CF['LY_au_to_phMev'] = ly_mean_singleCrystal / ly_mean_array

    # LY, SIGMA_T conversion factors from type 1,3 to type 2 arrays
    df_TOFPET_ARRAY_MEAN_OVER_TYPE = df_TOFPET_ARRAY.groupby(['KIND_OF_PART'], as_index=False).mean(numeric_only=True)
    
    for var in ['LY', 'SIGMA_T', 'XT']:
        type2_avg = df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains('2') ].iloc[0][var]
        for arraytype in ['1','3']:            
            array_avg = df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains(arraytype) ].iloc[0][var]
            CF[f'{var}_T{arraytype}_to_T2'] = type2_avg / array_avg

    saveConversionFactors(dirout_=dirout)


def saveConversionFactors(dirout_=DIRCONFIG):
    cfFile = open(f'{dirout_}/conversionFactors.txt','w')
    for cfName in CF:
        factor = CF[cfName]
        cfFile.write(f'{cfName} {factor}\n')
    cfFile.close()


def loadConversionFactors(dirconfig=DIRCONFIG):

    cfFileName = f'{dirconfig}/conversionFactors.txt'
    if not os.path.isfile(cfFileName):
        print(f'File {cfFileName} not found')
        print(f'Use default factors:')
        print(CF)
        return 0

    cfFile = os.open(cfFileName)
    for line in cfFile.read_lines():
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


def analyzeOmsData(dirin=DIRIN, dirout=DIROUT, evalSF=False, applySF=True):

    omsData = config.omsData

    # Get input dataframes from file
    df = {}
    for d in omsData:
        
        set_index = omsData[d]['index']
        filename = omsData[d]['filecsv']
        inputfile = f'/home/cmsdaq/BatchValidation/{dirin}/{filename}'
        
        df[d] = loadDataFrame(inputfile,set_index)

    #---------------------------------------------------------
    #-----------  Dataframes for single bars validation
    #---------------------------------------------------------

    # GALAXY for single bars
    df['GALAXY_SINGLEBAR'] = pd.merge( df['SINGLEBARS'], df['GALAXY'], how='inner', left_on='BARCODE', right_on='PART_BARCODE')

    # PMT for single bars
    df['PMT'] = pd.merge( df['SINGLEBARS'], df['PMT'], how='inner', left_on='BARCODE', right_on='PART_BARCODE')
    df['PMT']['LO'] =  df['PMT']['LY_ABS'] / (eff_PMT*pe_peak)    ## photons / MeV
    df['PMT']['LOoverDT'] = df['PMT']['LO'] / df['PMT']['DECAY_TIME'] 
    df['PMT']['LO_RSTD']  = df['PMT']['LO'].std() / df['PMT']['LO'].mean()*100
    df['PMT']['DT_RSTD']  = df['PMT']['DECAY_TIME'].std() / df['PMT']['DECAY_TIME'].mean()*100
    df['PMT']['LOoverDT_RSTD']  = df['PMT']['LOoverDT'].std() / df['PMT']['LOoverDT'].mean()*100

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
    df['TOFPET_ARRAY'] = pd.merge( df['ARRAYS'], df['TOFPET_ARRAY'], how='inner', left_on='BARCODE', right_on='PARENT_ARRAY')
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].loc[ ~df['TOFPET_ARRAY']['PART_BARCODE'].str.contains('-15') & ~df['TOFPET_ARRAY']['PART_BARCODE'].str.contains('-0')] # remove first and last bar of each array
    df['TOFPET_ARRAY']['XT'] = (df['TOFPET_ARRAY']['XTLEFT'] + df['TOFPET_ARRAY']['XTRIGHT'])/2.

    if(evalSF==True):
        evaluateConversionFactors(df['PMT'], df['TOFPET_ARRAY'])
    else:
        loadConversionFactors()
    if(applySF==True):
        applyConversionFactors(df['TOFPET_ARRAY'])

    df['TOFPET_ARRAY_RUN']  = df['TOFPET_ARRAY'][['PARENT_ARRAY','NAME']].drop_duplicates()
    df['TOFPET_ARRAY_MEAN'] = df['TOFPET_ARRAY'].groupby(['PARENT_ARRAY'], as_index=False).mean(numeric_only=True)
    df['TOFPET_ARRAY_STD']  = df['TOFPET_ARRAY'].groupby(['PARENT_ARRAY'], as_index=False).std(numeric_only=True)
    
    # Relative standard deviation
    df['TOFPET_ARRAY_RSTD'] = df['TOFPET_ARRAY_STD'].select_dtypes(exclude='object').div( 
                df['TOFPET_ARRAY_MEAN'].select_dtypes(exclude='object') ).combine_first(df['TOFPET_ARRAY_STD'])

    df['TOFPET_ARRAY_MEAN'] = df['TOFPET_ARRAY_MEAN'].add_suffix('_MEAN')
    df['TOFPET_ARRAY_STD']  = df['TOFPET_ARRAY_STD'].add_suffix('_STD')
    df['TOFPET_ARRAY_RSTD'] = df['TOFPET_ARRAY_RSTD'].add_suffix('_RSTD')

    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY_MEAN'].merge( df['TOFPET_ARRAY_STD'] , how='inner', left_on='PARENT_ARRAY_MEAN', right_on='PARENT_ARRAY_STD' )
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY']     .merge( df['TOFPET_ARRAY_RSTD'], how='inner', left_on='PARENT_ARRAY_MEAN', right_on='PARENT_ARRAY_RSTD')
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].merge( df['TOFPET_ARRAY_RUN'], left_on='PARENT_ARRAY_MEAN', right_on='PARENT_ARRAY')
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].merge( df['ARRAYS'], how='left', left_on='PARENT_ARRAY_MEAN', right_on='BARCODE')
    df['TOFPET_ARRAY'][['LY_RSTD','SIGMA_T_RSTD','XT_RSTD']] = df['TOFPET_ARRAY'][['LY_RSTD','SIGMA_T_RSTD','XT_RSTD']].apply(lambda x: x*100)

    #Dataframe for Optical measurements of Bar in Arrays
    df['TOFPET_BARINARRAY'] = df['TOFPET'].copy()
    df['TOFPET_BARINARRAY']['PARENT_ARRAY'] = list(list(zip(*df['TOFPET_BARINARRAY']['PART_BARCODE'].str.split("-")))[0])
    df['TOFPET_BARINARRAY'] = df['TOFPET_BARINARRAY'].merge( df['ARRAYS'], how='left', left_on='PARENT_ARRAY', right_on='BARCODE')
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

    
