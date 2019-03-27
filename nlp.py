from numpy import NaN
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions

with open('ibm-credentials.env') as f:
    api_key = f.readline().strip().split('=', 1)[1]
    url = f.readline().strip().split('=', 1)[1]

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2018-11-16',
    iam_apikey=api_key,
    url=url
)


def analyze(tweets):
    transformed = {}
    for (tweet_id, data) in map(lambda t: _analyze(t), tweets):
        transformed[tweet_id] = data

    return transformed


def _analyze(t):
    # first we create the columns we care about
    row = {
        'de': 0,  # which language is it
        'fr': 0,
        'ja': 0,
        'ko': 0,
        'sentiment': NaN,  # what is the numerical sentiment of the tweet
        'hashtags': len(t.entities['hashtags']),  # how many hashtags does the tweet have
        'user_mentions': len(t.entities['user_mentions']),  # how many user mentions are in the tweet body
        'author_followers_count': t.author.followers_count,  # how many followers does the author of the tweet have
        'author_friends_count': t.author.friends_count,  # how many friends does the author of the tweet have
        'author_statuses_count': t.author.statuses_count,  # how many statuses does the author of the tweet have
        'retweet_count': t.retweet_count,  # how many retweets this tweet has
        'favorite_count': t.retweeted_status.favorite_count if hasattr(t, 'retweeted_status') else t.favorite_count,
        # how many favourites this tweet has
        t.lang: 1  # set the actual language of the tweet to 1
    }

    tweet_text = (t.full_text if hasattr(t, 'full_text') else t.text)
    if hasattr(t, 'display_text_range'):
        # these are the cutoffs, if there is additional information in the tweet outside of the actual text content
        [a, b] = t.display_text_range
        tweet_text = tweet_text[a:b]  # clean the tweet of extras

    response = natural_language_understanding.analyze(
        text=tweet_text,
        features=Features(sentiment=SentimentOptions())
    ).get_result()
    row['sentiment'] = response['sentiment']['document']['score']

    {
        'de': _analyze_de,
        'fr': _analyze_fr,
        'ja': _analyze_ja,
        'ko': _analyze_ko
    }[t.lang](tweet_text)

    return t.id, row


def _analyze_de(text):
    pass


def _analyze_fr(text):
    import nltk.data
    from nltk.tokenize import word_tokenize
    from nltk.tag.stanford import StanfordPOSTagger
    nltk.data.path.append('nltk_data')

    sentence_tokenizer = nltk.data.load('nltk_data/tokenizers/punkt/PY3/french.pickle')
    tagger = StanfordPOSTagger(
        model_filename='/home/mdr/Desktop/stanford-postagger-full-2018-10-16/models/french.tagger',
        path_to_jar='/home/mdr/Desktop/stanford-postagger-full-2018-10-16/stanford-postagger.jar'

    )

    print(tagger.tag_sents(map(word_tokenize, sentence_tokenizer.tokenize(text))))


def _analyze_ja(text):
    from rakutenma import RakutenMA

    rma = RakutenMA()
    rma.load("model_ja.json")
    print(rma.tokenize(text))

def _analyze_ko(text):
    pass
