# Module that allows for an email to be sent from the snowbudget email account.
#
#   Connor Shugg

# Imports
import smtplib

# Globals
mailserver = None
notif_username = None
notif_password = None

# Initializes the notification code, given the server's SMTP username and
# passsword.
def notif_init(conf):
    global mailserver, notif_username, notif_password
    # create out SSL connection and attempt to log in
    mailserver = smtplib.SMTP_SSL("smtp.gmail.com", 465)
#    mailserver.login(conf.notif_email_username,
#                     conf.notif_email_password)
# TODO FIX
    # save credentials
    notif_username = conf.notif_email_username
    notif_password = conf.notif_email_password

# Tears down the connection to the SMTP server.
def notif_deinit():
    mailserver.quit()

# Function to send a string message to an email address.
def notif_send_email(address, message):
    mailserver.sendmail(notif_username, address, message)

