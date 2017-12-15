#!/usr/bin/env python

__title__ = "check_emails"
__version__ = "1.0.0"


import os
import sys
import datetime
import time
import uuid
import signal
import imaplib
import re
import dateutil.parser
from datetime import datetime
import pytz
import argparse
import ConfigParser
import smtplib
from email.mime.text import MIMEText
from email import utils


OLD_PYTHON = False
try:
	from subprocess import Popen, PIPE, STDOUT
except ImportError:
	OLD_PYTHON = True
	import commands
from optparse import OptionParser

EXIT_OK = 0
EXIT_WARNING = 1
EXIT_CRITICAL = 2
EXIT_UNKNOWN = 3

DEFAULT_PORT = 587
DEFAULT_PROFILECONFIG = '/etc/nagios-plugins/check_email_delivery_credentials.ini'

parser = argparse.ArgumentParser(description='This program sends a test email message over SMTP TLS.')
parser.add_argument('-H', dest='host', metavar='host', required=True, help='SMTP host')
parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='SMTP port (default=%i)'%DEFAULT_PORT)
parser.add_argument('--profile', required=True, help='credential profile in config file')
parser.add_argument('--profileconfig', metavar='config.ini', default=DEFAULT_PROFILECONFIG, help='location of the config file (default=%s)'%DEFAULT_PROFILECONFIG)
parser.add_argument('--mailfrom', metavar='sender@host1', required=True, help='email address of the test message sender')
parser.add_argument('--mailto', metavar='receiver@host2', required=True, help='email address of the test message receiver')

try:
    args = vars(parser.parse_args())
except SystemExit:
    sys.exit(EXIT_UNKNOWN)

host = args['host']
port = args['port']
profile = args['profile']
profileconfig = args['profileconfig']
mailfrom = args['mailfrom']
mailto = args['mailto']

config = ConfigParser.SafeConfigParser()
config.read(profileconfig)

try:
    username = config.get(profile,'username')
    password = config.get(profile,'password')
except ConfigParser.NoSectionError:
    print('Configuration error: profile %s does not exist' % profile)
    sys.exit(EXIT_UNKNOWN)
except ConfigParser.NoOptionError:
    print('Configuration error: profile %s does not contain username or password' % profile)
    sys.exit(EXIT_UNKNOWN)

#msg = MIMEText('This is a test message by the monitoring system to check if email delivery is running fine.')
#msg['Subject'] = 'TEST'
#msg['From'] = mailfrom
#msg['To'] = mailto
#msg['Message-ID'] = '<' + str(uuid.uuid4()) + '@' + host + '>'

#nowdt = datetime.datetime.now()
#nowtuple = nowdt.timetuple()
#nowtimestamp = time.mktime(nowtuple)

#msg['Date'] = utils.formatdate(nowtimestamp)

try:
    smtp = smtplib.SMTP(host, port)
    smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(mailfrom, mailto, msg.as_string())
except smtplib.SMTPServerDisconnected as e:
    # This exception is raised when the server unexpectedly disconnects, or when an attempt is made to use the SMTP instance before connecting it to a server.
    print e
    sys.exit(EXIT_CRITICAL)
except smtplib.SMTPResponseException as e:
    # Base class for all exceptions that include an SMTP error code. These exceptions are generated in some instances when the SMTP server returns an error code. The error code is stored in the smtp_code attribute of the error, and the smtp_error attribute is set to the error message.
    print e
    sys.exit(EXIT_CRITICAL)
except smtplib.SMTPSenderRefused as e:
    # Sender address refused. In addition to the attributes set by on all SMTPResponseException exceptions, this sets 'sender' to the string that the SMTP server refused.
    print e
    sys.exit(EXIT_CRITICAL)
except smtplib.SMTPRecipientsRefused as e:
    # All recipient addresses refused. The errors for each recipient are accessible through the attribute recipients, which is a dictionary of exactly the same sort as SMTP.sendmail() returns.
    print e
    sys.exit(EXIT_CRITICAL)
except smtplib.SMTPDataError as e:
    # The SMTP server refused to accept the message data.
    print e
    sys.exit(EXIT_CRITICAL)
except smtplib.SMTPConnectError as e:
    # Error occurred during establishment of a connection with the server.
    print e
    sys.exit(EXIT_CRITICAL)
except smtplib.SMTPHeloError as e:
    # The server refused our HELO message.
    print e
    sys.exit(EXIT_CRITICAL)
except smtplib.SMTPAuthenticationError as e:
    # SMTP authentication went wrong. Most probably the server didn't accept the username/password combination provided.
    print e
    sys.exit(EXIT_CRITICAL)
except smtplib.SMTPException as e:
    # The base exception class for all the other exceptions provided by this module.
    print e
    sys.exit(EXIT_CRITICAL)

print('OK')
sys.exit(EXIT_OK)
