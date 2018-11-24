#! /usr/bin/env python3
# coding: utf-8

from .simulation import Simulation, ValueBetSimulation
import datetime
import statistics
import matplotlib.pyplot as plt

DATE_FORMAT = '%Y-%m-%dT%H'
BET_ODD_POWER = 0.
RESOLUTION = 0.002


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
    print('Average time for wins: {}'.format(day_win / count_win))
    print('Average time for loses: {}'.format(day_lose / count_lose))


def stats_on_return(match_data):
    contrib_per_return = {}
    for summary, match in match_data.items():
        margins = ValueBetSimulation.get_margins(match)
        result = ValueBetSimulation.get_result(match['sides'])
        if not result:
            continue
        for side_id, side in match['sides'].items():
            for current_time in ValueBetSimulation.get_odd_times(side):
                current_odds = {}
                for website, odds in side['odds'].items():
                    for odd_time, odd in odds:
                        if datetime.datetime.strptime(odd_time, ValueBetSimulation.DATE_TIME_FORMAT) > current_time:
                            break
                        current_odds[website] = odd
                best_website, best_odd = ValueBetSimulation.get_best_odd(current_odds)
                prob = ValueBetSimulation.get_prob(current_odds, margins)
                rounded_return = float(int(best_odd * prob / RESOLUTION)) * RESOLUTION
                contrib = ValueBetSimulation.get_contribution(best_odd, result == side_id, BET_ODD_POWER)
                if rounded_return not in contrib_per_return:
                    contrib_per_return[rounded_return] = []
                contrib_per_return[rounded_return].append(contrib)
    x = []
    y = []
    for rounded_return, contribs in sorted(contrib_per_return.items()):
        x.append(rounded_return)
        y.append(sum(contribs))

    plt.plot(x, y)
    plt.title('Contribution per return')
    plt.xlabel('Rounded return')
    plt.ylabel('Contribution')
    plt.show()
