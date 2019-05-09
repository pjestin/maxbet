import unittest
from core.odds import cotes
from datetime import datetime, timezone, timedelta
from core.common.model import Match
from unittest.mock import patch, call
import core.common.download

COTES_LEAGUE_PATH = 'core/test/odds/data/cotes-league.html'
COTES_LEAGUE_DST_PATH = 'core/test/odds/data/cotes-league-dst.html'
COTES_FOOTBALL_PATH = 'core/test/odds/data/cotes-football.html'
URL_ROOT = 'http://www.cotes.fr/football/{}'
TEAM_1_1_NAME = 'FC Astana'
TEAM_1_2_NAME = 'Dynamo Kiev'
TEAM_2_1_NAME = 'Bate Borisov'
TEAM_2_2_NAME = 'FC Fehervar Videoton'
FAKE_URL = 'fake/url'


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

    @patch('core.common.download.get_page')
    def test_get_matches_wth_odds_from_page(self, mocked_get_page):
        with open(COTES_LEAGUE_PATH, encoding='latin_1', newline='') as file:
            mocked_get_page.return_value = file
            matches = cotes.get_matches_with_odds_from_url(FAKE_URL)
            self.assertEqual(24, len(matches))
            self.assertEqual(self.match_1, matches[0])
            self.assertEqual(self.match_2, matches[2])
    
    @patch('core.common.download.get_page')
    def test_get_matches_wth_odds_from_page_dst(self, mocked_get_page):
        match_datetime = datetime(2019, 5, 12, 15, 30, tzinfo=timezone(timedelta(hours=2)))
        expected_match = Match(match_datetime, 'Cologne', 'Regensburg')
        expected_match.teams['1'].odds = {'Betclic': 1.38, 'Betstars': 1.36, 'Bwin': 1.4, 'NetBet': 1.3, 'PMU': 1.26,
            'ParionsWeb': 1.4, 'Unibet': 1.36, 'Winamax': 1.38, 'ZEbet': 1.31}
        expected_match.teams['N'].odds = {'Betclic': 4.4, 'Betstars': 4.1, 'Bwin': 4.25, 'NetBet': 4.6, 'PMU': 4.4,
            'ParionsWeb': 4.4, 'Unibet': 4.3, 'Winamax': 4.4, 'ZEbet': 4.6}
        expected_match.teams['2'].odds = {'Betclic': 5.0, 'Betstars': 5.0, 'Bwin': 5.0, 'NetBet': 5.3, 'PMU': 5.6,
            'ParionsWeb': 5.0, 'Unibet': 5.25, 'Winamax': 5.0, 'ZEbet': 5.3}
        with open(COTES_LEAGUE_DST_PATH, encoding='latin_1', newline='') as file:
            mocked_get_page.return_value = file
            matches = cotes.get_matches_with_odds_from_url(FAKE_URL)
            self.assertEqual(9, len(matches))
            self.assertEqual(expected_match.teams['1'].odds, matches[0].teams['1'].odds)
            self.assertEqual(expected_match.teams['N'].odds, matches[0].teams['N'].odds)
            self.assertEqual(expected_match.teams['2'].odds, matches[0].teams['2'].odds)
            self.assertEqual(expected_match, matches[0])

    @patch('core.common.download.get_page')
    @patch('core.odds.cotes.get_matches_with_odds_from_url')
    def test_get_matches_wth_odds(self, mocked_get_matches_with_odds_from_page, mocked_get_page):
        mocked_get_matches_with_odds_from_page.return_value = [None]
        with open(COTES_FOOTBALL_PATH, encoding='latin_1', newline='') as file:
            mocked_get_page.return_value = file
            matches = cotes.get_matches_with_odds()
            self.assertEqual(35, len(matches))
            self.assertEqual(35, mocked_get_matches_with_odds_from_page.call_count)

            calls = [call(URL_ROOT.format('Ligue-des-Nations-ed2195')),
                     call(URL_ROOT.format("Coupe-d'Asie-des-Nations-ed1346")),
                     call(URL_ROOT.format('Ligue-des-Champions-ed7')),
                     call(URL_ROOT.format('Ligue-Europa-ed1181')),
                     call(URL_ROOT.format('France-Ligue-1-ed3')),
                     call(URL_ROOT.format('Angleterre-Premier-League-ed2')),
                     call(URL_ROOT.format('Espagne-LaLiga-ed6')),
                     call(URL_ROOT.format('Allemagne-Bundesliga-ed4')),
                     call(URL_ROOT.format('Italie-Serie-A-ed5')),
                     call(URL_ROOT.format('Belgique-Jupiler-League-ed11')),
                     call(URL_ROOT.format('Suisse-Super-League-ed12')),
                     call(URL_ROOT.format('Portugal-Liga-NOS-ed15')),
                     call(URL_ROOT.format("Coupe-d'Allemagne-ed23")),
                     call(URL_ROOT.format('Angleterre-EFL-Cup-ed21')),
                     call(URL_ROOT.format('Angleterre-FA-Cup-ed22')),
                     call(URL_ROOT.format('Espagne-Coupe-du-Roi-ed46')),
                     call(URL_ROOT.format('France-Coupe-de-la-Ligue-ed18')),
                     call(URL_ROOT.format('Coupe-de-France-ed317'))
                     ]

            mocked_get_matches_with_odds_from_page.assert_has_calls(calls)

    @patch('core.odds.cotes.get_matches_with_odds')
    def test_get_value_bets(self, mocked_get_matches_with_odds):
        mocked_get_matches_with_odds.return_value = [self.match_1, self.match_2]
        bet_matches = cotes.get_value_bets(params=[1., 0.26, 0.96, 5.])
        expected_bet_matches = {('2018-11-29T18:55:00+01:00: Bate Borisov vs FC Fehervar Videoton',
                                 'N', 'Winamax', 3.55, self.match_2_datetime, 0.14084507042253522)}
        self.assertEqual(expected_bet_matches, bet_matches)
