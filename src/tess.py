import subprocess
import glob
from ocr import chooseResult
from ocr import insertPeriod
from ocr import validateOCR


class ConvertCaller():
    def __init__(self):
        self.opts=[
            'convert $PATH -auto-level -resize 162x91 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 243x137 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 324x182 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 486x273 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 648x364 -compress none $NAME.tiff',
            'convert $PATH -despeckle -threshold 50% -auto-level -resize 638x364 -compress none $NAME.tiff',#effective
            'convert $PATH -auto-level -resize 837x455 -compress none $NAME.tiff',#effective
            'convert $PATH -auto-level -resize 1296x728 -compress none $NAME.tiff',
            'convert $PATH -auto-level -resize 1458x819 -compress none $NAME.tiff'
        ]
        self.path="$PATH"
        self.name="$NAME"
    def getNext(self,path,name):
        for cur in self.opts:
            yield cur.replace(self.path,path).replace(self.name,name).split(' ')
    

if __name__ == '__main__':
    conv = ConvertCaller()
    i=0
    imageDir = "../sprites/"
    for cur in glob.iglob(imageDir + '*.png'):
        print "cur path:",cur
        imageHash = cur.split('/')[-1].split('.')[0]
        print "hash",imageHash
        
        for convCall in conv.getNext(cur,imageHash):
            #print "conv args:",convCall
            rval = subprocess.call(convCall)
            if not rval == 0:
                #handle convert error
                print "error on convert"
            
            #tesseract creates a $imageHash.txt output file
            if not 0==subprocess.call(['tesseract', imageHash+'.tiff', imageHash, 'mitch']):
                #handle tesseract error
                print "tess error"
                break
            result = subprocess.check_output(['cat',imageHash+'.txt']).strip().split('\n')
            #print "le text:",result
            result = chooseResult(*result)
            print "\tchose:", result
            #if i>0:break
            #i+=1
            subprocess.check_output(['rm',imageHash+'.txt'])
            subprocess.check_output(['rm',imageHash+'.tiff'])
            if result is not None:
                print "done!"
                #break
            
        break
        #mv "$imageHash.png" "done"
        #rm "$imageHash.txt"
        
        #popen = subprocess.check_output(["/bin/bash", ocrScript, spriteDir])
        #for line in subprocess.check_output(["ls","-lah"]):
        #    print line

