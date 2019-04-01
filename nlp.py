import collections

import nltk.data
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize import word_tokenize
from numpy import NaN
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions

from _constants import jsc, flatten, markers

nltk.data.path.append('nltk_data')  # add local data folder to list of search locations
tagger_path = '/home/mdr/Desktop/stanford-postagger-full-2018-10-16/'  # TODO: change this to read the locations from either a file or an environment variable

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
        features=Features(sentiment=SentimentOptions()),
        language=t.lang
    ).get_result()
    row['sentiment'] = response['sentiment']['document']['score']

    row.update({
        'de': _analyze_de,
        'fr': _analyze_fr,
        'ja': _analyze_ja,
        'ko': _analyze_ko
    }[t.lang](tweet_text))

    # So it turns out that Python doesn't have switch-cases because, you guessed it, Guido is a total fucking melon.
    # The mapping inside the `update` call is an equivalent structure, something I learned from working with old
    # Javascript code and passing around functions

    return t.id, row


def _analyze_de(text):
    return {}


def _analyze_fr(text):
    tagger = StanfordPOSTagger(
        model_filename=(tagger_path + 'models/french.tagger'),
        path_to_jar=(tagger_path + 'stanford-postagger.jar')
    )

    # The next oneliner is a bit dense, but in essence it is having the tagger tag each sentence one by one, and then
    # it is pulling off just the tags from the resulting list of tuples, and feeding them into a Counter (histogram)
    tags = tagger.tag(word_tokenize(text, language='french'))
    counter = collections.Counter([x[1] for x in tags])

    # now we need to remove and modify some of the syntactic categories, because they either don't exist in the other
    # languages, or otherwise can't be matched up with everyone.
    counter['ADJ'] += counter['A'] + counter['ADJWH'] + counter['VPP']; del counter['A']; del counter['ADJWH']; del counter['VPP']
    counter['ADV'] += counter['ADVWH']; del counter['ADVWH']
    counter['CC'] += counter['C']; del counter['C']
    counter['CS'] += 0  # just to make sure it's there
    del counter['CL']  # clitic pronouns don't really exist outside of romance languages (and the Japanese tagger doesn't distinguish various pronouns)
    del counter['CLO']
    del counter['CLR']
    del counter['CLS']
    del counter['D']   # Japanese doesn't have determiners in the traditional sense: they have demonstrative nouns, but those aren't necessarily determiners to most linguists
    del counter['DET']
    del counter['DETWH']
    counter['ET'] += 0
    counter['I'] += 0
    counter['NC'] += counter['N'] + counter['VINF']; del counter['N']; del counter['VINF']
    counter['NP'] += counter['NPP']; del counter['NPP']
    del counter['P']   # The Japanese tag set doesn't account for prepositions. We could manually look for them using a table like this: http://mylanguages.org/japanese_prepositions.php
    counter['PREF'] += 0
    counter['PRO'] += counter['PROREL'] + counter['PROWH']; del counter['PROREL']; del counter['PROWH']
    counter['V'] += counter['VIMP'] + counter['VPR'] + counter['VS']; del counter['VIMP']; del counter['VPR']; del counter['VS']
    counter['PUNC'] += counter['.$$.']; del counter['.$$.']

    return dict(counter)


def _analyze_ja(text):
    from rakutenma import RakutenMA

    rma = RakutenMA()
    rma.load("model_ja.json")
    tags = rma.tokenize(text)
    counter = collections.Counter([x[1] for x in tags])  # see the same premise above in the French section
    subordinating_conjunctions = list(filter(lambda tup: tup[1] == 'C' and tup[0] in jsc, tags))

    return {  # we need to map the Japanese tagset to a subset of the French tagset, so that we can compare the two
        'ADJ':    counter['A-c'] + counter['A-dp'] + counter['J-c'] + counter['J-tari'] + counter['J-xs'] + counter['R'],
        'ADV':  counter['F'],
        'CC':   counter['C'] - len(subordinating_conjunctions),
        'CS':   len(subordinating_conjunctions),
        'ET':   counter['E'],
        'I':    counter['I-c'],
        'NC':   counter['N-n'] + counter['N-nc'],
        'NP':   counter['N-pn'],
        'PREF': counter['P'],
        'PRO':  counter['D'],
        'V':    counter['V-c'] + counter['V-dp'] + counter['X'],
        'PUNC': counter['M-aa'] + counter['M-cp'] + counter['M-op'] + counter['M-p'],
    }


def _analyze_ko(text):
    return {}


german_sentence_tokenizer = nltk.data.load('nltk_data/tokenizers/punkt/PY3/german.pickle')  # load French sentence splitter
german_fast_tagger = StanfordPOSTagger(
    model_filename=(tagger_path + 'models/german-fast.tagger'),
    path_to_jar=(tagger_path + 'stanford-postagger.jar')
)
def check_german_verb_construction(text):
    word = next(iter([i for i in markers['de'][0] if i in text.lower()] or []), None)
    if word is None:
        word = next(iter([i for i in markers['de'][1] if i in text.lower()] or []), None)
        if word is None:
            return False
        which = 1
    else:
        which = 0

    tags = german_fast_tagger.tag_sents(map(lambda x: word_tokenize(x, language='german'), german_sentence_tokenizer.tokenize(text)))

    for sentence in tags:
        words = [x[0] for x in sentence]
        tags  = [x[1] for x in sentence]
        condition = word in words and \
                    (('VVIZU' in tags or
                     ('PTKZU' in tags and ('VVINF' in tags or 'VAINF' in tags))) if which == 1
                     else 'VVINF' in tags)
        if condition:
            print('tags:', tags)
            return True
    return False
