import smtplib,os

def send_email(subject="Test Email", extra_body_text=''):
    gmail_user = "magic.itch@gmail.com"
    gmail_pwd = os.getenv("EMAIL_PASS","")
    FROM = 'magic.itch@gmail.com'
    TO = ['trigunshin@gmail.com'] #must be a list
    SUBJECT = subject
    TEXT = "Testing sending mail using gmail servers\n\n" + extra_body_text

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        #server = smtplib.SMTP(SERVER) 
        server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        #server.quit()
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"