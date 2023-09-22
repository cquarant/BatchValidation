#------------------------------------------------------------------
import pandas as pd
import numpy as np
import os


# Load one dataframe from file
def loadDataFrame(inputfile, set_index=''):

    df = pd.read_csv(inputfile)
    df.dropna(
        axis=0,
        how='all',
        subset=None,
        inplace=True
    )

    if 'NAME' in df.columns:
        df = df[ df['NAME'].notna() ]

    # Sort by selected column and set it as a string for further matching
    if set_index != '':
        df = df.sort_values(by=[set_index]) 
        df[set_index] = df[set_index].astype(str)
        df[set_index] = df[set_index].str.replace("\.0", "")

    return df

# round halfway to a specific decimal
def roundHalfWay(number, decimal=1):
    return round(number*2, decimal-1)/2.

def sortAndResetIndex(df, index_col):

    df = df.sort_values(by=index_col)
    df = df.reset_index()
    df = df.drop('index', axis='columns')
    return df



