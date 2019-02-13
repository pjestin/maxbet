#! /usr/bin/env python3
# coding: utf-8

import argparse
import logging

import scipy.optimize as optimize

from core.common import distribution
from core.odds import cotes, scibet, fivethirtyeight, oddschecker, sportinglife
from core.analysis import db, stats
from core.analysis.simulation import Simulation, ValueBetSimulation, ProbabilitySimulation, TradeSimulation


REGISTER = 'register'
ANALYSE = 'analyse'
OPTIMISE = 'optimise'
BET = 'bet'
ACTIONS = [REGISTER, ANALYSE, OPTIMISE, BET]

# WEBSITES = []
# WEBSITES = ['Bet365', 'Skybet', 'Ladbrokes', 'William Hill', 'Marathon Bet', 'Betfair Sportsbook',
#             'Bet Victor', 'Paddy Power', 'Coral', 'Boyle Sports', 'Black Type', 'Redzone', 'Betway', 'BetBright',
#             '10Bet', 'Sportingbet', '188Bet', '888sport', 'SportPesa', 'Royal Panda', 'Sport Nation', 'Betfair',
#             'Betdaq', 'Matchbook', 'Betfred', 'Smarkets', 'Spreadex']
# WEBSITES = ['William Hill', 'Marathon Bet', 'Boyle Sports', 'Betway', 'BetBright', '10Bet', 'SportPesa',
#             'Sport Nation', 'Smarkets', 'Coral', 'Sportingbet', 'Royal Panda', 'Matchbook']
# WEBSITES = ['Skybet', 'Marathon Bet', 'Betfair Sportsbook', 'Paddy Power', 'Coral', 'Boyle Sports', 'Black Type',
#             'Redzone', 'Betway', 'BetBright', '10Bet', 'Sportingbet', '188Bet', 'Royal Panda', 'Sport Nation',
#             'Betfair', 'Matchbook', 'Smarkets']
WEBSITES = ['Skybet', 'Marathon Bet', 'Betfair Sportsbook', 'Coral', 'Boyle Sports', 'Betway', 'Sportingbet',
            '888sport', 'Royal Panda', 'Sport Nation', 'Betfair', 'Smarkets', 'Spreadex']
# WEBSITES = ['Marathon Bet', 'Betway', 'Sportingbet', 'Matchbook', 'Smarkets']
# WEBSITES = ['Betway', 'William Hill', 'Sportingbet', 'Coral', 'Betdaq']


def register_matches():
    matches = []
    matches.extend(sportinglife.get_matches())
    matches.extend(scibet.get_matches())
    matches.extend(fivethirtyeight.get_matches())
    matches.extend(oddschecker.get_matches_with_odds())
    matches.extend(cotes.get_matches_with_odds())
    db.enrich(matches)
    # db.patch()
    # db.print_finished_matches_without_score()


def print_analysis():
    match_data = db.get_finished_match_data()
    # stats.stats_on_return(match_data)
    # stats.stats_on_return_integral(match_data)
    # stats.stats_on_probabilities(match_data)

    params = {Simulation.BET_ODD_POWER: 2., Simulation.BET_RETURN_POWER: 0., Simulation.MIN_PROB: 0.25,
              Simulation.MIN_RETURN: 1., Simulation.MAX_RETURN: 100., Simulation.WEBSITES: WEBSITES,
              Simulation.BET_FACTOR: .5 / len(WEBSITES)}
    distribution.plot_log(ValueBetSimulation.simulate_bets(match_data, params))
    # distribution.plot(ValueBetSimulation.simulate_contributions(match_data, params))
    # distribution.plot_log(ProbabilitySimulation.simulate_bets(match_data, params))

    # params = {Simulation.BET_ODD_POWER: 2., Simulation.BET_RETURN_POWER: 0., Simulation.MIN_RATIO_VARIATION: -100.,
    #           Simulation.MAX_RATIO_VARIATION: -0.55}
    # distribution.plot_log(TradeSimulation.simulate_bets(match_data, params))


def find_best_parameters():
    match_data = db.get_match_data()
    x_0 = [1.2, 0.25, 0.98, 5.]
    bounds = [(0., 5.), (0., 1.), (0., 2.), (0., 2.)]
    result = optimize.minimize(fun=lambda x: -ValueBetSimulation.simulate_bets(match_data, x)[-1],
                               x0=x_0, bounds=bounds, method='SLSQP', options={'eps': 0.001})
    if result.success:
        fitted_params = result.x
        print(fitted_params)
    else:
        raise ValueError(result.message)


def print_interesting_matches():
    matches = db.get_future_match_data()
    params = {Simulation.BET_ODD_POWER: 2., Simulation.BET_RETURN_POWER: 0., Simulation.MIN_PROB: 0.25,
              Simulation.MIN_RETURN: 1., Simulation.MAX_RETURN: 100., Simulation.WEBSITES: WEBSITES,
              Simulation.BET_FACTOR: .5}
    bet_matches = distribution.get_value_bets(params, matches)
    matches_summary = distribution.get_matches_summary(bet_matches)
    print('Matches summary:\n{}'.format(matches_summary))


def main():
    parser = argparse.ArgumentParser(description='Analysis on football matches')
    parser.add_argument('action', help='Specify script action')
    parser.add_argument('-v', '--verbose', help='Display more logs', action='store_true')
    args = parser.parse_args()

    log_format = '%(asctime)-15s %(message)s'
    if args.verbose:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
        logging.info("Verbose output.")
    else:
        logging.basicConfig(format=log_format)

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
