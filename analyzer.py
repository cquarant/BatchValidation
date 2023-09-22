## Python stuff
import os
import numpy as np
import pandas as pd
import importlib

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'

import Functions as func
from configs import config

#--- DEFAULTS
DEFAULTDIRIN  = f'{config.MAINDIR}/{config.DIRINANALYSIS}/{config.DEFAULTBATCH}'
DEFAULTDIROUT = f'{config.MAINDIR}/{config.DIROUTANALYSIS}/{config.DEFAULTBATCH}'

CF = {
        'LY_au_to_phMev'   : 1, # LY conversion factor from arbitrary units to ph/Mev (needs PMT input)
        'LY_T1_to_T2_PREIRR'      : 1, # LY conversion factor from type 1 to type 2 arrays
        'LY_T3_to_T2_PREIRR'      : 1, # LY conversion factor from type 3 to type 2 arrays
        'SIGMA_T_T1_to_T2_PREIRR' : 1, # SIGMA_T conversion factor from type 1 to type 2 arrays
        'SIGMA_T_T3_to_T2_PREIRR' : 1, # SIGMA_T conversion factor from type 3 to type 2 arrays
        'XT_T1_to_T2_PREIRR'      : 1, # XT conversion factor from type 1 to type 2 arrays
        'XT_T3_to_T2_PREIRR'      : 1, # XT conversion factor from type 3 to type 2 arrays
        'LY_T1_to_T2_PREIRR-GR'      : 1, # LY conversion factor from type 1 to type 2 arrays
        'LY_T3_to_T2_PREIRR-GR'      : 1, # LY conversion factor from type 3 to type 2 arrays
        'SIGMA_T_T1_to_T2_PREIRR-GR' : 1, # SIGMA_T conversion factor from type 1 to type 2 arrays
        'SIGMA_T_T3_to_T2_PREIRR-GR' : 1, # SIGMA_T conversion factor from type 3 to type 2 arrays
        'XT_T1_to_T2_PREIRR-GR'      : 1, # XT conversion factor from type 1 to type 2 arrays
        'XT_T3_to_T2_PREIRR-GR'      : 1, # XT conversion factor from type 3 to type 2 arrays
    }
    
#--- Set constants
eff_PMT = 0.25
pe_peak = 0.511 #MeV
ref_ly = 687.39 / (eff_PMT*pe_peak) # ref ly [ph/MeV]
ref_dt = 46.5 # [ns]

def evaluateConversionFactors(df_PMT, df_TOFPET_ARRAY, tag, dirout=config.DIRCONFIG):


    ### ARRAY LY CONVERSION FACTOR IN DRY COUPLING (a.u. --> ph/MeV)
    ### IMPORTANT: LY from singleBar FIXED AT AVERAGE FROM PREPRODBATCH 1
    ### In PreProdBatch2 the PMT results changed for reference bar, therefore we will keep PreProdBatch1 PMT LY as reference
    
    print(df_TOFPET_ARRAY[df_TOFPET_ARRAY['tag'].str.match(f"^{tag}$")][['PART_BARCODE','tag','LY']])
    if tag == 'PREIRR':
        ly_mean_array = df_TOFPET_ARRAY[ df_TOFPET_ARRAY['tag'].str.match(f"^{tag}$") & df_TOFPET_ARRAY['KIND_OF_PART'].str.contains('2') ]['LY'].mean()
        ly_mean_singleCrystal = 5368.2240278485615
        CF['LY_au_to_phMev'] = ly_mean_singleCrystal / ly_mean_array
    
    # UNCOMMENT following lines if you want, instead, to evaluate conversion factor using PMT measurement 
    # from the current production batch you are measuring
    # Array LO may result shifted w.r.t. PreProdBatch 1
    #
    # ly_mean_singleCrystal = df_PMT[ df_PMT['NAME'].str.contains('STP')==False ]['LO'].mean()
    # CF['LY_au_to_phMev'] = ly_mean_singleCrystal / ly_mean_array

    ### ARRAY LY CONVERSION FACTOR IN GREASE COUPLING (a.u. --> ph/MeV)
    # ly_mean_array_grease = df_TOFPET_ARRAY[ df_TOFPET_ARRAY['KIND_OF_PART'].str.contains('2') and df_TOFPET_ARRAY['NAME'].str.contains('PREIRR-GR') ]['LY'].mean()
    # CF['LY_grease_to_dry'] = ly_mean_array_grease / 51.5525

    # LY, SIGMA_T conversion factors from type 1,3 to type 2 arrays
    df_TOFPET_ARRAY_COPY = df_TOFPET_ARRAY.copy()
    df_TOFPET_ARRAY_COPY = df_TOFPET_ARRAY_COPY[df_TOFPET_ARRAY_COPY['tag'].str.match(f"^{tag}$") ]
    
    # Do mean over array of the same type, keeping also RefArrays as type 2
    array_type = ['#1','#2','#3']
    pat = '|'.join(array_type)
    s = df_TOFPET_ARRAY_COPY['KIND_OF_PART'].str.extract('('+ pat + ')', expand=False)
    df_TOFPET_ARRAY_MEAN_OVER_TYPE = df_TOFPET_ARRAY_COPY.groupby(s).mean().reset_index() # include RefArrays to type2
    # df_TOFPET_ARRAY_MEAN_OVER_TYPE = df_TOFPET_ARRAY_COPY.groupby(['KIND_OF_PART'], as_index=False).mean(numeric_only=True)
    print(df_TOFPET_ARRAY_MEAN_OVER_TYPE)
    print(df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains('2') ].iloc[0]['LY'])

    for var in ['LY', 'SIGMA_T', 'XT']:
        print(tag)
        type2_avg = df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains('2') ].iloc[0][var]
        for arraytype in ['1','3']:
            if not df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains(arraytype) ].empty:  
                array_avg = df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains(arraytype) ].iloc[0][var]
                CF[f'{var}_T{arraytype}_to_T2_{tag}'] = type2_avg / array_avg
            else:
                CF[f'{var}_T{arraytype}_to_T2_{tag}'] = 1

    saveConversionFactors()

