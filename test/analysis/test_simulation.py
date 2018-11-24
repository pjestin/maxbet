import unittest
from analysis.simulation import ValueBetSimulation, TradeSimulation, ProbabilitySimulation
import json


DATA_FOR_SIMULATION_FILE = 'test/analysis/data/data_for_simulation.json'


class SimulationTest(unittest.TestCase):

    def setUp(self):
        with open(DATA_FOR_SIMULATION_FILE, mode='r', encoding='latin-1') as file:
            self.match_data = json.load(file)

    def test_value_bet_money(self):
        money = ValueBetSimulation.simulate_bets(self.match_data, params=[1., 0.1, 0.8, 5.])
        expected_money = [1.0, 1.338709677419355, 1.0412186379928317, 0.8566054043061594]
        self.assertEqual(expected_money, money)

    def test_value_bet_contribution(self):
        contrib = ValueBetSimulation.simulate_contributions(self.match_data, params=[1., 0.1, 0.8, 5.])
        expected_contrib = [0.0, 0.33870967741935487, 0.11648745519713266, -0.06081750934187444]
        self.assertEqual(expected_contrib, contrib)

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
        expected_money = [1.0, 1.338709677419355, 1.0412186379928317]
        self.assertEqual(expected_money, money)

    def test_probability_contribution(self):
        contrib = ProbabilitySimulation.simulate_contributions(self.match_data, params=[1., 0.1, 0.8, 5.])
        expected_contrib = [0.0, 0.33870967741935487, 0.11648745519713266]
        self.assertEqual(expected_contrib, contrib)
