import unittest
from odds import scibet
from datetime import datetime, timezone
from model import Match

DATA_PATH = 'test/odds/data/scibet.html'
TEAM_1_NAME = 'Moreirense FC'
TEAM_2_NAME = 'SC Portimonense'


class ScibetTest(unittest.TestCase):

    def test_get_matches_wth_odds(self):
        matches = scibet.get_matches_with_odds_from_file(DATA_PATH)
        self.assertEqual(9, len(matches))
        match = matches[0]

        match_datetime = datetime(2018, 11, 9, 19, 0, tzinfo=timezone.utc)
        expected_match = Match(match_datetime, TEAM_1_NAME, TEAM_2_NAME)
        expected_match.teams['1'].odds = {'Scibet': 2.42}
        expected_match.teams['N'].odds = {'Scibet': 3.21}
        expected_match.teams['2'].odds = {'Scibet': 2.9}
        expected_match.teams['1'].prob = 0.491737
        expected_match.teams['N'].prob = 0.275461
        expected_match.teams['2'].prob = 0.232802
        expected_match.teams['1'].score = 2
        expected_match.teams['2'].score = 0

        self.assertEqual(expected_match, match)
