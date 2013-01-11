from glob import glob
from pymongo import Connection
from datetime import date
import time, re, argparse, sys, csv, subprocess

def validateOCR(aResult,verbose=False):
    ret = {}
    check = {}
    if verbose: print "checking",aResult
    for i in range(len(aResult)):
        #fail out if duplicate detected, OCR is inaccurate
        if verbose:print "\tchecking idx",i,"w/val",aResult[i]
        try:
            if check[aResult[i]]: return None
        except KeyError,e:
            ret[i] = aResult[i]
    return ret

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run OCR on downloaded sprite files.')
    parser.add_argument('-v', action='store_true', help='Verbose flag')
    parser.add_argument('-d', action='store_true', help='Debug flag')
    parser.add_argument('-s', help="Sprite file directory.")
    parser.add_argument('-f', help="OCR script location.")
    args = vars(parser.parse_args())
    
    verbose = False
    debug = False
    ocrScript = "tess.sh"
    spriteDir= "sprites/"
    
    c = Connection()
    db = c['cardData']
    coll = db['cards']
    sprites = db['sprites']
    
    if args['v']:
        verbose = args['v']
    if args['d']:
        debug = args['d']
    if args['f'] != None:
        ocrScript = args['f']
    if args['s'] != None:
        spriteDir = args['s']
    
    popen = subprocess.check_output(["/bin/bash", ocrScript, spriteDir]).split('\n')[:-1]
    triple = [line.split(' ') for line in popen]
    for t in triple:
        print "hash:", t[2]
        print "ocr_top:",validateOCR(t[0])
        print "ocr_bot:",validateOCR(t[1])
    
