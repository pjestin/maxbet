#! /usr/bin/env python3
# coding: utf-8


def get_matches_summary(bet_matches):
    print('Creating matches summary...')
    text = ''
    for summary, side_id, website, odd, match_datetime, bet_fraction in sorted(bet_matches, key=lambda x: x[4]):
        text += '{} ({}; {}; {}; {})\n'.format(summary, side_id, odd, website, bet_fraction)
    text += 'Number of bet matches: {}\n'.format(len(bet_matches))
    return text
