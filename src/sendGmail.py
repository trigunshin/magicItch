import pymongo
from pymongo import Connection
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os,argparse


def mail(to, subject, text, attach):
    msg = MIMEMultipart()

    print gmail_user
    msg['From'] = gmail_user
    realToString=''
    for s in to:
        realToString = realToString + s + ","
    print realToString
    msg['To'] = realToString
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(attach, 'rb').read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition',
            'attachment; filename="%s"' % os.path.basename(attach))
    msg.attach(part)

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Herp.')
    parser.add_argument('-f', required=True, help="File to send.")

    args = vars(parser.parse_args())
    gmail_user = "your_email@gmail.com"
    gmail_pwd = "your_password"
    file = None
    dest = None

    if args['f'] != None:
        file = args['f']

    c = Connection()
    db = c['emailList']
    coll = db['emails']
    dest=[]
    for cur in coll.find({'email':{'$exists':'true'}}):
        dest.append(cur['email'])

    for cur in coll.find({'sender':{'$exists':'true'}}).limit(1):
        print cur
        gmail_user = cur['sender']
        gmail_pwd = cur['pass']

    mail(dest,
       "Hello from magicItch!",
        "Hey, these are the SCG price changes from the last 24 hours. Let me know if you have any questions.",
        file)
