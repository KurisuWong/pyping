"""Python Ping Tool with email notification and logging for health monitoring
Created By  : Chris Wong
Created Date: 2022-08-08
version ='1.0'
"""
import os
import yaml
import time
from datetime import datetime

# email 
import smtplib
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# load config file
with open('config//config.yml') as stream:
    config = yaml.safe_load(stream)

# read config 
PING_DELAY = config['PING_DELAY']
PING_NUM = config['PING_NUM']
PING_TIMEOUT = config['PING_TIMEOUT']

LOG_FOLDER = config['LOG_FOLDER']

EMAIL_ENABLE = config['EMAIL_ENABLE']
EMAIL_SERVER = config['EMAIL_SERVER']
EMAIL_SERVER_PORT = config['EMAIL_SERVER_PORT']
EMAIL_SUBJECT = config['EMAIL_SUBJECT']
EMAIL_FROM = config['EMAIL_FROM']
EMAIL_TO = config['EMAIL_TO']

# Helper Function
def ping(host):
    response = os.popen(f"ping {host} -n {PING_NUM} -w {PING_TIMEOUT}").read()

    if 'unreachable' not in response and 'Received = {}'.format(PING_NUM) in response:
        return True

    return False

def printAndStoreToSummary(msg):
    print(msg)
    log_file_summary.write("{}\n".format(msg))

########
# MAIN #
########

# stat
reachable = 0
unreachable = 0
total = 0;

# log file
date = datetime.now().strftime("%Y%m%d-%H%M")
log_file_summary = open('{}//{}_pyping.log'.format(LOG_FOLDER, date), 'w', buffering=1)

printAndStoreToSummary('Ping result on {}\n'.format(date))

# load IP LIST
PINGLIST = open('config//pinglist.txt', 'r')

# loop every ip in list
for ip in PINGLIST:
    now = datetime.now()
    curr = ip.strip()

    if ping(curr):
        printAndStoreToSummary('{} is up.'.format(curr))
        reachable += 1
    else:
        printAndStoreToSummary('{} is down.'.format(curr))
        unreachable += 1

    total += 1

    # delay before next ping
    if PING_DELAY != 0:
        time.sleep(PING_DELAY)

# close pinglist
PINGLIST.close()

# print summary
summary = '\nUP\tDOWN\tTOTAL\n{}\t{}\t{}\n'.format(reachable, unreachable, total)
printAndStoreToSummary(summary)

if total == 0:
    resultMsg = "There's no IPs in pinglist. Please check your config.yml and pinglist."

elif reachable == 0:
    resultMsg = "All IPs are unreachable. Please check your network connection."

elif reachable == total:
    resultMsg = "All IPs are reachable."

else:
    resultMsg = "Some IPs are unreachable.".format(unreachable,total)

printAndStoreToSummary('{}\n'.format(resultMsg))

# Email result out
if EMAIL_ENABLE == 1:
    printAndStoreToSummary("A notification email will be send from '{}' to '{}'.\n".format(EMAIL_FROM, EMAIL_TO))

    # get result from summary log
    LOG = open('{}//{}_pyping.log'.format(LOG_FOLDER, date), "r")
    DATA = LOG.read()

    # append to email body
    msg = MIMEText(DATA)
    LOG.close()

    # prepare the header
    msg['Subject'] = "[{}] {} ({})".format(date, EMAIL_SUBJECT, resultMsg)
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    # send it out
    mail = smtplib.SMTP(EMAIL_SERVER,EMAIL_SERVER_PORT)
    mail.sendmail(EMAIL_FROM,EMAIL_TO,msg.as_string())
    mail.quit()

else:
    printAndStoreToSummary("Notification email is disabled.\n")

# close summary file
log_file_summary.close()