import pymongo
from pymongo import Connection
from bs4 import BeautifulSoup
from datetime import date
import time, re, argparse, sys, urllib, urllib2, inspect, csv, hashlib

class CardInfo:
    def __init__(self, spriteHash, setName, name, price, quantity=None, rarity=None):
        self.encoding = 'utf-8'
        self.failString = "None"
        
        self.spriteHash = spriteHash.encode(self.encoding) if spriteHash else self.failString
        self.setName = setName.encode(self.encoding) if setName else self.failString
        self.name = name.encode(self.encoding) if name else self.failString
        self.price = price.encode(self.encoding) if price else self.failString
        self.quantity = quantity.encode(self.encoding) if quantity else self.failString
        self.rarity = rarity.encode(self.encoding) if rarity else self.failString
        """
        self.setName = setName
        self.name = name
        self.price = price
        self.quantity = quantity
        self.rarity = rarity
        #"""
        
    def getString(self, delimiter = ","):
        result = self.setName + delimiter + \
            self.name + delimiter + \
            self.price + delimiter + \
            self.quantity + delimiter + \
            self.rarity + delimiter + \
            self.spriteHash
        return result
    
class URLRequestGenerator:
    def __init__(self):
        user_agent = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.102011-10-16 20:23:50'
        self.headers = { 'User-Agent' : user_agent }
        
    def urlopen(self, url):
        req = urllib2.Request(url, None, self.headers)
        return urllib2.urlopen(req).read()

class SetLinkBuilder:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.basePageSoupCallers = []
        self.urlOpener = URLRequestGenerator()
        self.scgUrl = "http://sales.starcitygames.com/spoiler/spoiler.php"
        self.symbToken = "SET_TOKEN"
        self.codeToken = "CODE_TOKEN"
        self.urlPattern = "http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s["+self.symbToken+"]="+self.codeToken+"&format=&c_all=All&multicolor=&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=3&numpage=100&action=Show+Results"
    
    def getURLGenerator(self):
        html = self.urlOpener.urlopen(self.scgUrl)
        soup = BeautifulSoup(html)
        urlTuples = self.getURLTuples(soup)
        return self.getURLList(urlTuples)
    
    def getURLList(self, tupleList):
        for cur in tupleList:
            yield self.urlPattern.replace(self.symbToken, cur[0]).replace(self.codeToken, cur[1])
    
    def getURLTuples(self, aSoup):
        section = aSoup.findAll('section',{'id':'content'})[0]
        tbl = section.findAll('table')[1]
        trs = tbl.findAll('tr')
        stable = trs[20].findAll('table')[0]
        strs = stable.findAll('tr')
        inputs = strs[0].findAll('input')[1:]
        #minputs = inputs[0].findAll('input')
        return ( (cur['name'],cur['value']) for cur in inputs if cur['name'] and cur['value'])
    
    def addBasePageSoupCaller(self, aFunc):
        self.basePageSoupCallers.append(aFunc)

