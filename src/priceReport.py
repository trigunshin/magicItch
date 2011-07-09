'''
Created on May 5, 2011

@author: trigunshin
'''
import datetime
import sqlite3,csv
import time, re, sys, urllib2,argparse

class PriceResult:
    def __init__(self, aRowResult):
        self.setName = aRowResult[0]
        self.cardName = aRowResult[1]
        self.firstCardPrice = int(float(aRowResult[2].strip(" \"\$"))*100)
        self.firstCardQuantity = aRowResult[3]
        self.firstCardDate = aRowResult[4]
        self.secondCardPrice = int(float(aRowResult[5].strip(" \"\$"))*100)
        self.secondCardQuantity = aRowResult[6]
        self.secondCardDate = aRowResult[7]
    
    def toString(self):
        #return "\"" + str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price) + "\", \"" +str(self.quantity)+ "\""
        diff = str(self.firstCardPrice - self.secondCardPrice)
        #return self.setName + self.cardName + str(self.firstCardPrice) + self.firstCardDate + str(self.secondCardPrice) + diffString
        return str(self.firstCardPrice) + ", " + diff + ", " + self.setName+ ", " + self.cardName+ ", " + self.firstCardDate+", " + self.secondCardDate

if __name__ == '__main__':
    setName = 0
    cardName = 1
    firstCardPrice = 2
    firstCardQuantity = 3
    firstCardDate = 4
    secondCardPrice = 5
    secondCardQuantity = 6
    secondCardDate = 7
    
    startDate = None
    endDate = None
    fileLoc = None
    dbFileLoc = '/Users/trigunshin/dev/magicItch/db/sqliteDB'
    

    parser = argparse.ArgumentParser(description='Upload a scg Xsv file to the sqlite db.')
    parser.add_argument('-o')
    parser.add_argument('-s')
    parser.add_argument('-e')
    parser.add_argument('-b')

    
    args = vars(parser.parse_args())
    
    if args['o'] != None:
        fileLoc = args['o']
    else:
        fileLoc = sys.stdout
    if args['s'] != None:
        startDate = args['s']
    if args['e'] != None:
        endDate = args['e']
    if args['b'] != None:
        dbFileLoc = args['b']    
    

    priceReport = "select s.Name, c.Name, p.price, p.quantity, p.date, p1.price, p1.quantity, p1.date from Card c join Price p on c.id = p.cardID join Price p1 on p1.cardID = p.cardID join CardSet s on c.setID = s.id where p1.price != p.price and p.date like ? and p1.date like ?"
    
    today = datetime.date.today().isoformat()
    
    db = sqlite3.connect(dbFileLoc)
    #print db.execute("SELECT a.id FROM store a where a.name like 'Star%'").fetchall()
    #print db.execute("SELECT count(s.name) FROM cardset s").fetchall()
    #print priceReport
    
#    current = datetime.date.today() + datetime.timedelta(days = 1)
#    yest = datetime.timedelta(days=-1)
    
    """
    for row in db.execute(priceReport, [current,current+yest]).fetchall():
        result = PriceResult(row)
        print result.toString()
        """
    
    print fileLoc
    print dbFileLoc
    with open(fileLoc, 'w') as f:
        for row in db.execute(priceReport, [endDate,startDate]).fetchall():
            #print row
            result = PriceResult(row)
            #print result.toString()
            f.write(result.toString())
    db.close()
