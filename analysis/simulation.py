#! /usr/bin/env python3
# coding: utf-8

from enum import Enum
import datetime
import matplotlib.pyplot as plt
import math
import statistics


class Simulation:

    BET_FACTOR = 0.5
    BET_ODD_POWER = 2.0
    DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M'
    WEBSITES = ['ZEbet', 'Betclic', 'ParionsWeb', 'Bwin', 'Betstars', 'Winamax']

    @classmethod
    def get_result(cls, side_data):
        if 'score' not in side_data['1'] or 'score' not in side_data['2']:
            return None
        score1 = side_data['1']['score']
        score2 = side_data['2']['score']
        result = '1'
        if score1 == score2:
            result = 'N'
        elif score1 < score2:
            result = '2'
        return result

    @classmethod
    def get_contribution(cls, odd, success, bet_odd_power):
        amount = cls.BET_FACTOR / pow(odd, bet_odd_power)
        if success:
            return amount * (odd - 1.0)
        else:
            return -amount

    @classmethod
    def bet(cls, money, odd, success, bet_odd_power):
        new_money = money[-1] * (1 + cls.get_contribution(odd, success, bet_odd_power))
        # print('Money: {}'.format(new_money))
        money.append(new_money)

    @classmethod
    def condition_for_bet(cls, match, side, params):
        return None

    @classmethod
    def plot(cls, money):
        plt.plot(range(len(money)), [math.log(m) for m in money])
        plt.title('Simulation result')
        plt.xlabel('Number of bets')
        plt.ylabel('Money')
        plt.show()

    @classmethod
    def simulate_bets(cls, match_data, params, plot=False):
        print('Simulation parameters: {}'.format(params))
        bet_odd_power = params[3]
        money = [1.0]
        for summary, match in match_data.items():
            result = cls.get_result(match['sides'])
            if not result:
                continue
            for side_id, side in match['sides'].items():
                condition = cls.condition_for_bet(match, side, params)
                if condition:
                    website, odd = condition
                    # print('Betting on {} ({})'.format(summary, side_id))
                    cls.bet(money, odd, result == side_id, bet_odd_power)
                    break
        print('Number of bets: {}'.format(len(money) - 1))
        if len(money) == 1:
            return 0.0
        print('Money: {}'.format(money[-1]))
        print('Geometric mean: {}'.format(math.pow(money[-1], (1.0 / len(money)))))
        if plot:
            cls.plot(money)
        return money[-1]

    @classmethod
    def simulate_contributions(cls, match_data, params):
        print('Simulation parameters: {}'.format(params))
        contrib = []
        bet_odd_power = params[3]
        for summary, match in match_data.items():
            result = cls.get_result(match['sides'])
            if not result:
                continue
            for side_id, side in match['sides'].items():
                condition = cls.condition_for_bet(match, side, params)
                if condition:
                    website, odd = condition
                    # print('Contribution on {} ({})'.format(summary, side_id))
                    contrib.append(cls.get_contribution(odd, result == side_id, bet_odd_power))
        print('Number of contributions: {}'.format(len(contrib)))
        if not contrib:
            return -1000.
        # contrib_mean = statistics.mean(contrib)
        # print('Mean: {}'.format(contrib_mean))
        contrib_sum = sum(contrib)
        print('Total: {}'.format(contrib_sum))
        return contrib_sum

    class Type(Enum):
        VALUE_BET = 1.
        TRADE = 2

    @classmethod
    def factory(cls, sim_type):
        if sim_type == cls.Type.VALUE_BET:
            return ValueBetSimulation()
        elif sim_type == cls.Type.TRADE:
            return TradeSimulation()
        else:
            return None


class ValueBetSimulation(Simulation):

    @classmethod
    def get_margins(cls, match_data):
        margins = {}
        for side in match_data['sides'].values():
            for website, odds in side['odds'].items():
                if website not in margins:
                    margins[website] = 0.0
                margins[website] += 1.0 / odds[0][1]
        return margins

    @classmethod
    def get_prob(cls, side_odds, margins):
        odd_sum = 0.0
        for website, odd in side_odds.items():
            odd_sum += odd * margins[website]
        return len(side_odds) / odd_sum

    @classmethod
    def get_best_odd(cls, odd_data):
        max_odd = 0.0
        max_odd_website = ''
        for website, odd in odd_data.items():
            if cls.WEBSITES and website not in cls.WEBSITES:
                continue
            if odd > max_odd:
                max_odd = odd
                max_odd_website = website
        return max_odd_website, max_odd

    @classmethod
    def get_odd_times(cls, side):
        odd_times = []
        for odds in side['odds'].values():
            for odd_time, odd in odds:
                odd_datetime = datetime.datetime.strptime(odd_time, cls.DATE_TIME_FORMAT)
                if odd_datetime not in odd_times:
                    odd_times.append(odd_datetime)
        return sorted(odd_times)

    @classmethod
    def condition_for_bet(cls, match, side, params):
        margins = cls.get_margins(match)
        min_prob, min_return, return_span = params[:3]
        for current_time in cls.get_odd_times(side):
            current_odds = {}
            for website, odds in side['odds'].items():
                for odd_time, odd in odds:
                    if datetime.datetime.strptime(odd_time, cls.DATE_TIME_FORMAT) > current_time:
                        break
                    current_odds[website] = odd
            best_website, best_odd = cls.get_best_odd(current_odds)
            prob = cls.get_prob(current_odds, margins)
            if min_return < best_odd * prob < min_return + return_span and prob > min_prob:
                return best_website, best_odd
        return None


class TradeSimulation(Simulation):

    @classmethod
    def get_best_odd_at_time(cls, side, bet_time):
        best_odd_website = None
        best_odd = 0.0
        bet_time_obj = datetime.datetime.strptime(bet_time, cls.DATE_TIME_FORMAT)
        for website, odds in side['odds'].items():
            for time, odd in reversed(odds):
                time_obj = datetime.datetime.strptime(time, cls.DATE_TIME_FORMAT)
                if time_obj <= bet_time_obj and odd > best_odd:
                    best_odd = odd
                    best_odd_website = website
        return best_odd_website, best_odd

    @classmethod
    def condition_for_bet(cls, match, side, params):
        bet_time = None
        max_ratio_variation = params[0]
        for website, odds in side['odds'].items():
            max_odd = None
            for time, odd in odds:
                if max_odd and (odd - max_odd) / max_odd < max_ratio_variation:
                    bet_time = time
                if not max_odd or odd > max_odd:
                    max_odd = odd
        if bet_time:
            return cls.get_best_odd_at_time(side, bet_time)
