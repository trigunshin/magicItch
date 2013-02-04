from pymongo import MongoClient
from datetime import date
import sys,csv,argparse,math

class ScgImports():
    def __init__(self, aDate, aStoreName, spriteColl, aDelimiter = "\t"):
        self.delimiter = aDelimiter
        self.sprites = spriteColl
        self.spriteCache = {}
        self.datestring = aDate
        self.db = None
        self.setIndex = 0
        self.nameIndex = 1
        self.priceIndex = 2
        self.quantIndex = 3
        self.rarityIndex = 4
        self.hashIndex = 5
        self.storeName = aStoreName

    def getReader(self, aFileObject):
        return csv.reader(aFileObject, delimiter=self.delimiter)
    
    def parseFile(self, aFilePath):
        with open(aFilePath, 'r') as f:
            reader=self.getReader(f)
            for row in reader:
                name = row[self.nameIndex]
                setName = row[self.setIndex]
                spriteHash = row[self.hashIndex]
                quant = self.hashParse(row[self.quantIndex], spriteHash)
                price = self.hashParse(row[self.priceIndex], spriteHash)
                #rarity = row[self.rarityIndex]
                yield {"name":name,"set":setName,"store":self.storeName,"quantity":quant,"price":price,"date":self.datestring}
    
    """
    def updatePriceListings(self, aFile, collection):
        with open(aFile, 'rb') as f:
            reader = self.getReader(f)
            for row in reader:
                name = row[self.nameIndex]
                setName = row[self.setIndex]
                quant = row[self.quantIndex]
                price = self.parsePrice(row[self.priceIndex])
                val = [{"name":name,"set":setName,"store":self.storeName,"quantity":quant,"price":price,"date":self.datestring}]
                collection.insert(val)
    #"""
    
    def hashParse(self, toParse, aHash):
        if toParse == "None": return "None"
        #print toParse
        try:
            try:
                spriteMap=self.spriteCache[aHash]
            except KeyError,e:
                #TODO this'll explode on a hash fail, but that's ok for now
                spriteMap = self.sprites.find_one({'hash':aHash})['values']
                self.spriteCache[aHash] = spriteMap
            return ''.join([spriteMap[val] for val in toParse.split('|')])
        except TypeError,e:
            raise Exception("Hash data not found:"+aHash)
    
if __name__ == '__main__':
    verbose = False
    datestring = None
    delimiter = "\t"
    fileSuffix = ".tsv"
    fileName = None
    fullFileDirectory = "/Users/trigunshin/mtgPrice/scg/"
    storeName = "StarCity Games"
    #datestring = date.today().isoformat()
    
    parser = argparse.ArgumentParser(description='Upload a scg Xsv file to the mongo db.')
    parser.add_argument('-f', required=True, help="Directory to find the file in")
    parser.add_argument('-d', required=False, help="Date to read data from. Currently only SCG supported if -n not used.")
    parser.add_argument('-n', required=False, help="File name to read data from")
    parser.add_argument('-t', action='store_true', help="Denote a TSV file")
    parser.add_argument('-c', action='store_true', help="Denote a CSV file")
    parser.add_argument('-s', required=False, help="Store name to use when storing file.")
#    parser.add_argument('',required=false, help="
    
    args = vars(parser.parse_args())
    
    if args['t']:
        delimiter = "\t"
        fileSuffix = ".tsv"
    elif args['c']:
        delimiter = ","
        fileSuffix = ".csv"
    if args['s']:
        storeName = args['s']
    if args['d'] != None:
        datestring = args['d']
#        fileName = "scg_"+datestring+fileSuffix
    if args['n'] != None:
        fileName = args['n']
#    else:
#        print "Date or name required!"
#        exit()
    if args['f'] != None:
        fullFileDirectory = args['f']
    
    if fileName == None:
        fileName = "scg_"+datestring+fileSuffix
    fileToUse = fullFileDirectory + fileName
    print "Reading from:",fileToUse
    
    c = MongoClient()
    db = c['cardData']
    coll = db['priceCollection']
    sprites = db['sprites']
    
    imp = ScgImports(datestring, storeName, sprites, delimiter)
    
    dateQueryParam = {"date":datestring, "store":storeName}
    
    if coll.find(dateQueryParam).count() == 0:
        results = imp.parseFile(fileToUse)
        for result in results:
            print result
        """
        imp.updatePriceListings(fileToUse, coll)
        for post in coll.find(dateQueryParam).limit(2).sort("name"):
            print post
    else:
        count = coll.find(dateQueryParam).count()
        print count, "listings exist for that date!"
    #"""
#    print json.dumps([p.__dict__ for p in ])
#    print args
#    print [str(args[a])+str(1) for a in args]
#        print a