def saveConversionFactors(dirout_=config.DIRCONFIG):
    cfFile = open(f'{dirout_}/conversionFactors.txt','w')
    print(f'Opening file: {dirout_}/conversionFactors.txt')
    for cfName in CF:
        print(cfName, CF[cfName])
        factor = CF[cfName]
        cfFile.write(f"{cfName} {factor}"+"\n")
    cfFile.close()


def loadConversionFactors(dirconfig=config.DIRCONFIG):

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
            df_TOFPET_ARRAY[var] = np.where(df_TOFPET_ARRAY['KIND_OF_PART'].str.contains(arraytype) & df_TOFPET_ARRAY['tag'].str.match(f"^PREIRR$"),
                               df_TOFPET_ARRAY[var] * CF[f'{var}_T{arraytype}_to_T2_PREIRR'],
                               df_TOFPET_ARRAY[var])
            df_TOFPET_ARRAY[var] = np.where(df_TOFPET_ARRAY['KIND_OF_PART'].str.contains(arraytype) & df_TOFPET_ARRAY['tag'].str.match(f"^POSTIRR$"),
                               df_TOFPET_ARRAY[var] * CF[f'{var}_T{arraytype}_to_T2_PREIRR'],
                               df_TOFPET_ARRAY[var])
            df_TOFPET_ARRAY[var] = np.where(df_TOFPET_ARRAY['KIND_OF_PART'].str.contains(arraytype) & df_TOFPET_ARRAY['tag'].str.match(f"^PREIRR-GR$"),
                               df_TOFPET_ARRAY[var] * CF[f'{var}_T{arraytype}_to_T2_PREIRR-GR'],
                               df_TOFPET_ARRAY[var])
            df_TOFPET_ARRAY[var] = np.where(df_TOFPET_ARRAY['KIND_OF_PART'].str.contains(arraytype) & df_TOFPET_ARRAY['tag'].str.match(f"^POSTIRR-GR"),
                               df_TOFPET_ARRAY[var] * CF[f'{var}_T{arraytype}_to_T2_PREIRR-GR'],
                               df_TOFPET_ARRAY[var])

# return df with average and standard deviation of any columns with numerical values
# if goupby column(s) is(are) specified, averages and std.dev. will be done grouping by selected column(s)
def averageAndStdDev(df, groupby_cols=None, index_col=False):
    
    df_mean = df.groupby(groupby_cols, as_index=False).mean(numeric_only=True)
    df_mean = df_mean.add_suffix('_MEAN')
    df_std  = df.groupby(groupby_cols, as_index=False).std(numeric_only=True)
    df_std  = df_std.add_suffix('_STD')
    df_mean_std = pd.merge(df_mean,df_std,how='inner',left_on=index_col+'_MEAN',right_on=index_col+'_STD')
    df_mean_std.rename(columns={index_col+'_MEAN':index_col})

    return df_mean_std

