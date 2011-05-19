'''
Created on Apr 22, 2011

@author: trigunshin
'''
import sqlite3,csv
from datetime import date

class scgImports(object):
    '''
    classdocs
    '''

    def __init__(self, aDate):
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
    
    def getStoreID(self):
        if self.storeID is None:
            self.storeID = self.db.execute("SELECT a.id FROM store a where a.name like ? limit 1", ('%'+self.storeName+'%',)).fetchone()[0]
        return self.storeID
    
    def updateStoreListing(self):
        data = (1, self.storeName,self.storeURL)
        self.db.execute("INSERT OR IGNORE INTO store VALUES(?,?,?)", data)
        self.db.commit()
       
    def updateCardListings(self, aCSVFile):
        with open(csvToUse, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                name = row[self.nameIndex]
                set = row[self.setIndex]
                self.db.execute("INSERT OR IGNORE INTO card select ?,?,s.id from cardset s where s.name like ? and s.storeid = ?",
                                 [None, name, set, self.getStoreID()])
            self.db.commit()
        
    def updatePriceListings(self, aCSVFile):
        with open(csvToUse, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                name = row[self.nameIndex]
                set = row[self.setIndex]
                quant = row[self.quantIndex]
                price = row[self.priceIndex]
                self.db.execute("INSERT OR REPLACE INTO price select ?,?,?,?,c.id from card c where c.name like ? and c.setID in (\
                                    select s.id from cardset s where s.name like ? and s.storeid = ?)",
                                 [None, quant, price, self.datestring, name, set, self.getStoreID()])
            self.db.commit()
        
    def getUniqueSetNames(self, aCSVFile):
        setListing = []
        with open(csvToUse, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                setListing.append(row[imp.setIndex])
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
        #db.execute("Delete from cardset")
        #db.execute("Delete from card")
        #db.execute("Delete from store")
        db.commit()
        db.close()
        
if __name__ == '__main__':
    datestring = "2011-05-16"
    csvToUse = "/Users/trigunshin/mtgPrice/scg/scg_"+datestring+".csv"
    today = date.today().isoformat()
    
    imp = scgImports(datestring)
    imp.connect()
    
    imp.updateStoreListing()
    print "Updated store listing for",imp.storeName
    setList = imp.getUniqueSetNames(csvToUse)
    print "Found", len(setList), "unique sets"
    imp.updateSetListings(setList)
    print "Updated set listings"
    print "Updating card listings"
    #imp.updateCardListings(csvToUse)
    print "Updated card listings"
    imp.updatePriceListings(csvToUse)
    imp.close()
    
    imp.connect()
    db = sqlite3.connect(imp.databaseLocation)
    print db.execute("SELECT a.id FROM store a where a.name like 'Star%'").fetchall()
    print db.execute("SELECT count(s.name) FROM cardset s").fetchall()
    imp.close()
    