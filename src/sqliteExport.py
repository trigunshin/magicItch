'''
Created on Apr 22, 2011

@author: trigunshin
'''
from datetime import date
import sqlite3,csv,getopt,sys,argparse

class scgImports(object):
    '''
    classdocs
    '''

    def __init__(self, aDate, aDelimiter = ","):
        self.delimiter = aDelimiter
        self.datestring = aDate
        self.databaseLocation = '/Users/trigunshin/dev/magicItch/db/sqliteDB'
        self.db = None
        self.setIndex = 0
        self.nameIndex = 1
        self.priceIndex = 2
        self.quantIndex = 3
        self.storeName = "StarCity Games"
        self.storeURL = "http://www.starcitygames.com/"
        self.storeID = None
    
    def connect(self):
        self.db = sqlite3.connect(self.databaseLocation)
    
    def close(self):
        self.db.close()
        
    def getReader(self, file):
        return csv.reader(file, delimiter=self.delimiter)
    
    def getStoreID(self):
        if self.storeID is None:
            self.storeID = self.db.execute("SELECT a.id FROM store a where a.name like ? limit 1", ('%'+self.storeName+'%',)).fetchone()[0]
        return self.storeID
    
    def updateStoreListing(self):
        data = (1, self.storeName,self.storeURL)
        self.db.execute("INSERT OR IGNORE INTO store VALUES(?,?,?)", data)
        self.db.commit()
       
    def updateCardListings(self, aFile):
        with open(aFile, 'rb') as f:
            reader = self.getReader(f)
            for row in reader:
                name = row[self.nameIndex]
                set = row[self.setIndex]
                self.db.execute("INSERT OR IGNORE INTO card select ?,?,s.id from cardset s where s.name like ? and s.storeid = ?",
                                 [None, name, set, self.getStoreID()])
            self.db.commit()
        
    def updatePriceListings(self, aFile):
        with open(aFile, 'rb') as f:
            reader = self.getReader(f)
            for row in reader:
                name = row[self.nameIndex]
                set = row[self.setIndex]
                quant = row[self.quantIndex]
                price = row[self.priceIndex]
                self.db.execute("INSERT OR REPLACE INTO price select ?,?,?,?,c.id from card c where c.name like ? and c.setID in (\
                                    select s.id from cardset s where s.name like ? and s.storeid = ?)",
                                 [None, quant, price, self.datestring, name, set, self.getStoreID()])
            self.db.commit()
        
    def getUniqueSetNames(self, aFile):
        setListing = []
        with open(aFile, 'rb') as f:
            reader = self.getReader(f)
            for row in reader:
                setListing.append(row[self.setIndex])
        return list(set(setListing))
    
    def updateSetListings(self, setList):
        for singleSet in setList:
            self.db.execute("INSERT OR IGNORE INTO cardset VALUES(?,?,?)", [None, singleSet, self.getStoreID()])
        self.db.commit()
    
    def getPrice(self, aTDSoup):
        priceTD = aTDSoup[self.priceIndex]
        return priceTD.text
    
    def clearDB(self, adbLocation):
        db = sqlite3.connect(adbLocation)
        db.execute("Delete from cardset")
        db.execute("Delete from card")
        db.execute("Delete from store")
        db.execute("Delete from price")
        db.commit()
        db.close()
        
if __name__ == '__main__':
    verbose = False
    datestring = "2011-05-19"
    delimiter = "\t"
    fileSuffix = ".tsv"
    fullFileDirectory = "/Users/trigunshin/mtgPrice/scg/"
    #datestring = date.today().isoformat()

    parser = argparse.ArgumentParser(description='Upload a scg Xsv file to the sqlite db.')
    parser.add_argument('-f')
    parser.add_argument('-d')
    parser.add_argument('-t', action='store_true')
    parser.add_argument('-c', action='store_true')
    
    args = vars(parser.parse_args())
    
    if args['t']:
        delimiter = "\t"
        fileSuffix = ".tsv"
    elif args['c']:
        delimiter = ","
        fileSuffix = ".csv"
    if args['d'] != None:
        datestring = args['d'] 
    if args['f'] != None:
        fullFileDirectory = args['f']
    
    fileName = "scg_"+datestring+fileSuffix
    fileToUse = fullFileDirectory + fileName

    #imp = scgImports(datestring)
    #imp.clearDB(*)
    """
    #Block to check an error case
    imp = scgImports(datestring)
    with open(fileToUse, 'rb') as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if row[1].find("Elesh") > 0:
                    #print row[1]
                    break
    #"""
    #"""
    imp = scgImports(datestring, delimiter)
    imp.connect()
    
    imp.updateStoreListing()
    print "Updated store listing for",imp.storeName
    setList = imp.getUniqueSetNames(fileToUse)
    print "Found", len(setList), "unique sets"
    imp.updateSetListings(setList)
    print "Updated set listings"
    print "Updating card listings"
    imp.updateCardListings(fileToUse)
    print "Updated card listings"
    imp.updatePriceListings(fileToUse)
    imp.close()
    #"""
    """
    imp = scgImports(datestring, delimiter)
    imp.connect()
    db = sqlite3.connect(imp.databaseLocation)
    print db.execute("SELECT a.id FROM store a where a.name like 'Star%'").fetchall()
    print db.execute("SELECT count(s.name) FROM cardset s").fetchall()
    print db.execute("select * from card c where c.name like \"%Elesh%\"").fetchall()
    imp.close()
    #"""
    