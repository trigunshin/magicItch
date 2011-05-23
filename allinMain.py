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
            #return "\"" + str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price) + "\", \"" +str(self.quantity)+ "\""
            return result
        
        """    
        def getString(self):
            #return "\"" + str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price) + "\""
            return "\"" + str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price) + "\", \"" +str(self.quantity)+ "\""
        """

class HtmlReader:
    def __init__(self, url):
        self.url = url

    def readHtml(self):
        file = urllib2.urlopen(self.url)
        return file.read();

class SCGURLBuilder:
        def __init__(self):
            self.baseURL = "http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[TOKEN]=TOKEN&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results"
            self.codeIndex = 0
            self.nameIndex = 1
            
        def getSetURLs(self, aSetIDList):
            urlList = []
            for set in aSetIDList:
                currentURL = self.baseURL.replace('TOKEN', set[self.codeIndex])
                urlList.append(currentURL)
                #print set[self.nameIndex] +"\t\t" + set[self.codeIndex]
            return urlList

class SCGSetHashBuilder:
    def __init__(self):
        self.scgUrl = "http://sales.starcitygames.com/spoiler/spoiler.php"
        self.codeRegex = re.compile("t\=a\&amp\;cat\=(\d{4})", re.M|re.S)

    def build(self):
        html = HtmlReader(self.scgUrl).readHtml()
        soup = BeautifulSoup(html)
        inputs = soup.findAll('input',{'class':re.compile('childbox magic.+')})
        list = []
        for input in inputs:
            info=[input['value'],input.nextSibling.strip()]
            list.append(info)
        self.setCodes = list
        return self

class SCGSpoilerParser:
    def __init__(self, verboseFlag=False):
        self.verbose = verboseFlag
        self.cardNameRegex = re.compile("\">(.+)", re.DOTALL)
        self.cardSetRegex = re.compile("(.+) Singles", re.DOTALL)
        #next link info
        self.nextLinkText = "Next"
        #indeces for card row info
        self.nameIndex = 0
        self.setIndex = 1
        self.priceIndex = 8
        self.quantIndex = 7
        #which table row contains the pagination links (1,2,3, next...)
        self.linkIndex = 1
        #The length>9 is a filter case for non-regular card info rows
        self.cardInfoArraySize = 9
        self.notInStockString = "Out of Stock"

    def getAllSetInfo(self):
        setBuilder = SCGSetHashBuilder()
        setBuilder.build()
        urls = SCGURLBuilder()
        urlList = urls.getSetURLs(setBuilder.setCodes)
        allCardInfo = []
        for url in urlList:
            allCardInfo += self.parseSetPageResults(url)
        return allCardInfo

    def parseSetPageResults(self, aSetURL):
        # download the page
        user_agent = 'Mozilla/5 (Solaris 10) Gecko'
        headers = { 'User-Agent' : user_agent }
        response = urllib2.urlopen(aSetURL)
        html = response.read()
        if self.verbose:
            print "Downloaded url:\t", aSetURL
        return self.getSetInfo(html)
    
    def getSetInfo(self, aPageSource):
        infoList = []
        soup = BeautifulSoup(aPageSource)
        trs = soup.findAll("tr", {"class":re.compile("deckdbbody*")})
        for tr in trs:
            tds = tr.findAll("td")
            info = scg.getCardInfo(tds)
            if self.verbose:
                print info.getString()
            if info.set != None:
                infoList.append(info)
        nextPageURL = self.getNextPage(soup)
        if nextPageURL != None:
            infoList += self.parseSetPageResults(nextPageURL)
        return infoList

    def getNextPage(self, aSoup):
        link = None
        aTRSoup = aSoup.findAll("tr")
        if len(aTRSoup) > 0:
            anchors = aTRSoup[self.linkIndex].findAll("a")
            for anchor in reversed(anchors):#next is usually the last link
                if anchor.text.find(self.nextLinkText) >= 0:
                    link = anchor["href"]
                    break
        return link

    def getPageLinks(self, aTRSoup):
        linkList = []
        anchors = aTRSoup[self.linkIndex].findAll("a")
        for anchor in anchors:
            if anchor.text.startswith("["):
                pageLink = anchor['href']
                linkList.append(pageLink)
        return linkList
    
    def getCardInfo(self, aTDSoup):
        if(len(aTDSoup) > self.cardInfoArraySize):
            name = self.getName(aTDSoup)
            price = self.getPrice(aTDSoup)
            set = self.getSet(aTDSoup)
            quant = self.getQuantity(aTDSoup)
        
        return CardInfo(set, name, price, quant)
        
    def getName(self, aTDSoup):
        nameTD = aTDSoup[self.nameIndex]
        anchors = nameTD.findAll("a")
        for anchor in anchors:
            matches = self.cardNameRegex.findall(anchor.text)
            if len(matches) > 0:
                return matches.pop().strip()
                
    def getSet(self, aTDSoup):
        setTD = aTDSoup[self.setIndex]
        return setTD.text
                    
    def getPrice(self, aTDSoup):
        priceTD = aTDSoup[self.priceIndex]
        return priceTD.text

    def getQuantity(self, aTDSoup):
        quant = aTDSoup[self.quantIndex]
        quantValue = quant.text
        if(self.notInStockString in quantValue):
            quantValue=None
        return quantValue

    def parseAllSets(self, aSetList):
        setIDIndex = 0
        setName = 1
        baseURL = "http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[TOKEN]=TOKEN&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results"
        for set in aSetList:
            currentURL = baseURL.replace('TOKEN', str(set[setIDIndex]))
            infoList = scg.parseSetPageResults(currentURL)
            som = open("test/scg_"+set[setName]+".csv", 'w')
            for info in infoList:
                #print info.getString()
                som.write(info.getString()+"\n")
            som.close()
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape sell data from SCG website to the given file.')
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-f')
    args = vars(parser.parse_args())
    
    fullFileDirectory = "SCG/"
    verbose = False
    
    if args['v']:
        verbose = args['v']
    if args['f'] != None:
        fullFileDirectory = args['f']
    
    scg = SCGSpoilerParser(verbose)
    allSetInfo = scg.getAllSetInfo()
    
    today = date.today()
    tabFileDest = fullFileDirectory+"scg_"+today.isoformat()+".tsv"
    
    print "Starting file output to: ", tabFileDest
    
    tab = open(tabFileDest, 'w')
    for card in allSetInfo:
        tab.write(card.getString("\t")+"\n")
    tab.close()
