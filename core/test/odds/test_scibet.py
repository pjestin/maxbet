import unittest
from unittest.mock import patch, call
from core.odds import scibet
from datetime import datetime, timezone
from core.common.model import Match

SCIBET_LEAGUE_PATH = 'core/test/odds/data/scibet-league.html'
SCIBET_FOOTBALL_PATH = 'core/test/odds/data/scibet-football.html'
SCIBET_FOOTBALL_ROOT_URL = 'https://www.scibet.com/football/{}'
TEAM_1_NAME = 'Moreirense FC'
TEAM_2_NAME = 'SC Portimonense'
TEAM_3_NAME = 'CD Santa Clara'
TEAM_4_NAME = 'Os Belenenses'
SCIBET = 'Scibet'
FAKE_URL = 'fake/url'


class ScibetTest(unittest.TestCase):

    @patch('core.common.download.get_page')
    def test_get_matches_wth_odds(self, mocked_get_page):
        with open(SCIBET_LEAGUE_PATH, encoding='latin_1') as file:
            mocked_get_page.return_value = file
            matches = scibet.get_matches_from_url(FAKE_URL)
            self.assertEqual(18, len(matches))

            # Finished match
            match_datetime = datetime(2018, 11, 9, 19, 0, tzinfo=timezone.utc)
            expected_match = Match(match_datetime, TEAM_1_NAME, TEAM_2_NAME)
            expected_match.teams['1'].score = 2
            expected_match.teams['2'].score = 0

            finished_match = matches[0]
            self.assertEqual(expected_match, finished_match)

            # Projected match
            projected_match_datetime = datetime(2018, 11, 30, 20, 30, tzinfo=timezone.utc)
            expected_projected_match = Match(projected_match_datetime, TEAM_3_NAME, TEAM_4_NAME)
            expected_projected_match.teams['1'].odds = {SCIBET: 2.2}
            expected_projected_match.teams['N'].odds = {SCIBET: 3.14}
            expected_projected_match.teams['2'].odds = {SCIBET: 3.31}
            expected_projected_match.teams['1'].probs = {SCIBET: 0.45073645073644997}
            expected_projected_match.teams['N'].probs = {SCIBET: 0.30617330617331}
            expected_projected_match.teams['2'].probs = {SCIBET: 0.24309024309024}

            projected_match = matches[9]
            self.assertEqual(expected_projected_match, projected_match)

    @patch('core.odds.scibet.get_matches_from_url')
    @patch('core.common.download.get_page')
    def test_get_matches(self, mocked_get_page, mocked_get_matches_from_url):
        mocked_get_matches_from_url.return_value = [None]
        with open(SCIBET_FOOTBALL_PATH, encoding='latin_1') as file:
            mocked_get_page.return_value = file
            matches = scibet.get_matches()
            self.assertEqual(55, len(matches))
            self.assertEqual(55, mocked_get_matches_from_url.call_count)

            calls = [call(SCIBET_FOOTBALL_ROOT_URL.format('albania/kategoria-superiore/')),
                     call(SCIBET_FOOTBALL_ROOT_URL.format('argentina/primera-division/')),
                     call(SCIBET_FOOTBALL_ROOT_URL.format('australia/a-league/')),
                     call(SCIBET_FOOTBALL_ROOT_URL.format('austria/bundesliga/')),
                     call(SCIBET_FOOTBALL_ROOT_URL.format('belarus/cempionat/')),
                     call(SCIBET_FOOTBALL_ROOT_URL.format('belgium/jupiler-league/')),
                     call(SCIBET_FOOTBALL_ROOT_URL.format('brazil/serie-a/')),
                     call(SCIBET_FOOTBALL_ROOT_URL.format('bulgaria/a-grupa/')),
                     ]

            mocked_get_matches_from_url.assert_has_calls(calls)
