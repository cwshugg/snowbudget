# Module that allows for an email to be sent from the snowbudget email account.
#
#   Connor Shugg

# Imports
import requests

# Globals
config = None
webhook_url = "https://maker.ifttt.com/trigger/%s/json/with/key/%s"

# Initializes the notification code, given the server's SMTP username and
# passsword.
def notif_init(conf):
    global webhook_url
    webhook_url = webhook_url % (conf.notif_webhook_event, conf.ifttt_webhook_key)

# Function to send a string message to an email address.
def notif_send_email(address, message, subject=""):
    # put together a JSON object to send to my IFTTT event.
    subject_pfx = "sb "
    jdata = {
        "to": address,
        "subject": "%s%s" % (subject_pfx, subject),
        "content": message
    }
    # attempt to send the request
    try:
        r = requests.post(webhook_url, data=jdata)
        return None
    except Exception as e:
        return e

