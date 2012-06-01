from BeautifulSoup import BeautifulSoup
from datetime import date
import time, re, argparse, sys, urllib2, inspect

class HtmlReader:
    def __init__(self, url):
        self.url = url

    def readHtml(self):
        file = urllib2.urlopen(self.url)
        return file.read();

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape sell data from SCG website to the given file.')
    parser.add_argument('-v', action='store_true', help='Verbose flag')
    args = vars(parser.parse_args())
    
    verbose = True
    
    if args['v']:
        verbose = args['v']
    
    #"""
    baseURL = "http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s_all=All&format=&c_all=All&multicolor=&colormatch=OR&ccl=0&ccu=99&t_all=All&z%5B%5D=&critter%5B%5D=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g%5BG1%5D=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=2&numpage=25&action=Show+Results"
    response = urllib2.urlopen(baseURL)
    html = response.read()
    if verbose: print "Downloaded url:\t", baseURL

    soup = BeautifulSoup(html)
    styleInfo = soup.findAll("style")[0]
    styleText = styleInfo.text
    print "Style Contents",styleInfo.text
    #"""
    """
    styleText = ".AjvxJd {background-position:-0.6em -2px;}\
.AjvxJd2 {background-position:-0.6em 21px;}\
.HIjJhV {background-position:-47.5pt -2px;width:3px; }\
.HIjJhV2 {background-position:-47.5pt 21px;width:3px; }"
    """
    cssPattern = "(\.[\S]+2) \{.+?:(.+?)[\s]"
    regex = re.compile(cssPattern, re.DOTALL)
    matches = regex.findall(styleText)
    if matches:
        for cur in matches:
            print "Current match", cur
            print "\tPattern:", cur[0]
            print "\tOffset:", cur[1]
    else:
        print "No matches!"
    
    
    tab = open("testText.txt", 'w')
    tab.write(html)
    tab.close()
