from BeautifulSoup import BeautifulSoup
from datetime import date
import time, re, argparse, sys, urllib, urllib2, inspect, csv

class URLRequest:
    def __init__(self):
        user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'
        self.headers = { 'User-Agent' : user_agent }
        
    def urlopen(self, url):
        req = urllib2.Request(url, None, self.headers)
        return urllib2.urlopen(req).read()

class CardInfo:
        def __init__(self, set, name, price, quantity=None, rarity=None):
            self.set = set
            self.name = name
            self.price = price
            self.quantity = quantity
            self.rarity = rarity
            
        def getString(self, delimiter = ","):
            result = str(self.set) + delimiter + str(self.name) + delimiter + str(self.price) + delimiter + str(self.quantity) + str(self.rarity)
            #return "\"" + str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price) + "\", \"" +str(self.quantity)+ "\""
            return result
        
        """
        def getString(self):
            #return "\"" + str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price) + "\""
            return "\"" + str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price) + "\", \"" +str(self.quantity)+ "\""
        """

class SCGURLBuilder:
        def __init__(self):
            self.baseURL = "http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[TOKEN]=TOKEN&format=&c_all=All&multicolor=&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=3&numpage=100&action=Show+Results"
            self.codeIndex = 0
            self.nameIndex = 1
            
        def getSetURLs(self, aSetIDList):
            urlList = []
            for set in aSetIDList:
                currentURL = self.baseURL.replace('TOKEN', set[self.codeIndex])
                urlList.append(currentURL)
            return urlList

class SCGSetHashBuilder:
    def __init__(self):
        self.urlOpener = URLRequest()
        self.scgUrl = "http://sales.starcitygames.com/spoiler/spoiler.php"
        self.codeRegex = re.compile("t\=a\&amp\;cat\=(\d{4})", re.M|re.S)

    def build(self):
        html = self.urlOpener.urlopen(self.scgUrl)
        soup = BeautifulSoup(html)
        inputs = soup.findAll('input',{'class':re.compile('childbox magic.+')})
        list = []
        for input in inputs:
            info=[input['value'],input.nextSibling.strip()]
            list.append(info)
        self.setCodes = list
        return self

class SCGSpoilerParser:
    def __init__(self, mappingGenerator, verboseFlag=False):
        self.urlOpener = URLRequest()
        self.cleanNamePattern = " \(Pre-Order.+?\)"
        self.verbose = verboseFlag
        self.cardNameRegex = re.compile("\">(.+)", re.DOTALL)
        self.cardSetRegex = re.compile("(.+) Singles", re.DOTALL)
        #next link info
        self.nextLinkText = "Next"
        #indeces for card row info
        self.nameIndex = 0
        self.setIndex = 1
        #self.manaIndex = 2
        #self.typeIndex = 3
        #self.ptIndex = 4
        self.rarityIndex = 5
        #self.conditionIndex = 6
        self.quantIndex = 7
        self.priceIndex = 8
        #which table row contains the pagination links (1,2,3, next...)
        self.linkIndex = 1
        #The length>9 is a filter case for non-regular card info rows
        self.cardInfoArraySize = 9
        self.notInStockString = "Out of Stock"
        self.mapgen = mappingGenerator

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
        html = self.urlOpener.urlopen(aSetURL)
        if self.verbose:
            print "Downloaded url:\t", aSetURL
        return self.getSetInfo(html)
    
    def getSetInfo(self, aPageSource):
        infoList = []
        valueMap = self.mapgen.generateValueMap(aPageSource)
        soup = BeautifulSoup(aPageSource)
        trs = soup.findAll("tr", {"class":re.compile("deckdbbody*")})
        for tr in trs:
            tds = tr.findAll("td")
            info = scg.getCardInfo(tds, valueMap)
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
        tables = aSoup.findAll("table")
        if len(tables) > 0:
            paginationTDs = tables[len(tables)-1].findAll("td",{"align":"center"})
            if len(paginationTDs) > 1:
                anchors = paginationTDs[1].findAll("a")
                for anchor in anchors:
                    if anchor.text.find(self.nextLinkText) >= 0:
                        link = anchor["href"]
                        if self.verbose: print "next link found",link
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
    
    def getCardInfo(self, aTDSoup, aValueMap):
        if(len(aTDSoup) > self.cardInfoArraySize):
            name = self.getName(aTDSoup)
            price = self.getPrice(aTDSoup, aValueMap)
            setName = self.getSet(aTDSoup)
            quant = self.getQuantity(aTDSoup, aValueMap)
            rarity = self.getRarity(aTDSoup, aValueMap)
        
        return CardInfo(setName, name, price, quant, rarity=rarity)
        
    def cleanName(self, aNameString):
        return re.sub(self.cleanNamePattern, "", aNameString)

    def getName(self, aTDSoup):
        nameTD = aTDSoup[self.nameIndex]
        anchors = nameTD.findAll("a")
        for anchor in anchors:
            matches = self.cardNameRegex.findall(anchor.text)
            if len(matches) > 0:
                return self.cleanName(matches.pop().strip())
                
    def getSet(self, aTDSoup):
        setTD = aTDSoup[self.setIndex]
        return setTD.text
    
    def getRarity(self, aTDSoup):
        rarityTD = aTDSoup[self.rarityIndex]
        return rarityTD.text
                    
    def getPrice(self, aTDSoup, aValueMap):
        priceTD = aTDSoup[self.priceIndex]
        return self.getSpriteValue(priceTD, aValueMap)

    def getQuantity(self, aTDSoup, aValueMap):
        quantTD = aTDSoup[self.quantIndex]
        quantValue = quantTD.text
        if(self.notInStockString in quantValue):
            quantValue=None
        else:
            quantValue = self.getSpriteValue(quantTD, aValueMap)
        return quantValue
    
    def getSpriteValue(self, aTDTag, aValueMap):
        retval = []
        divs = aTDTag.findAll("div", {'class':True})
        #return ''.join([curValue for curValue in [aValueMap[cur] for cur in [d['class'].split(' ') for d in divs]] if curValue != None])
        
        for d in divs:
            for cur in d['class'].split(' '):
                try:
                    curValue = aValueMap[cur]
                    retval.append(curValue)
                    #if self.verbose: print "Appended value", curValue
                except KeyError:
                    pass
        return ''.join(retval)
    
