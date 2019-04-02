#! /usr/bin/env python3
# coding: utf-8

import math
import logging
from datetime import datetime, timezone

import matplotlib.pyplot as plt

from core.analysis.simulation import ValueBetSimulation, Simulation

BET_FACTOR = 0.5


def condition_for_current_bet(match, side, params):
    margins = ValueBetSimulation.get_margins(match)
    if not margins:
        return None
    min_prob, min_return, max_return, websites = params[Simulation.MIN_PROB], params[Simulation.MIN_RETURN], \
                                                 params[Simulation.MAX_RETURN], params[Simulation.WEBSITES]
    odd_times = ValueBetSimulation.get_odd_times(side)
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    current_odds = ValueBetSimulation.current_numbers(side['odds'], current_time, odd_times)
    best_website, best_odd = ValueBetSimulation.get_best_odd(current_odds, websites)
    prob = ValueBetSimulation.get_prob(current_odds, margins)
    if min_return < best_odd * prob < max_return and prob > min_prob:
        return best_website, best_odd, prob
    else:
        return None


def get_value_bets(params, matches):
    logging.info('Parameters: {}'.format(params))
    bet_matches = set()
    bet_odd_power = params[ValueBetSimulation.BET_ODD_POWER]
    for summary, match in matches.items():
        for side_id, side in match['sides'].items():
            condition = condition_for_current_bet(match, side, params)
            if condition:
                website, odd, prob = condition
                bet_fraction = BET_FACTOR / math.pow(odd, bet_odd_power)
                bet_matches.add((summary, side_id, website, odd, match['datetime'], bet_fraction))
    return bet_matches


def get_matches_summary(bet_matches):
    logging.info('Creating matches summary...')
    text = ''
    for summary, side_id, website, odd, match_datetime, bet_fraction in sorted(bet_matches, key=lambda x: x[4]):
        text += '{} ({}; {}; {}; {})\n'.format(summary, side_id, odd, website, bet_fraction)
    text += 'Number of bet matches: {}\n'.format(len(bet_matches))
    return text


def plot(contrib):
    plt.plot(range(len(contrib)), contrib)
    plt.title('Simulation result')
    plt.xlabel('Number of bets')
    plt.ylabel('Money')
    plt.show()


def plot_log(money):
    plot([math.log(m) for m in money])
