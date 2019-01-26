import unittest
from datetime import datetime, timezone, timedelta

from core.analysis.simulation import Simulation
from core.common import distribution


class DistributionTest(unittest.TestCase):

    def setUp(self):
        self.match_datetime = datetime(2018, 11, 10, 4, 0, tzinfo=timezone(timedelta(seconds=3600)))

    def test_value_bets(self):
        distribution.WEBSITES = ['PMU', 'Winamax']
        datetime_string = self.match_datetime.strftime(Simulation.DATE_TIME_FORMAT)
        odd_datetime_string = (self.match_datetime - timedelta(hours=47)).strftime(Simulation.DATE_TIME_FORMAT)
        match = {
            'datetime': datetime_string,
            'sides': {
                '1': {
                    'name': 'Atlas Guadalajara',
                    'odds': {'PMU': [[odd_datetime_string, 1.8]], 'Winamax': [[odd_datetime_string, 1.92]]}
                },
                'N': {
                    'odds': {'PMU': [[odd_datetime_string, 2.95]], 'Winamax': [[odd_datetime_string, 3.55]]}
                },
                '2': {
                    'name': 'Pachuca',
                    'odds': {'PMU': [[odd_datetime_string, 3.8]], 'Winamax': [[odd_datetime_string, 3.9]]}
                }
            }
        }
        summary = '2018-11-10T04:00+0100 Atlas Guadalajara - Pachuca'
        websites = ['ZEbet', 'Betclic', 'ParionsWeb', 'Winamax']
        params = {Simulation.BET_ODD_POWER: 2., Simulation.BET_RETURN_POWER: 0., Simulation.MIN_PROB: 0.25,
                  Simulation.MIN_RETURN: 0., Simulation.MAX_RETURN: 100., Simulation.WEBSITES: websites}
        bet_matches = distribution.get_value_bets(params, {summary: match})

        expected_bet_matches = {(summary, '1', 'Winamax',
                                 1.92, '2018-11-10T04:00+0100', 0.13563368055555555),
                                (summary, 'N', 'Winamax',
                                 3.55, '2018-11-10T04:00+0100', 0.03967466772465781)}
        self.assertEqual(expected_bet_matches, bet_matches)

    def test_matches_summary(self):
        match_datetime = datetime(2018, 11, 10, 4, 0, tzinfo=timezone(timedelta(seconds=3600)))
        bet_matches = {('2018-11-10T04:00+0100 Atlas Guadalajara - Pachuca', '2', 'Bwin', 2.25,
                        match_datetime, 0.2)}
        matches_summary = distribution.get_matches_summary(bet_matches)
        expected_matches_summary = '2018-11-10T04:00+0100 Atlas Guadalajara - Pachuca (2; 2.25; Bwin; 0.2)\n'\
                                   'Number of bet matches: 1\n'
        self.assertEqual(expected_matches_summary, matches_summary)
