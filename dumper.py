## Python stuff
import os
import sys
import subprocess

from configs import config

# Default settings
DEBUG = False
DEFAULTPORT = '8113'
DEFAULTUSER = 'mtdloadb'
DEFAULTDIROUT = f'{config.MAINDIR}/{config.DIRDUMP}/{config.DEFAULTBATCH}' 


def omsQuery(query, outputfile, port=DEFAULTPORT):

    if os.path.isfile(outputfile):
        print('\t  ...overwriting '+outputfile)
        os.system("rm "+outputfile)    

    #print(f"python3 rhapi.py --all -f csv --url=http://localhost:{port} \"{query}\" > {outputfile}")
    os.system(f"python3 rhapi.py --all -f csv --url=http://localhost:{port} \"{query}\" > {outputfile}")


def openTunnel(user='mtdloadb',port=DEFAULTPORT):
    if user != DEFAULTUSER:
        print (f"Please type lxplus.cern.ch password for user {user}")
    os.system(f"ssh -f -N -L {port}:dbloader-mtd.cern.ch:{port} {user}@lxplus.cern.ch")
    print ("Tunnel for dbloader-mtd.cern.ch OPEN\n")


def closeTunnel(port=DEFAULTPORT):
    PID = subprocess.check_output(f"pgrep -f 'ssh.*{port}'", shell=True).decode()
    os.system(f"kill -9 {PID}")
    print("\nTunnel for dbloader-mtd.cern.ch CLOSED\n")


def dumpAll(dirout=DEFAULTDIROUT,port_=DEFAULTPORT,batch=config.DEFAULTBATCH):
    
    if not os.path.isdir(dirout):
        os.system(f'mkdir -p {dirout}')

    print("\nDumping all data from OMS DB\n")

    openTunnel(port=port_)
    
    omsData = config.omsData

    for tag in omsData:
        print(f"\n- retrieving data for {tag}")
        
        if 'query' in omsData[tag].keys():
            query = omsData[tag]['query']  
            filecsv = omsData[tag]['filecsv']

            if batch != 'all':
                query = f'{query} AND p.BATCH_NUMBER=\'{batch}\''

            if DEBUG:
                print(f'\n{query}\n')
            
            omsQuery(query, f'{dirout}/{filecsv}')

        else:
            location = omsData[tag]['location']
            filecsv  = omsData[tag]['filecsv']
            os.system(f'cp {location}/{filecsv} {dirout}')
            print(f'\t  No query for {tag}, data retrieved from file {filecsv}')

    closeTunnel(port=port_)
