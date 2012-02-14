import pymongo
from pymongo import Connection
from bintrees import AVLTree
import sys,argparse,jsonpickle,math
from time import time,clock

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

    def getCSVHeader(self):
        #ret = ''.join([`key`+',' for key in self.__dict__.iterkeys()])
        #return ret.rstrip(",")
        return "name,set,priceChange,price,quantityChange,quantity"

    def toString(self, csvflag=False):
        if csvflag:
            return toCSVString()
        return ''.join([`key`+":"+`value`+"," for key, value in self.__dict__.iteritems()])

    def toCSVString(self):
        #ret = ''
        #ret.join([`key`+',' for key in self.__dict__.iterkeys()])
        #ret.join('\n')
        #ret.join([`value`+',' for key, value in self.__dict__.iteritems()])
        #print "iterkeys",self.__dict__.iteritems(),"\n\t",self.__dict__.itervalues()
        #return ret.rstrip(",")
        #return ret
        p = str(self.endPrice)
        p = p[:-2] + "." + p[-2:]
        pc = str(self.priceChange)
        pc = pc[:-2] + "." + pc[-2:]
        return self.name+"," + self.set + "," + pc + "," + \
            p + "," + str(self.quantChange) + "," + str(self.endQuant)
    
    def toHumanString(self):
        p = str(self.endPrice)
        p = p[:-2] + "." + p[-2:]
        pc = str(self.priceChange)
        pc = pc[:-2] + "." + pc[-2:]
        return self.name + " from set " + self.set + " changed price by " + pc + " dollars to " + \
            p + " with a quantity change of " + str(self.quantChange) + " to " + str(self.endQuant) + "."

class ReportGenerator(object):
    def __init__(self,start,end,store,filter):
        self.storeName = store
        self.startDate = start
        self.endDate = end
        self.dbName = 'testCards'
        self.collName = 'priceCollection'
        if not filter:
            self.reportFilter = self.priceChange
        else:
            self.reportFilter = self.quantChange

    def generate(self):
        c = Connection()
        db = c[self.dbName]
        coll = db[self.collName]
        
        fullResultSet = []
        for currSet in coll.distinct("set"):
            start = coll.find({"store":self.storeName, "date":startDate, "set":currSet}).sort("name")
            end = coll.find({"store":self.storeName, "date":endDate, "set":currSet}).sort("name")
            startTree = self.getTree(start)
            endTree = self.getTree(end)
            result = self.getTreeResult(startTree,endTree)
            filteredResult = [res for res in result if res != None]
            fullResultSet = fullResultSet+filteredResult
        sortedResult = sorted(fullResultSet, reverse=True,key=lambda pricereport: math.fabs(pricereport.priceChange))
        return sortedResult
    
    def getTreeResult(self, startTree, endTree):
        g = startTree.intersection(endTree)
        reportList = [self.getReport(startTree.get(k),endTree.get(k)) for k in list(g.keys())]

        return reportList

    def getTree(self, objectList):
        return AVLTree([(v['name'],v) for v in objectList])

    def priceChange(self, report):
        if report.priceChange == 0:
            return False
        return True

    def quantChange(self, report):
        if report.quantChange == 0:
            return False
        return True

    def getReport(self,a,b):
        report = PriceReport(a,b)
        if self.reportFilter(report):
            return report
        return None
#        if report.priceChange == 0:
#            return None
        return report

if __name__ == '__main__':
    storeName = "StarCity Games"
    storeShort = 'scg'
    startDate = None
    endDate = None
    humanFormat = False
    outputLocation = None
    filename = None
    filterQuantity = False
    outputDir = ""
    sendDB = True

    parser = argparse.ArgumentParser(description='Use the mongo db to generate a price report.')
    parser.add_argument('-s', help="Start date in YYYY-MM-DD", required=True)
    parser.add_argument('-e', help="End date in YYYY-MM-DD", required=True)
    parser.add_argument('-o', help="Output file directory. If not given, will use stdout")
    parser.add_argument('-n', help="Output filename. If not given, will use a scgSTART_END format.")    
    parser.add_argument('-c', action='store_true', help="Store in human-readable format.")
    parser.add_argument('-q', action='store_true', help="Apply quantity filter instead of price filter.")
    parser.add_argument('-d', action='store_false', help="Don't send price report to the database.")
    parser.add_argument('-r', help="Set store name.")
    args = vars(parser.parse_args())

    if args['r']:
        storeName = args['r']
    if args['s']:
        startDate = args['s']
    if args['e']:
        endDate = args['e']
    if args['c'] != None:
        humanFormat = args['c']
    if args['q'] != None:
        filterQuantity = args['q']
    if args['n'] != None:
        filename = args['n']
    if args['d']:
        sendDB = args['d']
    if args['o'] != None:
        outputDir = args['o']
        if not outputDir.endswith('/'):
            outputDir = outputDir+'/'

    if filename is None:
        filename = storeShort.replace(' ','')+startDate+"_"+endDate+".tsv"

    outputLocation = outputDir + filename
    print "Outputting data to: ", outputLocation
    
    gen = ReportGenerator(startDate, endDate,storeName, filterQuantity)
    diffs = gen.generate()

    c=Connection()
    db=c[gen.dbName]
    diffCollection=db["priceReports"]

    if outputLocation is None:
        for result in diffs:
            print result.toString()
            diff = [{"cardName":result.name,"cardSet":result.set,"priceChange":result.priceChange,"endPrice":result.endPrice,"endDate":result.end,"store":result.store}]
#            print diff
            diffCollection.insert(diff)

    else:
        with open(outputLocation, 'w') as f:
            if not humanFormat:
                f.write(diffs[0].getCSVHeader())
                f.write("\r\n")
            for result in diffs:
#                f.write(result.toString())
#                print diff
                if sendDB:
                    diff = [{"cardName":result.name,"cardSet":result.set,"priceChange":result.priceChange,"endPrice":result.endPrice,"endDate":result.end,"store":result.store}]
                    diffCollection.insert(diff)
                if humanFormat:
                    f.write(result.toHumanString())
                else:
                    #f.write(jsonpickle.encode(result))
                    f.write(result.toCSVString())
                f.write("\r\n")
