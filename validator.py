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

pd.set_option('display.max_rows',3)

import Functions as func

#--- Set DEFAULTS
DIRIN = 'analyzed_data'
PLOTDIR = "plot"

#--- Import configuraiton
from configs import config
validationSteps = config.validationSteps
tenderSpecs = config.tenderSpecs

# Filter by run tag (row-wise) and for relevant columns
def filterDataFrame(df_meas, columns, runtag):
        df_meas_filtered = df_meas[ columns ]
        df_meas_filtered = df_meas_filtered[ df_meas_filtered['NAME'].str.match( runtag + '$') ]
        return df_meas_filtered


def checkThreshold( df_meas, colname, thr_min, thr_max, type ):
        if type == 'all':                
                summary_col = np.where( df_meas[colname].between(thr_min,thr_max), True, False )
        else:
                summary_col = np.where( ~df_meas['KIND_OF_PART'].str.contains(type) | (df_meas[colname].between(thr_min,thr_max)), True, False )
        return summary_col


def fillSummaryCol( summary_df, df_meas, meas ):

        summary_df_tmp = summary_df.copy()
        meas_cfg = tenderSpecs[meas]
        m_db_name = meas_cfg['db_name']

        for type_i,type in enumerate(meas_cfg['type_group']):
                                        
                thr_min = meas_cfg['thr'][type_i][0]
                thr_max = meas_cfg['thr'][type_i][1]

                summary_df_tmp[f'pass_{m_db_name}_{type}'] = checkThreshold(df_meas, m_db_name, thr_min, thr_max, type)

                if type_i == 0:
                        summary_df_tmp[f'pass_{m_db_name}'] = summary_df_tmp[f'pass_{m_db_name}_{type}']           
                else:
                        summary_df_tmp[f'pass_{m_db_name}'] = summary_df_tmp[f'pass_{m_db_name}'] & summary_df_tmp[f'pass_{m_db_name}_{type}']
                

        return summary_df_tmp[f'pass_{m_db_name}']


def plotHistogram(stepName, meas, tag, df_meas, plotdir):

        # Histogram axes settings
        meas_cfg = tenderSpecs[meas]
        m_db_name = meas_cfg['db_name']
        hist_fill = meas_cfg['histfill']
        hist_line = meas_cfg['histline']

        for type_i,type in enumerate(meas_cfg['type_group']):

                if type != 'all':
                        df_meas_by_type = df_meas[ df_meas['KIND_OF_PART'].str.contains(type) ]
                else:
                        df_meas_by_type = df_meas
                
                xmin_l = meas_cfg['xmin']
                xmax_l = meas_cfg['xmax']

                if len(xmin_l)==1:
                        xmin_set = xmin_l[0]
                elif len(xmin_l)==len(meas_cfg['type_group']):
                        xmin_set = xmin_l[type_i]
                else:
                        print(f"ERROR len(xmin list) should be 1 instead of {len(xmin_l)} or the same as type group list for {stepName}, {meas}")

                if len(xmax_l)==1:
                        xmax_set = xmax_l[0]
                elif len(xmax_l)==len(meas_cfg['type_group']):
                        xmax_set = xmax_l[type_i]
                else:
                        print(f"ERROR len(xmax list) should be 1 or the same as type group list for {stepName}")


                xmin = min( xmin_set, df_meas_by_type[m_db_name].min() )
                xmax = max( xmax_set, df_meas_by_type[m_db_name].max() )
                if len(df_meas_by_type[m_db_name]) > 5:
                        histo_std = df_meas_by_type[m_db_name].std()
                        binwidth = histo_std/2
                        nbin = int( float((xmax - xmin)) / binwidth ) 
                else:
                        nbin = max( int(len(df_meas_by_type.index)/3), 10 )
                xlab = meas_cfg['label']+" "+meas_cfg['unit']

                type = meas_cfg['type_group'][type_i]
                
                if type != 'all':
                        xlab += " (type #"+type+")"

                histoname = f'h1_{stepName}_{m_db_name}_{type}_{tag}'
                # Filling Histogram
                histos[histoname] = df_meas_by_type.plot.hist(column=m_db_name, bins=nbin, range=[xmin,xmax], color=hist_fill, ec=hist_line)

                # Draw Histogram
                histos[histoname].set_xlabel(xlab)
                histos[histoname].grid(True, linestyle='--', color='gray', linewidth=0.5)

                thr_min = meas_cfg['thr'][type_i][0]
                thr_max = meas_cfg['thr'][type_i][1]
                if thr_min > xmin:
                        histos[histoname].axvline(thr_min, color='red', linestyle='--')
                if thr_max < xmax:
                        histos[histoname].axvline(thr_max, color='red', linestyle='--')

                histos[histoname].get_figure().savefig(f'{plotdir}/{histoname}.png')

        plt.pyplot.close('all')


