from emailer import send_report_email
from datetime import date
import time
import pymongo
from pymongo import Connection
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os,argparse

class Preferences(object):
    def __init__(self):
        self.scg='scg'
        self.mtgtrdr='mtgtrdr'
        self.userEmail='email'
        self.formats='email_file_format'
        self.stores='mtg_stores'
        self.vals='values'
        self.prefs='prefs'
        self.emailArray='emails'
        self.attachments='files'
        self.tokenDelimiter='_'
        self.keyDelimiter='||'
    
    def getReportData(self, storeName, dataType, fileDate=date.today()):
        #defensively programmed, ifs not necessary in trusted case
        #this function could trust DB and serve as the complete token instead of using delimiters
        if storeName == self.scg or storeName == self.mtgtrdr:
            if dataType == "txt" or dataType == "csv":
                return storeName+"Daily"+str(fileDate)+"."+dataType
        return None

    def getUserArray(self, emailColl):
        """
        #TODO turn this into more of a real test case
        usr1={self.userEmail:"t@g.c",self.prefs:{self.stores:{self.vals:[self.scg]},
                                        self.formats:{self.vals:['txt']}}}
        usr2={self.userEmail:"g@g.c",self.prefs:{self.stores:{self.vals:[self.mtgtrdr]},
                                        self.formats:{self.vals:['csv']}}}
        usr3={self.userEmail:"x@g.c",self.prefs:{self.stores:{self.vals:[self.scg,self.mtgtrdr]},
                                        self.formats:{self.vals:['csv','txt']}}}
        usr4={self.userEmail:"y@g.c",self.prefs:{self.stores:{self.vals:[self.scg,self.mtgtrdr]},
                                        self.formats:{self.vals:['csv']}}}
        usr5={self.userEmail:"a@g.c",self.prefs:{self.stores:{self.vals:[self.scg]},
                                        self.formats:{self.vals:['txt']}}}
        #return [usr1,usr2,usr3,usr4,usr5]
        #"""
        findQuery = {'email':{'$exists':'true'},
            'prefs.'+self.formats+'.values':{'$not':{'$size':0}},
            'prefs.'+self.stores+'.values':{'$not':{'$size':0}},
        }
        
        ret = [cur for cur in emailColl.find(findQuery)]
        #ret = [cur for cur in emailColl.find({'email':"trigunshin@gmail.com"})]
        
        return ret

    def getPrefMap(self, usrs):
        emailMap = {}
        for curUser in usrs:
            try:
                usrHash = self.prefHash(curUser[self.prefs][self.stores][self.vals],
                               curUser[self.prefs][self.formats][self.vals])
            except KeyError:#default case
                usrHash = self.scg+self.tokenDelimiter+"txt"

            try:
                emailMap[usrHash][self.emailArray].append(curUser[self.userEmail])
            except KeyError:
                emailMap[usrHash]={self.emailArray:[curUser[self.userEmail]]}
        return emailMap

    def prefHash(self, stores, formats):
        #this could return the filepaths instead of delimited strings
        ret=""
        for curStore in sorted(stores):
            for curFormat in sorted(formats):
                ret+=curStore+self.tokenDelimiter+curFormat
                ret+=self.keyDelimiter
        return ret.rstrip(self.keyDelimiter)

    def getFileArray(self, keyToken):
        ret=[]
        for store, format in [curKey.split(self.tokenDelimiter) for curKey in keyToken.split(self.keyDelimiter)]:
                ret.append(self.getReportData(store, format))
        return ret
    
    def getEmailFileMapping(self,emailColl):
        usrs = self.getUserArray(emailColl)
        emailMap = self.getPrefMap(usrs)
        for curKey in emailMap.keys():
            emailMap[curKey][self.attachments] = self.getFileArray(curKey)
        return emailMap

def mail(to, subject, text, attach):
    msg = MIMEMultipart()
    
    print gmail_user
    msg['From'] = gmail_user
    realToString=''
    for s in to:
        realToString = realToString + s + ","
#    print realToString,to, [gmail_user]+[]+to
    msg['To'] = gmail_user#realToString
    msg['Subject'] = subject
    
    msg.attach(MIMEText(text)) 
    
    
    #attach each file in the list
    for cur_file in attach:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(cur_file, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(cur_file))
        msg.attach(part)
    
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, [gmail_user]+[]+to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()

#def send_report_email(gmail_user='magic.itch@gmail.com',gmail_pwd=None,recipients=None,gmail_port=587,gmail_server_address='smtp.gmail.com',subject="test",text_body="test",attachment_paths=None,report_file_path=None,**kwargs):
def send_mux_mail(emailColl,verbose=False,debug=False,**kwargs):
    for cur in emailColl.find({'sender':{'$exists':'true'}}).limit(1):
        if verbose: print "Found email handler:",cur['sender']
        gmail_user = cur['sender']
        gmail_pwd = cur['pass']
    
    p=Preferences()
    emailMap = p.getEmailFileMapping(emailColl)
    
    for key in emailMap.keys():
        files = [curFile for curFile in [directory+curFilename for curFilename in emailMap[key][p.attachments]]]
        dest=emailMap[key][p.emailArray]
        
        if verbose: print "\tTo:",dest
        if verbose: print "\tFiles:",files
        #msg="Hey,\nLast night there was an issue with (only) Avacyn Restored data for SCG. I'm re-sending the emails as there were a couple big moves from SCG on prices. Sorry for any inconvenience."
        msg="\nHey, these are the price changes from the last 24 hours. Let me at know at magic.itch@gmail.com if you have any questions, comments or requests."
        msg+="\n\nDon't forget; you can set your store and format preferences on the website now."
        subject="Hello from magicItch",str(date.today())
        
        send_report_email(gmail_user=gmail_user, gmail_pwd=gmail_pwd, recipients=dest, subject=subject, text_body=msg, attachment_paths=files)
        
        #mail(dest, subject, msg, files)
        time.sleep(2)

if __name__ == '__main__':
    #p=Preferences()
    #emailMap = p.getEmailFileMapping()
    #for key in emailMap.keys():
    #    print "To:",emailMap[key][p.emailArray]
    #    print "\tFiles:",emailMap[key][p.attachments]
    
    parser = argparse.ArgumentParser(description='Herpaderp.')
    parser.add_argument('-d', required=True, help="Directory to find files in.")
    args = vars(parser.parse_args())
    if args['d'] != None:
        directory = args['d']

    gmail_user = "your_email@gmail.com"
    gmail_pwd = "your_password"

    c = Connection()
    db = c['emailList']
    coll = db['emails']
    for cur in coll.find({'sender':{'$exists':'true'}}).limit(1):
        print "Sending via",cur['sender']
        gmail_user = cur['sender']
        gmail_pwd = cur['pass']

    p=Preferences()
    emailMap = p.getEmailFileMapping(coll)
    for key in emailMap.keys():
        files = []
        for curFile in [directory+curFilename for curFilename in emailMap[key][p.attachments]]:
            files.append(curFile)
        dest=emailMap[key][p.emailArray]
        
        print "\tTo:",dest
        print "\tFiles:",files
        #msg="Hey,\nLast night there was an issue with (only) Avacyn Restored data for SCG. I'm re-sending the emails as there were a couple big moves from SCG on prices. Sorry for any inconvenience."
        msg="\nHey, these are the price changes from the last 24 hours. Let me at know at magic.itch@gmail.com if you have any questions, comments or requests."
        msg+="\n\nDon't forget; you can set your store and format preferences on the website now."
        subject="Hello from magicItch"#", "+str(date.today())
        mail(dest, subject, msg, files)
        time.sleep(2)
