from core.common import download
import json
import re
from datetime import datetime, timezone
import unidecode

from bs4 import BeautifulSoup

from core.common.model import Match


DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000%z'
THRESHOLD_DATE = datetime(2018, 11, 1, tzinfo=timezone.utc)

FOOTBALL = 'football'
COMPETITIONS = 'competitions'
LIST = 'list'
COMPETITION_REFERENCE = 'competition_reference'
ID = 'id'
COMPETITION_MATCHES = 'competitionMatches'
MATCHES = 'matches'
MATCH = 'match'
MATCH_DATE = 'match_date'
TEAM_SCORE_A = 'team_score_a'
TEAM_SCORE_B = 'team_score_b'
TEAM = 'team'
NAME = 'name'
FULL_TIME_SCORE = 'full_time_score'
HOME = 'home'
AWAY = 'away'
STATE = 'state'
FULL_TIME = 'FULLTIME'

SPORTING_LIFE_FOOTBALL = 'https://www.sportinglife.com/football/results'
SPORTING_LIFE_COMPETITION_ROOT = 'https://www.sportinglife.com/football/results/competitions/id/{}'


def get_json_data(url):
    page = download.get_page(url)
    soup = BeautifulSoup(page, 'html.parser')
    data = soup.find('script', {'src': False, 'id': False, 'type': False})
    search = re.search('__data=(.*); window', data.get_text())
    return json.loads(search.group(1))


def get_matches_from_url(url):
    print('Processing league: {}'.format(url))
    json_data = get_json_data(url)
    matches = []
    if MATCHES not in json_data[FOOTBALL][COMPETITION_MATCHES]:
        return []
    for match_data in json_data[FOOTBALL][COMPETITION_MATCHES][MATCHES][MATCH]:
        match_datetime = datetime.strptime(match_data[MATCH_DATE], DATE_TIME_FORMAT)
        if match_data[STATE] != FULL_TIME or FULL_TIME_SCORE not in match_data or match_datetime < THRESHOLD_DATE:
            continue
        home_team_name = unidecode.unidecode(match_data[TEAM_SCORE_A][TEAM][NAME])
        away_team_name = unidecode.unidecode(match_data[TEAM_SCORE_B][TEAM][NAME])
        match = Match(match_datetime, home_team_name, away_team_name)
        match.teams['1'].score = int(match_data[FULL_TIME_SCORE][HOME])
        match.teams['2'].score = int(match_data[FULL_TIME_SCORE][AWAY])
        print('Decoded match: {}'.format(match))
        matches.append(match)
    return matches


def get_matches():
    json_data = get_json_data(SPORTING_LIFE_FOOTBALL)
    matches = []
    for competition in json_data[FOOTBALL][COMPETITIONS][LIST]:
        competition_id = competition[COMPETITION_REFERENCE][ID]
        competition_url = SPORTING_LIFE_COMPETITION_ROOT.format(competition_id)
        matches.extend(get_matches_from_url(competition_url))
    return matches
