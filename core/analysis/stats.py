#! /usr/bin/env python3
# coding: utf-8

import datetime
import statistics
import math
import logging

import matplotlib.pyplot as plt

from .simulation import Simulation, ValueBetSimulation

DATE_FORMAT = '%Y-%m-%dT%H'
BET_ODD_POWER = 0.
RESOLUTION = 0.005
PROB_POWER = 1.

WEBSITES = ['Bet365', 'Skybet', 'Ladbrokes', 'William Hill', 'Marathon Bet', 'Betfair Sportsbook',
            'Bet Victor', 'Paddy Power', 'Coral', 'Boyle Sports', 'Black Type', 'Redzone', 'Betway', 'BetBright',
            '10Bet', 'Sportingbet', '188Bet', '888sport', 'SportPesa', 'Royal Panda', 'Sport Nation', 'Betfair',
            'Betdaq', 'Matchbook', 'Betfred', 'Smarkets', 'Spreadex']


def stats_on_day(match_data):
    day_lose = 0
    count_lose = 0
    day_win = 0
    count_win = 0
    for summary, match in match_data.items():
        match_datetime = datetime.datetime.strptime(match['datetime'][:13], DATE_FORMAT)
        result = Simulation.get_result(match['sides'])
        if not result:
            continue
        for side_id, side in match['sides'].items():
            for odds in side['odds'].values():
                for odd_time, odd in odds:
                    odd_datetime = datetime.datetime.strptime(odd_time[:13], DATE_FORMAT)
                    time_difference = (odd_datetime - match_datetime).total_seconds()
                    if result == side_id:
                        day_win += time_difference
                        count_win += 1
                    else:
                        day_lose += time_difference
                        count_lose += 1
    logging.info('Average time for wins: {}'.format(day_win / count_win))
    logging.info('Average time for loses: {}'.format(day_lose / count_lose))


def get_contrib_per_return(match_data):
    contrib_per_return = {}
    for summary, match in match_data.items():
        margins = ValueBetSimulation.get_margins(match)
        result = ValueBetSimulation.get_result(match['sides'])
        if not result:
            continue
        for side_id, side in match['sides'].items():
            odd_times = ValueBetSimulation.get_odd_times(side)
            for current_time in odd_times.values():
                current_odds = ValueBetSimulation.current_numbers(side['odds'], current_time, odd_times)
                best_website, best_odd = ValueBetSimulation.get_best_odd(current_odds, WEBSITES)
                prob = ValueBetSimulation.get_prob(current_odds, margins)
                rounded_return = float(int(best_odd * math.pow(prob, PROB_POWER) / RESOLUTION)) * RESOLUTION
                contrib = ValueBetSimulation.get_contribution(best_odd, result == side_id, BET_ODD_POWER, prob, 0.)
                if rounded_return not in contrib_per_return:
                    contrib_per_return[rounded_return] = []
                contrib_per_return[rounded_return].append(contrib)
    return contrib_per_return


def stats_on_return(match_data):
    contrib_per_return = get_contrib_per_return(match_data)
    x, y = [], []
    for rounded_return, contribs in sorted(contrib_per_return.items()):
        x.append(rounded_return)
        y.append(sum(contribs))

    plt.plot(x, y)
    plt.plot(x, [0 for _ in y])
    plt.title('Contribution per return')
    plt.xlabel('Rounded return')
    plt.ylabel('Contribution')
    plt.show()


def stats_on_return_integral(match_data):
    contrib_per_return = get_contrib_per_return(match_data)
    x, y, z = [0.], [0.], [0]
    for rounded_return, contribs in sorted(contrib_per_return.items()):
        x.append(rounded_return)
        y.append(y[-1] + sum(contribs))
        z.append(len(contribs))

    plt.plot(x, y)
    plt.plot(x, z)
    plt.title('Contribution per return')
    plt.xlabel('Rounded return')
    plt.ylabel('Contribution')
    plt.show()


def stats_on_probabilities(match_data):
    contrib_per_prob = {}
    for summary, match in match_data.items():
        result = ValueBetSimulation.get_result(match['sides'])
        if not result:
            continue
        for side_id, side in match['sides'].items():
            if 'probs' not in side or 'odds' not in side:
                continue
            for current_time in ValueBetSimulation.get_odd_times(side):
                current_odds = ValueBetSimulation.current_numbers(side['odds'], current_time)
                best_website, best_odd = ValueBetSimulation.get_best_odd(current_odds)
                current_probs = ValueBetSimulation.current_numbers(side['probs'], current_time)
                if current_probs:
                    prob = statistics.mean(current_probs.values())
                    rounded_prob = float(int(prob / RESOLUTION)) * RESOLUTION
                    contrib = ValueBetSimulation.get_contribution(best_odd, result == side_id, BET_ODD_POWER, prob, 0.)
                    if rounded_prob not in contrib_per_prob:
                        contrib_per_prob[rounded_prob] = []
                        contrib_per_prob[rounded_prob].append(contrib)
    x, y = [], []
    for rounded_prob, contribs in sorted(contrib_per_prob.items()):
        x.append(rounded_prob)
        y.append(sum(contribs))

    plt.plot(x, y)
    plt.title('Contribution per probability')
    plt.xlabel('Rounded probability')
    plt.ylabel('Contribution')
    plt.show()
