from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404

from .models import BetMatch, RefreshTime
from core.analysis import db
from core.analysis.simulation import Simulation
from core.common import distribution

WEBSITES = ['William Hill', 'Marathon Bet', 'Boyle Sports', 'Betway', 'BetBright', '10Bet', 'SportPesa',
            'Sport Nation', 'Smarkets', 'Coral', 'Sportingbet', 'Royal Panda']


def index(request):
    return render(request, 'dashboard/index.html')


def register(request):
    raise Http404


def analyse(request):
    context = {'area_chart_data': [{'x': 1, 'y': 2}]}
    return render(request, 'dashboard/analyse.html', context)


def optimise(request):
    raise Http404


def search(request):
    raise Http404


def bet(request):
    bet_matches = sorted(BetMatch.objects.all(), key=lambda x: x.summary)
    if RefreshTime.objects.exists():
        refresh_time = RefreshTime.objects.all()[0].refresh_datetime
    else:
        refresh_time = 'Never'
    context = {'bet_matches': bet_matches, 'refresh_time': refresh_time}
    return render(request, 'dashboard/bet.html', context)


def bet_refresh(request):
    BetMatch.objects.all().delete()
    matches = db.get_future_match_data()
    params = {Simulation.BET_ODD_POWER: 2., Simulation.BET_RETURN_POWER: 0., Simulation.MIN_PROB: 0.25,
              Simulation.MIN_RETURN: 1.05, Simulation.MAX_RETURN: 100., Simulation.WEBSITES: WEBSITES}
    bet_matches = distribution.get_value_bets(params, matches)
    for summary, side_id, website, odd, match_datetime, bet_fraction in bet_matches:
        bet_match = BetMatch(summary=summary, side=side_id, website=website, odd=odd,
                             bet_fraction=bet_fraction, match_datetime=match_datetime)
        bet_match.save()
    RefreshTime.objects.filter(type='bet').delete()
    RefreshTime(type='bet').save()
    return redirect('dashboard:bet')