class CardInfoParser:
    def __init__(self, urlBuilder, mappingGenerator, spriteFetcher=None, verboseFlag=False, debugFlag=False):
        self.soupCallers = []
        self.urlBuilder = urlBuilder
        self.spriteManager = spriteFetcher
        self.urlOpener = URLRequestGenerator()
        self.cleanNamePattern = " \(Pre-Order.+?\)"
        self.verbose = verboseFlag
        self.debug = debugFlag
        self.cardNameRegex = re.compile("\">(.+)", re.DOTALL)
        self.cardSetRegex = re.compile("(.+) Singles", re.DOTALL)
        #next link info
        self.nextLinkText = " - Next"
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
    
    def addSoupCaller(self, aFunc):
        self.soupCallers.append(aFunc)
    
    def getAllSetInfo(self):
        urlList = self.urlBuilder.getURLGenerator()
        allCardInfo = []
        for url in urlList:
            if self.verbose: print "currently on set url:", url
            allCardInfo.extend(self.parseSetPageResults(url))
            if self.debug: break
        return allCardInfo
    
    def parseSetPageResults(self, aSetURL):
        html = self.urlOpener.urlopen(aSetURL)
        if self.verbose:
            print "Downloaded url:\t", aSetURL
        return self.getSetInfo(html)
    
    def getSetInfo(self, aPageSource):
        infoList = []
        soup = BeautifulSoup(aPageSource)
        #call all things that wanted to know about the soup
        ret = [(soupfunc.__name__, soupfunc(soup)) for soupfunc in self.soupCallers]
        nextPageURL = self.getNextPage(soup)
        if nextPageURL != None:
            np = self.parseSetPageResults(nextPageURL)
            print "nplen:", len(np)
            ret.extend(self.parseSetPageResults(nextPageURL))
        return ret
    
    def getSetData(self, aSoup):
        if self.verbose: print "getting set info"
        infoList = []
        valueMap = self.mapgen.generateValueMap(aSoup)
        fileHash = self.spriteManager.getFileInfo(aSoup)[1]#this value is calculated more than once per page...
        trs = aSoup.findAll("tr", {"class":re.compile("deckdbbody*")})
        for tr in trs:
            tds = tr.findAll("td")
            info = self.getCardInfo(tds, fileHash, valueMap)
            if self.verbose: print info.getString()
            if info.setName != None and info.name != None and info.price != None and info.spriteHash != None: infoList.append(info)
        return infoList
    
    def getNextPage(self, aSoup):
        link = None
        nextLinks = aSoup('a', text=re.compile(self.nextLinkText))
        if len(nextLinks) > 0:
            link = nextLinks[0]['href']
            if self.verbose: print "next link found",link
        return link
    
    def getPageLinks(self, aTRSoup):
        linkList = []
        anchors = aTRSoup[self.linkIndex].findAll("a")
        for anchor in anchors:
            if anchor.text.startswith("["):
                pageLink = anchor['href']
                linkList.append(pageLink)
        return linkList
    
    def getCardInfo(self, aTDSoup, fileHash, aValueMap):
        if(len(aTDSoup) > self.cardInfoArraySize):
            name = self.getName(aTDSoup)
            price = self.getPrice(aTDSoup, aValueMap)
            setName = self.getSet(aTDSoup)
            quant = self.getQuantity(aTDSoup, aValueMap)
            rarity = self.getRarity(aTDSoup, aValueMap)
        return CardInfo(fileHash, setName, name, price, quant, rarity=rarity)
    
    def cleanName(self, aNameString):
        return re.sub(self.cleanNamePattern, "", aNameString)
    
    def getName(self, aTDSoup):
        #TODO
        """
        some entries have multiple data fields but no names; this could be 
        extended to eventually deal with a 'lastName' to deal with these edge
        cases while still storing relevant data.
        """
        try:
            nameTD = aTDSoup[self.nameIndex]
            anchors = nameTD.findAll("a")
            return self.cleanName(anchors[0].text.strip())
        except IndexError,e:
            return None
    
    def getSet(self, aTDSoup):
        setTD = aTDSoup[self.setIndex]
        return setTD.text
    
    def getRarity(self, aTDSoup, aValueMap):
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
    """
    Map CSS values to OCR value offsets. Returns a pipe-delimited string.
    """
    def getSpriteValue(self, aTDTag, aValueMap):
        retval = []
        divs = aTDTag.findAll("div", {'class':True})
        for d in divs:
            for cur in d['class']:
                try:
                    curValue = aValueMap[cur]
                    retval.append(curValue)
                    #if self.verbose: print "Appended value", curValue
                except KeyError:
                    pass
        return '|'.join(retval)

class SpriteFetcher:
    def __init__(self, aDBCollection, aTargetDirectory="test/", aFileType=".png", verbose=False):
        self.spriteRegex = re.compile("url\(//(sales.+)\);", re.DOTALL)
        self.verbose = verbose
        self.coll = aDBCollection
        self.saveDir = aTargetDirectory
        self.fileType = aFileType
    
    def saveFile(self, aSoup):
        try:
            fileURL, hashValue, imageData = self.getFileInfo(aSoup)
            hashResults = self.getOneByHash(hashValue)
            if hashResults is None:
                if self.verbose: print "found file with new md5 at url:\n\t", fileURL
                fileLoc = self.saveDir + hashValue + self.fileType
                with open (fileLoc, 'w') as f:
                    f.write(imageData)
                self.coll.insert({
                                  'path':fileLoc,
                                  'url':fileURL,
                                  'values':None,
                                  'hash':hashValue
                              })
        except ValueError: pass
        
        
    def getFileInfo(self, aSoup):
        styleInfo = aSoup.findAll("style")[0]
        styleText = styleInfo.text
        match = self.spriteRegex.search(styleText)
        if match:
            baseURL = match.group(1)
            fileURL = "http://" + str(baseURL)
            imageData = urllib2.urlopen(fileURL).read()
            hashValue = hashlib.md5(imageData).hexdigest()
            return (fileURL,hashValue,imageData)
        else: return None
    def getOneByHash(self, aHash):
        #return self.coll.find_one({'hash':aHash, 'values':{'$ne':None}})
        return self.coll.find_one({'hash':aHash})
    def getAllByHash(self, aHash):
        return self.coll.find({'hash':aHash})

