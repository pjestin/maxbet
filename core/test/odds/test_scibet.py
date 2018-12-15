import unittest
from core.odds import scibet
from datetime import datetime, timezone
from core.common.model import Match

DATA_PATH = 'core/test/odds/data/scibet.html'
TEAM_1_NAME = 'Moreirense FC'
TEAM_2_NAME = 'SC Portimonense'
TEAM_3_NAME = 'CD Santa Clara'
TEAM_4_NAME = 'Os Belenenses'
SCIBET = 'Scibet'


class ScibetTest(unittest.TestCase):

    def test_get_matches_wth_odds(self):
        matches = scibet.get_matches_from_file(DATA_PATH)
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
