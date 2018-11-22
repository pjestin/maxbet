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


def get_matches_summary(matches_by_league):
    print('Creating matches summary...')
    text = ''
    count = 0
    for league, matches in matches_by_league.items():
        league_text = ''
        sure_bet_matches = []
        for match in matches:
            for team in match.teams.values():
                website, odd = team.get_best_odd()
                if website:
                    league_text += '{}; {}; {} ({})\n'.format(match, team, odd, website)
                    count += 1
            if match.sure_bet:
                sure_bet_matches.append(match)
        if league_text:
            text += '\n{}\n{}'.format(league, league_text)
    text += '\nTotal number of matches: {}\n'.format(count)
    if sure_bet_matches:
        text += '\nSure bets\n'
        for match in sure_bet_matches:
            text += '{}\n'.format(match)
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
