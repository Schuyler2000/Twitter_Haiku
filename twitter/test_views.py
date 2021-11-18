from logging import raiseExceptions
import unittest
import tweepy
from views import count_syllables_from_string
from views import shorten_to_n_syllables
from views import list_of_user_IDs

#python -m unittest test_views.py

class TestViews(unittest.TestCase):

    def test_count_syllables_from_string(self):
        ### make sure syllables are being counted correctly

        ### incorrectly spelled words
        result = count_syllables_from_string("helloo")
        self.assertEqual(result, 100)
        result = count_syllables_from_string("wwwwwww")
        self.assertEqual(result, 100)
        result = count_syllables_from_string("baq qab")
        self.assertEqual(result, 200)
        result = count_syllables_from_string("bloosossos")
        self.assertEqual(result, 100)
        
        ### words with symbols
        result = count_syllables_from_string("(hello)")
        self.assertEqual(result, 2)
        result = count_syllables_from_string("h-ello")
        self.assertEqual(result, 2)
        result = count_syllables_from_string("hel$#!lo")
        self.assertEqual(result, 2)
        result = count_syllables_from_string("hel$#!loooo")
        self.assertEqual(result, 100)
        result = count_syllables_from_string("what's up")
        self.assertEqual(result, 2)


        ### words with numbers 
        result = count_syllables_from_string("he11o")
        self.assertEqual(result, 100)
        result = count_syllables_from_string("hello5")
        self.assertEqual(result, 100)
        result = count_syllables_from_string("2hell2o")
        self.assertEqual(result, 100)

    def test_list_of_user_IDs(self):
        ### testing all ids are valid

        acc_token = "REDACTED"
        acc_token_secret = "REDACTED"
        consumer_api_key = "REDACTED"
        consumer_api_key_secret = "REDACTED"

        auth = tweepy.OAuthHandler(consumer_api_key, consumer_api_key_secret)
        auth.set_access_token(acc_token, acc_token_secret)
        api = tweepy.API(auth)

        for id in list_of_user_IDs:
            try:
                u=api.get_user(id)
                self.assertEqual(id, u.screen_name)
            except Exception:
                raiseExceptions("some users do not exist")




