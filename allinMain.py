"""
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

class SCGSpoilerParser:
    """
    """

    def __init__(self):
        self.scarsURL = "test/scars_1.html"#"http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[5197]=5197&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results"
        #unreadMessageREGEX = re.compile("(?:<tr class=\"entry trigger new\" id=\"\w+\">.+?href=\"(index.php\?.+?)\">)+", re.DOTALL)
        self.cardNameRegex = re.compile("\">(.+)", re.DOTALL)
        self.cardSetRegex = re.compile("(.+) Singles", re.DOTALL)
        
        #indeces for card row info
        self.nameIndex = 0
        self.setIndex = 1
        self.priceIndex = 8
        
        #which TR contains the pagination links
        self.linkIndex = 1

    def getPageLinks(self, aTRSoup):
        linkList = []
        anchors = aTRSoup[self.linkIndex].findAll("a")
        for anchor in anchors:
            if anchor.text.startswith("["):
                pageLink = anchor["href"]
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
        
if __name__ == '__main__':
    scg = SCGSpoilerParser()
    # download the page
    
    #user_agent = 'Mozilla/5 (Solaris 10) Gecko'
    #headers = { 'User-Agent' : user_agent }
    #
    #response = urllib2.urlopen(scarsURL)
    #html = response.read()
    html = ""
    file = open(scg.scarsURL)
    
    while 1:
        line = file.readline()
        if not line:
            break
        html+= line
    file.close()
    
    # create a beautiful soup object
    
    soup = BeautifulSoup(html)
    print "Souping!"
    trs = soup.findAll("tr", { "class":None})
    
    
    scg.getPageLinks(trs)
    
    for tr in trs:
        #print tr
        tds = tr.findAll("td")
        info = scg.getCardInfo(tds)
        
        if info.set != None:
            #print info.getString()
            break
        
    """
    # all links to detailed boat information have class lfloat
    links = soup.findAll("a", { "class" : "lfloat" })
    for link in links:
        print link['href']
        print link.string
    """
    
    # all prices are spans and have the class rfloat
    """
    prices = soup.findAll("span", { "class" : "rfloat" })
    for price in prices:
        print price
        print price.string
    """
    # all boat images have attribute height=105
    """"
    images = soup.findAll("img",height="105")
    for image in images:
        print image            # print the whole image tag
        print image['src']    # print the url of the image only
    """
    #Helpful resources:
