#! /usr/bin/env python3
# coding: utf-8

import math

import matplotlib.pyplot as plt

from core.analysis.simulation import ValueBetSimulation

BET_FACTOR = 0.5
WEBSITES = ['Bet365', 'Skybet', 'Ladbrokes', 'William Hill', 'Marathon Bet', 'Betfair Sportsbook',
            'Bet Victor', 'Paddy Power', 'Coral', 'Boyle Sports', 'Black Type', 'Redzone', 'Betway', 'BetBright',
            '10Bet', 'Sportingbet', '188Bet', '888sport', 'SportPesa', 'Royal Panda', 'Sport Nation', 'Betfair',
            'Betdaq', 'Matchbook', 'Betfred', 'Smarkets', 'Spreadex']


def get_value_bets(params, matches):
    print('Parameters: {}'.format(params))
    bet_matches = set()
    bet_odd_power = params[ValueBetSimulation.BET_ODD_POWER]
    for summary, match in matches.items():
        for side_id, side in match['sides'].items():
            condition = ValueBetSimulation.condition_for_bet(match, side, params)
            if condition:
                website, odd, prob = condition
                bet_fraction = BET_FACTOR / math.pow(odd, bet_odd_power)
                bet_matches.add((summary, side_id, website, odd, match['datetime'], bet_fraction))
    return bet_matches


def get_matches_summary(bet_matches):
    print('Creating matches summary...')
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
