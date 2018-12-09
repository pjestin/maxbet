import unittest
from odds import cotes
from datetime import datetime, timezone, timedelta
from common.model import Match
from unittest.mock import patch

DATA_PATH = 'test/odds/data/cotes.html'
TEAM_1_1_NAME = 'FC Astana'
TEAM_1_2_NAME = 'Dynamo Kiev'
TEAM_2_1_NAME = 'Bate Borisov'
TEAM_2_2_NAME = 'FC Fehervar Videoton'


class CotesTest(unittest.TestCase):

    def setUp(self):
        self.match_1_datetime = datetime(2018, 11, 29, 16, 50, tzinfo=timezone(timedelta(hours=1)))
        self.match_1 = Match(self.match_1_datetime, TEAM_1_1_NAME, TEAM_1_2_NAME)
        self.match_1.teams['1'].odds = {'Betclic': 2.52, 'Betstars': 2.25, 'Bwin': 2.5, 'NetBet': 2.52,
                                        'ParionsWeb': 2.55, 'PMU': 2.35, 'Unibet': 2.5, 'Winamax': 2.57, 'ZEbet': 2.57}
        self.match_1.teams['N'].odds = {'Betclic': 2.42, 'Betstars': 2.63, 'Bwin': 2.55, 'NetBet': 2.45,
                                        'ParionsWeb': 2.45, 'PMU': 2.35, 'Unibet': 2.58, 'Winamax': 2.47, 'ZEbet': 2.47}
        self.match_1.teams['2'].odds = {'Betclic': 3.3, 'Betstars': 2.65, 'Bwin': 3.3, 'NetBet': 3.35,
                                        'ParionsWeb': 3.35, 'PMU': 3.25, 'Unibet': 3.2, 'Winamax': 3.4, 'ZEbet': 3.4}
        self.match_2_datetime = datetime(2018, 11, 29, 18, 55, tzinfo=timezone(timedelta(hours=1)))
        self.match_2 = Match(self.match_2_datetime, TEAM_2_1_NAME, TEAM_2_2_NAME)
        self.match_2.teams['1'].odds = {'PMU': 1.8, 'Winamax': 1.92}
        self.match_2.teams['N'].odds = {'PMU': 2.95, 'Winamax': 3.55}
        self.match_2.teams['2'].odds = {'PMU': 3.8, 'Winamax': 3.9}

    def test_get_matches_wth_odds(self):
        matches = cotes.get_matches_with_odds_from_file(DATA_PATH)
        self.assertEqual(24, len(matches))
        self.assertEqual(self.match_1, matches[0])
        self.assertEqual(self.match_2, matches[2])

    @patch('odds.cotes.get_matches_with_odds')
    def test_get_value_bets(self, mocked_get_matches_with_odds):
        mocked_get_matches_with_odds.return_value = [self.match_1, self.match_2]
        bet_matches = cotes.get_value_bets(params=[1., 0.26, 0.96, 5.])
        expected_bet_matches = {('2018-11-29T18:55:00+01:00: Bate Borisov vs FC Fehervar Videoton',
                                 'N', 'Winamax', 3.55, self.match_2_datetime, 0.14084507042253522)}
        self.assertEqual(expected_bet_matches, bet_matches)
