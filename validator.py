## Python stuff
import os
import numpy as np
from collections import defaultdict
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

pd.options.mode.chained_assignment = None  # default='warn'

# pd.set_option('display.max_rows',6)

import Functions as func

#--- Import configuraiton
from configs import config
validationSteps = config.validationSteps
tenderSpecs = config.tenderSpecs
correlationPairs = config.correlationPairs

#--- Set DEFAULTS
DEBUG = False
NBIN = 30
DEFAULTDIRIN  = f'{config.MAINDIR}/{config.DIRINVAL}/{config.DEFAULTBATCH}'
DEFAULTDIROUT = f'{config.MAINDIR}/{config.DIROUTVAL}/{config.DEFAULTBATCH}'

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

def automaticBinning(values, xmin, xmax):

        histo_std = np.std(values)

        if abs(histo_std)<0.0000000001:
                if DEBUG:
                        print(f'bin width = histo dev. std. = 0')
                        print(f'Setting nbin to default ({NBIN})')
                nbin = NBIN

        elif len(values) > 5:
                binwidth = histo_std/2
                nbin = int( float((xmax - xmin)) / binwidth ) 
        else:
                nbin = max( int(len(values)/3), 30 )

        return nbin

def plotHistogram(stepName, meas, tag, df_meas, plotdir):

        # Histogram axes settings
        meas_cfg = tenderSpecs[meas]
        m_db_name = meas_cfg['db_name']
        hist_fill = meas_cfg['histfill']
        hist_line = meas_cfg['histline']
        
        if 'legend_pos' in meas_cfg.keys():
                legend_pos=meas_cfg['legend_pos']
        else:
                legend_pos='R'

        if meas_cfg['DrawHisto'] == 'DivideByType':
                for type_i,type in enumerate(meas_cfg['type_group']):

                        if type != 'all':
                                df_meas_by_type = df_meas[ df_meas['KIND_OF_PART'].str.contains(type) ]
                        else:
                                df_meas_by_type = df_meas
                        
                        xmin_set = meas_cfg['xmin'][type_i]
                        xmax_set = meas_cfg['xmax'][type_i]

                        xmin = min( xmin_set, df_meas_by_type[m_db_name].min() )
                        xmax = max( xmax_set, df_meas_by_type[m_db_name].max() )

                        histo_mean = round(df_meas_by_type[m_db_name].mean(), 3)
                        histo_std  = round(df_meas_by_type[m_db_name].std() , 3)

                        nbin = automaticBinning( df_meas_by_type[m_db_name].tolist(), xmin, xmax )
                        xlab = meas_cfg['label']+" "+meas_cfg['unit']               
                        if type != 'all':
                                xlab += " (type #"+type+")"


                        # Filling Histogram
                        histoname = f'h1_{stepName}_{m_db_name}_{type}_{tag}'
                        histos[histoname] = df_meas_by_type.plot.hist(column=m_db_name, bins=nbin, range=[xmin,xmax], color=hist_fill[type_i], ec=hist_line)

                        t = histos[histoname].text(0.05, 0.78, f'Mean: {round(histo_mean,3)}\nStd.Dev: {round(histo_std,3)}', ha='left', rotation=0, fontsize=14, wrap=True, transform = histos[histoname].transAxes)
                        t.set_bbox(dict(facecolor='white', alpha=0.75, lw=0))

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

                plt.close('all')
        
        elif meas_cfg['DrawHisto'] == 'Overlay':

                xlab = meas_cfg['label']+" "+meas_cfg['unit']          

                xmin = min( min(meas_cfg['xmin']), df_meas[m_db_name].min() )
                xmax = max( max(meas_cfg['xmax']), df_meas[m_db_name].max() )


                plt.figure()
                text = ''
                for type_i,type in enumerate(meas_cfg['type_group']):

                        df_meas_by_type = df_meas      
                        if type != 'all':
                                df_meas_by_type = df_meas[ df_meas['KIND_OF_PART'].str.contains(type) ]
                                                       
                        nbin = automaticBinning( df_meas_by_type[m_db_name].tolist(), xmin, xmax )
                        histo_mean = round(df_meas_by_type[m_db_name].mean(), 3)
                        histo_std  = round(df_meas_by_type[m_db_name].std() , 3)
                        text += f'Mean: {histo_mean}\nStd.Dev: {histo_std}\n'

                        # Filling Histogram
                        histoname = f'h1_{stepName}_{m_db_name}_{tag}'
                        histos[histoname] = plt.hist(df_meas_by_type[m_db_name], range=[xmin,xmax], bins=nbin, color=hist_fill[type_i], ec=hist_line[type_i], lw=0.5, alpha=0.5,
                                                            label=f'{meas} type {type}')
                
                # Draw Histogram
                plt.xlabel(xlab)
                plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
                plt.legend(loc='upper right')

                for type_i,type in enumerate(meas_cfg['type_group']):
                        thr_min = meas_cfg['thr'][type_i][0]
                        thr_max = meas_cfg['thr'][type_i][1]
                        if thr_min > xmin:
                                plt.axvline(thr_min, color='red', linestyle='--')
                        if thr_max < xmax:
                                plt.axvline(thr_max, color='red', linestyle='--')

                plt.savefig(f'{plotdir}/{histoname}_overlayed.png')

                plt.close('all')

        elif meas_cfg['DrawHisto'] == 'Stack':

                xlab = meas_cfg['label']+" "+meas_cfg['unit']          

                xmin = min( min(meas_cfg['xmin']), df_meas[m_db_name].min() )
                xmax = max( max(meas_cfg['xmax']), df_meas[m_db_name].max() )

                nbin = automaticBinning( df_meas[m_db_name].tolist(), xmin, xmax )

                fig = plt.figure()
                fig, ax = plt.subplots()
                text = ''
                histo_values_list = []
                labels = []
                for type_i,type in enumerate(meas_cfg['type_group']):

                        df_meas_by_type = df_meas      
                        if type != 'all':
                                df_meas_by_type = df_meas[ df_meas['KIND_OF_PART'].str.contains(type) ]

                        histo_values_list.append(df_meas_by_type[m_db_name].tolist())
                        labels.append(f'{meas} type {type}')
                        histo_mean = round(df_meas_by_type[m_db_name].mean(), 3)
                        histo_std  = round(df_meas_by_type[m_db_name].std() , 3)
                        text += f'Mean (type {type}): {histo_mean}\nStd.Dev: {histo_std}\n'

                        
                # Filling Histogram
                histoname = f'h1_{stepName}_{m_db_name}_{tag}'
                xh,yh,histos[histoname] = plt.hist(histo_values_list, range=[xmin,xmax], bins=nbin, color=hist_fill, ec=hist_line, lw=0.5, stacked=True,
                                                label=labels)
                                 
                # Draw Histogram
                plt.xlabel(xlab)
                plt.grid(True, linestyle='--', color='gray', linewidth=0.5)
                
                if legend_pos == 'R':
                        plt.legend(loc='upper right')
                        t = plt.text(0.6,0.45, text, ha='left', va='bottom', fontsize=11, rotation=0, wrap=True, transform = ax.transAxes)
                else:
                        plt.legend(loc='upper left')
                        t = plt.text(0.03,0.45, text, ha='left', va='bottom', fontsize=11, rotation=0, wrap=True, transform = ax.transAxes)

                ax_list = fig.axes
                t.set_bbox(dict(facecolor='white', alpha=0.75, lw=0))

                # limit y range when entry number is low
                # if yh.max() < 3:
                #         plt.ylim([0,3])

                for type_i,type in enumerate(meas_cfg['type_group']):
                        thr_min = meas_cfg['thr'][type_i][0]
                        thr_max = meas_cfg['thr'][type_i][1]
                        if thr_min > xmin:
                                plt.axvline(thr_min, color='red', linestyle='--')
                        if thr_max < xmax:
                                plt.axvline(thr_max, color='red', linestyle='--')

                plt.savefig(f'{plotdir}/{histoname}_stacked.png')

                plt.close('all')


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

