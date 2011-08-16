import pymongo
from pymongo import Connection
from datetime import date
import sys,csv,argparse,jsonpickle,math

class scgImports(object):

    def __init__(self, aDate, aStoreName, aDelimiter = ","):
        self.delimiter = aDelimiter
        self.datestring = aDate
        self.db = None
        self.setIndex = 0
        self.nameIndex = 1
        self.priceIndex = 2
        self.quantIndex = 3
        self.storeName = aStoreName

    def getReader(self, file):
        return csv.reader(file, delimiter=self.delimiter)

    def updatePriceListings(self, aFile, collection):
        with open(aFile, 'rb') as f:
            reader = self.getReader(f)
            for row in reader:
                name = row[self.nameIndex]
                set = row[self.setIndex]
                quant = row[self.quantIndex]
                price = self.parsePrice(row[self.priceIndex])
                val = [{"name":name,"set":set,"store":self.storeName,"quantity":quant,"price":price,"date":self.datestring}]
                collection.insert(val)

    def parsePrice(self, aPriceString):
        a = aPriceString.replace('$', '')
        a = a.replace('.', '')
        a = a.replace(',', '')
        return a

class PriceReport(object):

    def __init__(self, start, end):
        self.set = start['set']
        self.store = start['store']
        self.name = start['name']
        self.start = start['date']
        self.end = end['date']
        self.priceChange = self.getDiff(start['price'], end['price'])
        self.quantChange = self.getDiff(start['quantity'],end['quantity'])
        self.startPrice = start['price']
        self.endPrice = end['price']
        self.startQuant = start['quantity']
        self.endQuant = end['quantity']

    def getDiff(self, start, end):
        startval=start
        endval=end
        if startval == 'None':
            startval= 0
        if endval == 'None':
            endval = 0
        diff = int(endval) - int(startval)
        return diff

    def toString(self):
        return ''.join([`key`+":"+`value`+"," for key, value in self.__dict__.iteritems()])
        
def getSortKey(obj):
    if obj is None:
        return 0
    return obj.priceChange

def getReport(a,b):
#    print a['name'],b['name']
    if a['name']!=b['name']:
        print "BRICKSHIT",a['name'],b['name']
    report = PriceReport(a,b)
    if report.priceChange == 0:
        return None
    return report

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

    c = Connection()
    db = c['testCards']
    coll = db['priceCollection']

    imp = scgImports(datestring, storeName, delimiter)
    
    dateQueryParam = {"date":datestring, "store":storeName}
    
    if coll.find(dateQueryParam).count() == 0:
        imp.updatePriceListings(fileToUse, coll)
        for post in coll.find(dateQueryParam).limit(5).sort("name"):
            print post
    else:
        count = coll.find(dateQueryParam).count()
        print count, "listings exist for that date!"
#    print json.dumps([p.__dict__ for p in ])
#    print jsonpickle.encode(imp)
#    print args
#    print [str(args[a])+str(1) for a in args]
#        print a
