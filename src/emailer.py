import smtplib,os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

def send_report_email(gmail_user='magic.itch@gmail.com',gmail_pwd=None,recipients=None,gmail_port=587,gmail_server_address='smtp.gmail.com',subject="test",text_body="test",attachment_paths=None,report_file_path=None,**kwargs):
    #addrList is for sendmail's delivery, not for TO/CC/BCC display
    if gmail_pwd is None: gmail_pwd = os.getenv("EMAIL_PASS","")
    if addrList is None: addrList = ['trigunshin@gmail.com']
    if attachment_paths is None: attachment_paths=[]
    if report_file_path is not None: attach.append(report_file_path)#XXX wrap function to remove this field
    FROM = gmail_user#FROM is displayed addr, gmail_user is gmail login
    TO = ', '.join(addrList)#TO is displayed addrlist
    SUBJECT = subject
    TEXT = text_body
    
    msg = MIMEMultipart()
    #these are the displayed values
    msg['From'] = FROM
    msg['To'] = FROM
    msg['CC'] = ""
    msg['BCC'] = TO
    msg['Subject'] = SUBJECT
    
    #text portion of email
    msg.attach(MIMEText(TEXT)) 
    
    #attach each file in the list
    for cur_file in attachment_paths:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(cur_file, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(cur_file))
        msg.attach(part)
    
    server = smtplib.SMTP(gmail_server_address, gmail_port) #or port 465 doesn't seem to work!
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(gmail_user, [gmail_user] + addrList, msg.as_string())
    server.close()
    

def send_email(subject="Test Email", body_text='test email',attach=None,addrList=None,report_file_path=None,**kwargs):
    #addrList is for sendmail's delivery, not for TO/CC/BCC display
    if addrList is None: addrList = ['trigunshin@gmail.com']
    if attach is None: attach=[]
    if report_file_path is not None: attach.append(report_file_path)
    gmail_pwd = os.getenv("EMAIL_PASS","")
    gmail_user = "magic.itch@gmail.com"
    FROM = gmail_user#FROM is displayed addr, gmail_user is gmail login
    TO = ', '.join(addrList)#TO is displayed addrlist
    SUBJECT = subject
    TEXT = body_text
    
    msg = MIMEMultipart()
    #these are for display
    msg['From'] = FROM
    msg['To'] = FROM
    msg['CC'] = ""
    msg['BCC'] = TO
    msg['Subject'] = SUBJECT
    
    #text portion of email
    msg.attach(MIMEText(TEXT)) 
    
    #attach each file in the list
    for cur_file in attach:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(cur_file, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(cur_file))
        msg.attach(part)
    
    #send email
    #try:
    server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(gmail_user, [gmail_user] + addrList, msg.as_string())
    server.close()
    #except Error,e:
    #    print "failed to send mail",e

def send_email_attach(to, subject, text, attach):
    gmail_user = "magic.itch@gmail.com"
    gmail_pwd = os.getenv("EMAIL_PASS","")
    msg = MIMEMultipart()
    
    msg['From'] = gmail_user
    realToString = ','.join(to)
    
    #realToString=''
    #for s in to:
    #    realToString = realToString + s + ","
    #print realToString,to, [gmail_user]+[]+to
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
