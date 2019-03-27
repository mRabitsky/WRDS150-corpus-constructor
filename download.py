import numpy as np
import pandas as pd
import tweepy
import nlp
import json

from _constants import markers, flatten

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
HOW_MANY_TWEETS = 1


# function to remove retweets
def clear_retweets(status):
    """
    Turns the given tweet into the retweet if there is one.
    :param status: A tweet
    :return: The given tweet, or whatever tweet it is retweeting, if it is.
    """
    return status.retweeted_status if hasattr(status, 'retweeted_status') else status


# now we define our stream listener
class TweetStreamListener(tweepy.StreamListener):
    def __init__(self):
        super().__init__(api)
        self.data = []
        self.stream = None

    def on_status(self, status):
        if hasattr(status, 'extended_tweet'):
            status.full_text = status.extended_tweet['full_text']
            status.display_text_range = status.extended_tweet['display_text_range']

        text = status.full_text if hasattr(status, 'full_text') else status.text
        if len(text.split()) >= 8:
            self.data.append(clear_retweets(status))
        if len(self.data) >= HOW_MANY_TWEETS and self.stream:
            self.stream.disconnect()

    def on_error(self, status_code):
        import sys
        print('Error, code: ', status_code, file=sys.stderr)
        return False

    def get_data(self):
        return self.data

    def register_stream(self, new_stream: tweepy.Stream):
        self.stream = new_stream


def get_french():
    french = TweetStreamListener()  # get listener
    stream = tweepy.Stream(auth=api.auth, listener=french, tweet_mode='extended')  # get stream
    french.register_stream(stream)
    stream.filter(track=markers['fr'], languages=['fr'])  # set the stream to look for these markers
    tweets['fr'] = french.get_data()  # put the collected data into the general tweets array.
    # get_german()
    get_japanese()


def get_german():
    german = TweetStreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=german, tweet_mode='extended')
    german.register_stream(stream)
    stream.filter(track=markers['de'], languages=['de'])
    tweets['de'] = german.get_data()
    get_japanese()


def get_japanese():
    for tweet in tweepy.Cursor(api.search, tweet_mode='extended', q=' OR '.join(markers['ja']), lang='ja').items(15):
        if len(tweets['ja']) < HOW_MANY_TWEETS and len(tweet.full_text) >= 8:
            tweets['ja'].append(clear_retweets(tweet))
    if len(tweets['ja']) < HOW_MANY_TWEETS:
        get_japanese()
    # else:
    #     get_korean()


def get_korean():
    for tweet in tweepy.Cursor(api.search, tweet_mode='extended', q=' OR '.join(markers['ko']), lang='ko').items(15):
        if len(tweets['ko']) < HOW_MANY_TWEETS and len(tweet.full_text) >= 8:
            tweets['ko'].append(clear_retweets(tweet))
    if len(tweets['ko']) < HOW_MANY_TWEETS:
        get_korean()


# create a map that stores each list of tweets by language
tweets = {'de': [], 'fr': [], 'ja': [], 'ko': []}
# call the french runner, which will call the others subsequently (as each finishes)
get_french()

# store all the texts, keyed by tweet ID
texts = {}
for language_data in tweets.values():
    for datum in language_data:
        try:
            texts[datum.id] = {'lang': datum.lang, 'text': datum.full_text}
        except AttributeError:
            texts[datum.id] = {'lang': datum.lang, 'text': datum.text}

# write the texts to file
pd.Series(texts).to_json('tweets/texts.json', force_ascii=False)

# print the data collected
for language_data in tweets.values():
    for datum in language_data:
        try:
            print(datum.id, ': ', datum.full_text)
        except AttributeError:
            print(datum.id, ': ', datum.text)

nlp_data = nlp.analyze(flatten(list(tweets.values())))
pd.DataFrame.from_dict(nlp_data, orient='index').to_csv('tweets/data.csv')
