import unittest
from odds import fivethirtyeight
import json
from model import Match
from datetime import datetime, timezone
from collections import OrderedDict

FIVETHIRTYEIGHT_DATA_PATH = 'test/odds/data/fivethirtyeight.json'
TEAM_1_NAME = 'Erzurumspor'
TEAM_2_NAME = 'Antalyaspor'
FIVETHIRTYEIGHT = '538'


class FiveThirtyEightTest(unittest.TestCase):

    def test_create_matches(self):
        with open(FIVETHIRTYEIGHT_DATA_PATH, mode='r', encoding='latin-1') as file:
            data = json.load(file, object_pairs_hook=OrderedDict)
        matches = fivethirtyeight.create_matches(data)
        self.assertEqual(31, len(matches))
        match = next(iter(matches.values()))[0]
        print('Match: {}'.format(match))

        match_datetime = datetime(2018, 11, 24, 10, 30, tzinfo=timezone.utc)
        expected_match = Match(match_datetime, TEAM_1_NAME, TEAM_2_NAME)
        expected_match.teams['1'].probs[FIVETHIRTYEIGHT] = 0.41623
        expected_match.teams['N'].probs[FIVETHIRTYEIGHT] = 0.2934
        expected_match.teams['2'].probs[FIVETHIRTYEIGHT] = 0.29038
        print('Expected match: {}'.format(expected_match))

        self.assertEqual(expected_match, match)
