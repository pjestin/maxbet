import unittest
from unittest.mock import patch
from core.analysis import db
from core.common.model import Match
from datetime import datetime, timezone, timedelta
import json

DATA_AFTER_REGISTER_FILE = 'core/test/analysis/data/data_after_register.json'
DATA_BEFORE_ENRICH_FILE = 'core/test/analysis/data/data_before_enrich.json'
DATA_AFTER_ENRICH_FILE = 'core/test/analysis/data/data_after_enrich.json'
DATA_AFTER_ENRICH_MISSING_TIME_ZONE_FILE = 'core/test/analysis/data/data_after_enrich_missing_time_zone.json'
DATA_WITH_WRONG_PROBS_FILE = 'core/test/analysis/data/data_with_wrong_probs.json'
DATA_WITHOUT_WRONG_PROBS_FILE = 'core/test/analysis/data/data_without_wrong_probs.json'

FIVETHIRTYEIGHT = '538'


class DbTest(unittest.TestCase):

    def setUp(self):
        self.team_1_name = 'FC Barcelona'
        self.team_1_name_similar = 'FC Barca'
        self.team_2_name = 'Anderlecht'
        self.website_1 = 'MaxBet'
        self.website_2 = 'Freebet'
        self.odd_1 = 1.53
        self.odd_2 = 2.67
        self.time = datetime(2018, 8, 15, 11, 57, tzinfo=timezone.utc)
        with open(DATA_AFTER_REGISTER_FILE, mode='r', encoding='latin-1') as file:
            self.data_after_register = json.load(file)
        with open(DATA_BEFORE_ENRICH_FILE, mode='r', encoding='latin-1') as file:
            self.data_before_enrich = json.load(file)
        with open(DATA_AFTER_ENRICH_FILE, mode='r', encoding='latin-1') as file:
            self.data_after_enrich = json.load(file)
        with open(DATA_AFTER_ENRICH_MISSING_TIME_ZONE_FILE, mode='r', encoding='latin-1') as file:
            self.data_after_enrich_missing_time_zone = json.load(file)
        with open(DATA_WITH_WRONG_PROBS_FILE, mode='r', encoding='latin-1') as file:
            self.data_with_wrong_probs = json.load(file)
        with open(DATA_WITHOUT_WRONG_PROBS_FILE, mode='r', encoding='latin-1') as file:
            self.data_without_wrong_probs = json.load(file)

    def test_similar_strings(self):
        self.assertFalse(db.are_strings_similar('AGF Aarhus', 'Aarhus GF'))
        self.assertTrue(db.are_strings_similar('BrA,ndby IF', 'Brondby IF'))
        self.assertFalse(db.are_strings_similar('Standard Liege', 'Besiktas'))
        self.assertTrue(db.are_strings_similar('Auxerre', 'AJ Auxerre'))
        self.assertFalse(db.are_strings_similar('Niort', 'Chamois Niortais'))

    @patch('datetime.datetime')
    def test_get_new_match_data(self, mocked_datetime):
        mocked_datetime.utcnow.return_value = self.time - timedelta(minutes=3251)
        match = Match(self.time, self.team_1_name, self.team_2_name)
        match.teams['1'].odds = {self.website_1: self.odd_1, self.website_2: self.odd_2}
        match.teams['N'].odds = {self.website_1: self.odd_1}
        match.teams['2'].odds = {self.website_2: self.odd_2}
        data = {}
        db.enrich_data([match], data)
        self.assertEqual(self.data_after_register, data)

    @patch('datetime.datetime')
    def test_get_enriched_data(self, mocked_datetime):
        mocked_datetime.utcnow.return_value = self.time - timedelta(minutes=3251)
        mocked_datetime.strptime = datetime.strptime
        match = Match(self.time, self.team_1_name_similar, self.team_2_name)
        match.teams['1'].score = 1
        match.teams['2'].score = 0
        match.teams['1'].probs = {FIVETHIRTYEIGHT: 0.38}
        match.teams['N'].probs = {FIVETHIRTYEIGHT: 0.45}
        match.teams['2'].probs = {FIVETHIRTYEIGHT: 0.22}
        data = self.data_before_enrich
        db.enrich_data([match], data)
        self.assertEqual(self.data_after_enrich, data)

    def test_patch_add_time_zone(self):
        data = self.data_after_enrich_missing_time_zone
        db.add_bet_time_zone(data)
        self.assertEqual(self.data_after_enrich, data)

    def test_patch_remove_late_odds(self):
        data = self.data_with_wrong_probs
        db.remove_late_odds(data)
        self.assertEqual(self.data_without_wrong_probs, data)
