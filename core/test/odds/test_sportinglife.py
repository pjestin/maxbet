import unittest
from unittest.mock import patch, call
from datetime import datetime, timezone

from core.odds import sportinglife
from core.common.model import Match

FAKE_URL = 'fake/url'
SPORTINGLIFE_LEAGUE_PATH = 'core/test/odds/data/sportinglife-league.html'
SPORTINGLIFE_FOOTBALL_PATH = 'core/test/odds/data/sportinglife-football.html'

SPORTING_LIFE_COMPETITION_ROOT = 'https://www.sportinglife.com/football/results/competitions/id/{}'

HOME_TEAM = 'Marseille'
AWAY_TEAM = 'Bordeaux'


class FlashscoreTest(unittest.TestCase):

    @patch('core.common.download.get_page')
    def test_get_matches_from_url(self, mocked_get_page):
        with open(SPORTINGLIFE_LEAGUE_PATH, encoding='utf-8') as file:
            mocked_get_page.return_value = file
            matches = sportinglife.get_matches_from_url(FAKE_URL)
            self.assertEqual(17, len(matches))

            expected_match_datetime = datetime(2019, 2, 5, 18, 0, tzinfo=timezone.utc)
            expected_match = Match(expected_match_datetime, HOME_TEAM, AWAY_TEAM)
            expected_match.teams['1'].score = 1
            expected_match.teams['2'].score = 0

            self.assertEqual(expected_match, matches[0])

    @patch('core.odds.sportinglife.get_matches_from_url')
    @patch('core.common.download.get_page')
    def test_get_matches(self, mocked_get_page, mocked_get_matches_from_url):
        mocked_get_matches_from_url.return_value = [None]
        with open(SPORTINGLIFE_FOOTBALL_PATH, encoding='utf-8') as file:
            mocked_get_page.return_value = file
            matches = sportinglife.get_matches()
            self.assertEqual(54, len(matches))

            calls = [call(SPORTING_LIFE_COMPETITION_ROOT.format('47')),
                     call(SPORTING_LIFE_COMPETITION_ROOT.format('1')),
                     call(SPORTING_LIFE_COMPETITION_ROOT.format('63')),
                     call(SPORTING_LIFE_COMPETITION_ROOT.format('10')),
                     call(SPORTING_LIFE_COMPETITION_ROOT.format('98')),
                     call(SPORTING_LIFE_COMPETITION_ROOT.format('16')),
                     call(SPORTING_LIFE_COMPETITION_ROOT.format('83')),
                     call(SPORTING_LIFE_COMPETITION_ROOT.format('62')),
                     ]

            mocked_get_matches_from_url.assert_has_calls(calls)
