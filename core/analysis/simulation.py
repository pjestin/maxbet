#! /usr/bin/env python3
# coding: utf-8

import datetime
import math
import statistics
import logging
from collections import OrderedDict


class Simulation:

    BET_FACTOR = 0.5
    DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M%z'
    WEBSITES = 'websites'
    BET_ODD_POWER = 'bet_odd_power'
    BET_RETURN_POWER = 'bet_return_power'
    MIN_PROB = 'min_prob'
    MIN_RETURN = 'min_return'
    MAX_RETURN = 'max_return'
    MIN_RATIO_VARIATION = 'min_ratio_variation'
    MAX_RATIO_VARIATION = 'max_ratio_variation'

    datetime_cache = {}

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
    def get_contribution(cls, odd, success, bet_odd_power, prob, bet_return_power):
        amount = cls.BET_FACTOR / pow(odd, bet_odd_power)
        if prob:
            amount *= pow(odd * prob - 1., bet_return_power)
        if amount < 0.:
            raise ValueError('Negative amount for bet')
        if success:
            return amount * (odd - 1.)
        else:
            return -amount

    @classmethod
    def bet(cls, money, odd, success, bet_odd_power, prob, bet_return_power):
        new_money = money[-1] * (1 + cls.get_contribution(odd, success, bet_odd_power, prob, bet_return_power))
        money.append(new_money)

    @classmethod
    def condition_for_bet(cls, match, side, params):
        return None

    @classmethod
    def simulate_bets(cls, match_data, params):
        print('Simulation parameters: {}'.format(params))
        bet_odd_power, bet_return_power = params[cls.BET_ODD_POWER], params[cls.BET_RETURN_POWER]
        money = [1.0]
        for summary, match in match_data.items():
            result = cls.get_result(match['sides'])
            if not result:
                continue
            for side_id, side in match['sides'].items():
                condition = cls.condition_for_bet(match, side, params)
                if condition:
                    website, odd, prob = condition
                    print('Money: {}; betting on {}, {}, {}, {} - Bet: {}; Result: {}'
                          .format(money[-1], summary, website, odd, prob, side_id, result))
                    cls.bet(money, odd, result == side_id, bet_odd_power, prob, bet_return_power)
        print('Number of bets: {}'.format(len(money) - 1))
        print('Money: {}'.format(money[-1]))
        print('Geometric mean: {}'.format(math.pow(money[-1], (1.0 / len(money)))))
        return money

    @classmethod
    def simulate_contributions(cls, match_data, params):
        print('Simulation parameters: {}'.format(params))
        contrib = [0.]
        bet_odd_power, bet_return_power = params[cls.BET_ODD_POWER], params[cls.BET_RETURN_POWER]
        for match in match_data.values():
            result = cls.get_result(match['sides'])
            if not result:
                continue
            for side_id, side in match['sides'].items():
                condition = cls.condition_for_bet(match, side, params)
                if condition:
                    _, odd, prob = condition
                    contrib.append(contrib[-1] +
                                   cls.get_contribution(odd, result == side_id, bet_odd_power, prob, bet_return_power))
        print('Number of contributions: {}'.format(len(contrib)))
        print('Total: {}'.format(contrib[-1]))
        return contrib


class ValueBetSimulation(Simulation):

    @classmethod
    def get_margins(cls, match_data):
        margins = {}
        for side in match_data['sides'].values():
            if 'odds' not in side:
                continue
            for website, odds in side['odds'].items():
                if not odds:
                    continue
                if website not in margins:
                    margins[website] = 0.0
                margins[website] += 1.0 / odds[0][1]
        return margins

    @classmethod
    def get_prob(cls, side_odds, margins):
        odd_sum = sum(odd * margins[website] for website, odd in side_odds.items())
        return len(side_odds) / odd_sum

    @classmethod
    def get_best_odd(cls, odd_data, websites):
        filtered_odd_data = dict(website_odd for website_odd in odd_data.items()
                                 if not websites or website_odd[0] in websites)
        if not filtered_odd_data:
            return 0., 0.
        return max(filtered_odd_data.items(), key=lambda website_odd: website_odd[1])

    @classmethod
    def get_odd_times(cls, side):
        odd_times = {}
        if 'odds' not in side:
            return odd_times
        for odds in side['odds'].values():
            for odd_time, _ in odds:
                odd_datetime = datetime.datetime.strptime(odd_time, cls.DATE_TIME_FORMAT)
                if odd_time not in odd_times:
                    odd_times[odd_time] = odd_datetime
        return OrderedDict(sorted(odd_times.items()))

    @classmethod
    def condition_for_bet(cls, match, side, params):
        margins = cls.get_margins(match)
        if not margins:
            return None
        min_prob, min_return, max_return, websites = params[cls.MIN_PROB], params[cls.MIN_RETURN],\
                                                     params[cls.MAX_RETURN], params[cls.WEBSITES]
        odd_times = cls.get_odd_times(side)
        for current_time in odd_times.values():
            current_odds = cls.current_numbers(side['odds'], current_time, odd_times)
            best_website, best_odd = cls.get_best_odd(current_odds, websites)
            prob = cls.get_prob(current_odds, margins)
            if min_return < best_odd * prob < max_return and prob > min_prob:
                return best_website, best_odd, prob
        return None

    @classmethod
    def get_website_number(cls, website_numbers, current_time, odd_times):
        result_number = website_numbers[0][1]
        for time, number in website_numbers:
            if odd_times[time] > current_time:
                return result_number
            result_number = number
        return result_number

    @classmethod
    def current_numbers(cls, numbers, current_time, odd_times):
        current_number = {website: cls.get_website_number(website_numbers, current_time, odd_times)
                          for website, website_numbers in numbers.items()
                          if website_numbers
                          and odd_times[website_numbers[0][0]] <= current_time}
        return current_number


class ProbabilitySimulation(ValueBetSimulation):

    @classmethod
    def condition_for_bet(cls, match, side, params):
        if 'probs' not in side or 'odds' not in side:
            return None
        min_prob, min_return, max_return, websites = params[cls.MIN_PROB], params[cls.MIN_RETURN],\
                                                     params[cls.MAX_RETURN], params[cls.WEBSITES]
        odd_times = cls.get_odd_times(side)
        for current_time in odd_times.values():
            current_odds = cls.current_numbers(side['odds'], current_time, odd_times)
            best_website, best_odd = cls.get_best_odd(current_odds, websites)
            current_probs = cls.current_numbers(side['probs'], current_time, odd_times)
            if current_probs:
                prob = statistics.mean(current_probs.values())
                if min_return < best_odd * prob < max_return and prob > min_prob:
                    return best_website, best_odd, prob
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
        return best_odd_website, best_odd, None

    @classmethod
    def condition_for_bet(cls, match, side, params):
        bet_time = None
        min_ratio_variation, max_ratio_variation = params[cls.MIN_RATIO_VARIATION], params[cls.MAX_RATIO_VARIATION]
        if 'odds' not in side:
            return None
        for odds in side['odds'].values():
            max_odd = None
            for time, odd in odds:
                if max_odd and min_ratio_variation < (odd - max_odd) / max_odd < max_ratio_variation:
                    bet_time = time
                if not max_odd or odd > max_odd:
                    max_odd = odd
        if bet_time:
            return cls.get_best_odd_at_time(side, bet_time)
        return None
