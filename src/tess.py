import subprocess
import glob

if __name__ == '__main__':
    for cur in glob.iglob('*.png'):
        imageHash = cur.split('.')[0]
        
        #convert "$imageHash".png -auto-level -resize 648x364 -compress none "$imageHash".tiff
        rval = subprocess.call(['convert',imageHash+'.png','-auto-level','-resize','648x364','-compress','none',imageHash+'.tiff'])
        if not rval == 0:
            #handle convert error
            print "error on convert"
        
        #tesseract creates a $imageHash.txt output file
        #tesseract "$imageHash".tiff "$imageHash" mitch 1>/dev/null 2>&1
        if not 0==subprocess.call(['tesseract', imageHash+'.tiff', imageHash, 'mitch']:
            #handle tesseract error
        txt = subprocess.check_output(['cat',imageHash+'.txt'])
        print "le text",txt
        break
        #subprocess.check_output(['paste','-s','-d','|',txt])
        #TEXT=`cat $imageHash.txt | paste -s -d '|'`
        #TEXT="$TEXT$imageHash"
        #mv "$imageHash.png" "done"
        #rm "$imageHash.txt"
        
        #popen = subprocess.check_output(["/bin/bash", ocrScript, spriteDir])
        #for line in subprocess.check_output(["ls","-lah"]):
        #    print line