# return dataframe with the comparison (relative variation) of measurement with different runtag
# es.: comparison between pre-post irradiation measurement
def relativeVariationByTag(df, tag1, tag2, index_col):

    df_tag1 = df[ df['tag'].str.match(f'{tag1}$') ]
    df_tag2 = df[ df['tag'].str.match(f'{tag2}$') ]
    df_tag1 = df_tag1[ df_tag1[index_col].isin( df_tag2[index_col] ) ]
    df_tag2 = df_tag2[ df_tag2[index_col].isin( df_tag1[index_col] ) ]

    df_tag1 = func.sortAndResetIndex(df_tag1, index_col)
    df_tag2 = func.sortAndResetIndex(df_tag2, index_col)


    df_tag1_values = df_tag1.select_dtypes(include=np.number) 
    df_tag2_values = df_tag2.select_dtypes(include=np.number)

    df_variation = df_tag1_values.subtract(df_tag2_values, axis='columns')
    df_relative_variation = df_variation.div(df_tag2_values,axis='columns')
    df_relative_variation = df_relative_variation.apply(lambda x: x*100)
    df_relative_variation = df_relative_variation.add_suffix('_REL_VARIATION')
    df_relative_variation = df_relative_variation.merge(df_tag1[index_col], how='left',left_index=True,right_index=True ) 


    return (df_relative_variation)

#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#
#  _  _ ____ _ _  _    ____ _  _ ____ _    _   _ ___  ____ ____  #
#  |\/| |__| | |\ |    |__| |\ | |__| |     \_/    /  |___ |__/  #
#  |  | |  | | | \|    |  | | \| |  | |___   |    /__ |___ |  \  #
#                                                                #
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#                                                             


