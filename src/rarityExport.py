import pymongo
from pymongo import Connection
from datetime import date
import sys,csv,argparse,jsonpickle,math

class scgImports(object):
    def __init__(self, aDelimiter = ",", verbose=None):
        self.verbose = verbose
        self.delimiter = aDelimiter
        self.setIndex = 0
        self.nameIndex = 1
        self.rarityIndex = 4

    def getReader(self, file):
        return csv.reader(file, delimiter=self.delimiter)

    def getCardInfo(self, aFile, collection):
        ret = []
        with open(aFile, 'rb') as f:
            reader = self.getReader(f)
            for row in reader:
                cardName = row[self.nameIndex]
                cardSet = row[self.setIndex]
                cardRarity = row[self.rarityIndex]
                ret.append({"name":name,"set":set,"rarity":cardRarity,"date":self.datestring})
                #collection.insert(val)
        return ret

if __name__ == '__main__':
    verbose = False
    delimiter = "\t"
    fileSuffix = ".tsv"
    fileName = None
    fullFileDirectory = ""
    
    parser = argparse.ArgumentParser(description='Upload a scg Xsv file to the mongo db.')
    parser.add_argument('-d', required=True, help="Directory to find the file in")
    parser.add_argument('-f', required=False, help="File name to read data from")
    parser.add_argument('-t', action='store_true', help="Denote a TSV file")
    parser.add_argument('-c', action='store_true', help="Denote a CSV file")
    
    args = vars(parser.parse_args())
    
    if args['t']:
        delimiter = "\t"
        fileSuffix = ".tsv"
    elif args['c']:
        delimiter = ","
        fileSuffix = ".csv"
    if args['f'] != None:
        fileName = args['f']
    if args['d'] != None:
        fullFileDirectory = args['d']
    if fileName == None:
        fileName = "scg_"+datestring+fileSuffix
    fileToUse = fullFileDirectory + fileName
    
    print "Reading from:",fileToUse
    
    c = Connection()
    db = c['cardInfo']
    coll = db['cards']
    
    imp = scgImports(delimiter)
    
    listings = imp.getCardInfo(fileToUse, coll)
    coll.insert(listings)
    #for post in coll.find(dateQueryParam).limit(2).sort("name"):
    #    print post
    