class MappingGenerator:
    def __init__(self, path, delimiter=',', verbose=False):
        self.path = path
        self.delimiter = delimiter
        self.offsetIndexes = [0]
        self.valueIndex = 1
        self.cssPattern = "\.([\S]+2) \{.+?:(.+?)[\s]"
        self.cssRegex = re.compile(self.cssPattern, re.DOTALL)
        self.verbose = verbose
    
    def generateOffsetMap(self):
        offsetValueMap = {}
        reader = csv.reader(open(self.path, 'r'), delimiter=self.delimiter)
        reader.next()#skip header line
        for row in reader:
            for val in self.offsetIndexes:
                offsetValueMap[row[val]] = row[self.valueIndex]
        self.offsetValueMap = offsetValueMap
        if self.verbose: print "offsetValMap",offsetValueMap
        return offsetValueMap
    
    def generateValueMap(self, soup):
        patternValueMap = {}
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
    parser.add_argument('-d', action='store_true', help='Debug flag')
    parser.add_argument('-f', help="File directory to download data to.")
    parser.add_argument('-s', help="File directory to download sprite images to.")
    parser.add_argument('-m', help="File path of css mapping file.")
    args = vars(parser.parse_args())
    
    fullFileDirectory = "SCG/"
    verbose = False
    debug = False
    mappingFilePath = "ocr_map.csv"
    spriteFilePath = "sprites/"
    
    c = Connection()
    db = c['cardData']
    coll = db['cards']
    sprites = db['sprites']
    
    if args['v']:
        verbose = args['v']
    if args['d']:
        debug = args['d']
    if args['f'] != None:
        fullFileDirectory = args['f']
    if args['s'] != None:
        spriteFilePath = args['s']
    if args['m'] != None:
        mappingFilePath = args['m']
    
    spriteFetcher = SpriteFetcher(sprites, aTargetDirectory=spriteFilePath, verbose=verbose)
    mapGen = MappingGenerator(mappingFilePath, ',', verbose)
    oMap = mapGen.generateOffsetMap()
    setLinkBuilder = SetLinkBuilder()
    #example for other module to use spoilerpage soup data
    #setLinkBuilder.addBasePageSoupCaller(aFunction(theSoup))
    
    cardInfoParser = CardInfoParser(setLinkBuilder, mapGen, spriteFetcher=spriteFetcher, verboseFlag=verbose,debugFlag=debug)
    #this is executed per-page with base soup argument passed in
    cardInfoParser.addSoupCaller(spriteFetcher.saveFile)
    cardInfoParser.addSoupCaller(cardInfoParser.getSetData)
    
    parseResults = cardInfoParser.getAllSetInfo()
    #now we want to fetch out the card data
    allSetInfo = []
    #"""
    for result in parseResults:
        print result[0]
        if result[0] == cardInfoParser.getSetData.__name__:
            allSetInfo.extend(result[1])
    
    #"""
    print "done w/# of records:",len(allSetInfo)
    #allSetInfo = allinfo[1][1]#maps to infoparser's data value
    
    """
    coll.insert(allSetInfo)
    #"""
    
    #"""
    today = date.today()
    tabFileDest = fullFileDirectory+"scg_"+today.isoformat()+".tsv"
    
    print "Starting file output to: ", tabFileDest
    
    tab = open(tabFileDest, 'w')
    for card in allSetInfo:
        tab.write(card.getString("\t")+"\n")

    tab.close()
    #"""
