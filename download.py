import logging
import sys

import pandas as pd
import tweepy
from tweepy import TweepError

import nlp
from _constants import markers, flatten

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

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
HOW_MANY_TWEETS = 100


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
        if status.id in map(lambda x: x.id, self.data):
            return  # stop here if we've seen this one before.
        # print('a potential tweet has been discovered!')
        if hasattr(status, 'extended_tweet'):
            status.full_text = status.extended_tweet['full_text']
            status.display_text_range = status.extended_tweet['display_text_range']
        # if 'extended_tweet' in status._json.keys():
        #     et = status._json['extended_tweet']
        #     print(et)
        #     status.full_text = et['full_text']
        #     status.display_text_range = et['display_text_range']
        # # for some reason, truncated tweets sneak through still from the streaming API, even with their 'truncated' section set to false

        text = status.full_text if hasattr(status, 'full_text') else status.text
        if len(text.split()) >= 8:
            if status.lang == 'de' and not nlp.check_german_verb_construction(text):
                return  # stop here if the german tweet has the word but not the right structure
            self.data.append(clear_retweets(status))
            logging.info(f"Added a tweet in {status.lang}, [{len(self.data)}/{HOW_MANY_TWEETS}]")
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
    get_german()


# def get_german():
#     german = TweetStreamListener()
#     stream = tweepy.Stream(auth=api.auth, listener=german, tweet_mode='extended')
#     german.register_stream(stream)
#     # stream.filter(track=(list(markers['de'][0]) + [s + ' zu' for s in list(markers['de'][1])]), languages=['de'])
#     stream.filter(track=list(markers['de'][1]), languages=['de'])
#     tweets['de'] = german.get_data()
#     get_japanese()
def get_german():
    for tweet in tweepy.Cursor(api.search, tweet_mode='extended', q=(' OR '.join(markers['de'][1]) + ' zu'), lang='de').items(2*HOW_MANY_TWEETS - 2*len(tweets['de'])):
        if len(tweets['de']) < HOW_MANY_TWEETS and tweet.id not in map(lambda x: x.id, tweets['de']) and len(tweet.full_text) >= 8 and nlp.check_german_verb_construction(tweet.full_text):
            tweets['de'].append(clear_retweets(tweet))
            logging.info(f"Added a tweet in German, [{len(tweets['de'])}/{HOW_MANY_TWEETS}]")
    if len(tweets['de']) < HOW_MANY_TWEETS:
        get_german()
    else:
        get_japanese()


def get_japanese():
    for tweet in tweepy.Cursor(api.search, tweet_mode='extended', q=' OR '.join(markers['ja']), lang='ja').items(2*HOW_MANY_TWEETS - 2*len(tweets['ja'])):
        if len(tweets['ja']) < HOW_MANY_TWEETS and tweet.id not in map(lambda x: x.id, tweets['ja']) and len(tweet.full_text) >= 8:
            tweets['ja'].append(clear_retweets(tweet))
            logging.info(f"Added a tweet in Japanese, [{len(tweets['ja'])}/{HOW_MANY_TWEETS}]")
    if len(tweets['ja']) < HOW_MANY_TWEETS:
        get_japanese()
    else:
        get_korean()


def get_korean():
    for tweet in tweepy.Cursor(api.search, tweet_mode='extended', q=' OR '.join(map(lambda x: x[0], markers['ko'])), lang='ko').items(2*HOW_MANY_TWEETS - 2*len(tweets['ko'])):
        if len(tweets['ko']) < HOW_MANY_TWEETS and tweet.id not in map(lambda x: x.id, tweets['ko']) and len(tweet.full_text) >= 8 and nlp.check_korean_regex(tweet.full_text):
            tweets['ko'].append(clear_retweets(tweet))
            logging.info(f"Added a tweet in Korean, [{len(tweets['ko'])}/{HOW_MANY_TWEETS}]")
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
pd.DataFrame.from_dict(nlp_data, orient='index').to_csv('tweets/data.csv')  # save the data to csv
