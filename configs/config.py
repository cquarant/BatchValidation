# DEFAULT IN/OUT DIRS

MAINDIR = 'LYSO_VALIDATION'
DIRCONFIG = 'configs'
DIRDUMP = 'dbdata'
DIRINANALYSIS  = 'dbdata'
DIROUTANALYSIS = 'analyzed_data'
DIRINVAL = 'analyzed_data'
DIROUTVAL = 'results'
PLOTDIR = 'plot'
CORRPLOTDIR = 'correlationPlots'
REPORTDIR = 'report'
DEFAULTBATCH = 'all'


omsData = {

    ### for more details on MTD database see https://cmsdca.cern.ch/mtd_rhapi/table/mtd_cmsr/

    'SINGLEBARS' : { 'query' : "select p.BARCODE,p.KIND_OF_PART,p.BATCH_NUMBER,c1.BATCH_INGOT_DATA,p2.AINGOT_REGION "
                               "from mtd_cmsr.parts p "
                               "left join mtd_cmsr.c2600 c1 on p.BARCODE=c1.PART_BARCODE "
                               "left join mtd_cmsr.p3040 p2 on p.BARCODE=p2.BARCODE " # p3040=table for singleCrystal #2
                               "where (p.BATCH_NUMBER like 'A69%' and p.KIND_OF_PART like 'singleCrystal%') ",
                            #    " ORDER BY p.BARCODE asc ;",
                               #"where p.LOCATION_ID = 4980 and p.KIND_OF_PART like 'singleCrystal%'",
                     'filecsv' : 'data_SINGLEBARS.csv',
                     'index': 'BARCODE',
                 },

    'ARRAYS'     : { 'query' : "select p.BARCODE,p.KIND_OF_PART,p.BATCH_NUMBER,c1.BATCH_INGOT_DATA, CONCAT( CONCAT( CONCAT(p4.AINGOT_REGION, p5.AINGOT_REGION), p6.AINGOT_REGION), p7.AINGOT_REGION) AS AINGOT_REGION "
                               " from mtd_cmsr.parts p "
                               "left join mtd_cmsr.c2600 c1 on p.BARCODE=c1.PART_BARCODE "
                               "left join mtd_cmsr.p4 p4 on p.BARCODE=p4.BARCODE " # p4=table for LYSO Matrix #1
                               "left join mtd_cmsr.p5 p5 on p.BARCODE=p5.BARCODE " # p5=table for LYSO Matrix #2
                               "left join mtd_cmsr.p6 p6 on p.BARCODE=p6.BARCODE " # p6=table for LYSO Matrix #3
                               "left join mtd_cmsr.p1080 p7 on p.BARCODE=p7.BARCODE " # p6=table for RefArray #2
                               "where p.BATCH_NUMBER like 'A69%' and (p.KIND_OF_PART like 'LYSOMatrix%' or p.KIND_OF_PART like 'RefArray%') ",
                               #"where p.LOCATION_ID = 4980 and (p.KIND_OF_PART like 'LYSOMatrix%' or p.KIND_OF_PART like 'RefArray%')",
                            #    "order by p.BARCODE ",
                     'filecsv' : 'data_ARRAYS.csv',
                     'index'   : 'BARCODE',
                 },

    'TOFPET'     : { 'query' : "select c1.PART_BARCODE, r.NAME, r.BEGIN_DATE, "
                               "c1.XTLEFT, c1.XTRIGHT, c1.LY, c1.LY_NORM, c1.SIGMA_T, c1.SIGMA_T_NORM "
                               #"c1.CTR, c1.CTR_NORM, c1.TEMPERATURE "
                               "from mtd_cmsr.parts p "
                               "left join mtd_cmsr.c1400 c1 on c1.PART_BARCODE = p.BARCODE "
                               "left join mtd_cmsr.datasets ds on (ds.ID = c1.CONDITION_DATA_SET_ID) "
                               "left join mtd_cmsr.runs r on (r.ID = ds.RUN_ID) "
                               "where p.BATCH_NUMBER like 'A69%' ",
                               #"where p.LOCATION_ID = 4980",
                            #    "order by p.PART_BARCODE ",
                     'filecsv' : 'data_TOFPET.csv',
                     'index'   : 'PART_BARCODE',
                 },

    'PMT'        : { 'query' : "select c2.PART_BARCODE, r.NAME, r.BEGIN_DATE, "
                               "c2.LY_ABS, c2.LY_NORM as LY_NORMAL, c2.DECAY_TIME "
                               #"c2.B_RMS, c2.B_3S_ASYM, c2.B_2S_ASYM "
                               "from mtd_cmsr.parts p "
                               "left join mtd_cmsr.c1420 c2 on c2.PART_BARCODE = p.BARCODE "
                               "left join mtd_cmsr.datasets ds on (ds.ID = c2.CONDITION_DATA_SET_ID) "
                               "left join mtd_cmsr.runs r on (r.ID = ds.RUN_ID) "
                               "where p.BATCH_NUMBER like 'A69%' ",
                            #    "order by p.PART_BARCODE ",
                               #"where p.LOCATION_ID = 4980",
                     'filecsv' : 'data_PMT.csv',
                     'index'   : 'PART_BARCODE',
                 },

    'GALAXY'     : { 'query' : "select c3.PART_BARCODE, r.NAME, r.BEGIN_DATE, c3.BARLENGTH, "
                               "c3.BARLENGTH_STD, c3.LMAXVAR_LS, c3.LMAXVAR_LN, c3.L_MAX, c3.L_MEAN, c3.L_MEAN_STD, c3.WMAXVAR_LO, "
                               "c3.WMAXVAR_LE, c3.W_MAX, c3.W_MEAN, c3.W_MEAN_STD, c3.TMAXVAR_FS, c3.TMAXVAR_FS_STD, c3.T_MAX, c3.T_MEAN, "
                               "c3.T_MEAN_STD, c3.LMAXVAR_LS_STD, c3.LMAXVAR_LN_STD, c3.WMAXVAR_LO_STD, c3.WMAXVAR_LE_STD "
                               # "c3.T_STD_MITU, c3.LMAXVAR_LS_STD, c3.LMAXVAR_LN_STD, c3.WMAXVAR_LO_STD, c3.WMAXVAR_LE_STD, "
                               # "c3.L_MEAN_MITU, c3.L_STD_MITU, c3.W_MEAN_MITU, c3.W_STD_MITU, c3.T_MEAN_MITU, "
                               "from mtd_cmsr.parts p "
                               "left join mtd_cmsr.c3400 c3 on c3.PART_BARCODE = p.BARCODE "
                               "left join mtd_cmsr.datasets ds on (ds.ID = c3.CONDITION_DATA_SET_ID) "
                               "left join mtd_cmsr.runs r on (r.ID = ds.RUN_ID) "
                               "where p.BATCH_NUMBER like 'A69%' ",
                            #    "order by p.PART_BARCODE ",
                               #"where p.LOCATION_ID = 4980",
                     'filecsv' : 'data_GALAXY.csv',
                     'index'   : 'PART_BARCODE',
                 },
    # 'CALIBER'    : {                  
    #                  'filecsv' : 'data_CALIBER.csv',
    #                  'location': 'EXTERNAL_DATA',
    #                  'index'   : 'BARCODE',
    #                 },
}

