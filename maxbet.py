#! /usr/bin/env python3
# coding: utf-8

import argparse
import logging

from core.common import distribution
from core.odds import cotes, scibet, fivethirtyeight, oddschecker, sportinglife
from core.analysis import db, stats
from core.analysis.simulation import Simulation, ValueBetSimulation, ProbabilitySimulation, TradeSimulation


REGISTER = 'register'
ANALYSE = 'analyse'
BET = 'bet'
ACTIONS = [REGISTER, ANALYSE, BET]

# WEBSITES = []
# WEBSITES = ['Bet365', 'Skybet', 'Ladbrokes', 'William Hill', 'Marathon Bet', 'Betfair Sportsbook',
            # 'Bet Victor', 'Paddy Power', 'Coral', 'Boyle Sports', 'Black Type', 'Redzone', 'Betway', 'BetBright',
            # '10Bet', 'Sportingbet', '188Bet', '888sport', 'SportPesa', 'Royal Panda', 'Sport Nation', 'Betfair',
            # 'Betdaq', 'Matchbook', 'Betfred', 'Smarkets', 'Spreadex']
# WEBSITES = ['William Hill', 'Marathon Bet', 'Boyle Sports', 'Betway', 'BetBright', '10Bet', 'SportPesa',
#             'Sport Nation', 'Smarkets', 'Coral', 'Sportingbet', 'Royal Panda', 'Matchbook']
# WEBSITES = ['Skybet', 'Marathon Bet', 'Betfair Sportsbook', 'Paddy Power', 'Coral', 'Boyle Sports', 'Black Type',
#             'Redzone', 'Betway', 'BetBright', '10Bet', 'Sportingbet', '188Bet', 'Royal Panda', 'Sport Nation',
#             'Betfair', 'Matchbook', 'Smarkets']
# WEBSITES = ['Skybet', 'Marathon Bet', 'Betfair Sportsbook', 'Coral', 'Boyle Sports', 'Betway', 'Sportingbet',
#             '888sport', 'Royal Panda', 'Sport Nation', 'Betfair', 'Spreadex']
# WEBSITES = ['Betway', 'William Hill', 'Sportingbet', 'Coral', 'Betdaq']
# WEBSITES = ['Boyle Sports', 'Coral', 'Betway', 'Sportingbet', 'Royal Panda', 'Sport Nation']
WEBSITES = ['Smarkets']

PARAMS = {Simulation.BET_ODD_POWER: 2., Simulation.BET_RETURN_POWER: 0., Simulation.MIN_PROB: 0.15,
          Simulation.MIN_RETURN: 1.05, Simulation.MAX_RETURN: 100., Simulation.WEBSITES: WEBSITES,
          Simulation.BET_FACTOR: .5 / len(WEBSITES)}


def register_matches():
    matches = []
    logging.info('Sporting life')
    matches.extend(sportinglife.get_matches())
    logging.info('Scibet')
    matches.extend(scibet.get_matches())
    logging.info('538')
    matches.extend(fivethirtyeight.get_matches())
    logging.info('Oddschecker')
    matches.extend(oddschecker.get_matches_with_odds())
    logging.info('Cotes')
    matches.extend(cotes.get_matches_with_odds())
    db.enrich(matches)
    # db.patch()
    # db.print_finished_matches_without_score()


def print_analysis():
    match_data = db.get_finished_match_data()
    # stats.stats_on_return(match_data)
    # stats.stats_on_return_integral(match_data)
    # stats.stats_on_probabilities(match_data)

    distribution.plot_log(ValueBetSimulation.simulate_bets(match_data, PARAMS))
    # distribution.plot(ValueBetSimulation.simulate_contributions(match_data, params))
    # distribution.plot_log(ProbabilitySimulation.simulate_bets(match_data, params))

    # params = {Simulation.BET_ODD_POWER: 2., Simulation.BET_RETURN_POWER: 0., Simulation.MIN_RATIO_VARIATION: -100.,
    #           Simulation.MAX_RATIO_VARIATION: -0.55}
    # distribution.plot_log(TradeSimulation.simulate_bets(match_data, params))


def print_interesting_matches():
    matches = db.get_future_match_data()
    bet_matches = distribution.get_value_bets(PARAMS, matches)
    matches_summary = distribution.get_matches_summary(bet_matches)
    logging.info('Matches summary:\n{}'.format(matches_summary))


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
        logging.basicConfig(format=log_format, level=logging.INFO)

    if args.action == REGISTER:
        register_matches()
    elif args.action == ANALYSE:
        print_analysis()
    elif args.action == BET:
        print_interesting_matches()


if __name__ == '__main__':
    main()
