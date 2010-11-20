"""
http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[5197]=5197&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results
"""

from BeautifulSoup import BeautifulSoup
import re
import urllib2

class Weblogic:
    """
    Methods here interface directly with the code on the website and return
    results which can be used by systems of higher intelligence.
    """

    def __init__(self):
        self.requestQueue = Queue.Queue()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        self.lastFetchedURL = None
        f = open("login.ogame")
        info = f.read()
        self.user = re.search("user:\s(.*?);", info, re.M).group(1)
        self.passwd = re.search("password:\s(.*?);", info, re.M).group(1)
        self.server = re.search("server:\s(.*?);", info, re.M).group(1)
        self.SESSION_REGEX = re.compile(r"[0-9A-Fa-f]{12}")
        self.PLAYER_REGEX = re.compile("id=\"playerName\".*?efy\"\>(.*?)\<", re.S|re.M)
        self.session = None

        headers = [('Keep-Alive', "300")]
        self.opener.addheaders = headers

    def delayTime(self, lowerBound=2, upperBound=4):
        delay = random.randint(lowerBound, upperBound)
        print "Sleeping " + str(delay) + " seconds after request..."
        time.sleep(delay)
        return delay


if __name__ == '__main__':
    scarsURL = "/Users/trigunshin/magicItch/test/scars_1.html"#"http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s[5197]=5197&format=&c_all=All&colormatch=OR&ccl=0&ccu=99&t_all=All&z[]=&critter[]=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g[G1]=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=4&numpage=100&action=Show+Results"
    
    # download the page
    
    #user_agent = 'Mozilla/5 (Solaris 10) Gecko'
    #headers = { 'User-Agent' : user_agent }
    #
    #response = urllib2.urlopen(scarsURL)
    #html = response.read()
    html = ""
    file = open(scarsURL)
    
    while 1:
        line = file.readline()
        if not line:
            break
        html+= line
    file.close()
    
    # create a beautiful soup object
    soup = BeautifulSoup(html)
    
    print "Souping!"
    #unreadMessageREGEX = re.compile("(?:<tr class=\"entry trigger new\" id=\"\w+\">.+?href=\"(index.php\?.+?)\">)+", re.DOTALL)
    cardNameRegex = re.compile(">(.+)</a>", re.DOTALL)
    
    # all links to detailed boat information have class lfloat
    trs = soup.findAll("tr", { "class":None})
    for tr in trs:
        #print tr
        tds = tr.findAll("td")
        count = 0;
        for td in tds:
            if count == 0:
                anchors = td.findAll("a")
                for anchor in anchors:
                    print "ANCHOR STRING"
                    #name = cardNameRegex.findall(anchor.string)
                    #if name != None:
                    #    print name
                    #else:
                    #    print anchor
                    print anchor.contents[0]
                    print anchor
            elif count == 1:
                a=1
            elif count == 8:
                a=1
            count = count+1
            break;
    
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