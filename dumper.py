## Python stuff
import os
import sys
import subprocess

import configs.config

# Default settings
DEFAULTPORT = '8113'
DEFAULTUSER = 'mtdloadb'
DEFAULTDIROUT = 'data' 


def omsQuery(query, outputfile, port=DEFAULTPORT):

    if os.path.isfile(outputfile):
        print('\t  ...overwriting '+outputfile)
        os.system("rm "+outputfile)    

    #print(f"python3 rhapi.py --all -f csv --url=http://localhost:{port} \"{query}\" > {outputfile}")
    os.system(f"python3 rhapi.py --all -f csv --url=http://localhost:{port} \"{query}\" > {outputfile}")


def openTunnel(user='mtdloadb',port=DEFAULTPORT):
    if user != DEFAULTUSER:
        print (f"Please type lxplus.cern.ch password for user {user}")
    os.system(f"ssh -f -N -L 8113:dbloader-mtd.cern.ch:8113 {user}@lxplus.cern.ch")
    print ("Tunnel for dbloader-mtd.cern.ch OPEN\n")


def closeTunnel(port=DEFAULTPORT):
    PID = subprocess.check_output(f"pgrep -f 'ssh.*{port}'", shell=True).decode()
    os.system(f"kill -9 {PID}")
    print("Tunnel for dbloader-mtd.cern.ch CLOSED\n")


def dumpAll(dirout=DEFAULTDIROUT,port=DEFAULTPORT):
    
    if not os.path.isdir(dirout):
        os.system(f'mkdir -p {dirout}')

    print("\nDumping all data from OMS DB\n")

    openTunnel()
    
    omsData = condig.omsData

    for tag in omsData:
        print(f"- retrieving data for {q}")
        query = omsData[tag]['query']
        filecsv = omsData[tag]['filecsv']
        omsQuery(query, f'{dirout}/{filecsv}')

    closeTunnel()
