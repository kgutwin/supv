#!/usr/bin/python

import socket
import smtplib
from email.mime.text import MIMEText
import email

import nodes

class Email(nodes.Consumer):
    def __init__(self, to_addr, from_addr=None, server='localhost', **kwargs):
        nodes.Consumer.__init__(self, **kwargs)
        self.server = server
        self.to_addr = to_addr
        self.from_addr = from_addr
        if self.from_addr is None:
            self.from_addr = to_addr
        self.hostname = socket.gethostname()
        self.previous_msgid = None

    def do(self):
        text = []
        for inp in self.inputs:
            val = self.inputs[inp].get()
            text.append("%s ======\n" % inp)
            text.append("\n")
            text.append(str(val))
            text.append("\n")
        # prep email
        msg = MIMEText("".join(text))
        msg['Subject'] = "supv [%s]" % self.hostname
        msg['From'] = self.from_addr
        msg['To'] = self.to_addr
        msg['message-id'] = email.utils.make_msgid()
        if self.previous_msgid is not None:
            msg['In-Reply-To'] = self.previous_msgid
        # send email
        self.logger.info('sending mail to %s (%d chars)' % (self.to_addr, len("".join(text))))
        s = smtplib.SMTP()
        s.connect(self.server)
        s.sendmail(self.from_addr, self.to_addr, msg.as_string())
        s.close()
        # save message id
        self.previous_msgid = msg['message-id']


