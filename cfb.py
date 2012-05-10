from BeautifulSoup import BeautifulSoup
from datetime import date
import time, re, argparse, sys, urllib2, inspect

class CardInfo:
        def __init__(self, set, name, price, quantity=None):
            self.set = set
            self.name = name
            self.price = price
            self.quantity = quantity
            
        def getString(self, delimiter = ","):
            result = str(self.set) + delimiter + str(self.name) + delimiter + str(self.price) + delimiter + str(self.quantity)
            return result

class CFBParser:
    def __init__(self, setId, verbose=False):
        self.pageToken = "PAGE_NUM"
        self.setToken = "SET_TOKEN"
        self.baseURL = "http://store.channelfireball.com/advanced_search?page="+self.pageToken+"&search[sort]=name&search[direction]=ascend&search[category_ids_with_descendants][]="+self.setToken+"&buylist_mode=0&search[in_stock]=0&commit=Search&search[with_descriptor_values][256][]=Regular&search[variants_with_identifier][14][]=NM-Mint&search[variants_with_identifier][15][]=English"
        self.verbose = verbose
        self.setId = setId
        self.curPage = 1
        
    def handleSet(self):
        return self.getCardData(self.getPageData(self.baseURL.replace(self.setToken, str(self.setId)).replace(self.pageToken, str(self.curPage))))
    
    def getPageData(self, aSetURL):
        html = urllib2.urlopen(aSetURL).read()
        if self.verbose:
            print "Downloaded url:\t", aSetURL
        time.sleep(1)
        return html
    
    def getCardData(self, htmlData):
        ret = []
        soup = BeautifulSoup(htmlData)
        dataDiv = None
        try:
            dataDiv = soup.findAll(name="div", attrs={"class":"products"}, limit=1)[0]
        except IndexError:
            return ret
        dataTable = dataDiv.findAll(name="table", attrs={"id":"products"}, limit=1)[0]
        trs = dataTable.findAll(name="tr", attrs={"class":"product_row "})
        for tr in trs:
            dataTD = tr.findAll(name="td",limit=2)[1]
            name = dataTD.findAll(name="a",limit=1)[0].text
            infoTDs = dataTD.findAll(name="tr",attrs={"class":"variantRow"})[0].findAll(name="td")
            spanSetCond = infoTDs[0].findAll(name="span", limit=2)
            setName = spanSetCond[0].text.strip()
            cond = spanSetCond[1].text.strip()
            
            price = infoTDs[1].text.strip()
            qty = infoTDs[2].text.strip()[2:]
            ret.append(CardInfo(setName, name, price, qty))
        #failnext = dataDiv.findAll(name="span",attr={"class":"disabled next_page"})
        #print failnext
        #if len(failnext) == 0:
        self.curPage+=1
        print "Paginating to page", self.curPage
        ret.extend(self.handleSet())
        
        return ret

def muxSets(setList, verbose=False):
    ret = []
    for cur in setList:
        curParser = CFBParser(cur, verbose)
        ret.append(curParser.handleSet())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape sell data from CFB website to the given file.')
    parser.add_argument('-v', action='store_true', help='Verbose flag')
    parser.add_argument('-f', help="File directory to download data to.")
    args = vars(parser.parse_args())
    
    fullFileDirectory = "cfb/"
    #verbose = False
    verbose = True
    
    if args['v']:
        verbose = args['v']
    if args['f'] != None:
        fullFileDirectory = args['f']
    
    
    today = date.today()
    sets = [616]
    parser = CFBParser(verbose)
    setResults = muxSets(sets)
    for curSet in setResults:
        print len(curSet)
        for card in curSet:
            if verbose:
                print card.getString("\t")
