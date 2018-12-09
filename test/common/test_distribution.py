import unittest
from datetime import datetime, timezone, timedelta
from common import distribution


class DistributionTest(unittest.TestCase):

    def test_matches_summary(self):
        matches = {('2018-11-10T04:00+0100 Atlas Guadalajara - Pachuca', '2', 'Bwin', 2.25,
                    datetime(2018, 11, 10, 4, 0, tzinfo=timezone(timedelta(seconds=3600))), 0.2)}
        matches_summary = distribution.get_matches_summary(matches)
        expected_matches_summary = '2018-11-10T04:00+0100 Atlas Guadalajara - Pachuca (2; 2.25; Bwin; 0.2)\n'\
                                   'Number of bet matches: 1\n'
        self.assertEqual(expected_matches_summary, matches_summary)
