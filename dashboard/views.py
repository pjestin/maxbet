from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404

from .models import BetMatch, RefreshTime

from core.odds import cotes


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
    bet_matches = cotes.get_value_bets(params=[1., 0., 1.02, 1.08])
    for summary, side_id, website, odd, match_datetime, bet_fraction in bet_matches:
        bet_match = BetMatch(summary=summary, side=side_id, website=website, odd=odd,
                             bet_fraction=bet_fraction, match_datetime=match_datetime)
        bet_match.save()
    RefreshTime.objects.filter(type='bet').delete()
    RefreshTime(type='bet').save()
    return redirect('dashboard:bet')
