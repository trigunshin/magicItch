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
                """
                #XXX debug a broken solve, leaving the skeleton here for it
                if name == "Mountain (#376)":
                    print  {"name":name,"set":setName,"store":self.storeName,"quantity":quant,"price":price,"date":self.datestring}
                    print 'hash:',spriteHash,'\tsolve:',self.spriteCache[spriteHash]
                    print 'raw_quant',row[self.quantIndex],'raw_price:',row[self.priceIndex]
                #"""
                yield {"name":name,"set":setName,"store":self.storeName,"quantity":quant,"price":price,"date":self.datestring}
    
    def hashParse(self, toParse, aHash):
        if toParse == "None": return "None"
        try:
            try:
                spriteMap=self.spriteCache[aHash]
            except KeyError,e:
                #TODO this'll explode on a hash fail, but that's ok for now
                spriteMap = self.sprites.find_one({'hash':aHash})['values']
                self.spriteCache[aHash] = spriteMap
            return self.formatNumber(''.join([spriteMap[val] for val in toParse.split('|')]))
        except TypeError,e:
            raise Exception("Hash data not found:"+aHash)
    
    def formatNumber(self, aNumberString):
        ret = aNumberString.replace('$', '')
        ret = ret.replace('.', '')
        ret = ret.replace(',', '')
        return ret

def spliceSpriteData(spriteColl,cardDataColl,dataDirectory='scg_data/',datestring=None,storeName="StarCity Games",delimiter=',',verbose=False,debug=False,**kwargs):
    ret={}
    if datestring is None: datestring = date.today().isoformat()
    imp = ScgImports(datestring, storeName, spriteColl, delimiter)
    dateQueryParam = {"date":datestring, "store":storeName}
    
    fileToUse = dataDirectory + 'scg_'+datestring+'.tsv'
    ret['filePath']=fileToUse
    ret['date_query']=dateQueryParam
    if debug:
        results = imp.parseFile(fileToUse)
        for result in results:
            print result
        ret['result']='debug printed'
    else:
        if cardDataColl.find(dateQueryParam).count() == 0:
            results = imp.parseFile(fileToUse)
            cardDataColl.insert(results)
            for post in cardDataColl.find(dateQueryParam).limit(2).sort("name"):
                print post
            ret['result'] = 'inserted listings to db'
        else:
            count = cardDataColl.find(dateQueryParam).count()
            print count, "listings exist for that date!"
            ret['result']=str(count)+" listings exist for date " + datestring
    return ret

if __name__ == '__main__':
    verbose = False
    datestring = None
    delimiter = "\t"
    fileSuffix = ".tsv"
    fileName = None
    fullFileDirectory = "/Users/trigunshin/mtgPrice/scg/"
    storeName = "StarCity Games"
    test_flag = False
    #datestring = date.today().isoformat()
    
    parser = argparse.ArgumentParser(description='Upload a scg Xsv file to the mongo db.')
    parser.add_argument('-f', required=True, help="Directory to find the file in")
    parser.add_argument('-d', required=True, help="Date to read data from. Currently only SCG supported if -n not used.")
    parser.add_argument('-n', required=False, help="File name to read data from")
    parser.add_argument('-t', action='store_true', help="Denote a TSV file")
    parser.add_argument('-c', action='store_true', help="Denote a CSV file")
    parser.add_argument('-z', action='store_true', help="Test Mode. Will print results to stdout instead of storing in Mongo")
    parser.add_argument('-s', required=False, help="Store name to use when storing file.")
    
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
    if args['n'] != None:
        fileName = args['n']
    if args['f'] != None:
        fullFileDirectory = args['f']
    if args['z']: test_flag = True
    
    if fileName == None:
        fileName = "scg_"+datestring+fileSuffix
    fileToUse = fullFileDirectory + fileName
    print "Reading from:",fileToUse
    #"""
    c = MongoClient()
    db = c['cardData']
    coll = db['priceCollection']
    sprites = db['sprites']
    
    imp = ScgImports(datestring, storeName, sprites, delimiter)
    
    dateQueryParam = {"date":datestring, "store":storeName}
    print 'date query',dateQueryParam
    if test_flag:
        results = imp.parseFile(fileToUse)
        for result in results:
            print result
    else:
        if coll.find(dateQueryParam).count() == 0:
            results = imp.parseFile(fileToUse)
            coll.insert(results)
            for post in coll.find(dateQueryParam).limit(2).sort("name"):
                print post
        else:
            count = coll.find(dateQueryParam).count()
            print count, "listings exist for that date!"
    
    #"""
