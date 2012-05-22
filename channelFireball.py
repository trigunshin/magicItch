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
        self.statusText = "English, NM-Mint"
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
        try:
            dataDiv = soup.findAll(name="div", attrs={"class":"products"}, limit=1)[0]
            dataTable = dataDiv.findAll(name="table", attrs={"id":"products"}, limit=1)[0]
            trs = dataTable.findAll(name="tr", attrs={"class":"product_row "})
        except IndexError:
            return ret
        for cur in trs:#get product data row
            name = cur.findAll(name="td", limit=2)[1].findAll(name="a",limit=1)[0].text
            for tr in cur.findAll(name="tr", attrs={"class":"variantRow"}):#get condition info rows
                infoTDs = tr.findAll(name="td")
                spanSetCond = infoTDs[0].findAll(name="span", limit=2)
                
                cond = spanSetCond[1].text.strip()
                if cond == self.statusText:
                    setName = spanSetCond[0].text.strip()
                    price = infoTDs[1].text.strip()
                    qty = infoTDs[2].text.strip()[2:]
                    ret.append(CardInfo(setName, name, price, qty))
                else:
                    if verbose:
                        print "skipping wrong quality"
        self.curPage+=1
        if verbose:
            print "Paginating to page", self.curPage
        ret.extend(self.handleSet())
        
        return ret

def muxSets(setList, verbose=False):
    ret = []
    for cur in setList:
        print "Parsing set", cur['name']
        curParser = CFBParser(cur['id'], verbose)
        ret.append(curParser.handleSet())
        break
    return ret

class CFBSetGetter:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.setURL = "http://store.channelfireball.com/advanced_search"
    
    def getPageData(self, url):
        html = urllib2.urlopen(url).read()
        if self.verbose:
            print "Downloaded url:\t", self.setURL
        time.sleep(1)
        return html
    
    def getSetIds(self):
        ret = []
        html = self.getPageData(self.setURL)
        soup = BeautifulSoup(html)
        sel = soup.findAll(name="select",attrs={"id":"search_category_ids_with_descendants","name":"search[category_ids_with_descendants][]"}, limit=1)[0]
        options = sel.findAll(name="option")
        for cur in options:
            #print cur.text[0:5]
            if cur.text[0:5] == "---- ":
                ret.append({"id":cur['value'],"name":cur.text[5:]})
            elif cur.text == "Sets":#terminate here to only parse singles
                if self.verbose:
                    print "Hit sets, returning with results of len", len(ret)
                break
        return ret

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape sell data from CFB website to the given file.')
    parser.add_argument('-v', action='store_true', help='Verbose flag')
    parser.add_argument('-f', help="File directory to download data to.")
    args = vars(parser.parse_args())
    
    fullFileDirectory = "cfb/"
    verbose = False
    #verbose = True
    
    if args['v']:
        verbose = True
    if args['f'] != None:
        fullFileDirectory = args['f']
    
    
    today = date.today()
    sets = CFBSetGetter(verbose).getSetIds()
    #sets = [616]
    #print len(sets)
    
    parser = CFBParser(verbose)
    setResults = muxSets(sets)
    
    today = date.today()
    tabFileDest = fullFileDirectory+"cfb_"+today.isoformat()+".tsv"
    
    print "Starting file output to: ", tabFileDest
    #print "Sets",setResults
    tab = open(tabFileDest, 'w')
    for curSet in setResults:
        for card in curSet:
            if verbose:
                print card.getString("\t")
            tab.write(card.getString("\t")+"\n")
    tab.close()
    
    """
    """
