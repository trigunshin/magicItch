import subprocess
import glob

if __name__ == '__main__':
    imageDir = "../sprites/"
    for cur in glob.iglob(imageDir + '*.png'):
        print "cur path:",cur
        imageHash = cur.split('/')[-1].split('.')[0]
        print "hash",imageHash
        #convert "$imageHash".png -auto-level -resize 648x364 -compress none "$imageHash".tiff
        rval = subprocess.call(['convert',cur,'-auto-level','-resize','648x364','-compress','none',imageHash+'.tiff'])
        if not rval == 0:
            #handle convert error
            print "error on convert"
        
        #tesseract creates a $imageHash.txt output file
        #tesseract "$imageHash".tiff "$imageHash" mitch 1>/dev/null 2>&1
        if not 0==subprocess.call(['tesseract', imageHash+'.tiff', imageHash, 'mitch']):
            #handle tesseract error
            print "tess error"
            break
        txt = subprocess.check_output(['cat',imageHash+'.txt'])
        print "le text:\n",txt.strip().split('\n')
        break
        #subprocess.check_output(['paste','-s','-d','|',txt])
        #TEXT=`cat $imageHash.txt | paste -s -d '|'`
        #TEXT="$TEXT$imageHash"
        #mv "$imageHash.png" "done"
        #rm "$imageHash.txt"
        
        #popen = subprocess.check_output(["/bin/bash", ocrScript, spriteDir])
        #for line in subprocess.check_output(["ls","-lah"]):
        #    print line

