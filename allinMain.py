"""
http://sales.starcitygames.com/spoiler/spoiler.php
http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[5197]=5197&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results
"""

from BeautifulSoup import BeautifulSoup
import re
import urllib2

class CardInfo:
        def __init__(self, set, name, price):
            self.set = set
            self.name = name
            self.price = price
            
        def getString(self):
            return "\""+str(self.set) + "\", \"" + str(self.name) + "\", \"" + str(self.price)+"\""

class HtmlReader:
    def __init__(self, url):
        self.url = url

    def readHtml(self):
        file = urllib2.urlopen(self.url)
        return file.read();

class SCGURLBuilder:
        def __init__(self):
            self.baseURL = "http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[TOKEN]=TOKEN&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results"
            
        def getSetURLs(self, aSetIDList):
            urlList = []
            for set in aSetIDList:
                currentURL = self.baseURL.replace('TOKEN', set)
                urlList.append(currentURL)
            return urlList

class SCGSetHashBuilder:
    def __init__(self):
        self.scgUrl = "http://sales.starcitygames.com/spoiler/spoiler.php"
        self.codeRegex = re.compile("t\=a\&amp\;cat\=(\d{4})", re.M|re.S)

    def build(self):
        html = HtmlReader(self.scgUrl).readHtml()
        soup = BeautifulSoup(html)
        self.matches = filter(lambda x: x is not None, \
                              map(lambda y: self.codeRegex.search(str(y)), \
                                  soup.findAll("a")))
        self.setCodes = map(lambda x: x.group(1), self.matches)
        return self

class SCGSpoilerParser:
    """
    """

    def __init__(self):
        self.cardNameRegex = re.compile("\">(.+)", re.DOTALL)
        self.cardSetRegex = re.compile("(.+) Singles", re.DOTALL)
        #next link info
        self.nextLinkText = "Next"
        #indeces for card row info
        self.nameIndex = 0
        self.setIndex = 1
        self.priceIndex = 8
        #which TR contains the pagination links
        self.linkIndex = 1

    def parseSetPageResults(self, aSetURL):
        # download the page
        user_agent = 'Mozilla/5 (Solaris 10) Gecko'
        headers = { 'User-Agent' : user_agent }
        response = urllib2.urlopen(aSetURL)
        html = response.read()
        return self.getSetInfo(html)

    def getSetInfo(self, aPageSource):
        infoList = []
        soup = BeautifulSoup(aPageSource)
        trs = soup.findAll("tr", {"class":None})
        for tr in trs:
            tds = tr.findAll("td")
            info = scg.getCardInfo(tds)
            if info.set != None:
                infoList.append(info)
        nextPageURL = self.getNextPage(trs)
        if nextPageURL != None:
            infoList += self.parseSetPageResults(nextPageURL)
        return infoList

    def getNextPage(self, aTRSoup):
        link = None
        if len(aTRSoup) > 0:
            anchors = aTRSoup[self.linkIndex].findAll("a")
            for anchor in anchors:
                if anchor.text.find(self.nextLinkText) >= 0:
                    link = anchor["href"]
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
        name = self.getName(aTDSoup)
        price = self.getPrice(aTDSoup)
        set = self.getSet(aTDSoup)
        
        return CardInfo(set, name, price)
        
    def getName(self, aTDSoup):
        if len(aTDSoup) > 9:
            nameTD = aTDSoup[self.nameIndex]
            anchors = nameTD.findAll("a")
            for anchor in anchors:
                matches = self.cardNameRegex.findall(anchor.text)
                if len(matches) > 0:
                    return matches.pop().strip()
                
    def getSet(self, aTDSoup):
        if len(aTDSoup) > 9:
            setTD = aTDSoup[self.setIndex]
            anchors = setTD.findAll("a")
            for anchor in anchors:
                matches = self.cardSetRegex.findall(anchor.text)
                if len(matches) > 0:
                    return matches.pop().strip()
                    
    def getPrice(self, aTDSoup):
        if len(aTDSoup) > 9:
            priceTD = aTDSoup[self.priceIndex]
            return priceTD.text

    def parseAllSets(self, aSetList):
        setIDIndex = 0
        setName = 1
        baseURL = "http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[TOKEN]=TOKEN&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results"
        for set in sets:
            currentURL = baseURL.replace('TOKEN', str(set[setIDIndex]))
            infoList = scg.parseSetPageResults(currentURL)
            som = open("test/scg_"+set[setName]+".csv", 'w')
            for info in infoList:
                print info.getString()
                som.write(info.getString()+"\n")
            som.close()
            
if __name__ == '__main__':
    scg = SCGSpoilerParser()
    #self.scarsURL = "test/scars_1.html"#"http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[5197]=5197&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results"
    #sets=[[5197, "Scars of Mirrodin"]]
    #scg.parseAllSets(sets)
        
    setBuilder = SCGSetHashBuilder()
    setBuilder.build()
    #print setBuilder.setCodes
    urls = SCGURLBuilder()
    urlList = urls.getSetURLs(setBuilder.setCodes)
    print "Acquired URLs!"
    allCardInfo = []
    for url in urlList:
        allCardInfo += scg.parseSetPageResults(url)
    
    
    """
    html = ""
    file = open(scg.scarsURL)
    while 1:
        line = file.readline()
        if not line:
            break
        html+= line
    file.close()

    infoList = scg.parseSetPageResults(scarsURL)
    """
    print "Starting file output!"
    som = open("test/scg_all.csv", 'w')
    for card in allCardInfo:
        som.write(card.getString()+"\n")
    som.close()