def analyzeOmsData(dirin=DEFAULTDIRIN, dirout=DEFAULTDIROUT, evalSF=False, applySF=True, skipRunFile=''):

    omsData = config.omsData

    # Get input dataframes from file
    df = {}
    for d in omsData:
        
        set_index = omsData[d]['index']
        filename = omsData[d]['filecsv']
        inputfile = f'/home/cmsdaq/BatchValidation/{dirin}/{filename}'
        
        df[d] = func.loadDataFrame(inputfile,set_index)

    # Load runs to be skipped
    if skipRunFile != '':

        skipRunFile = skipRunFile.replace('/','.')
        skipRunFile = skipRunFile.replace('.py','')

        print(f'importing {skipRunFile}')
        skipRuns = importlib.import_module(skipRunFile).skipRuns

        for tag in skipRuns:
            print(f'Skipping selected runs for {tag}')
            df[tag] = df[tag][ ~df[tag]['NAME'].isin(skipRuns[tag]) ]


    #---------------------------------------------------------
    #-----------  Dataframes for single bars validation
    #---------------------------------------------------------

    ### GALAXY for single bars
    df['GALAXY_SINGLEBAR'] = pd.merge( df['SINGLEBARS'], df['GALAXY'], how='inner', left_on='BARCODE', right_on='PART_BARCODE')

    ### PMT for single bars
    df['PMT'] = pd.merge( df['SINGLEBARS'], df['PMT'], how='inner', left_on='BARCODE', right_on='PART_BARCODE')
    df['PMT']['LO'] =  df['PMT']['LY_ABS'] / (eff_PMT*pe_peak)    ## photons / MeV
    df['PMT']['LOoverDT'] = df['PMT']['LO'] / df['PMT']['DECAY_TIME'] 
    df['PMT']['LOoverDT_NORM'] = df['PMT']['LOoverDT'] / ((df['PMT']['LO']/df['PMT']['LY_NORMAL']) / 46.5 )
    df['PMT']['LOscaledToRef'] = df['PMT']['LY_NORMAL'] * ref_ly
    df['PMT']['LOoverDTscaledToRef'] = df['PMT']['LOoverDT_NORM'] * ref_ly / ref_dt

    # Eval relatve dev. std. grouping by tag
    df['PMT']['tag'] = df['PMT']['NAME'].str.replace('(Run_LO_)?BAR\d{3,14}_', '')
    df['PMT_MEAN'] = df['PMT'][['tag','LO','DECAY_TIME','LOoverDT']].groupby(['tag'], as_index=False).mean(numeric_only=True)
    df['PMT_STD']  = df['PMT'][['tag','LO','DECAY_TIME','LOoverDT']].groupby(['tag'], as_index=False).std(numeric_only=True)
    df['PMT_RSTD'] = df['PMT_STD'].select_dtypes(exclude='object').div( 
                df['PMT_MEAN'].select_dtypes(exclude='object') ).combine_first(df['PMT_STD'])
    df['PMT_RSTD'] = df['PMT_RSTD'].add_suffix('_RSTD')
    df['PMT'] = df['PMT'].merge(df['PMT_RSTD'], how='left', left_on='tag', right_on='tag_RSTD')
    df['PMT'] = df['PMT'].drop(['tag_RSTD'], axis=1)

    # Average by ingot number
    df['PMT_INGOT_MEAN'] = df['PMT'][['BARCODE','tag','BATCH_INGOT_DATA','LY_NORMAL','LO','DECAY_TIME','LOoverDT']].groupby(['BATCH_INGOT_DATA','tag'], as_index=False).mean(numeric_only=True)
    df['PMT_INGOT_MEAN'] = df['PMT_INGOT_MEAN'].add_suffix('_MEAN')
    df['PMT_INGOT_STD']  = df['PMT'][['BARCODE','tag','BATCH_INGOT_DATA','LY_NORMAL','LO','DECAY_TIME','LOoverDT']].groupby(['BATCH_INGOT_DATA','tag'], as_index=False).std(numeric_only=True)
    df['PMT_INGOT_STD']  = df['PMT_INGOT_STD'].add_suffix('_STD')
    df['PMT_INGOT'] = pd.merge(df['PMT_INGOT_MEAN'],df['PMT_INGOT_STD'],how='inner',left_on=['BATCH_INGOT_DATA_MEAN','tag_MEAN'],right_on=['BATCH_INGOT_DATA_STD','tag_STD'])
    df['PMT_INGOT'] = df['PMT_INGOT'].rename(columns={'BATCH_INGOT_DATA_MEAN':'BATCH_INGOT_DATA', 'tag_MEAN':'tag'})
    df['PMT_INGOT']['NAME'] = df['PMT_INGOT']['BATCH_INGOT_DATA']+"_"+df['PMT_INGOT']['tag']

    #---------------------------------------------------------
    #-----------  Dataframes for array validation
    #---------------------------------------------------------

    # Dataframe with array types + galaxy measurements for whole array
    df['GALAXY_ARRAY'] = pd.merge( df['ARRAYS'], df['GALAXY'], how='inner', left_on='BARCODE', right_on='PART_BARCODE')
    df['GALAXY_ARRAY']['LMAXVAR'] = df['GALAXY_ARRAY'][['LMAXVAR_LS','LMAXVAR_LN']].max(axis=1)
    df['GALAXY_ARRAY']['LMAXVAR_STD'] = df['GALAXY_ARRAY'][['LMAXVAR_LS_STD','LMAXVAR_LN_STD']].max(axis=1)
    df['GALAXY_ARRAY'][ df['GALAXY_ARRAY'].select_dtypes(include=['float']).columns ] = df['GALAXY_ARRAY'].select_dtypes(include=['float']).transform( lambda x: func.roundHalfWay(x, 3) )

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
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].loc[ ~df['TOFPET_ARRAY']['PART_BARCODE'].str.contains('-1$') | ~df['TOFPET_ARRAY']['tag'].str.contains('-GR')] # remove second bar of each array for PREIRR-GR measurements
    df['TOFPET_ARRAY']['XT'] = (df['TOFPET_ARRAY']['XTLEFT'] + df['TOFPET_ARRAY']['XTRIGHT'])
    df['TOFPET_ARRAY'] = df['TOFPET_ARRAY'].drop(['XTLEFT','XTRIGHT'], axis='columns')

    if(evalSF==True):
        for tag in ['PREIRR', 'PREIRR-GR']:
            evaluateConversionFactors(df['PMT'], df['TOFPET_ARRAY'], tag)
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
    df['TOFPET_ARRAY']['tag'] = df['TOFPET_ARRAY']['NAME'].str.replace('Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_', '') # create tag column
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
    df['TOFPET_BARINARRAY']['XT'] = (df['TOFPET_BARINARRAY']['XTLEFT'] + df['TOFPET_BARINARRAY']['XTRIGHT'])
    df['TOFPET_BARINARRAY'] = df['TOFPET_BARINARRAY'].drop(['XTLEFT','XTRIGHT'], axis='columns')


    # apply conversion
    if(applySF==True):
        applyConversionFactors(df['TOFPET_BARINARRAY'])
    
    #---------------------------------------------------------
    #-----------  Dataframes for Caliber measurements
    #---------------------------------------------------------
    if 'CALIBER_ARRAY' in df.keys():
        if not df['CALIBER_ARRAY'].empty:
            df['CALIBER_ARRAY'] = pd.merge( df['CALIBER'], df['ARRAYS'], how='left', left_on='BARCODE', right_on='BARCODE')


    #---------------------------------------------------------
    #-----------  Dataframes for postirr validation
    #---------------------------------------------------------

    df['PMT_POSTIRR'] = df['PMT'][ df['PMT']['tag'].str.match('POSTIRR_0$') ]
    df['PMT_POSTIRR'] = df['PMT_POSTIRR'].merge( relativeVariationByTag(df['PMT'],'POSTIRR_0','PREIRR_0','BARCODE'), how='inner', left_on='BARCODE', right_on='BARCODE' )
    
    df['PMT_INGOT_POSTIRR'] = averageAndStdDev(df['PMT_POSTIRR'],groupby_cols=['BATCH_INGOT_DATA'],index_col='BATCH_INGOT_DATA')
    
    df['TOFPET_ARRAY_POSTIRR'] = df['TOFPET_ARRAY'][ df['TOFPET_ARRAY']['tag'].str.match('POSTIRR$') ]
    df['TOFPET_ARRAY_POSTIRR'] = df['TOFPET_ARRAY_POSTIRR'].merge( relativeVariationByTag(df['TOFPET_ARRAY'],'POSTIRR','PREIRR','BARCODE'), how='inner', left_on='BARCODE', right_on='BARCODE' )
    
    df['TOFPET_BARINARRAY_POSTIRR'] = df['TOFPET_BARINARRAY'][ df['TOFPET_BARINARRAY']['tag'].str.match('POSTIRR$') ]
    df['TOFPET_BARINARRAY_POSTIRR'] = df['TOFPET_BARINARRAY_POSTIRR'].merge( relativeVariationByTag(df['TOFPET_BARINARRAY'],'POSTIRR','PREIRR','PART_BARCODE'), how='inner', left_on='PART_BARCODE', right_on='PART_BARCODE' )

    df['TOFPET_ARRAY_POSTIRR-GR'] = df['TOFPET_ARRAY'][ df['TOFPET_ARRAY']['tag'].str.match('POSTIRR-GR$') ]
    df['TOFPET_ARRAY_POSTIRR-GR'] = df['TOFPET_ARRAY_POSTIRR-GR'].merge( relativeVariationByTag(df['TOFPET_ARRAY'],'POSTIRR-GR','PREIRR-GR','BARCODE'), how='inner', left_on='BARCODE', right_on='BARCODE' )

    df['TOFPET_BARINARRAY_POSTIRR-GR'] = df['TOFPET_BARINARRAY'][ df['TOFPET_BARINARRAY']['tag'].str.match('POSTIRR-GR$') ]
    df['TOFPET_BARINARRAY_POSTIRR-GR'] = df['TOFPET_BARINARRAY_POSTIRR-GR'].merge( relativeVariationByTag(df['TOFPET_BARINARRAY'],'POSTIRR-GR','PREIRR-GR','PART_BARCODE'), how='inner', left_on='PART_BARCODE', right_on='PART_BARCODE' )


    # Save to file
    if not os.path.isdir(dirout):
        os.system(f'mkdir -p {dirout}')
    for tag in df:
        df[tag].to_csv(f'{dirout}/data_{tag}.csv')
        df[tag] = df[tag].T.drop_duplicates().T
        with open(f'{dirout}/data_{tag}.txt', 'w') as file:
            df_string = df[tag].to_string()
            file.write(df_string)
