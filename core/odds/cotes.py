#! /usr/bin/env python3
# coding: utf-8

from core.common import download
from core.common.model import Match
from bs4 import BeautifulSoup
import datetime
import locale
import re
import unidecode
import math


URL_ROOT = 'http://www.cotes.fr/football/{}'
FILE_PATH_ROOT = 'core/cache/cotes/league-{}.html'
LEAGUE_URLS = {1818: 'Ligue-des-Champions-ed7', 1849: 'Pays-Bas-Eredivisie-ed10', 1844: 'France-Ligue-2-ed9',
               2411: 'Angleterre-Premier-League-ed2', 1951: 'Etats-Unis-MLS-ed60', 2105: 'Bresil-Campeonato-ed116',
               1882: 'Turquie-Super-Lig-ed50', 1845: 'Allemagne-Bundesliga-ed4', 1869: 'Espagne-LaLiga-ed6',
               1866: 'Russie-Premier-Ligue-ed51', 1843: 'France-Ligue-1-ed3', 1947: 'Japon-J-League-ed34',
               1846: 'Allemagne-Bundesliga-2-ed44', 1859: 'Norvege-Eliteserien-ed56', 1874: 'Suede-Allsvenskan-ed28',
               1871: 'Espagne-LaLiga-2-ed47', 1854: 'Italie-Serie-A-ed5', 1975: 'Mexico-Primera-A-ed109',
               5641: 'Argentine-Apuerta/Clausura-ed57', 1856: 'Italie-Serie-B-ed14',
               2417: 'Ecosse-Premier-League-ed120', 2412: 'Angleterre-Championship-ed13',
               1837: 'Danemark-Superligue-ed26', 1884: 'Grece-Superleague-ed19', 1879: 'Suisse-Super-League-ed12',
               1827: 'Autriche-Bundesliga-ed17', 1820: 'Ligue-Europa-ed1181', 1864: 'Portugal-Liga-NOS-ed15',
               1832: 'Belgique-Jupiler-League-ed11', 0: 'Ukraine-Premier-League-ed61',
               1: 'Pologne-Ekstraklasa-ed30', 2: 'Slovenie-Division-1-ed35',
               3: 'P.-de-Galles--Premier-League-ed137', 4: 'Chypre-Division-1-ed65',
               5: 'Rep.-Tcheque-1-Liga-ed45', 6: 'Angleterre-EFL-Cup-ed21', 7: 'Hongrie-NB-1-ed141',
               8: 'Roumanie-Liga-1-ed54', 9: 'Slovaquie-Liga-1-ed36'}
BET_FACTOR = 0.5
WEBSITES = ['ZEbet', 'Betclic', 'ParionsWeb', 'Winamax']


def get_matches_with_odds_from_file(file_path):
    locale.setlocale(locale.LC_ALL, 'fr_FR')
    matches = []
    with open(file_path, encoding='latin_1', newline='') as file:
        soup = BeautifulSoup(file, 'html.parser')
        bettable = soup.find('table', {'class': 'bettable'})
        try:
            for row in bettable.find_all('tr'):
                row_attr = row.attrs
                if 'style' in row_attr:
                    teams = row.find_all('a', {'class': 'otn'})
                    team1 = unidecode.unidecode(teams[0].string)
                    team2 = unidecode.unidecode(teams[1].string)
                    subrow = row.find('td', {'class': re.compile('maincol.*')})
                    match_text = subrow.get_text()
                    regex_match = re.search('(\d* \w* \d{4} à \d{2}h\d{2})', match_text)
                    match_time = datetime.datetime.strptime(regex_match.group(0), '%d %B %Y à %Hh%M')\
                        .replace(tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
                    sure_bet = 'surebetbox' in subrow.attrs['class']
                    match = Match(match_time, team1, team2)
                    match.sure_bet = sure_bet
                    matches.append(match)
                elif 'class' in row_attr:
                    website = row_attr['title'][12:]
                    bets = row.find_all('td', {'class': 'bet'})
                    odd1 = float(bets[0].string)
                    oddx = float(bets[1].string)
                    odd2 = float(bets[2].string)
                    matches[-1].teams['1'].odds[website] = odd1
                    matches[-1].teams['N'].odds[website] = oddx
                    matches[-1].teams['2'].odds[website] = odd2
        except ValueError:
            print('Parsing of match failed')
    return matches


def get_matches_with_odds_for_league(league_id):
    print('Processing league {}'.format(league_id))
    if league_id not in LEAGUE_URLS:
        print('Unrecognized league: {}'.format(league_id))
        return
    url = URL_ROOT.format(LEAGUE_URLS[league_id])
    file_path = FILE_PATH_ROOT.format(league_id)
    download.download_data(url, file_path)
    return get_matches_with_odds_from_file(file_path)


def get_matches_with_odds():
    matches = []
    for league_id in LEAGUE_URLS:
        matches.extend(get_matches_with_odds_for_league(league_id))
    return matches


def enrich_matches(matches_by_league):
    for league, matches in matches_by_league.items():
        matches_with_odds = get_matches_with_odds_for_league(league)
        if not matches_with_odds:
            print('No match for this league')
            continue
        merged_matches = []
        for match_with_odds in matches_with_odds:
            found_match = False
            for match in matches:
                if match_with_odds and match.datetime == match_with_odds.datetime \
                        and (match.teams['1'].name == match_with_odds.teams['1'].name
                             or match.teams['2'].name == match_with_odds.teams['2'].name):
                    merged_match = Match(match.datetime, match_with_odds.teams['1'].name,
                                         match_with_odds.teams['2'].name)
                    for team_id in ['1', 'N', '2']:
                        merged_match.teams[team_id].prob = match.teams[team_id].prob
                        merged_match.teams[team_id].score = match.teams[team_id].score
                        merged_match.teams[team_id].odds = match_with_odds.teams[team_id].odds
                    merged_match.sure_bet = match_with_odds.sure_bet
                    merged_matches.append(merged_match)
                    found_match = True
                    break
            if not found_match:
                merged_matches.append(match_with_odds)

        matches_by_league[league] = merged_matches


def get_value_bets(params):
    bet_odd_power, min_prob, min_return, max_return = params
    bet_matches = set()
    matches = get_matches_with_odds()
    for match in matches:
        margins = {}
        for site in match.teams['1'].odds.keys():
            margins[site] = 0.0
            for team in match.teams.values():
                margins[site] += 1 / team.odds[site]
        for side_id, side in match.teams.items():
            prob = 0.0
            for site in margins.keys():
                prob += 1 / side.odds[site] / margins[site]
            prob /= len(margins)
            best_website, best_odd = None, 0.0
            for website, odd in side.odds.items():
                if (not WEBSITES or website in WEBSITES) and odd > best_odd:
                    best_odd, best_website = odd, website
            if not best_odd:
                continue
            bet_fraction = BET_FACTOR / math.pow(best_odd, bet_odd_power)
            if prob > min_prob and min_return < prob * best_odd < max_return:
                bet_matches.add((str(match), side_id, best_website, best_odd, match.datetime, bet_fraction))
    return bet_matches
