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

"""Emailer is an extremely simple class for sending emails via SMTP.

Example:
    import emailer
    sender = emailer.Emailer({
        'host': 'smtp.gmail.com'
        'port': 465
        'username': 'nobody@domain.com'
        'password': 'password123'
        'recipients': ['']
    })
    sender.send('Hello', 'World', ['somebody@domain.com'])
)
    sender('Russell 3000 Report -- 4444-55-22', universe)
"""

import email.mime.multipart
import email.mime.text
import logging
import re
import smtplib
import sys

class Emailer(object):
    """Contains all functionality for the emailer module.
    """
    def __init__(self, config):
        """Emailer must be initialized with a config arg similar to that shown
        in the example at the top of this file.

        Args:
            config: Determines the behavior of this instance.
        """
        self._config = config
        self._logger = logging.getLogger(__name__)

    @staticmethod
    def get_message_str(from_address, to_addresses, subject, body):
        """Creates a string containing a multipart email message with both plain
        text and monospaced HTML parts.

        Args:
            from_address: Email address of the sender.
            to_addresses: Comma-separated email addresses of recipients.
            subject: Subject line of the email.
            body: Body of the email.
        """
        # Create message container with MIME type multipart/alternative.
        message = email.mime.multipart.MIMEMultipart('alternative')
        message['From'] = from_address
        message['To'] = to_addresses
        message['Subject'] = subject

        # Force CRLF line endings per SMTP spec.
        plain_body = re.sub('\r?\n', '\r\n', body)

        html_body = re.sub('\r?\n', '<br>', body)
        html_body = html_body.replace(' ', '&nbsp;')
        html_body = '<div dir="ltr"><font face="monospace, monospace">' + (
            html_body + '</font></div>')

        # Record the MIME types of both parts - text/plain and text/html.
        plain_part = email.mime.text.MIMEText(plain_body, 'plain',
                                              _charset='utf-8')
        html_part = email.mime.text.MIMEText(html_body, 'html',
                                             _charset='utf-8')

        # Attach parts into message container. According to RFC 2046, the last
        # part of a multipart message, in this case the HTML message, is best
        # and preferred.
        message.attach(plain_part)
        message.attach(html_part)

        return message.as_string()

    def send(self, subject, body, recipients=None):
        """Connects to the SMTP server and sends an email.

        Args:
            subject: Subject line of the email.
            body: Body of the email.
            recipients: List of email addresses to receive the email.
        """
        # Default to recipients in config if none provided.
        if recipients is None:
            recipients = self._config['recipients']

        message_str = self.get_message_str(self._config['username'],
                                           ', '.join(recipients),
                                           subject, body)

        try:
            server = smtplib.SMTP_SSL(self._config['host'],
                                      self._config['port'])
            server.login(self._config['username'], self._config['password'])
            server.sendmail(self._config['username'], recipients,
                            message_str)
            server.close()
            self._logger.info('Successfully sent the email')
        except smtplib.SMTPException:
            self._logger.error('Failed to send the email: ' + str(
                sys.exc_info()[0]))
