from django.urls import path
from dashboard import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('analyse/', views.analyse, name='analyse'),
    path('optimise/', views.optimise, name='optimise'),
    path('search/', views.search, name='search'),
    path('bet/', views.bet, name='bet'),
    path('bet/refresh', views.bet_refresh, name='bet-refresh')
]
