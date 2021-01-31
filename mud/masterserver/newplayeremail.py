# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.MIMEText import MIMEText

from mud.gamesettings import GAMEROOT,SERVER_EMAIL_USE_GMAIL

SUPPORTEMAIL_ADDRESS = ""
SUPPORTEMAIL_ACCOUNT = ""
SUPPORTEMAIL_PASSWORD = ""
SUPPORTEMAIL_SERVER = ""
SUPPORTEMAIL_PORT = ""

def ConfigureEmail(config):
    global SUPPORTEMAIL_ADDRESS,SUPPORTEMAIL_ACCOUNT,SUPPORTEMAIL_PASSWORD,SUPPORTEMAIL_SERVER,SUPPORTEMAIL_PORT
    SUPPORTEMAIL_ADDRESS = config["Support Email Address"]
    SUPPORTEMAIL_ACCOUNT = config["Support Email Account"]
    SUPPORTEMAIL_PASSWORD = config["Support Email Password"]
    SUPPORTEMAIL_SERVER = config["Support Email Server"]
    SUPPORTEMAIL_PORT = config["Support Email Port"]

def NewPlayerEmail(to,publicName,password, regkey,fromProduct):

    me = SUPPORTEMAIL_ADDRESS
    
    if not fromProduct:
        body = FREE_BODY%(publicName,password)

    else:
        body = PREMIUM_BODY%(publicName,password)
    
    msg = MIMEText(body)
    
    if fromProduct:
        msg['Subject'] = PREMIUM_SUBJECT
    else:
        msg['Subject'] = FREE_SUBJECT
        
    msg['From'] = me
    msg['To'] = to

    s = smtplib.SMTP(SUPPORTEMAIL_SERVER,SUPPORTEMAIL_PORT)
    #s.set_debuglevel(1)

    if SERVER_EMAIL_USE_GMAIL: 
        s.ehlo() 
        s.starttls() 
        s.ehlo()

    s.login(SUPPORTEMAIL_ACCOUNT,SUPPORTEMAIL_PASSWORD)
    s.sendmail(me, [to], msg.as_string())
    msg['To'] = SUPPORTEMAIL_ADDRESS
    s.sendmail(me, SUPPORTEMAIL_ADDRESS, msg.as_string())
    s.quit()


def LostPasswordEmail(to,publicName,password):

    me = SUPPORTEMAIL_ADDRESS
    
    body = """Hello %s,

Your password is: %s (case sensitive)

Please do not share this password with anyone.

You are receiving this email because someone requested your password. If this person wasn't you,
please email support with your public name.

Have fun!!!
"""%(publicName,password)
    
    msg = MIMEText(body)
    
    msg['Subject'] = PASSWORD_SUBJECT
        
    msg['From'] = me
    msg['To'] = to

    s = smtplib.SMTP(SUPPORTEMAIL_SERVER,SUPPORTEMAIL_PORT)
    #s.set_debuglevel(1)

    if SERVER_EMAIL_USE_GMAIL: 
        s.ehlo() 
        s.starttls() 
        s.ehlo()

    s.login(SUPPORTEMAIL_ACCOUNT,SUPPORTEMAIL_PASSWORD)
    s.sendmail(me, [to], msg.as_string())
    msg['To'] = SUPPORTEMAIL_ADDRESS
    s.sendmail(me, SUPPORTEMAIL_ADDRESS, msg.as_string())
    s.quit()


PASSWORD_SUBJECT = "Password Request"

FREE_SUBJECT = "Registration Information"

PREMIUM_SUBJECT = "Registration Information"

PREMIUM_BODY = FREE_BODY = """Hello,

Please use the information below to login to your account.

Public Login Name:
%s (case sensitive)

Password:
%s (case sensitive)

Email support if there are any problems with your account.

Have fun!!!
"""

