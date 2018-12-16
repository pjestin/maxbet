from django.db import models


class BetMatch(models.Model):

    SIDE_CHOICES = (
        ('1', 'Home'),
        ('N', 'Draw'),
        ('2', 'Away')
    )

    summary = models.CharField(max_length=200, primary_key=True)
    side = models.CharField(max_length=1, choices=SIDE_CHOICES)
    website = models.CharField(max_length=100)
    odd = models.FloatField()
    bet_fraction = models.FloatField()
    match_datetime = models.DateTimeField()

    def __str__(self):
        return self.summary


class RefreshTime(models.Model):

    TYPE_CHOICES = (
        ('bet', 'bet'),
        ('ana', 'analyse')
    )

    type = models.CharField(max_length=3, choices=TYPE_CHOICES, primary_key=True)
    refresh_datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.refresh_datetime
