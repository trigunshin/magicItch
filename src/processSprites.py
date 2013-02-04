import subprocess, glob, argparse
from pymongo import MongoClient

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

class ConvertCaller():
    def __init__(self):
        self.opts=[
            'convert $PATH -despeckle -threshold 50% -auto-level -resize 638x364 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 648x364 -compress none $NAME.tiff',
            'convert $PATH -despeckle -threshold 50% -auto-level -resize 837x455 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 837x455 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 162x91 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 243x137 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 324x182 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 486x273 -compress none $NAME.tiff',
            'convert $PATH -despeckle -threshold 50% -auto-level -resize 1296x728 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 1296x728 -compress none $NAME.tiff',
            'convert $PATH -despeckle -threshold 50% -auto-level -resize 1458x819 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 1458x819 -compress none $NAME.tiff'
        ]
        self.path="$PATH"
        self.name="$NAME"
    def getNext(self,path,name):
        for cur in self.opts:
            yield cur.replace(self.path,path).replace(self.name,name).split(' ')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run OCR with varying arguments over sprite files.')
    parser.add_argument('-v', action='store_true', help='Verbose flag')
    parser.add_argument('-d', action='store_true', help='Debug flag')
    parser.add_argument('-s', help="Sprite file directory. Will break if path contains spaces.")
    args = vars(parser.parse_args())
    
    verbose = False
    debug = False
    imageDir= "sprites/"
    
    c = MongoClient('localhost',27017)
    db = c['cardData']
    sprites = db['sprites']
    
    if args['v']:
        verbose = args['v']
    if args['d']:
        debug = args['d']
    if args['s'] != None:
        imageDir = args['s']
    
    conv = ConvertCaller()
    for cur in glob.iglob(imageDir + '*.png'):
        print "cur path:",cur
        imageHash = cur.split('/')[-1].split('.')[0]
        chosen = None
        for convCall in conv.getNext(cur,imageHash):
            convertResult = subprocess.call(convCall)
            if not convertResult == 0:
                #handle convert error
                print "error on convert"
                break
            #tesseract creates a $imageHash.txt output file
            if not 0==subprocess.call(['tesseract', imageHash+'.tiff', imageHash, 'mitch']):
                #handle tesseract error
                print "tess error"
                break
            result = subprocess.check_output(['cat',imageHash+'.txt']).strip().split('\n')
            chosen = chooseResult(*result)
            print "\tchose:", chosen
            subprocess.check_output(['rm',imageHash+'.txt'])
            subprocess.check_output(['rm',imageHash+'.tiff'])
            if chosen is not None:
                if debug is False:
                    sprites.update({'hash':imageHash},{'$set':{'values':chosen}}, upsert=True)
                    code = subprocess.call(["mv", imageDir+imageHash+".png", imageDir+"done/"])
                    if not code == 0: print "error moving hashfile",imageDir+imageHash+".png","to",imageDir+"done/"
                break
        if chosen is None:
            print "failed to tesseract:",imageHash
