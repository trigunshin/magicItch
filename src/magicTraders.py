'''
Created on Aug 6, 2011

@author: trigunshin
'''
from datetime import date
import time, re, csv, argparse, sys, urllib2

class CardInfo:
        def __init__(self, set, name, price, quantity=None):
            self.set = set
            self.name = name
            self.price = price
            self.quantity = quantity
            
        def getString(self, delimiter = ","):
            result = str(self.set) + delimiter + str(self.name) + delimiter + str(self.price) + delimiter + str(self.quantity)
            #return "\"" + str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price) + "\", \"" +str(self.quantity)+ "\""
            return result

class FileFetcher:
    def __init__(self, url):
        self.url = url
        
    def getHtmlReader(self):
        file = urllib2.urlopen(self.url)
        return file

class MtgTrdrFileParser:
    def __init__(self, fileReader):
        self.fileReader = fileReader;
        self.cardNameLoc = 0;
        self.priceLoc = 1;
    
    def processFile(self):
        infoList = []
        spamReader = csv.reader(self.fileReader, delimiter='|')
        i=0;
        for row in spamReader:
            if(i==0):
                i=i+1
                continue
            #print None, "\t", row[self.cardNameLoc],"\t", row[self.priceLoc],"\t",None
            a=CardInfo(None,row[self.cardNameLoc],row[self.priceLoc],None)
            infoList.append(a)
            #print a.getString("\t")
            #print "".join(row[self.cardNameLoc]).join(" ").join(row[self.priceLoc])
            #i+=1
            #if(i>10):
            #    break
        return infoList

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape sell data from MagicTraders website to the given file.')
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-f', help='File directory to store to.')
    args = vars(parser.parse_args())
    
    fullFileDirectory = "info/"
    verbose = False
    
    if args['v']:
        verbose = args['v']
    if args['f'] != None:
        fullFileDirectory = args['f']
    
    netfile = FileFetcher("http://www.magictraders.com/pricelists/current-magic-excel.txt")
    psvDataReader = netfile.getHtmlReader();
    parser = MtgTrdrFileParser(psvDataReader);
    infoList = parser.processFile()
#    scg = SCGSpoilerParser(verbose)
    #allSetInfo = scg.getAllSetInfo()
    
    today = date.today()
    tabFileDest = fullFileDirectory+"mtgtrdr_"+today.isoformat()+".tsv"
    
    print "Starting file output to: ", tabFileDest
    
    tab = open(tabFileDest, 'w')
    for card in infoList:
        tab.write(card.getString("\t")+"\n")
    tab.close()