import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

_smtp_server = 'imap.gene.com'
_smtp_usrname = 'sabinaz'
_smtp_pwd = ''

def GMailAccountInfo(pServer='',pUser='',pPassword=''):
    print 'test ' + pServer
    if len(pServer) > 0:
        _smtp_server = pServer
        print 'test ' + pServer
    if len(pUser) > 0:
        _smpt_usrname = pUser
    if len(pPassword) > 0:
        _smtp_pwd = pPassword
        
def SendMail(pRecipient,pSubject,pMessage,pAttachments):
    email_subject = pSubject
    body_of_email = pMessage
    recipient = pRecipient
    
    # The following code taken verbatim from:
    # http://jmduke.com/posts/how-to-send-emails-through-python-and-gmail/

    # The below code never changes, though obviously those variables need values.
    session = smtplib.SMTP(_smtp_server, 587)
    session.ehlo()
    session.starttls()
    session.login(_smtp_usrname, _smtp_pwd)

    headers = "\r\n".join(["from: " + _smtp_usrname,
                           "subject: " + email_subject,
                           "to: " + recipient,
                           "mime-version: 1.0",
                           "content-type: text/html"])

    # body_of_email can be plaintext or html!                    
    content = headers + "\r\n\r\n" + body_of_email
    session.sendmail(_smtp_usrname, recipient, content)

# THE FOLLOWING CODE JACKED FROM
# http://kutuma.blogspot.com/2007/08/sending-emails-via-gmail-with-python.html

def mail(to, subject, text, attach):
   msg = MIMEMultipart()

   msg['From'] = _smtp_usrname
   msg['To'] = to
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attach, 'rb').read())
   Encoders.encode_base64(part)
   part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
   msg.attach(part)

   mailServer = smtplib.SMTP(_smtp_server, 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(_smtp_usrname, _smtp_pwd)
   mailServer.sendmail(_smtp_usrname, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()
