#!/usr/bin/python

# Copyright 2016 Peter Dymkar Brandt All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""TODO

TODO: Usage!
"""

import email.mime.multipart
import email.mime.text
import logging
import logging.config
import re
import smtplib
import sys

import yaml

import historical_data
import universe_report

def send_email(user, pwd, recipients, subject, body):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = email.mime.multipart.MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = ', '.join(recipients)

    # Force CRLF line endings per SMTP spec.
    plain_body = re.sub('\r?\n', '\r\n', body)

    html_body = re.sub('\r?\n', '<br>', body)
    html_body = html_body.replace(' ', '&nbsp;')
    html_body = '<div dir="ltr"><font face="monospace, monospace">' + (
        html_body + '</font></div>')

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = email.mime.text.MIMEText(plain_body, 'plain', _charset='utf-8')
    part2 = email.mime.text.MIMEText(html_body, 'html', _charset='utf-8')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    try:
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.login(user, pwd)
        server_ssl.sendmail(user, recipients, msg.as_string())
        server_ssl.close()
        print 'Successfully sent the email'
    except:
        print 'Failed to send the email: ', sys.exc_info()[0]

def usage():
    """Print Unix-style usage string.
    """
    print 'usage: main.py [config_file]'

def main():
    """Begin executing main logic of the script.
    """
    # Load config and setup logger
    if len(sys.argv) == 1:
        config_path = 'config.yaml'  # Default config file.
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['-h', '--help']:
            usage()
            sys.exit()

        config_path = sys.argv[1]
    else:
        usage()
        sys.exit(2)
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file.read())

    logging.config.dictConfig(config['logging_config'])
    logger = logging.getLogger(__name__)

    # config['historical_data_config']['end_date'] = '20160115'
    # config['historical_data_config']['output_dir'] = 'blarg/'
    blah = historical_data.HistoricalData(config['historical_data_config'],
                                          config['tor_scraper_config'])

    daily = blah.get_daily()
    if daily is None:
        logger.error('No daily dataframe')
        return

    universe = universe_report.UniverseReport(daily).get_default_report()
    print universe

    send_email('admin@blankbits.com', '', ['peterbrandt84@gmail.com'],
               'Russell 3000 Report -- 1234-56-78', universe)

# If in top-level script environment, run main().
if __name__ == '__main__':
    main()
