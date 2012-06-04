from BeautifulSoup import BeautifulSoup
from datetime import date
import csv, re, argparse, sys, urllib2

class MappingGenerator:
    def __init__(self, path, delimiter=',', verbose=False):
        self.path = path
        self.delimiter = delimiter
        self.offsetIndexes = [0,1,2]
        self.valueIndex = 3
        self.cssPattern = "(\.[\S]+2) \{.+?:(.+?)[\s]"
        self.cssRegex = re.compile(self.cssPattern, re.DOTALL)
        self.verbose = verbose
    
    def generateOffsetMap(self):
        map = {}
        print self.path
        reader = csv.reader(open(self.path, 'r'), delimiter=self.delimiter)
        reader.next()#skip header line
        for row in reader:
            for val in self.offsetIndexes:
                map[row[val]] = row[self.valueIndex]
        return map
    
    def generateValueMap(self, offsetValueMap, html):
        patternValueMap = {}
        soup = BeautifulSoup(html)
        styleInfo = soup.findAll("style")[0]
        styleText = styleInfo.text
        
        matches = self.cssRegex.regex.findall(styleText)
        if matches:
            if self.verbose: print "Matches"
            for cur in matches:
                if verbose: print "\tPattern:", cur[0], "\tOffset:", cur[1]
                #TODO: if no mapping found, handle / raise error here
                patternValueMap[cur[0]] = offsetValueMap[cur[1]]
        else:
            if self.verbose: print "No matches!"
        if self.verbose: print "patValMap",patternValueMap
        
        return patternValueMap

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape sell data from SCG website to the given file.')
    parser.add_argument('-v', action='store_true', help='Verbose flag')
    parser.add_argument('-m', help='File containing mappings for offset/values')
    parser.add_argument('-d', help='Delimiter for mapping file')
    args = vars(parser.parse_args())
    
    verbose = False
    mappingFileLocation = "src/conf/mappings.csv"
    mappingFileDelimiter = ","
    
    if args['v']: verbose = args['v']
    if args['m']: mappingFileLocation = args['m']
    if args['d']: mappingFileDelimiter = args['d']

    #"""
    baseURL = "http://sales.starcitygames.com/spoiler/display.php?name=&namematch=EXACT&text=&oracle=1&textmatch=AND&flavor=&flavormatch=EXACT&s_all=All&format=&c_all=All&multicolor=&colormatch=OR&ccl=0&ccu=99&t_all=All&z%5B%5D=&critter%5B%5D=&crittermatch=OR&pwrop=%3D&pwr=&pwrcc=&tghop=%3D&tgh=-&tghcc=-&mincost=0.00&maxcost=9999.99&minavail=0&maxavail=9999&r_all=All&g%5BG1%5D=NM%2FM&foil=nofoil&for=no&sort1=4&sort2=1&sort3=10&sort4=0&display=2&numpage=25&action=Show+Results"
    response = urllib2.urlopen(baseURL)
    html = response.read()
    if verbose: print "Downloaded url:\t", baseURL
    #"""
    
    #TODO:NEED TO CHECK/COMPARE EXISTING/CURRENT IMAGE FILE
    #TODO:NEED TO QUIT/COMPLAIN ON MAPPING ERRORS
    #"""This is durable throughout the run process
    mapGen = MappingGenerator(mappingFileLocation, mappingFileDelimiter, verbose)
    offsetValueMap = mapGen.generateOffsetMap()
    patternValueMap = {}
    #"""
    patternValueMap = mapGen.generateValueMap(offsetValueMap, html)
    
