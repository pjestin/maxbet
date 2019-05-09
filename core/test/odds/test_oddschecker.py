import unittest
from unittest.mock import patch, call
from core.common.model import Match
from core.odds import oddschecker
from datetime import datetime, timezone, timedelta
import core.common.download


ODDSCHECKER_TEST_FILE_MATCH = 'core/test/odds/data/oddschecker_match.html'
ODDSCHECKER_TEST_FILE_MATCH_DST = 'core/test/odds/data/oddschecker_match_dst.html'
ODDSCHECKER_TEST_FILE_LEAGUE = 'core/test/odds/data/oddschecker_league.html'
ODDSCHECKER_TEST_FILE_FOOTBALL = 'core/test/odds/data/oddschecker_football.html'
FAKE_URL = 'fake/url'
ODDSCHECKER_EREDIVISIE_URL = 'https://www.oddschecker.com/football/netherlands/eredivisie/{}/winner'
ODDSCHECKER_FOOTBALL_ROOT = 'https://www.oddschecker.com/football/{}'


class OddsCheckerTest(unittest.TestCase):

    @patch('datetime.datetime')
    @patch('core.common.download.get_page')
    def test_decode_match(self, mocked_get_page, mocked_datetime):
        match_datetime = datetime(2018, 12, 18, 19, 45, tzinfo=timezone.utc)
        mocked_datetime.utcnow.return_value = match_datetime - timedelta(minutes=3251)
        mocked_datetime.strptime = datetime.strptime
        home_team_name = 'Aberdeen'
        away_team_name = 'Dundee'
        with open(ODDSCHECKER_TEST_FILE_MATCH, encoding='latin_1', newline='') as match_page:
            mocked_get_page.return_value = match_page
            match = oddschecker.decode_match(FAKE_URL, home_team_name, away_team_name)

            expected_match = Match(match_datetime, home_team_name, away_team_name)
            expected_match.teams['1'].odds = {'Unibet': 1.54, 'Bet365': 1.53, 'Skybet': 1.44, 'Ladbrokes': 1.57,
                                              'William Hill': 1.5, 'Marathon Bet': 1.52, 'Betfair Sportsbook': 1.53,
                                              'Bet Victor': 1.55, 'Paddy Power': 1.5, 'Coral': 1.57, 'Betfred': 1.53,
                                              'Boyle Sports': 1.55, 'Black Type': 1.53, 'Redzone': 1.54, 'Betway': 1.55,
                                              'BetBright': 1.53, '10Bet': 1.53, 'Sportingbet': 1.48, '188Bet': 1.55,
                                              '888sport': 1.52, 'SportPesa': 1.54, 'Spreadex': 1.53,
                                              'Sport Nation': 1.51, 'Betfair': 1.54, 'Betdaq': 1.56, 'Matchbook': 1.57,
                                              'Smarkets': 1.56}
            expected_match.teams['N'].odds = {'Unibet': 3.75, 'Bet365': 4.2, 'Skybet': 4.2, 'Ladbrokes': 3.9,
                                              'William Hill': 4.0, 'Marathon Bet': 4.2, 'Betfair Sportsbook': 3.9,
                                              'Bet Victor': 4.1, 'Paddy Power': 3.75, 'Coral': 3.9, 'Betfred': 4.0,
                                              'Boyle Sports': 3.8, 'Black Type': 4.0, 'Redzone': 3.85, 'Betway': 3.8,
                                              'BetBright': 4.1, '10Bet': 3.8, 'Sportingbet': 4.1, '188Bet': 3.95,
                                              '888sport': 3.7, 'SportPesa': 3.85, 'Spreadex': 3.8, 'Sport Nation': 3.75,
                                              'Betfair': 4.04, 'Betdaq': 4.14, 'Matchbook': 4.1, 'Smarkets': 4.14}
            expected_match.teams['2'].odds = {'Unibet': 6.75, 'Bet365': 5.75, 'Skybet': 7.0, 'Ladbrokes': 6.5,
                                              'William Hill': 7.0, 'Marathon Bet': 6.55, 'Betfair Sportsbook': 7.0,
                                              'Bet Victor': 6.25, 'Paddy Power': 7.0, 'Coral': 6.5, 'Betfred': 6.5,
                                              'Boyle Sports': 6.5, 'Black Type': 7.0, 'Redzone': 6.85, 'Betway': 6.5,
                                              'BetBright': 6.5, '10Bet': 6.7, 'Sportingbet': 6.5, '188Bet': 6.5,
                                              '888sport': 6.75, 'SportPesa': 6.75, 'Spreadex': 7.0, 'Sport Nation': 6.6,
                                              'Betfair': 7.08, 'Betdaq': 7.27, 'Matchbook': 7.39, 'Smarkets': 7.47}

            self.assertEqual(expected_match, match)

    @patch('datetime.datetime')
    @patch('core.common.download.get_page')
    def test_decode_match_dst(self, mocked_get_page, mocked_datetime):
        match_datetime = datetime(2019, 5, 8, 20, 00, tzinfo=timezone(timedelta(hours=1)))
        mocked_datetime.utcnow.return_value = match_datetime - timedelta(minutes=3251)
        mocked_datetime.strptime = datetime.strptime
        home_team_name = 'Ajax'
        away_team_name = 'Tottenham'
        with open(ODDSCHECKER_TEST_FILE_MATCH_DST, encoding='latin_1', newline='') as match_page:
            mocked_get_page.return_value = match_page
            match = oddschecker.decode_match(FAKE_URL, home_team_name, away_team_name)

            expected_match = Match(match_datetime, home_team_name, away_team_name)
            expected_match.teams['1'].odds = {'10Bet': 2.25, '888sport': 2.25, 'Bet Victor': 2.3, 'Bet365': 2.3,
                'Betdaq': 2.33, 'Betfair': 2.29, 'Betfair Sportsbook': 2.3, 'Betfred': 2.3, 'Bethard': 2.35,
                'Betway': 2.3, 'Black Type': 2.2, 'Boyle Sports': 2.25, 'Coral': 2.3, 'Ladbrokes': 2.25, 'Marathon Bet': 2.3,
                'Matchbook': 2.34, 'MoPlay': 2.15, 'Paddy Power': 2.25, 'Redzone': 2.25, 'Royal Panda': 2.23, 'Skybet': 2.25,
                'Smarkets': 2.33, 'Sport Nation': 2.25, 'SportPesa': 2.25, 'Sportingbet': 2.25, 'Spreadex': 2.3, 'Unibet': 2.27,
                'William Hill': 2.25}
            expected_match.teams['N'].odds = {'10Bet': 3.65, '888sport': 3.7, 'Bet Victor': 3.7, 'Bet365': 3.75,
                'Betdaq': 3.69, 'Betfair': 3.61, 'Betfair Sportsbook': 3.7, 'Betfred': 3.7, 'Bethard': 3.65, 'Betway': 3.6,
                'Black Type': 3.6, 'Boyle Sports': 3.6, 'Coral': 3.6, 'Ladbrokes': 3.5, 'Marathon Bet': 3.68,
                'Matchbook': 3.71, 'MoPlay': 3.55, 'Paddy Power': 3.5, 'Redzone': 3.65, 'Royal Panda': 3.61, 'Skybet': 3.6,
                'Smarkets': 3.65, 'Sport Nation': 3.65, 'SportPesa': 3.65, 'Sportingbet': 3.7, 'Spreadex': 3.6, 'Unibet': 3.75,
                'William Hill': 3.6}
            expected_match.teams['2'].odds = {'10Bet': 3.05, '888sport': 3.05, 'Bet Victor': 3.1, 'Bet365': 3.1,
                'Betdaq': 3.11, 'Betfair': 3.04, 'Betfair Sportsbook': 3.1, 'Betfred': 3.1, 'Bethard': 3.0, 'Betway': 3.1,
                'Black Type': 3.0, 'Boyle Sports': 3.1, 'Coral': 3.1, 'Ladbrokes': 3.0, 'Marathon Bet': 3.16, 'Matchbook': 3.18,
                'MoPlay': 3.05, 'Paddy Power': 3.0, 'Redzone': 3.0, 'Royal Panda': 3.07, 'Skybet': 3.0, 'Smarkets': 3.16,
                'Sport Nation': 3.05, 'SportPesa': 3.05, 'Sportingbet': 3.1, 'Spreadex': 3.1, 'Unibet': 3.15, 'William Hill': 3.2}

            self.assertEqual(expected_match.teams['1'].odds, match.teams['1'].odds)
            self.assertEqual(expected_match.teams['N'].odds, match.teams['N'].odds)
            self.assertEqual(expected_match.teams['2'].odds, match.teams['2'].odds)
            self.assertEqual(expected_match, match)

    @patch('core.common.download.get_page')
    @patch('core.odds.oddschecker.decode_match')
    def test_get_matches_from_page(self, mocked_decode_match, mocked_get_page):
        mocked_decode_match.return_value = Match(datetime.utcnow(), None, None)
        with open(ODDSCHECKER_TEST_FILE_LEAGUE, encoding='latin_1', newline='') as page:
            mocked_get_page.return_value = page
            matches = oddschecker.get_matches_with_odds_from_url(FAKE_URL)

            self.assertEqual(18, len(matches))
            self.assertEqual(18, mocked_decode_match.call_count)

            calls = [call(ODDSCHECKER_EREDIVISIE_URL.format('venlo-v-zwolle'), 'Venlo', 'Zwolle'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('fort-sittard-v-groningen'), 'Fort Sittard', 'Groningen'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('nac-breda-v-heerenveen'), 'NAC Breda', 'Heerenveen'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('psv-v-az-alkmaar'), 'PSV', 'AZ Alkmaar'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('sbv-excelsior-v-heracles'), 'Heracles Almelo', 'Excelsior Rotterdam'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('utrecht-v-ajax'), 'Utrecht', 'Ajax'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('de-graafschap-v-vitesse'), 'De Graafschap', 'Vitesse'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('den-haag-v-feyenoord'), 'Den Haag', 'Feyenoord'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('emmen-v-willem-ii'), 'Emmen', 'Willem II'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('vitesse-v-excelsior-rotterdam'), 'Vitesse', 'Excelsior Rotterdam'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('az-alkmaar-v-utrecht'), 'AZ Alkmaar', 'Utrecht'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('den-haag-v-venlo'), 'Den Haag', 'Venlo'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('zwolle-v-feyenoord'), 'Zwolle', 'Feyenoord'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('groningen-v-heracles-almelo'), 'Groningen', 'Heracles Almelo'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('willem-ii-v-nac-breda'), 'Willem II', 'NAC Breda'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('de-graafschap-v-fort-sittard'), 'De Graafschap', 'Fort Sittard'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('emmen-v-psv'), 'Emmen', 'PSV'),
                     call(ODDSCHECKER_EREDIVISIE_URL.format('ajax-v-heerenveen'), 'Ajax', 'Heerenveen')
                     ]

            mocked_decode_match.assert_has_calls(calls)

    @patch('core.common.download.get_page')
    @patch('core.odds.oddschecker.get_matches_with_odds_from_url')
    def test_get_matches_with_odds(self, mocked_get_matches_from_url, mocked_get_page):
        mocked_get_matches_from_url.return_value = []
        with open(ODDSCHECKER_TEST_FILE_FOOTBALL, encoding='latin_1', newline='') as page:
            mocked_get_page.return_value = page

            oddschecker.get_matches_with_odds()

            self.assertEqual(94, mocked_get_matches_from_url.call_count)
            mocked_get_matches_from_url.assert_any_call(ODDSCHECKER_FOOTBALL_ROOT.format('sweden/allsvenskan'))
            mocked_get_matches_from_url.assert_any_call(ODDSCHECKER_FOOTBALL_ROOT.format('denmark/1st-division'))
            mocked_get_matches_from_url.assert_any_call(ODDSCHECKER_FOOTBALL_ROOT.format('france/ligue-1'))
