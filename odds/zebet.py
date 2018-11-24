#! /usr/bin/env python3
# coding: utf-8

import download
from bs4 import BeautifulSoup
import datetime
from model import Match

HTML_ROOT = 'https://www.zebet.fr/fr/competition/{}'
HTML_URLS = {2411: '94-premier_league', 1844: '97-dominos_ligue_2', 1951: '5-major_league_soccer',
             2105: '81-serie_a_bre', 1882: '254-spor_toto_sueper_lig', 1845: '268-bundesliga',
             1869: '306-liga_santander', 1866: '86-premier_liga', 1843: '96-ligue_1_conforama',
             1947: '771-jleague', 1846: '267-bundesliga_2', 1849: '102-eredivisie', 1859: '63-eliteserien',
             1827: '131-tipico_bundesliga', 1874: '99-allsvenskan', 1871: '18-laliga2', 1854: '305-serie_a',
             1975: '2807-primera_division_mex', 5641: '2530-primera_division_arg', 1856: '604-serie_b',
             2417: '100-scottish_premiership', 2412: '202-championship', 1832: '101-pro_league_1a',
             1837: '130-superligaen', 1884: '169-super_league_gre'}
HTML_PATH = 'cache/zebet/league-{}.html'
WEBSITE = 'ZEbet'


def get_odds_from_html_with_league_id(league_id):
    if league_id not in HTML_URLS:
        print('Unrecognized league: {}'.format(league_id))
        return None
    html_path = HTML_PATH.format(league_id)
    url = HTML_ROOT.format(HTML_URLS[league_id])
    download.download_data(url, html_path)
    with open(html_path, encoding='utf-8', newline='') as file:
        soup = BeautifulSoup(file, 'html.parser')
        matches = []
        for bet_group in soup.find_all('div', {'class': 'item-content catcomp item-bloc-type-1'}):
            actors = bet_group.find_all('span', {'class': 'pmq-cote-acteur'})
            team1 = actors[0].string
            team2 = actors[3].string
            odds = bet_group.find_all('span', {'class': 'pmq-cote'})
            odd1 = float(odds[0].string)
            odd2 = float(odds[3].string)
            match_time_string = bet_group.find('div', {'class': 'bet-time'}).string
            try:
                match_time = datetime.datetime.strptime(match_time_string, '%d/%m %H:%M')
                match_time = match_time.replace(year=datetime.datetime.utcnow().year,
                                                tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
                match_time = match_time.astimezone(datetime.timezone.utc)
                match = Match(match_time, team1, team2)
                match.teams[0].odds[WEBSITE] = odd1
                match.teams[1].odds[WEBSITE] = odd2
                matches.append(match)
            except ValueError as err:
                print(err)
    return matches


def enrich_matches(matches_by_league):
    for league, matches in matches_by_league.items():
        print('Processing league {}'.format(league))
        matches_with_odds = get_odds_from_html_with_league_id(league.league_id)
        if not matches_with_odds:
            continue
        merged_matches = []
        for match in matches:
            for match_with_odds in matches_with_odds:
                if match_with_odds and match.datetime == match_with_odds.datetime \
                        and (match.teams[0].name == match_with_odds.teams[0].name
                             or match.teams[1].name == match_with_odds.teams[1].name):
                    merged_match = Match(match.datetime, match.teams[0].name, match.teams[1].name)
                    merged_match.teams[0].prob = match.teams[0].prob
                    merged_match.teams[1].prob = match.teams[1].prob
                    merged_match.teams[0].odds = match_with_odds.teams[0].odds
                    merged_match.teams[1].odds = match_with_odds.teams[1].odds
                    merged_matches.append(merged_match)
                    break
        matches_by_league[league] = merged_matches
