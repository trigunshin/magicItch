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
            if check[aResult[i]]:
                if verbose: print "had result",aResult[i],"at",i," quitting"
                #print check
                return None
        except KeyError,e:
            check[aResult[i]] = True
            ret[str(i)] = aResult[i]
    return ret

def insertPeriod(aString):
    return aString[0:9] + '.' + aString[-1]

def chooseResult(first, second, verbose=False):
    #11 length dict should be correct, use that one
    if len(first) == 11: return validateOCR(first, verbose)
    elif len(second) == 11: return validateOCR(second, verbose)
    
    #try the first
    if len(first) == 10:
        ret = validateOCR(insertPeriod(first), verbose)
        if ret is not None: return ret
    #first had bad len or didn't convert, try second
    if len(second) == 10:
        return validateOCR(insertPeriod(second), verbose)
    #nothing had length or converted
    return None

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
    triple = [line.split('|') for line in popen]
    for t in triple:
        first = t[0].replace(" ","")
        second = t[1].replace(" ","")
        print "hash:", t[2],":",first,"|",second
        result = chooseResult(first, second)
        print "\tchose:", result
        if result is not None:
            sprites.update({'hash':t[2]},
                            {'$set':{'values':result}
                        }, upsert=True)
            code = subprocess.call(["mv", spriteDir+str(t[2])+".png", spriteDir+"done/"])
            if not code == 0: print "error moving hashfile",spriteDir+str(t[2])+".png","to",spriteDir+"done/"
        #print "ocr_top:",validateOCR(first)
        #print "ocr_bot:",validateOCR(second)
    
