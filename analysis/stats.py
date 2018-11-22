#! /usr/bin/env python3
# coding: utf-8

from .simulation import Simulation
import datetime
import math
import matplotlib.pyplot as plt

DATE_FORMAT = '%Y-%m-%dT%H'


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