def correlationPlot( pairName, xval, yval, xlab, ylab, plotdir, xrange, yrange ):
        plt.scatter(xval,yval)

        plt.xlabel(xlab)
        plt.ylabel(ylab)
        plt.grid(True, linestyle='--', color='gray', linewidth=0.5)

        m, b = np.polyfit(xval, yval, 1)        
        xseq = np.linspace(min(xval), max(xval), num=100)

        from scipy.stats import pearsonr
        corr, _ = pearsonr(xval, yval)
        
        plt.plot(xseq, b + m * xseq, color="red", lw=2.5, linestyle='--');

        # Use plt.legend to automatically place text in plot
        text1 = "slope: {:.3e}".format(m)
        text2 = f"offset: {round(b,3)}"
        text3 = f"Pears. r: {round(corr,3)}"
        # text = text1 + '\n' + text2 + '\n' + text3
        text = text1 + '\n' +text2+'\n' + text3

        # Create an empty plot with the required text.
        plt.plot([], label=text)
        plt.xlim(xrange)
        plt.ylim(yrange)
        # Remove the handle from the legend box.
        plt.legend(handlelength=0)

        plt.savefig(f'{plotdir}/{pairName}_correlation.png')
        plt.close()

#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#
#  _    _ _______        _____ ______  _______ _______  _____   ______ #
#   \  /  |_____| |        |   |     \ |_____|    |    |     | |_____/ #
#    \/   |     | |_____ __|__ |_____/ |     |    |    |_____| |    \_ #
#                                                                      #
#°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°#

