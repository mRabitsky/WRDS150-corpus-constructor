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
    for (tweet_id, data) in map(lambda t: {
        'de': _analyze_de(t),
        'fr': _analyze_fr(t),
        'ja': _analyze_jp(t),
        'nl': _analyze_nl(t),
    }[t.lang], tweets):
        transformed[tweet_id] = data

    return transformed


def _analyze_de(t):
    row = {'data': {'de': 1, 'fr': 0, 'jp': 0, 'nl': 0, 'sentiment': NaN}}

    response = natural_language_understanding.analyze(
        text=t.text,
        features=Features(sentiment=SentimentOptions())
    ).get_result()
    row['data']['sentiment'] = response['sentiment']['document']['score']

    return t.id, row


def _analyze_fr(t):
    row = {'data': {'de': 0, 'fr': 1, 'jp': 0, 'nl': 0, 'sentiment': NaN}}

    response = natural_language_understanding.analyze(
        text=t.text,
        features=Features(sentiment=SentimentOptions())
    ).get_result()
    row['data']['sentiment'] = response['sentiment']['document']['score']

    return t.id, row


def _analyze_jp(t):
    row = {'data': {'de': 0, 'fr': 0, 'jp': 1, 'nl': 0, 'sentiment': NaN}}

    response = natural_language_understanding.analyze(
        text=t.text,
        features=Features(sentiment=SentimentOptions())
    ).get_result()
    row['data']['sentiment'] = response['sentiment']['document']['score']

    return t.id, row


def _analyze_nl(t):
    row = {'data': {'de': 0, 'fr': 0, 'jp': 0, 'nl': 1, 'sentiment': NaN}}

    # import subprocess
    # process = subprocess.run(['python', 'pattern_nlp.py', t.text], capture_output=True, encoding='utf-8', check=True)
    # row['data']['sentiment'] = process.stdout

    return t.id, row
