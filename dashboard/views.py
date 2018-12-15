from django.shortcuts import render
from django.http import HttpResponse, Http404

from core.odds import cotes
from core.common import distribution


def index(request):
    return render(request, 'dashboard/index.html')


def register(request):
    raise Http404


def analyse(request):
    return render(request, 'dashboard/analyse.html')


def optimise(request):
    raise Http404


def search(request):
    raise Http404


def bet(request):
    bet_matches = cotes.get_value_bets(params=[1., 0.26, 0.954, 5.])
    # matches_summary = distribution.get_matches_summary(bet_matches)
    context = {'matches': sorted(bet_matches, key=lambda x: x[4])}
    return render(request, 'dashboard/bet.html', context)
