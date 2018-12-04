#! /usr/bin/env python3
# coding: utf-8

import smtplib
from email.mime.text import MIMEText

EMAIL_FROM = 'jestin_17@hotmail.com'
EMAIL_TO = 'jestin_17@hotmail.com'
SUBJECT = '[Bet] Interesting matches of this week'
SMTP_ADDRESS = 'smtp-mail.outlook.com'
SMTP_PORT = '587'
PASSWORD = 'Z4tH,yHt'


def get_matches_summary(bet_matches):
    print('Creating matches summary...')
    text = ''
    for summary, side_id, website, odd, match_datetime, bet_fraction in sorted(bet_matches, key=lambda x: x[4]):
        text += '{} ({}; {}; {}; {})\n'.format(summary, side_id, odd, website, bet_fraction)
    text += 'Number of bet matches: {}\n'.format(len(bet_matches))
    return text


def send_email(matches_summary):
    print('Sending email...')
    msg = MIMEText(matches_summary)
    msg['Subject'] = SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    s = smtplib.SMTP(SMTP_ADDRESS, SMTP_PORT)
    s.starttls()
    s.login(EMAIL_FROM, PASSWORD)
    s.send_message(msg)
    s.quit()
    print('Email sent')
