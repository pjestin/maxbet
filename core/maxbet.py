#! /usr/bin/env python3
# coding: utf-8

from common import distribution
from odds import cotes, scibet, fivethirtyeight, oddschecker
from analysis import db, stats
from analysis.simulation import Simulation, ValueBetSimulation, ProbabilitySimulation, TradeSimulation
import scipy.optimize as optimize
import argparse


REGISTER = 'register'
ANALYSE = 'analyse'
OPTIMISE = 'optimise'
BET = 'bet'
ACTIONS = [REGISTER, ANALYSE, OPTIMISE, BET]


def register_matches():
    matches = []
    matches.extend(cotes.get_matches_with_odds())
    matches.extend(scibet.get_matches())
    matches.extend(fivethirtyeight.get_matches())
    matches.extend(oddschecker.get_matches_with_odds())
    db.enrich(matches)
    # db.patch()


def print_analysis():
    match_data = db.get_finished_match_data()
    # stats.stats_on_return(match_data)
    # stats.stats_on_return_integral(match_data)
    # stats.stats_on_probabilities(match_data)

    params = {Simulation.BET_ODD_POWER: 0.8, Simulation.BET_RETURN_POWER: 0., Simulation.MIN_PROB: 0.2,
              Simulation.MIN_RETURN: 1., Simulation.MAX_RETURN: 10.}
    distribution.plot_log(ValueBetSimulation.simulate_bets(match_data, params))
    # distribution.plot(ValueBetSimulation.simulate_contributions(match_data, params))
    # distribution.plot_log(ProbabilitySimulation.simulate_bets(match_data, params))

    # params = {Simulation.BET_ODD_POWER: 1., Simulation.MIN_RATIO_VARIATION: -1., Simulation.MAX_RATIO_VARIATION: -0.3}
    # distribution.plot_log(TradeSimulation.simulate_bets(match_data, params))


def find_best_parameters():
    match_data = db.get_match_data()
    x0 = [1.2, 0.25, 0.98, 5.]
    bounds = [(0., 5.), (0., 1.), (0., 2.), (0., 2.)]
    result = optimize.minimize(fun=lambda x: -ValueBetSimulation.simulate_bets(match_data, x)[-1],
                               x0=x0, bounds=bounds, method='SLSQP', options={'eps': 0.001})
    if result.success:
        fitted_params = result.x
        print(fitted_params)
    else:
        raise ValueError(result.message)


def print_interesting_matches():
    bet_matches = cotes.get_value_bets(params=[1., 0.07, 1.02, 1.08])
    matches_summary = distribution.get_matches_summary(bet_matches)
    print('Matches summary:\n{}'.format(matches_summary))


def main():
    parser = argparse.ArgumentParser(description='Analysis on football matches')
    parser.add_argument('action', help='Specify script action')
    args = parser.parse_args()
    if args.action == REGISTER:
        register_matches()
    elif args.action == ANALYSE:
        print_analysis()
    elif args.action == OPTIMISE:
        find_best_parameters()
    elif args.action == BET:
        print_interesting_matches()


if __name__ == '__main__':
    main()
