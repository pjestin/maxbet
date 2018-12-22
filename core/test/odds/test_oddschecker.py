import unittest
from unittest.mock import patch, call
from core.common.model import Match
from core.odds import oddschecker
from datetime import datetime, timezone


ODDSCHECKER_TEST_FILE_MATCH = 'core/test/odds/data/oddschecker_match.html'
ODDSCHECKER_TEST_FILE_LEAGUE = 'core/test/odds/data/oddschecker_league.html'
HOME_TEAM_NAME = 'Aberdeen'
AWAY_TEAM_NAME = 'Dundee'
FAKE_URL = 'fake/url'
ODDSCHECKER_FOOTBALL_URL = 'https://www.oddschecker.com/football/netherlands/eredivisie/{}/winner'


class OddsCheckerTest(unittest.TestCase):

    @patch('core.common.download.get_page')
    def test_decode_match(self, mocked_get_page):
        with open(ODDSCHECKER_TEST_FILE_MATCH, encoding='latin_1', newline='') as match_page:
            mocked_get_page.return_value = match_page
            match = oddschecker.decode_match(FAKE_URL, HOME_TEAM_NAME, AWAY_TEAM_NAME)

            expected_match = Match(datetime(2018, 12, 18, 19, 45, tzinfo=timezone.utc), HOME_TEAM_NAME, AWAY_TEAM_NAME)
            expected_match.teams['1'].odds = {'Unibet': 1.54, 'Bet365': 1.53, 'Skybet': 1.44, 'Ladbrokes': 1.57,
                                              'William Hill': 1.5, 'Marathon Bet': 1.52, 'Betfair Sportsbook': 1.53,
                                              'Bet Victor': 1.55, 'Paddy Power': 1.5, 'Coral': 1.57, 'Betfred': 1.53,
                                              'Boyle Sports': 1.55, 'Black Type': 1.53, 'Redzone': 1.54, 'Betway': 1.55,
                                              'BetBright': 1.53, '10Bet': 1.53, 'Sportingbet': 1.48, '188Bet': 1.55,
                                              '888sport': 1.52, 'SportPesa': 1.54, 'Spreadex': 1.53,
                                              'Sport Nation': 1.51, 'Betfair': 1.54, 'Betdaq': 1.56, 'Matchbook': 1.57,
                                              'Smarkets': 1.56, 'Royal Panda': 0.0}
            expected_match.teams['N'].odds = {'Unibet': 3.75, 'Bet365': 4.2, 'Skybet': 4.2, 'Ladbrokes': 3.9,
                                              'William Hill': 4.0, 'Marathon Bet': 4.2, 'Betfair Sportsbook': 3.9,
                                              'Bet Victor': 4.1, 'Paddy Power': 3.75, 'Coral': 3.9, 'Betfred': 4.0,
                                              'Boyle Sports': 3.8, 'Black Type': 4.0, 'Redzone': 3.85, 'Betway': 3.8,
                                              'BetBright': 4.1, '10Bet': 3.8, 'Sportingbet': 4.1, '188Bet': 3.95,
                                              '888sport': 3.7, 'SportPesa': 3.85, 'Spreadex': 3.8, 'Sport Nation': 3.75,
                                              'Betfair': 4.04, 'Betdaq': 4.14, 'Matchbook': 4.1, 'Smarkets': 4.14,
                                              'Royal Panda': 0.0}
            expected_match.teams['2'].odds = {'Unibet': 6.75, 'Bet365': 5.75, 'Skybet': 7.0, 'Ladbrokes': 6.5,
                                              'William Hill': 7.0, 'Marathon Bet': 6.55, 'Betfair Sportsbook': 7.0,
                                              'Bet Victor': 6.25, 'Paddy Power': 7.0, 'Coral': 6.5, 'Betfred': 6.5,
                                              'Boyle Sports': 6.5, 'Black Type': 7.0, 'Redzone': 6.85, 'Betway': 6.5,
                                              'BetBright': 6.5, '10Bet': 6.7, 'Sportingbet': 6.5, '188Bet': 6.5,
                                              '888sport': 6.75, 'SportPesa': 6.75, 'Spreadex': 7.0, 'Sport Nation': 6.6,
                                              'Betfair': 7.08, 'Betdaq': 7.27, 'Matchbook': 7.39, 'Smarkets': 7.47,
                                              'Royal Panda': 0.0}

            self.assertEqual(expected_match, match)

    @patch('core.common.download.get_page')
    @patch('core.odds.oddschecker.decode_match')
    def test_get_matches_from_page(self, mocked_decode_match, mocked_get_page):
        mocked_decode_match.return_value = None
        with open(ODDSCHECKER_TEST_FILE_LEAGUE, encoding='latin_1', newline='') as page:
            mocked_get_page.return_value = page
            matches = oddschecker.get_matches_with_odds_from_url(FAKE_URL)

            self.assertEqual(18, len(matches))
            self.assertEqual(18, mocked_decode_match.call_count)

            calls = [call(ODDSCHECKER_FOOTBALL_URL.format('venlo-v-zwolle'), 'Venlo', 'Zwolle'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('fort-sittard-v-groningen'), 'Fort Sittard', 'Groningen'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('nac-breda-v-heerenveen'), 'NAC Breda', 'Heerenveen'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('psv-v-az-alkmaar'), 'PSV', 'AZ Alkmaar'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('sbv-excelsior-v-heracles'), 'Heracles Almelo', 'Excelsior Rotterdam'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('utrecht-v-ajax'), 'Utrecht', 'Ajax'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('de-graafschap-v-vitesse'), 'De Graafschap', 'Vitesse'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('den-haag-v-feyenoord'), 'Den Haag', 'Feyenoord'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('emmen-v-willem-ii'), 'Emmen', 'Willem II'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('vitesse-v-excelsior-rotterdam'), 'Vitesse', 'Excelsior Rotterdam'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('az-alkmaar-v-utrecht'), 'AZ Alkmaar', 'Utrecht'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('den-haag-v-venlo'), 'Den Haag', 'Venlo'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('zwolle-v-feyenoord'), 'Zwolle', 'Feyenoord'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('groningen-v-heracles-almelo'), 'Groningen', 'Heracles Almelo'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('willem-ii-v-nac-breda'), 'Willem II', 'NAC Breda'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('de-graafschap-v-fort-sittard'), 'De Graafschap', 'Fort Sittard'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('emmen-v-psv'), 'Emmen', 'PSV'),
                     call(ODDSCHECKER_FOOTBALL_URL.format('ajax-v-heerenveen'), 'Ajax', 'Heerenveen')
                     ]

            mocked_decode_match.assert_has_calls(calls)