class MappingGenerator:
    def __init__(self, path, delimiter=',', verbose=False):
        self.path = path
        self.delimiter = delimiter
        self.offsetIndexes = [0,1,2]
        self.valueIndex = 3
        self.cssPattern = "\.([\S]+2) \{.+?:(.+?)[\s]"
        self.cssRegex = re.compile(self.cssPattern, re.DOTALL)
        self.verbose = verbose
    
    def generateOffsetMap(self):
        offsetValueMap = {}
        print self.path
        reader = csv.reader(open(self.path, 'r'), delimiter=self.delimiter)
        reader.next()#skip header line
        for row in reader:
            for val in self.offsetIndexes:
                offsetValueMap[row[val]] = row[self.valueIndex]
        self.offsetValueMap = offsetValueMap
        if self.verbose: print "offsetValMap",offsetValueMap
        return offsetValueMap
    
    def generateValueMap(self, html):
        patternValueMap = {}
        soup = BeautifulSoup(html)
        styleInfo = soup.findAll("style")[0]
        styleText = styleInfo.text
        
        matches = self.cssRegex.findall(styleText)
        if matches:
            if self.verbose: print "Matches"
            for cur in matches:
                if verbose: print "\tPattern:", cur[0], "\tOffset:", cur[1]
                #TODO: if no mapping found, handle / raise error here
                patternValueMap[cur[0]] = self.offsetValueMap[cur[1]]
                patternValueMap[cur[0][:6]] = self.offsetValueMap[cur[1]]#we want to add a match w/o the trailing '2'
        else:
            if self.verbose: print "No matches!"
        if self.verbose: print "patValMap",patternValueMap
        
        return patternValueMap

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape sell data from SCG website to the given file.')
    parser.add_argument('-v', action='store_true', help='Verbose flag')
    parser.add_argument('-f', help="File directory to download data to.")
    args = vars(parser.parse_args())
    
    fullFileDirectory = "SCG/"
    verbose = False
    mappingFilePath = "src/conf/mappings.csv"
    
    if args['v']:
        verbose = args['v']
    if args['f'] != None:
        fullFileDirectory = args['f']
    
    mapGen = MappingGenerator(mappingFilePath, ',', verbose)
    mapGen.generateOffsetMap()
    scg = SCGSpoilerParser(mapGen, verbose)
    allSetInfo = scg.getAllSetInfo()
    #"""
    today = date.today()
    tabFileDest = fullFileDirectory+"scg_"+today.isoformat()+".tsv"
    
    print "Starting file output to: ", tabFileDest
    
    tab = open(tabFileDest, 'w')
    for card in allSetInfo:
        tab.write(card.getString("\t")+"\n")

    tab.close()
    #"""