def writeReportTXT(stepConf, tag, summary_df, outputfile):

        outputfile.write("\n")
        outputfile.write("##############################################################"+"\n")
        outputfile.write( str(stepConf['title'] +"  "+tag).ljust(60)+"\n")
        outputfile.write("##############################################################"+"\n")    
        outputfile.write("\n")
        outputfile.write("Number of parts measured: "+str( len(summary_df) )+"\n" )
        outputfile.write("\n")

        if len(summary_df)==0:
                outputfile.write("\n")
                outputfile.write("No measurements to analyze\n")
                return 0

        for m in stepConf['meas']:
                meas_cfg = tenderSpecs[m]
                m_db_name = meas_cfg['db_name']
                col = f'pass_{m_db_name}'
                xlab = meas_cfg['label']+" "+meas_cfg['unit']
        
                outputfile.write(f"{xlab.ljust(25)}"+" ==> Pass : "+str( round(100*len(summary_df[summary_df[col]==True]) / len(summary_df), 1) )+" % \n" )

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


def writeHTML(stepName, tag, plotdir):

        stepConf = validationSteps[stepName]

        index = open(f"{plotdir}/index_{stepName}_{tag}.html", "w")
        index.write("<!DOCTYPE html>\n")
        index.write("<html lang=\"en\">\n")
        
        index.write("<head>\n")
        index.write(f"  <title>Batch validation {stepName}</title>\n")
        index.write("</head>\n")
        
        
        index.write("<body>\n")

        for meas in stepConf['meas']:

                meas_cfg = tenderSpecs[meas]
                m_db_name = meas_cfg['db_name']

                for type in meas_cfg['type_group']:

                        histoname = f'h1_{stepName}_{m_db_name}_{type}_{tag}'
                        index.write(f"<img src=\"{histoname}.png\" alt=\"\" >\n")

                index.write("<br>\n")

        index.write("</body>\n")
        index.write("</html>\n")
        index.close()



#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#
#  _    _ _______        _____ ______  _______ _______  _____   ______ #
#   \  /  |_____| |        |   |     \ |_____|    |    |     | |_____/ #
#    \/   |     | |_____ __|__ |_____/ |     |    |    |_____| |    \_ #
#                                                                      #
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#

histos = {}
summary_df = {}
def runValidation(dirin=DIRIN,plotdir=PLOTDIR, outputfilename='results.txt'):

        outputfile = open(outputfilename, 'w')
        
        for stepName in validationSteps:

                stepConf = validationSteps[stepName]
         
                runformat = stepConf['runformat']
                df_file = stepConf['df_file']
                df_meas = func.loadDataFrame(f'{dirin}/{df_file}')

                # Lists with relevant columns
                run_info = stepConf['run_info_col']
                meas_list = stepConf['meas']

                meas_db_names = []
                for meas in meas_list:
                        meas_db_names.append(tenderSpecs[meas]['db_name'])
                columns = run_info + meas_db_names

                for tag in stepConf['tag']:

                        # filtering out columns not relevant for validation and filtering by run tag
                        runtag = runformat+tag
                        df_meas_filtered = filterDataFrame(df_meas, columns, runtag)

                        print(df_meas_filtered)

                        # Create summary dataframe (initialized)
                        summary_name = f'{stepName}_{tag}'
                        summary_df[summary_name] = df_meas_filtered[ run_info ]
                        summary_df_step = summary_df[summary_name]
                        
                        if len(summary_df)==0:
                                continue
                        
                        # Check if part pass MTD requirements for measurement m
                        # (if type_sel != None then apply only to parts of selected type)
                        for m in meas_list:

                                print(f'\n\nAnalyzing {stepName}, {tag}, {m}\n\n')

                                m_db_name = tenderSpecs[m]['db_name']
                                summary_df_step[f'pass_{m_db_name}'] = fillSummaryCol( summary_df_step, df_meas_filtered, m )

                                # Create and draw histogram
                                if tenderSpecs[m]['DrawHisto'] == True:
                                        plotHistogram(stepName, m, tag, df_meas_filtered, plotdir)

                        writeReportTXT( stepConf, tag, summary_df_step, outputfile )

                        # Include plots in html to be shown on browser
                        writeHTML(stepName, tag, plotdir)

        #--- Close result file
        outputfile.close()
        

