import unittest
from unittest.mock import patch
from core.analysis.simulation import Simulation, ValueBetSimulation, TradeSimulation, ProbabilitySimulation
import json
from datetime import datetime, timezone, timedelta
from collections import OrderedDict


DATA_FOR_SIMULATION_FILE = 'core/test/analysis/data/data_for_simulation.json'


class SimulationTest(unittest.TestCase):

    def setUp(self):
        with open(DATA_FOR_SIMULATION_FILE, mode='r', encoding='latin-1') as file:
            self.match_data = json.load(file, object_pairs_hook=OrderedDict)
        self.params_value_bet = {Simulation.BET_ODD_POWER: 1., Simulation.BET_RETURN_POWER: 0.,
                                 Simulation.MIN_PROB: 0.1, Simulation.MIN_RETURN: 0.8, Simulation.MAX_RETURN: 5.}
        self.params_trade = {Simulation.BET_ODD_POWER: 1., Simulation.BET_RETURN_POWER: 0.,
                             Simulation.MIN_RATIO_VARIATION: -0.1, Simulation.MAX_RATIO_VARIATION: 0.}

    def test_value_bet_money(self):
        money = ValueBetSimulation.simulate_bets(self.match_data, self.params_value_bet)
        expected_money = [1.0, 1.3360655737704918, 1.0179547228727557, 0.8374662968314869]
        self.assertEqual(expected_money, money)

    def test_value_bet_contribution(self):
        contrib = ValueBetSimulation.simulate_contributions(self.match_data, self.params_value_bet)
        expected_contrib = [0.0, 0.3360655737704918, 0.0979703356752537, -0.07933462886375339]
        self.assertEqual(expected_contrib, contrib)

    def test_trade_money(self):
        money = TradeSimulation.simulate_bets(self.match_data, self.params_trade)
        expected_money = [1.0, 1.3412698412698412, 1.0432098765432098, 0.8693415637860082]
        self.assertEqual(expected_money, money)

    def test_trade_contribution(self):
        contrib = TradeSimulation.simulate_contributions(self.match_data, self.params_trade)
        expected_contrib = [0.0, 0.3412698412698412, 0.11904761904761901, -0.047619047619047644]
        self.assertEqual(expected_contrib, contrib)

    def test_probability_money(self):
        money = ProbabilitySimulation.simulate_bets(self.match_data, self.params_value_bet)
        expected_money = [1.0, 1.3360655737704918, 1.0179547228727557]
        self.assertEqual(expected_money, money)

    def test_probability_contribution(self):
        contrib = ProbabilitySimulation.simulate_contributions(self.match_data, self.params_value_bet)
        expected_contrib = [0.0, 0.3360655737704918, 0.0979703356752537]
        self.assertEqual(expected_contrib, contrib)
