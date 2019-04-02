import unittest
from core.analysis.simulation import Simulation, ValueBetSimulation, TradeSimulation, ProbabilitySimulation
import json
from collections import OrderedDict


DATA_FOR_SIMULATION_FILE = 'core/test/analysis/data/data_for_simulation.json'


class SimulationTest(unittest.TestCase):

    def setUp(self):
        with open(DATA_FOR_SIMULATION_FILE, mode='r', encoding='latin-1') as file:
            self.match_data = json.load(file, object_pairs_hook=OrderedDict)
        websites = ['ZEbet', 'Betclic', 'ParionsWeb', 'Winamax']
        self.params_value_bet = {Simulation.BET_ODD_POWER: 1., Simulation.BET_RETURN_POWER: 0.,
                                 Simulation.MIN_PROB: 0.1, Simulation.MIN_RETURN: 0.88, Simulation.MAX_RETURN: 100.,
                                 Simulation.WEBSITES: websites, Simulation.BET_FACTOR: .5}
        self.params_trade = {Simulation.BET_ODD_POWER: 1., Simulation.BET_RETURN_POWER: 0.,
                             Simulation.MIN_RATIO_VARIATION: -0.1, Simulation.MAX_RATIO_VARIATION: 0.,
                             Simulation.WEBSITES: websites, Simulation.BET_FACTOR: .5}

    def test_value_bet_money(self):
        money = ValueBetSimulation.simulate_bets(self.match_data, self.params_value_bet)
        expected_money = [1.0, 1.3461538461538463, 1.1254728877679698, 0.9496177490542246]
        self.assertEqual(expected_money, money)

    def test_value_bet_contribution(self):
        contrib = ValueBetSimulation.simulate_contributions(self.match_data, self.params_value_bet)
        expected_contrib = [0.0, 0.34615384615384615, 0.18221941992433793, 0.025969419924337933]
        self.assertEqual(expected_contrib, contrib)

    def test_trade_money(self):
        money = TradeSimulation.simulate_bets(self.match_data, self.params_trade)
        expected_money = [1.0, 1.3412698412698412, 1.1213895394223263, 0.9461724238875878]
        self.assertEqual(expected_money, money)

    def test_trade_contribution(self):
        contrib = TradeSimulation.simulate_contributions(self.match_data, self.params_trade)
        expected_contrib = [0.0, 0.3412698412698412, 0.177335415040333, 0.02108541504033301]
        self.assertEqual(expected_contrib, contrib)

    def test_probability_money(self):
        money = ProbabilitySimulation.simulate_bets(self.match_data, self.params_value_bet)
        expected_money = [1.0, 1.3360655737704918, 1.0179547228727557]
        self.assertEqual(expected_money, money)

    def test_probability_contribution(self):
        contrib = ProbabilitySimulation.simulate_contributions(self.match_data, self.params_value_bet)
        expected_contrib = [0.0, 0.3360655737704918, 0.0979703356752537]
        self.assertEqual(expected_contrib, contrib)
