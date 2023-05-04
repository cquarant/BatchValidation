#------------------------------------------------------------------
import pandas as mypd
import ROOT as R
R.gROOT.SetBatch(1)
import tdrstyle
tdrstyle.setTDRStyle()

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

