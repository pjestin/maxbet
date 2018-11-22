import unittest
from odds import cotes
from datetime import datetime, timezone, timedelta
from model import Match

DATA_PATH = 'test/odds/data/cotes.html'
TEAM_1_NAME = 'Bate Borisov'
TEAM_2_NAME = 'FC Fehervar Videoton'


class CotesTest(unittest.TestCase):

    def test_get_matches_wth_odds(self):
        matches = cotes.get_matches_with_odds_from_file(DATA_PATH)
        self.assertEqual(24, len(matches))
        match = matches[2]

        match_datetime = datetime(2018, 11, 29, 18, 55, tzinfo=timezone(timedelta(hours=1)))
        expected_match = Match(match_datetime, TEAM_1_NAME, TEAM_2_NAME)
        expected_match.teams['1'].odds = {'PMU': 1.8, 'Winamax': 1.92}
        expected_match.teams['N'].odds = {'PMU': 2.95, 'Winamax': 3.15}
        expected_match.teams['2'].odds = {'PMU': 3.8, 'Winamax': 3.9}

        self.assertEqual(expected_match, match)
