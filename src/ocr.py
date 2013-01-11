from glob import glob
from pymongo import Connection
from datetime import date
import time, re, argparse, sys, csv, subprocess

if __name__ == '__main__':
    wdir = "../stest/"
    sdir = "../stest/"
    scriptName = "tess.sh"
    print "working dir:",wdir
    print "scriptdir:",sdir+scriptName
    popen = subprocess.check_output(["/bin/bash", sdir+scriptName, wdir]).split('\n')[:-1]
    triple = [line.split(' ') for line in popen]
    for t in triple: print t
    #print "result:",popen
    """
    for file in glob(wdir+"*.png"):
        print file
        #subprocess.call(script + [arg1])
    #"""
    

