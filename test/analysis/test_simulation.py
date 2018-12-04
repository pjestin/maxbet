import unittest
from unittest.mock import patch
from analysis.simulation import ValueBetSimulation, TradeSimulation, ProbabilitySimulation
import json
from datetime import datetime, timezone, timedelta


DATA_FOR_SIMULATION_FILE = 'test/analysis/data/data_for_simulation.json'


class SimulationTest(unittest.TestCase):

    def setUp(self):
        with open(DATA_FOR_SIMULATION_FILE, mode='r', encoding='latin-1') as file:
            self.match_data = json.load(file)

    def test_value_bet_money(self):
        money = ValueBetSimulation.simulate_bets(self.match_data, params=[1., 0.1, 0.8, 5.])
        expected_money = [1.0, 1.3360655737704918, 1.0179547228727557, 0.8374662968314869]
        self.assertEqual(expected_money, money)

    def test_value_bet_contribution(self):
        contrib = ValueBetSimulation.simulate_contributions(self.match_data, params=[1., 0.1, 0.8, 5.])
        expected_contrib = [0.0, 0.3360655737704918, 0.0979703356752537, -0.07933462886375339]
        self.assertEqual(expected_contrib, contrib)

    @patch('datetime.datetime')
    def test_value_bet_get_bets(self, mocked_datetime):
        mocked_datetime.utcnow.return_value = datetime(2018, 11, 7, 10, 43, tzinfo=timezone.utc)
        mocked_datetime.strptime = datetime.strptime
        matches = ValueBetSimulation.get_bet_matches(self.match_data, params=[1., 0.35, 0., 5.])
        expected_matches = {('2018-11-10T04:00+0100 Atlas Guadalajara - Pachuca', '2', 'ParionsWeb', 2.1,
                             datetime(2018, 11, 10, 4, 0, tzinfo=timezone(timedelta(seconds=3600))))}
        self.assertEqual(expected_matches, matches)

    def test_trade_money(self):
        money = TradeSimulation.simulate_bets(self.match_data, params=[1.2, -0.1, 0.])
        expected_money = [1.0, 1.2712912581743752, 1.031078514751118, 0.8931302518796627]
        self.assertEqual(expected_money, money)

    def test_trade_contribution(self):
        contrib = TradeSimulation.simulate_contributions(self.match_data, params=[1., -0.1, 0.])
        expected_contrib = [0.0, 0.3412698412698412, 0.11904761904761901, -0.047619047619047644]
        self.assertEqual(expected_contrib, contrib)

    def test_probability_money(self):
        money = ProbabilitySimulation.simulate_bets(self.match_data, params=[1., 0.1, 0.8, 5.])
        expected_money = [1.0, 1.3360655737704918, 1.0179547228727557]
        self.assertEqual(expected_money, money)

    def test_probability_contribution(self):
        contrib = ProbabilitySimulation.simulate_contributions(self.match_data, params=[1., 0.1, 0.8, 5.])
        expected_contrib = [0.0, 0.3360655737704918, 0.0979703356752537]
        self.assertEqual(expected_contrib, contrib)
