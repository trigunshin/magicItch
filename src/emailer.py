import smtplib,os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

def send_email(subject="Test Email", extra_body_text='',attach=None,report_file_path=None,**kwargs):
    if attach is None: attach=[]
    if report_file_path is not None: attach.append(report_file_path)
    gmail_user = "magic.itch@gmail.com"
    gmail_pwd = os.getenv("EMAIL_PASS","")
    FROM = 'magic.itch@gmail.com'
    TO = ['trigunshin@gmail.com'] #must be a list
    SUBJECT = subject
    TEXT = "Testing sending mail using gmail servers\n\n" + extra_body_text
    
    msg = MIMEMultipart()
    msg['From'] = FROM#gmail_user
    #realToString = ','.join(to)
    msg['To'] = TO#gmail_user#realToString
    msg['Subject'] = SUBJECT
    
    # Prepare actual message
    messageText = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    
    msg.attach(MIMEText(TEXT)) 
    
    #attach each file in the list
    for cur_file in attach:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(cur_file, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                'attachment; filename="%s"' % os.path.basename(cur_file))
        msg.attach(part)
    
    #try:
    #server = smtplib.SMTP(SERVER) 
    server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, message)
    mailServer.sendmail(gmail_user, [gmail_user]+[]+to, msg.as_string())
    #server.quit()
    server.close()
    print 'successfully sent the mail'
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