#---------------------------------------------------------
#-------- Configuration of Validation steps


validationSteps = {

    ###########################################################################
    ##         ___                      _ _    _      _   _                  ##
    ##        | _ ) __ _ _ _  __ ____ _| (_)__| |__ _| |_(_)___ _ _          ##
    ##        | _ \/ _` | '_| \ V / _` | | / _` / _` |  _| / _ \ ' \         ##
    ##        |___/\__,_|_|    \_/\__,_|_|_\__,_\__,_|\__|_\___/_||_|        ##
    ##                                                                       ##
    ###########################################################################
                                                        
    "GALAXY_SINGLEBAR": {
        'title'  : 'Validation of SINGLE XTAL dimensions',
        'tag'    : ['PREIRR'],
        'meas'   : ['L_MEAN_SINGLEBAR', 'W_MEAN_SINGLEBAR','T_MEAN_SINGLEBAR'], #RSTD = relative standard deviation 
        'df_file': 'data_GALAXY_SINGLEBAR.csv',
        'run_info_col' : ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_BAR\d{3,14}_',
    },

    "PMT_SINGLEBAR": {
        'title'  : 'Validation of SINGLE XTAL optical properties',
        'tag'    : ['PREIRR_0'],
        'meas'   : ['LO','DT','LOoverDT','LO_RSTD','DT_RSTD','LOoverDT_RSTD','LY_NORM','LOoverDT_NORM','LOscaled','LOoverDTscaled'], #RSTD = relative standard deviation 
        'df_file': 'data_PMT.csv',
        'run_info_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : '(Run_LO_)?BAR\d{3,14}_',
    },

    "PMT_SINGLEBAR-STP": {
        'title'  : 'Validation of SINGLE XTAL optical properties (STP)',
        'tag'    : ['STP_PREIRR'],
        'meas'   : ['LO','DT','LOoverDT','LO_RSTD','DT_RSTD','LOoverDT_RSTD'], #RSTD = relative standard deviation 
        'df_file': 'data_PMT.csv',
        'run_info_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : '(Run_LO_)?BAR\d{3,14}_',
    },

    "PMT_SINGLEBAR_POSTIRR": {
        'title'  : 'Validation of SINGLE XTAL optical properties after Irradiation',
        'tag'    : ['POSTIRR_0'],
        'meas'   : ['LY_NORMAL_REL_VARIATION','DT_REL_VARIATION','LOoverDT_REL_VARIATION'], #RSTD = relative standard deviation 
        'df_file': 'data_PMT_POSTIRR.csv',
        'run_info_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : '(Run_LO_)?BAR\d{3,14}_',
    },


    ###########################################################################
    ##      _                                _ _    _      _   _             ##
    ##     /_\  _ _ _ _ __ _ _  _  __ ____ _| (_)__| |__ _| |_(_)___ _ _     ##
    ##    / _ \| '_| '_/ _` | || | \ V / _` | | / _` / _` |  _| / _ \ ' \    ##
    ##   /_/ \_\_| |_| \__,_|\_, |  \_/\__,_|_|_\__,_\__,_|\__|_\___/_||_|   ##
    ##                       |__/                                            ##
    ###########################################################################

    # "CALIBER_ARRAY": {
    #     'title'  : 'Validation of ARRAY dimensions measured with CALIBER',
    #     'tag'    : ['CALIBER'],
    #     'meas'   : ["L_MAX","W_MAX","T_MAX"], 
    #     'df_file': 'data_CALIBER_ARRAY.csv',
    #     'run_info_col': ['BARCODE','KIND_OF_PART','NAME'],
    #     'runformat' : 'Run\d{6}_ARRAY_\d{3,14}_',
    # },

    "GALAXY_ARRAY": {
        'title'  : 'Validation of ARRAY dimensions',
        'tag'    : ['PREIRR'],
        'meas'   : ["L_MAX","L_MEAN","LMAXVAR","LMAXVAR_LN_STD","LMAXVAR_LS_STD","W_MAX","W_MEAN","T_MAX","T_MEAN"], 
        'df_file': 'data_GALAXY_ARRAY.csv',
        'run_info_col': ['BARCODE','KIND_OF_PART','NAME'],
        'runformat' : '(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_',
    },

    "GALAXY_ARRAY-STP": {
        'title'  : 'Validation of ARRAY dimensions',
        'tag'    : ['STP_PREIRR'],
        'meas'   : ["L_MAX-STP","W_MAX-STP","T_MAX-STP"], 
        'df_file': 'data_GALAXY_ARRAY.csv',
        'run_info_col': ['BARCODE','KIND_OF_PART','NAME'],
        'runformat' : '(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_',
    },

    "GALAXY_BARINARRAY" : {
        'title'  : 'Validation of XTALS IN ARRAY dimensions',
        'tag'    : ['PREIRR'],
        'meas'   : ["BARLENGTH"],
        'df_file': 'data_GALAXY_BARINARRAY.csv',
        'run_info_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : '(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_',
    },    

    "TOFPET_ARRAY" : {
        'title'  : 'Validation of ARRAY optical properties',
        'tag' : ['PREIRR'],
        'meas': ['LY_MEAN','LY_RSTD','SIGMA_T_MEAN','SIGMA_T_RSTD','XT_MEAN','XT_STD'],
        'df_file': 'data_TOFPET_ARRAY.csv',
        'run_info_col' : ['PARENT_ARRAY','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_',
    },

    "TOFPET_BARINARRAY" : {
        'title'  : 'Validation of XTALS IN ARRAY optical properties',
        'tag' : ['PREIRR'],
        'meas': ['LY','SIGMA_T','XT'],
        'df_file': 'data_TOFPET_BARINARRAY.csv',
        'run_info_col' : ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_',
    },

    "TOFPET_ARRAY-GREASE" : {
        'title'  : 'Validation of ARRAY optical properties (grease coupling)',
        'tag' : ['PREIRR-GR'],
        'meas': ['LY_MEAN-GR','LY_RSTD-GR','SIGMA_T_MEAN-GR','SIGMA_T_RSTD-GR','XT_MEAN-GR','XT_STD-GR'],
        'df_file': 'data_TOFPET_ARRAY.csv',
        'run_info_col' : ['PARENT_ARRAY','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_',
    },

    "TOFPET_BARINARRAY-GREASE" : {
        'title'  : 'Validation of XTALS IN ARRAY optical properties (grease coupling)',
        'tag' : ['PREIRR-GR'],
        'meas': ['LY-GR','SIGMA_T-GR','XT-GR'],
        'df_file': 'data_TOFPET_BARINARRAY.csv',
        'run_info_col' : ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_',
    },

    "TOFPET_ARRAY_POSTIRR": {
        'title'  : 'Validation of ARRAY optical properties after Irradiation (dry coupling)',
        'tag'    : ['POSTIRR'],
        'meas': ['LY_MEAN-POSTIRR','SIGMA_T_MEAN-POSTIRR','XT_MEAN-POSTIRR','LY_MEAN_REL_VARIATION','SIGMA_T_MEAN_REL_VARIATION','XT_MEAN_REL_VARIATION'],
        'df_file': 'data_TOFPET_ARRAY_POSTIRR.csv',
        'run_info_col': ['BARCODE','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_',
    },

    "TOFPET_BARINARRAY_POSTIRR": {
        'title'  : 'Validation of ARRAY optical properties after Irradiation (dry coupling)',
        'tag'    : ['POSTIRR'],
        'meas': ['LY-POSTIRR','SIGMA_T-POSTIRR','XT','LY_REL_VARIATION','SIGMA_T_REL_VARIATION'],
        'df_file': 'data_TOFPET_BARINARRAY_POSTIRR.csv',
        'run_info_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_',
    },

    "TOFPET_ARRAY_POSTIRR-GR": {
        'title'  : 'Validation of ARRAY optical properties after Irradiation (grease coupling)',
        'tag'    : ['POSTIRR-GR'],
        'meas': ['LY_MEAN-POSTIRR-GR','SIGMA_T_MEAN-POSTIRR-GR','XT_MEAN-POSTIRR-GR','LY_MEAN_REL_VARIATION-GR','SIGMA_T_MEAN_REL_VARIATION-GR'],
        'df_file': 'data_TOFPET_ARRAY_POSTIRR-GR.csv',
        'run_info_col': ['BARCODE','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_',
    },

    "TOFPET_BARINARRAY_POSTIRR-GR": {
        'title'  : 'Validation of ARRAY optical properties after Irradiation (dry coupling)',
        'tag'    : ['POSTIRR-GR'],
        'meas': ['LY-POSTIRR-GR','SIGMA_T-POSTIRR-GR','XT-GR','LY_REL_VARIATION-GR','SIGMA_T_REL_VARIATION-GR'],
        'df_file': 'data_TOFPET_BARINARRAY_POSTIRR-GR.csv',
        'run_info_col': ['PART_BARCODE','KIND_OF_PART','NAME'],
        'runformat' : 'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_',
    },


    ###########################################################################
    ##     ___               _              _ _    _      _   _              ##
    ##    |_ _|_ _  __ _ ___| |_  __ ____ _| (_)__| |__ _| |_(_)___ _ _      ##
    ##     | || ' \/ _` / _ \  _| \ V / _` | | / _` / _` |  _| / _ \ ' \     ##
    ##    |___|_||_\__, \___/\__|  \_/\__,_|_|_\__,_\__,_|\__|_\___/_||_|    ##
    ##             |___/                                                     ##
    ###########################################################################

    "PMT_INGOT": {
        'title'  : 'INGOT optical properties (average over single bars)',
        'tag'    : ['STP_PREIRR','PREIRR_0'],#,'POSTIRR_0'],
        'meas'   : ['LO_MEAN','DT_MEAN','LOoverDT_MEAN'], #RSTD = relative standard deviation 
        'df_file': 'data_PMT_INGOT.csv',
        'run_info_col': ['BATCH_INGOT_DATA','NAME'],
        'runformat' : 'TL\d{3}_',
    },

}


# Measurements to be checked
tenderSpecs = {
    # Single xtal dimensions 
    "L_MEAN_SINGLEBAR"   : {'db_name': 'L_MEAN'   , 'xmin':[54.6], 'xmax':[54.8], 'thr':[[54.67,54.73]], 'label':'Single Xtal Length'       , 'unit':'[mm]'   , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['salmon'], 'histline':'darkred'},
    "W_MEAN_SINGLEBAR"   : {'db_name': 'W_MEAN'   , 'xmin':[3.05], 'xmax':[3.20], 'thr':[[ 3.09, 3.15]], 'label':'Single Xtal Width'        , 'unit':'[mm]'   , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['salmon'], 'histline':'darkred'},
    "T_MEAN_SINGLEBAR"   : {'db_name': 'T_MEAN'   , 'xmin':[2.95], 'xmax':[3.05], 'thr':[[ 2.97, 3.03]], 'label':'Single Xtal Thickness'    , 'unit':'[mm]'   , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['salmon'], 'histline':'darkred'},
   
    # Single xtal optical properties
    "LO"       : {'db_name': 'LO'       , 'xmin':[3750], 'xmax':[7000], 'thr':[[4000,999999]], 'label':'Single Xtal Light Output', 'unit':'[ph/MeV]'   , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "DT"       : {'db_name': 'DECAY_TIME', 'xmin':[30] , 'xmax':[50]  , 'thr':[[-1, 45]     ], 'label':'Decay Time'              , 'unit':'[ns]'       , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "LOoverDT" : {'db_name': 'LOoverDT' , 'xmin':[80]  , 'xmax':[160] , 'thr':[[105,9999999]], 'label':'LO/DT'                   , 'unit':'[ph/MeV/ns]', 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "LO_RSTD"  : {'db_name': 'LO_RSTD'  , 'xmin':[0.00], 'xmax':[15.0], 'thr':[[-1, 10]     ], 'label':'LO relative std. dev.'   , 'unit':'(%)'        , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "LY_NORM"  : {'db_name': 'LY_NORMAL', 'xmin':[0.95], 'xmax':[1.05], 'thr':[[-10,10]     ], 'label':'Array Light Output norm' , 'unit':''           , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "LOscaled" : {'db_name': 'LOscaledToRef' , 'xmin':[3750], 'xmax':[7000], 'thr':[[4000,999999]], 'label':'Array Light Output ' , 'unit':''           , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "LOoverDT_NORM"  : {'db_name': 'LOoverDT_NORM', 'xmin':[0.95], 'xmax':[1.05], 'thr':[[-10,10]], 'label':'Array LO/DT norm'   , 'unit':''           , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "LOoverDTscaled" : {'db_name': 'LOoverDTscaledToRef', 'xmin':[80], 'xmax':[1.60], 'thr':[[105,99999]], 'label':'Array LO/DT '   , 'unit':''           , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "DT_RSTD"  : {'db_name': 'DECAY_TIME_RSTD'  , 'xmin':[0.00], 'xmax':[15.00], 'thr':[[-1,5]], 'label':'DT relative std. dev.'   , 'unit':'(%)'        , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    "LOoverDT_RSTD": {'db_name': 'LOoverDT_RSTD', 'xmin':[0.00], 'xmax':[15.00], 'thr':[[-1,5]], 'label':'LO/DT relative std. dev.', 'unit':'(%)'        , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},

    # Ingot PMT optical properties
    "LO_MEAN"       : {'db_name': 'LO_MEAN'       , 'xmin':[3750] , 'xmax':[7000] , 'thr':[[-1,999999]], 'label':'LO (ingot)'   , 'unit':'[ph/MeV]'   , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['violet'], 'histline':'darkgoldenrod'},
    "DT_MEAN"       : {'db_name': 'DECAY_TIME_MEAN', 'xmin':[30]  , 'xmax':[50]   , 'thr':[[-1,999999]], 'label':'DT (ingot)'   , 'unit':'[ns]'       , 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['violet'], 'histline':'darkgoldenrod'},
    "LOoverDT_MEAN" : {'db_name': 'LOoverDT_MEAN' , 'xmin':[80]   , 'xmax':[160]  , 'thr':[[-1,999999]], 'label':'LO/DT (ingot)', 'unit':'[ph/MeV/ns]', 'DrawHisto' :'DivideByType', 'type_group':['all'], 'histfill':['violet'], 'histline':'darkgoldenrod'},

    # Array Dimensions
    "L_MAX"  : {'db_name': 'L_MAX'  , 'xmin':[54.6,54.6,54.6] , 'xmax':[54.8,54.8,54.8] , 'thr':[[54.65,54.75],[54.65,54.75],[54.65,54.75]], 'label':'Array Max Length' , 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    # "L_MEAN" : {'db_name': 'L_MEAN' , 'xmin':[54.6,54.6,54.6] , 'xmax':[54.8,54.8,54.8] , 'thr':[[54.65,54.75],[54.65,54.75],[54.65,54.75]], 'label':'Array Mean Length', 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "L_MEAN" : {'db_name': 'L_MEAN' , 'xmin':[54.6,54.6,54.6] , 'xmax':[54.8,54.8,54.8] , 'thr':[[0,100],[0,100],[0,100]], 'label':'Array Mean Length', 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "LMAXVAR": {'db_name': 'LMAXVAR', 'xmin':[0.00,0.00,0.00] , 'xmax':[0.07,0.07,0.07] , 'thr':[[-1.00, 0.06],[-1.00, 0.06],[-1.00, 0.06]], 'label':'Array Planarity'  , 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "W_MAX"  : {'db_name': 'W_MAX'  , 'xmin':[51.08,51.08,51.08], 'xmax':[51.88,51.88,51.88], 'thr':[[51.38,51.58],[51.38,51.58],[51.38,51.58]], 'label':'Array Max Width'  , 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "W_MEAN" : {'db_name': 'W_MEAN' , 'xmin':[51.08,51.08,51.08], 'xmax':[51.88,51.88,51.88], 'thr':[[51.38,51.58],[51.38,51.58],[51.38,51.58]], 'label':'Array Mean Width' , 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    # "T_MAX"  : {'db_name': 'T_MAX'  , 'xmin':[ 3.96, 3.21, 2.61], 'xmax': [4.26,3.51,2.91], 'thr':[[4.01,4.21], [3.26,3.46], [2.66,2.86]], 'label':'Array Max Thickness' , 'unit':'[mm]', 'DrawHisto' :'Overlay', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':['black','black','black'] },
    # "T_MEAN" : {'db_name': 'T_MEAN' , 'xmin':[ 3.96, 3.21, 2.61], 'xmax': [4.26,3.51,2.91], 'thr':[[4.01,4.21], [3.26,3.46], [2.66,2.86]], 'label':'Array Mean Thickness', 'unit':'[mm]', 'DrawHisto' :'Overlay', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':['black','black','black'] },
    "T_MAX"  : {'db_name': 'T_MAX'  , 'xmin':[ 3.96, 3.21, 2.61], 'xmax': [4.26,3.51,2.91], 'thr':[[4.01,4.21], [3.26,3.46], [2.66,2.86]], 'label':'Array Max Thickness' , 'unit':'[mm]', 'DrawHisto' :'DivideByType', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black' },
    "T_MEAN" : {'db_name': 'T_MEAN' , 'xmin':[ 3.96, 3.21, 2.61], 'xmax': [4.26,3.51,2.91], 'thr':[[4.01,4.21], [3.26,3.46], [2.66,2.86]], 'label':'Array Mean Thickness', 'unit':'[mm]', 'DrawHisto' :'DivideByType', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black' },
    "LMAXVAR_LN_STD": {'db_name': 'LMAXVAR_LN_STD', 'xmin':[0.00,0.00,0.00] , 'xmax':[0.01,0.01,0.01] , 'thr':[[-1.00, 1.06],[-1.00, 1.06],[-1.00, 1.06]], 'label':'Array Planarity RMS LN'  , 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "LMAXVAR_LS_STD": {'db_name': 'LMAXVAR_LS_STD', 'xmin':[0.00,0.00,0.00] , 'xmax':[0.01,0.01,0.01] , 'thr':[[-1.00, 1.06],[-1.00, 1.06],[-1.00, 1.06]], 'label':'Array Planarity RMS LS'  , 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},

    # Bar in array dimensions
    "BARLENGTH":{'db_name':'BARLENGTH', 'xmin':[54.6,54.6,54.6] , 'xmax':[54.8,54.8,54.8], 'thr':[[54.67,54.73],[54.67,54.73],[54.67,54.73]], 'label':'Length of Xtals in Arrays', 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},

    # Array Dimensions (STP)
    "L_MAX-STP" : {'db_name': 'L_MAX', 'xmin':[54.6,54.6,54.6] , 'xmax':[54.8,54.8,54.8] , 'thr':[[54.65,54.75],[54.65,54.75],[54.65,54.75]], 'label':'Array Max Length'   , 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "W_MAX-STP" : {'db_name': 'W_MAX', 'xmin':[51.08,51.08,51.08], 'xmax':[51.88,51.88,51.88], 'thr':[[51.38,51.58],[51.38,51.58],[51.38,51.58]], 'label':'Array Max Width'    , 'unit':'[mm]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    # "T_MAX-STP" : {'db_name': 'T_MAX', 'xmin': [ 3.91, 3.21, 2.56], 'xmax': [4.31,3.51,2.96], 'thr':[[ 4.01, 4.21],[ 3.26, 3.46],[ 2.66, 2.86]], 'label':'Array Max Thickness'     , 'unit':'[mm]', 'DrawHisto' :'Overlay', 'type_group':['1','2','3'], 'histfill':['red','green','blue'], 'histline':['red','green','blue'] },
    "T_MAX-STP" : {'db_name': 'T_MAX', 'xmin': [ 3.91, 3.21, 2.56], 'xmax': [4.31,3.51,2.96], 'thr':[[ 4.01, 4.21],[ 3.26, 3.46],[ 2.66, 2.86]], 'label':'Array Max Thickness'     , 'unit':'[mm]', 'DrawHisto' :'DivideByType', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black' },


    ## STACKED PLOTS
    # Array optical properties (dry)
    "LY_MEAN"  : {'db_name': 'LY_MEAN'  , 'xmin':[3999], 'xmax':[6000], 'thr':[[4000,6500],[4000,9999999],[4000,9999999]], 'label':'Array Light Output'     , 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    #"LY_MEAN"  : {'db_name': 'LY_MEAN'  , 'xmin':[50,60,70], 'xmax':[70,80,90], 'thr':[[000,9999999],[000,9999999],[000,9999999]], 'label':'Array Light Output'   , 'unit':'[ph/MeV]', 'DrawHisto' :'DivideByType', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "LY_RSTD"  : {'db_name': 'LY_RSTD'  , 'xmin':[0.00], 'xmax':[10.0], 'thr':[[ 0.00,  7.00],[ 0.00,  7.00],[ 0.00,  7.00]], 'label':'Array Light Output RMS'   , 'unit':'(%)' , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "SIGMA_T_MEAN": {'db_name':'SIGMA_T_MEAN', 'xmin':[115], 'xmax':[150], 'thr':[[0.00,140.00],[0.00,140.00],[0.00,140.00]], 'label':'Array Time resolution'    , 'unit':'[ps]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    # "SIGMA_T_MEAN": {'db_name':'SIGMA_T_MEAN', 'xmin':[140,120,120], 'xmax':[160,140,140], 'thr':[[0.00,180.00],[0.00,180.00],[0.00,180.00]], 'label':'Array Time resolution'    , 'unit':'[ps]', 'DrawHisto' :'DivideByType', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "SIGMA_T_RSTD": {'db_name':'SIGMA_T_RSTD', 'xmin':  [0], 'xmax':[10.], 'thr':[[0.00,  6.00],[0.00,  6.00],[0.00,  6.00]], 'label':'Array Time resolution RMS', 'unit':'(%)' , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "XT_MEAN"  : {'db_name': 'XT_MEAN'  , 'xmin':[-0.10], 'xmax':[0.26], 'thr':[[  -999,  0.25],[-999,  0.25],[-999,  0.25]], 'label':'Array Cross Talk'         , 'unit':''    , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "XT_STD"   : {'db_name': 'XT_STD'   , 'xmin':[0.00], 'xmax':[7.00], 'thr':[[ 0.00,  6.00],[ 0.00,  6.00],[ 0.00,  6.00]], 'label':'Array Cross Talk RMS'     , 'unit':'(%)' , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},

    # Bar in array
    "LY"      : {'db_name': 'LY'     , 'xmin':[3750], 'xmax':[7000], 'thr':[[4000,999999],[4000,999999],[4000,999999]], 'label':'Light Output (bars in arrays)', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "SIGMA_T" : {'db_name': 'SIGMA_T', 'xmin':[90]  , 'xmax':[150] , 'thr':[[0.00,145.00],[0.00,145.00],[0.00,145.00]], 'label':'Time resolution (bars in arrays)', 'unit':'[ps]' , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "XT"      : {'db_name': 'XT'     , 'xmin':[0.00], 'xmax':[0.30], 'thr':[[0.00,  0.25],[0.00,  0.25],[0.00,  0.25]], 'label':'Cross Talk (bars in arrays)'     , 'unit':''     , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},

    # Array optical properties (grease)
    "LY_MEAN-GR"  : {'db_name': 'LY_MEAN'  , 'xmin':[3750] , 'xmax':[7000] , 'thr':[[-1,9999999],[-1,9999999],[-1,9999999]], 'label':'Array Light Output (grease coupling)'   , 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "LY_RSTD-GR"  : {'db_name': 'LY_RSTD'  , 'xmin': [0.00], 'xmax':[10.00], 'thr':[[-1,9999999],[-1,9999999],[-1,9999999]], 'label':'Array Light Output RMS (grease coupling)'   , 'unit':'(%)' , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "SIGMA_T_MEAN-GR": {'db_name':'SIGMA_T_MEAN', 'xmin':[80], 'xmax':[110], 'thr':[[0.00,98.00],[0.00,98.00],[0.00,98.00]], 'label':'Array Time resolution (grease coupling)'    , 'unit':'[ps]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "SIGMA_T_RSTD-GR": {'db_name':'SIGMA_T_RSTD', 'xmin': [0], 'xmax':[10.], 'thr':[[-1,9999999],[-1,9999999],[-1,9999999]], 'label':'Array Time resolution RMS (grease coupling)', 'unit':'(%)' , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "XT_MEAN-GR"  : {'db_name': 'XT_MEAN'  , 'xmin': [0.00], 'xmax':[0.30] , 'thr':[[-1,9999999],[-1,9999999],[-1,9999999]], 'label':'Array Cross Talk (grease coupling)'         , 'unit':''    , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black', 'legend_pos':'L'},
    "XT_STD-GR"   : {'db_name': 'XT_STD'   , 'xmin': [0.00], 'xmax':[7.00] , 'thr':[[-1,9999999],[-1,9999999],[-1,9999999]], 'label':'Array Cross Talk RMS (grease coupling)'     , 'unit':'(%)' , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},

    # Bar in array
    "LY-GR"      : {'db_name': 'LY'     , 'xmin':[4500], 'xmax':[6200], 'thr':[[-1,9999999],[-1,9999999],[-1,9999999]], 'label':'Xtals in Arrays Light Output (grease coupling)', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "SIGMA_T-GR" : {'db_name': 'SIGMA_T', 'xmin':[90]  , 'xmax':[120] , 'thr':[[-1,9999999],[-1,9999999],[-1,9999999]], 'label':'Time resolution (bars in arrays)'              , 'unit':'[ps]'    , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    "XT-GR"      : {'db_name': 'XT'     , 'xmin':[0.00], 'xmax':[0.30], 'thr':[[-1,9999999],[-1,9999999],[-1,9999999]], 'label':'Xtals in Arrays Cross Talk (grease coupling)'  , 'unit':''        , 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black', 'legend_pos':'L'},

    ####### IRRADIATED QUANTITIES ##########
    # PMT single bar POSTIRR
    'LY_NORMAL_REL_VARIATION': {'db_name': 'LY_NORMAL_REL_VARIATION', 'xmin':[-25], 'xmax':[0], 'thr':[[-20,1],[-20,1],[-20,1]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    'DT_REL_VARIATION': {'db_name': 'DECAY_TIME_REL_VARIATION', 'xmin':[-3], 'xmax':[7], 'thr':[[-100,100],[-100,100],[-100,100]], 'label':'DT relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    'LOoverDT_REL_VARIATION': {'db_name': 'LOoverDT_REL_VARIATION', 'xmin':[-10], 'xmax':[10], 'thr':[[-100,100],[-100,100],[-100,100]], 'label':'LOoverDT relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['gold'], 'histline':'darkgoldenrod'},
    
    # TOFPET ARRAY POSTIRR
    'LY_MEAN-POSTIRR': {'db_name': 'LY_MEAN', 'xmin':[3750], 'xmax':[6450], 'thr':[[-1,9999998],[-1,9999998],[-1,9999998]], 'label':'LO', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black', 'legend_pos':'L'},
    'LY_MEAN_REL_VARIATION': {'db_name': 'LY_MEAN_REL_VARIATION', 'xmin':[-22], 'xmax':[0], 'thr':[[-20,1],[-20,1],[-20,1]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black', 'legend_pos':'L'},
    'SIGMA_T_MEAN-POSTIRR': {'db_name': 'SIGMA_T_MEAN', 'xmin':[100], 'xmax':[160], 'thr':[[-1,150],[-1,150],[-1,150]], 'label':'Array Time Resolution', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black', 'legend_pos':'L'},
    'SIGMA_T_MEAN_REL_VARIATION': {'db_name': 'SIGMA_T_MEAN_REL_VARIATION', 'xmin':[-10], 'xmax':[10], 'thr':[[-100,100],[-100,100],[-100,100]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black', 'legend_pos':'L'},
    'XT_MEAN-POSTIRR': {'db_name': 'XT_MEAN', 'xmin':[0], 'xmax':[0.25], 'thr':[[-1,0.25],[-1,0.25],[-1,0.25]], 'label':'Array Cross Talk', 'unit':'', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    'XT_MEAN_REL_VARIATION': {'db_name': 'XT_MEAN_REL_VARIATION', 'xmin':[-10], 'xmax':[10], 'thr':[[-100,100],[-100,100],[-100,100]], 'label':'XT relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},

    # TOFPET BARINARRAY POSTIRR
    'LY-POSTIRR': {'db_name': 'LY', 'xmin':[3750], 'xmax':[6450], 'thr':[[-1,9999998],[-1,9999998],[-1,9999998]], 'label':'LO', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['#9fd18a'], 'histline':'black', 'legend_pos':'L'},
    'LY_REL_VARIATION': {'db_name': 'LY_REL_VARIATION', 'xmin':[-22], 'xmax':[-5], 'thr':[[-20,1],[-20,1],[-20,1]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['#9fd18a'], 'histline':'black', 'legend_pos':'L'},
    'SIGMA_T-POSTIRR': {'db_name': 'SIGMA_T', 'xmin':[100], 'xmax':[160], 'thr':[[-1,150],[-1,150],[-1,150]], 'label':'Array Time Resolution', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['#9fd18a'], 'histline':'black', 'legend_pos':'L'},
    'SIGMA_T_REL_VARIATION': {'db_name': 'SIGMA_T_REL_VARIATION', 'xmin':[-10], 'xmax':[10], 'thr':[[-100,100],[-100,100],[-100,100]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['#9fd18a'], 'histline':'black', 'legend_pos':'L'},
    'XT_MEAN-POSTIRR-GR': {'db_name': 'XT_MEAN', 'xmin':[0], 'xmax':[0.25], 'thr':[[-1,0.25],[-1,0.25],[-1,0.25]], 'label':'Array Cross Talk', 'unit':'', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black', 'legend_pos':'L'},

   # TOFPET ARRAY POSTIRR GREASE
    'LY_MEAN-POSTIRR-GR': {'db_name': 'LY_MEAN', 'xmin':[3750], 'xmax':[6450], 'thr':[[-1,9999998],[-1,9999998],[-1,9999998]], 'label':'LO', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    'LY_MEAN_REL_VARIATION-GR': {'db_name': 'LY_MEAN_REL_VARIATION', 'xmin':[-22], 'xmax':[-5], 'thr':[[-999,999],[-999,999],[-999,999]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    'SIGMA_T_MEAN-POSTIRR-GR': {'db_name': 'SIGMA_T_MEAN', 'xmin':[100], 'xmax':[160], 'thr':[[-999,999],[-999,999],[-999,999]], 'label':'Array Time Resolution', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},
    'SIGMA_T_MEAN_REL_VARIATION-GR': {'db_name': 'SIGMA_T_MEAN_REL_VARIATION', 'xmin':[-10], 'xmax':[10], 'thr':[[-999,999],[-999,999],[-999,999]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['1','2','3'], 'histfill':['#ed6b7c','#9fd18a','#e5da1e'], 'histline':'black'},

    # TOFPET BARINARRAY POSTIRR GREASE
    'LY-POSTIRR-GR': {'db_name': 'LY', 'xmin':[3750], 'xmax':[6450], 'thr':[[-1,9999998],[-1,9999998],[-1,9999998]], 'label':'LO', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['#9fd18a'], 'histline':'black'},
    'LY_REL_VARIATION-GR': {'db_name': 'LY_REL_VARIATION', 'xmin':[-22], 'xmax':[-5], 'thr':[[-999,999],[-999,999],[-999,999]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['#9fd18a'], 'histline':'black','legend_pos':'L'},
    'SIGMA_T-POSTIRR-GR': {'db_name': 'SIGMA_T', 'xmin':[100], 'xmax':[160], 'thr':[[-999,999],[-999,999],[-999,999]], 'label':'Array Time Resolution', 'unit':'[ph/MeV]', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['#9fd18a'], 'histline':'black'},
    'SIGMA_T_REL_VARIATION-GR': {'db_name': 'SIGMA_T_REL_VARIATION', 'xmin':[-10], 'xmax':[10], 'thr':[[-999,999],[-999,999],[-999,999]], 'label':'LO relative variation', 'unit':'(%)', 'DrawHisto' :'Stack', 'type_group':['all'], 'histfill':['#9fd18a'], 'histline':'black'},
}

correlationPairs = {
    'lyTianle_vs_lyRome' : {
        'dfx':'data_PMT.csv', 
        'dfy':'data_PMT.csv',
        'colx':'LY_ABS',
        'coly':'LY_ABS',
        'tagx':'STP_PREIRR',
        'tagy':'PREIRR_0',
        'type':'all',
        'xlab':'Xtal LO (STP)  [ps]',
        'ylab':'Xtal LO (Rome) [ps]',
    },
    'dtTianle_vs_dtRome' : {
        'dfx':'data_PMT.csv', 
        'dfy':'data_PMT.csv',
        'colx':'DECAY_TIME',
        'coly':'DECAY_TIME',
        'tagx':'STP_PREIRR',
        'tagy':'PREIRR_0',
        'type':'all',
        'xlab':'Xtal Decay Time (STP)  [ps]',
        'ylab':'Xtal Decay Time (Rome) [ps]',
    },
    # 'sigmaT_vs_LOoverTau' : {
    #     'dfx':'data_TOFPET_ARRAY.csv', 
    #     'dfy':'data_TOFPET_ARRAY.csv',
    #     'colx':'LY_MEAN',
    #     'coly':'SIGMA_T_MEAN',
    #     'tagx':'PREIRR',
    #     'tagy':'PREIRR',
    #     'type':'all',
    #     'xlab':'Array LO [ph/MeV]',
    #     'ylab':r'Array $\sigma_{t}$ [ps]',
    # },
    # 'CaliberWidth_vs_GalaxyWidth' : {
    #     'dfx':'data_CALIBER_ARRAY.csv', 
    #     'dfy':'data_GALAXY_ARRAY.csv',
    #     'colx':'W_MAX',
    #     'coly':'W_MEAN',
    #     'tagx':'CALIBER',
    #     'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
    #     'type':'all',
    #     'xlab':'Array Width (caliber) [mm]',
    #     'ylab':'Array Width (galaxy)  [mm]',
    # },
    # 'CaliberWidth_vs_TianleWidth' : {
    #     'dfx':'data_CALIBER_ARRAY.csv', 
    #     'dfy':'data_GALAXY_ARRAY.csv',
    #     'colx':'W_MAX',
    #     'coly':'W_MAX',
    #     'tagx':'CALIBER',
    #     'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_STP_PREIRR',
    #     'type':'all',
    #     'xlab':'Array Width (caliber) [mm]',
    #     'ylab':'Array Width (Tianle)  [mm]',
    # },
    'GalaxyWidth_vs_TianleWidth' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_GALAXY_ARRAY.csv',
        'colx':'W_MAX',
        'coly':'W_MAX',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_STP_PREIRR',
        'type':'all',
        'xlab':'Array Width (galaxy)  [mm]',
        'ylab':'Array Width (Tianle)  [mm]',
    },
    'GalaxyThickness_vs_TianleThickness_T1' : {
        'dfx':'data_GALAXY_ARRAY.csv',
        'dfy':'data_GALAXY_ARRAY.csv',
        'colx':'T_MAX',
        'coly':'T_MAX',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_STP_PREIRR',
        'type':'1',
        'xlab':'Array Thickness (galaxy)  [mm]',
        'ylab':'Array Thickness (Tianle)  [mm]',
    },
    'GalaxyThickness_vs_TianleThickness_T2' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_GALAXY_ARRAY.csv',
        'colx':'T_MAX',
        'coly':'T_MAX',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_STP_PREIRR',
        'type':'2',
        'xlab':'Array Thickness (galaxy)  [mm]',
        'ylab':'Array Thickness (Tianle)  [mm]',
    },
    'GalaxyThickness_vs_TianleThickness_T3' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_GALAXY_ARRAY.csv',
        'colx':'T_MAX',
        'coly':'T_MAX',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_STP_PREIRR',
        'type':'3',
        'xlab':'Array Thickness (galaxy)  [mm]',
        'ylab':'Array Thickness (Tianle)  [mm]',
    },
    'GalaxyLength_vs_TianleLength' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_GALAXY_ARRAY.csv',
        'colx':'L_MAX',
        'coly':'L_MAX',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_STP_PREIRR',
        'type':'all',
        'xlab':'Array Length (galaxy)  [mm]',
        'ylab':'Array Length (Tianle)  [mm]',
    },
    'LO_vs_Planarity' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_TOFPET_ARRAY.csv',
        'colx':'LMAXVAR',
        'coly':'LY_MEAN',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_PREIRR',
        'type':'all',
        'xlab':'Array Planarity  [mm]',
        'ylab':'Array LO [ph/MeV]',
    },
    'sigmaT_vs_Planarity' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_TOFPET_ARRAY.csv',
        'colx':'LMAXVAR',
        'coly':'SIGMA_T_MEAN',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_PREIRR',
        'type':'all',
        'xlab':'Array Planarity  [mm]',
        'ylab':'Array Time Resolution [ps]',
    },
    'LO_RMS_vs_Planarity' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_TOFPET_ARRAY.csv',
        'colx':'LMAXVAR',
        'coly':'LY_RSTD',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_PREIRR',
        'type':'all',
        'xlab':'Array Planarity  [mm]',
        'ylab':'Array LO RMS [ph/MeV]',
    },
    'sigmaT_RMS_vs_Planarity' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_TOFPET_ARRAY.csv',
        'colx':'LMAXVAR',
        'coly':'SIGMA_T_RSTD',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'Run\d{6}_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}_ARRAY\d{3,14}_IARR\d_POS\d_X[\d.]*_Y[\d.]*_Z[\d.]*_PREIRR',
        'type':'all',
        'xlab':'Array Planarity  [mm]',
        'ylab':'Array Time Resolution RMS [ph/MeV]',
    },
    'LMAXVAR_vs_LMAXVAR_RMS_LN' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_GALAXY_ARRAY.csv',
        'colx':'LMAXVAR_LN_STD',
        'coly':'LMAXVAR_LN',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'type':'all',
        'xlab':'Array Planarity RMS LN [mm]',
        'ylab':'Array Planarity (Max.Var.) LN [mm]',
    },
    'LMAXVAR_vs_LMAXVAR_RMS_LS' : {
        'dfx':'data_GALAXY_ARRAY.csv', 
        'dfy':'data_GALAXY_ARRAY.csv',
        'colx':'LMAXVAR_LS_STD',
        'coly':'LMAXVAR_LS',
        'tagx':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'tagy':'(Run\d{6}_|Run_Galaxy_)?ARRAY\d{3,14}_PREIRR',
        'type':'all',
        'xlab':'Array Planarity RMS LS [mm]',
        'ylab':'Array Planarity (Max.Var.) LS [mm]',
    },
}
