import unittest
from unittest.mock import patch
from core.odds import fivethirtyeight
from core.common.model import Match
from datetime import datetime, timezone

FIVETHIRTYEIGHT_DATA_PATH = 'core/test/odds/data/fivethirtyeight.json'
TEAM_1_NAME = 'Erzurumspor'
TEAM_2_NAME = 'Antalyaspor'
FIVETHIRTYEIGHT = '538'


class FiveThirtyEightTest(unittest.TestCase):

    @patch('core.common.download.get_page')
    def test_get_matches(self, mocked_get_page):
        with open(FIVETHIRTYEIGHT_DATA_PATH, mode='r', encoding='latin-1') as file:
            mocked_get_page.return_value = file
            matches = fivethirtyeight.get_matches()
            self.assertEqual(317, len(matches))
            match = matches[0]
            print('Match: {}'.format(match))

            match_datetime = datetime(2018, 11, 24, 10, 30, tzinfo=timezone.utc)
            expected_match = Match(match_datetime, TEAM_1_NAME, TEAM_2_NAME)
            expected_match.teams['1'].probs[FIVETHIRTYEIGHT] = 0.41623
            expected_match.teams['N'].probs[FIVETHIRTYEIGHT] = 0.2934
            expected_match.teams['2'].probs[FIVETHIRTYEIGHT] = 0.29038
            print('Expected match: {}'.format(expected_match))

            self.assertEqual(expected_match, match)
