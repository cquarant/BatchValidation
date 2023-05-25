#------------------------------------------------------------------
import ROOT as R
R.gROOT.SetBatch(1)
import tdrstyle
import pandas as pd
import numpy as np
import os

def GetDataframe(barcode,df_input,tag,type,verbose):

    df_output = mypd.DataFrame()
    
    if str(barcode)=="all":
        df_output = df_input[ ( df_input['NAME'].str.contains(str(tag)) ) ]
    else:    
        df_output = df_input[ ( df_input['PART_BARCODE']==str(barcode) ) & ( df_input['NAME'].str.contains(str(tag)) ) ]

    df_empty = mypd.DataFrame()

    if df_output.empty:
        if verbose==1:
            print ( "WARNING -- Missing "+str(type)+" data "+str(tag) , str(barcode))
        return df_empty
    
    return df_output

def GetDataframeArray(barcode,df_input,tag,type,verbose):

    df_output = df_input[ ( df_input['PART_BARCODE'].str.contains(str(barcode)+"-") ) & ( df_input['NAME'].str.contains(str(tag)) ) ]

    df_empty = mypd.DataFrame()

    if df_output.empty:
        if verbose==1:
            print ( "WARNING -- Missing "+str(type)+" data "+str(tag) , str(barcode))
        return df_empty

    if str(type)=="TOFPET":

        if len(df_output) != 16:
            if verbose==1:
                print ( "WARNING -- Incorrect "+str(type)+" data "+"(measurements for "+str(len(df_output))+" bars) "+str(tag) , str(barcode))
            return df_empty
    
        return df_output

    if str(type)=="GALAXY_BARINARRAY":

        df_output = df_output[ df_output['BARLENGTH'].notna() ]

        if len(df_output) != 10:
            if verbose==1:
                print ( "WARNING -- Incorrect "+str(type)+" data "+"(measurements for "+str(len(df_output))+" bars) "+str(tag) , str(barcode))
            return df_empty
    
        return df_output


def SaveHisto(histo,thrmin,thrmax):

    c = R.TCanvas()

    latex = R.TLatex()
    latex.SetTextSize(0.025)
    latex.SetTextAlign(13) 

    histo.Draw()
    if(str(thrmin)!="none"):        
        linemin = R.TLine(thrmin,0.,thrmin,histo.GetMaximum())
        linemin.SetLineColor(2)
        linemin.SetLineWidth(2)
        linemin.Draw("same")

    if(str(thrmax)!="none"):        
        linemax = R.TLine(thrmax,0.,thrmax,histo.GetMaximum())
        linemax.SetLineColor(2)
        linemax.SetLineWidth(2)
        linemax.Draw("same")

    latex.DrawLatexNDC(.7,.9,"Total entries = "+str(int(histo.GetEntries())) )
    latex.DrawLatexNDC(.7,.85,"Underflow entries = "+str(int(histo.GetBinContent(0))) )
    latex.DrawLatexNDC(.7,.8,"Overflow entries = "+str(int(histo.GetBinContent(histo.GetNbinsX()+1))) )

    c.SaveAs(histo.GetName()+".pdf")

def evaluateConversionFactors(df_PMT, df_TOFPET_ARRAY):

    CF = {}

    # array LY conversion factor (a.u. --> ph/MeV)
    ly_mean_singleCrystal = df_PMT[ df_PMT['NAME'].str.contains('STP')==False ]['LO'].mean()
    ly_mean_array = df_TOFPET_ARRAY[ df_TOFPET_ARRAY['KIND_OF_PART'].str.contains('2') ]['LY'].mean()
    print(ly_mean_singleCrystal,ly_mean_array,ly_mean_singleCrystal / ly_mean_array)
    CF['LY_au_to_phMev'] = ly_mean_singleCrystal / ly_mean_array

    # LY, SIGMA_T conversion factors from type 1,3 to type 2 arrays
    df_TOFPET_ARRAY_MEAN_OVER_TYPE = df_TOFPET_ARRAY.groupby(['KIND_OF_PART'], as_index=False).mean(numeric_only=True)
    
    for var in ['LY', 'SIGMA_T']:
        type2_avg = df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains('2') ].iloc[0][var]
        for arraytype in ['1','3']:            
            array_avg = df_TOFPET_ARRAY_MEAN_OVER_TYPE[ df_TOFPET_ARRAY_MEAN_OVER_TYPE['KIND_OF_PART'].str.contains(arraytype) ].iloc[0][var]
            CF[f'{var}_t{arraytype}_to_t2'] = type2_avg / array_avg

    return CF


def applyConversion(df_TOFPET_ARRAY, CF):

    df_TOFPET_ARRAY['LY'] = df_TOFPET_ARRAY['LY'] * CF['LY_au_to_phMev']
                            
    for var in ['LY', 'SIGMA_T']:
        for arraytype in ['1','3']:
            df_TOFPET_ARRAY[var] = np.where(df_TOFPET_ARRAY['KIND_OF_PART'].str.contains(arraytype),
                               df_TOFPET_ARRAY[var] * CF[f'{var}_t{arraytype}_to_t2'],
                               df_TOFPET_ARRAY[var])

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
        df[set_index] = df[set_index].str.replace("\.0", "")

    return df

