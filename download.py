import numpy as np
import pandas as pd
from pprint import pprint
import tweepy
import nlp
import json

# first get the secrets
with open('.env') as f:
    api_key = f.readline().strip()
    api_secret = f.readline().strip()
    access_token = f.readline().strip()
    access_secret = f.readline().strip()

# next create the auth
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# set how many tweets we want to read
HOW_MANY_TWEETS = 2


# now we define our stream listener
class TweetStreamListener(tweepy.StreamListener):
    def __init__(self):
        super().__init__(api)
        self.data = []

    def on_status(self, status):
        self.data.append(status)
        if len(self.data) >= HOW_MANY_TWEETS:
            stream.disconnect()

    def on_error(self, status_code):
        import sys
        print('Error, code: ', status_code, file=sys.stderr)
        return False

    def get_data(self):
        return self.data


# create and start a stream
french = TweetStreamListener()
stream = tweepy.Stream(auth=api.auth, listener=french)
stream.filter(track=['peux', 'pourrez'], languages=['fr'])

# japanese = TweetStreamListener()
# stream = tweepy.Stream(auth=api.auth, listener=japanese)
# stream.filter(track=['よう', 'みたい'], languages=['ja'])

# # store all the texts
# texts = {}
# for datum in french.get_data():
#     texts[datum.id] = datum.text
#
# # write the texts to file
# pd.Series(texts).to_json('tweets/texts.json')

for datum in french.get_data():
    print(datum.id, ': ', datum.text)
# for datum in japanese.get_data():
#     print(datum.id, ': ', datum.text)

print(nlp.analyze(french.get_data()))

