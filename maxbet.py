#! /usr/bin/env python3
# coding: utf-8

import distribution
from odds import cotes, scibet, fivethirtyeight
from analysis import db
from analysis.simulation import ValueBetSimulation
import scipy.optimize as optimize


def print_interesting_matches(send_mail=False):
    matches_by_league = fivethirtyeight.read_weekly_matches()
    cotes.enrich_matches(matches_by_league)
    matches_summary = distribution.get_matches_summary(matches_by_league)
    print('Matches summary:\n{}'.format(matches_summary))
    if send_mail:
        distribution.send_email(matches_summary)


def print_value_bets(send_mail=False):
    value_bet_matches = cotes.get_value_bets()
    matches_summary = distribution.get_matches_summary(value_bet_matches)
    print('Matches summary:\n{}'.format(matches_summary))
    if send_mail:
        distribution.send_email(matches_summary)


def register_matches():
    db.enrich(cotes.get_matches_with_odds())
    db.enrich(scibet.get_matches())
    db.enrich(fivethirtyeight.get_matches())


def find_best_parameters():
    match_data = db.get_match_data()
    x0 = [0., 1.03, 0.05, 1.2]
    bounds = [(0., 1.), (0., 2.), (0., 2.), (0., 5.)]
    result = optimize.minimize(fun=lambda x: -ValueBetSimulation.simulate_bets(match_data, x),
                               x0=x0, bounds=bounds, method='SLSQP', options={'eps': 0.001})
    if result.success:
        fitted_params = result.x
        print(fitted_params)
    else:
        raise ValueError(result.message)


def print_analysis():
    match_data = db.get_match_data()
    # stats.stats_on_return(match_data)
    params = [0., 1.03, 0.05, 1.2]
    ValueBetSimulation.simulate_bets(match_data, params, plot=True)
    # ValueBetSimulation.simulate_contributions(match_data, params=params)


def main():
    # print_interesting_matches()
    # print_value_bets()
    register_matches()
    # find_best_parameters()
    # print_analysis()


if __name__ == '__main__':
    main()
