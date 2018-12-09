#! /usr/bin/env python3
# coding: utf-8

import distribution
from odds import cotes, scibet, fivethirtyeight
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
    db.enrich(cotes.get_matches_with_odds())
    db.enrich(scibet.get_matches())
    db.enrich(fivethirtyeight.get_matches())


def print_analysis():
    match_data = db.get_finished_match_data()
    # stats.stats_on_return(match_data)
    # stats.stats_on_probabilities(match_data)
    # Simulation.plot_log(ValueBetSimulation.simulate_bets(match_data, params=[1., 0.26, 0.954, 5.]))
    Simulation.plot(ValueBetSimulation.simulate_contributions(match_data, params=[1., 0.26, 0.954, 5.]))
    # Simulation.plot_log(ProbabilitySimulation.simulate_bets(match_data, params=[1., 0.26, 0.96, 5.]))
    # Simulation.plot_log(TradeSimulation.simulate_bets(match_data, params=[1.2, -1., -0.2]))


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


def print_interesting_matches(send_mail=False):
    bet_matches = cotes.get_value_bets(params=[1., 0., 1.04, 5.])
    bet_matches.update(cotes.get_value_bets(params=[1., 0.26, 0.954, 5.]))
    matches_summary = distribution.get_matches_summary(bet_matches)
    print('Matches summary:\n{}'.format(matches_summary))
    if send_mail:
        distribution.send_email(matches_summary)


def main():
    parser = argparse.ArgumentParser(description='Analysis on football matches')
    parser.add_argument('action', help='Specify script action')
    parser.add_argument('--email', dest='send_mail', action='store_true', default=False,
                        help='Send an email with the matches summary')
    args = parser.parse_args()
    if args.action == REGISTER:
        register_matches()
    elif args.action == ANALYSE:
        print_analysis()
    elif args.action == OPTIMISE:
        find_best_parameters()
    elif args.action == BET:
        print_interesting_matches(args.send_mail)


if __name__ == '__main__':
    main()