histos = {}
summary_df = {}
def runValidation(dirin=DEFAULTDIRIN,dirout=DEFAULTDIROUT, outputfilename=f'results_{config.DEFAULTBATCH}.txt', batch=config.DEFAULTBATCH):

        if not os.path.isdir(dirin):                
                os.system(f'Missing analyzed data for {batch}. Run the analysis step:\n\tpython3 Validate.py --analysis --batch XXX')
        if DEBUG:
                print(f'\n Input directory {dirin}')

        plotdir = f'{dirout}/{config.PLOTDIR}'
        if not os.path.isdir(dirout):
                os.system(f'mkdir -p {dirout}')
        if not os.path.isdir(plotdir):
                os.system(f'mkdir -p {plotdir}')

        print('\n\n#######################################################')
        print(f'\t Running VALIDATION for {batch}')

        outputfile = open(f'{dirout}/{outputfilename}', 'w')

        for stepName in validationSteps:

                print(f'\n\t Validation step: {stepName}')

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
                        if DEBUG:
                                print(df_meas)
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

                                m_db_name = tenderSpecs[m]['db_name']
                                summary_df_step[f'pass_{m_db_name}'] = fillSummaryCol( summary_df_step, df_meas_filtered, m )

                                # Create and draw histogram
                                plotHistogram(stepName, m, tag, df_meas_filtered, plotdir)

                        writeReportTXT( stepConf, tag, summary_df_step, outputfile )

                        # Include plots in html to be shown on browser
                        writeHTML(stepName, tag, plotdir)

        #--- Close result file
        outputfile.close()

def makeCorrelationPlots(dirin=DEFAULTDIRIN,dirout=DEFAULTDIROUT):

        corrplotdir = f'{dirout}/{config.CORRPLOTDIR}'
        if not os.path.isdir(corrplotdir):
                os.system(f'mkdir -p {corrplotdir}')

        for pairName in correlationPairs:

                print('Correlation plot: '+pairName)

                pair = correlationPairs[pairName]
                dfx = func.loadDataFrame(f'{dirin}/'+pair['dfx'])
                dfy = func.loadDataFrame(f'{dirin}/'+pair['dfy'])
                colx = pair['colx']+"_X"
                coly = pair['coly']+"_Y"

                if 'tag' in pair:
                        dfx = dfx[ dfx['NAME'].str.match('.*'+pair['tag']+'$')]
                        dfy = dfy[ dfy['NAME'].str.match('.*'+pair['tag']+'$')]

                if 'tagx' in pair:
                        dfx = dfx[ dfx['NAME'].str.match('.*'+pair['tagx']+'$')]
                if 'tagy' in pair:
                        dfy = dfy[ dfy['NAME'].str.match('.*'+pair['tagy']+'$')]
                        
                dfx = dfx.add_suffix('_X')
                dfy = dfy.add_suffix('_Y')

                # remove outlier caused by typos in STP file
                # dfx = dfx[ abs( (dfx[colx] - dfx[colx].mean()) / dfx[colx].std() ) < 2 ]
                # dfy = dfy[ abs( (dfy[coly] - dfy[coly].mean()) / dfy[coly].std() ) < 2 ]

                df_merged = dfx.merge(dfy, how='inner', left_on='BARCODE_X', right_on='BARCODE_Y') 

                
                if pair['type'] != 'all':
                        dfx = dfx[ dfx['KIND_OF_PART_X'].str.contains(pair['type']) ]
                        dfy = dfy[ dfy['KIND_OF_PART_Y'].str.contains(pair['type']) ]

                xmin_ = dfx[colx].min() - (dfx[colx].max()-dfx[colx].min())*0.1
                xmax_ = dfx[colx].max() + (dfx[colx].max()-dfx[colx].min())*0.1
                ymin_ = dfy[coly].min() - (dfy[coly].max()-dfy[coly].min())*0.1
                ymax_ = dfy[coly].max() + (dfy[coly].max()-dfy[coly].min())*0.1

                if 'xmin' in pair:
                        xmin_ = pair['xmin']
                if 'xmax' in pair:
                        xmax_ = pair['xmax']
                if 'ymin' in pair:
                        ymin_ = pair['ymin']
                if 'ymax' in pair:
                        ymax_ = pair['ymax']

                xrange_ = [xmin_,xmax_]
                yrange_ = [ymin_,ymax_]

                correlationPlot( pairName, df_merged[colx], df_merged[coly], xlab=pair['xlab'], ylab=pair['ylab'], plotdir=corrplotdir, xrange=xrange_, yrange=yrange_)
