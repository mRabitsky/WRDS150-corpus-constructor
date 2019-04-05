import re



jsc = [
    '時', 'とき',    # 'toki'   - when
    '前', 'まえ',    # 'mae'    - before
    'あと',          # 'ato'    - after
    '間', 'あいだ',  # 'aida'   - while
    '殻', 'から',    # 'kara'   - because
    'ので',          # 'node'   - since
    'のに',          # 'noni'   - but
    'ねがら',        # 'negara' - when
    '迄', 'まで'     # 'made'   - until
]  # jsc = Japanese Subordinating Conjunctions
# This is not an exhaustive list, obviously, but it is a list of the most common one, according to this website:
# http://www.japaneselanguageguide.com/grammar/subordinating-conjunction.asp

markers = {
    'de': [
        {'werde', 'wirst', 'wird', 'werden', 'werdet', 'wurde', 'wurdest', 'wurden', 'wurdet', 'geworden', 'werdest', 'würde', 'würdest', 'würden', 'würdet'},
        {'scheine', 'scheinst', 'scheint', 'scheinen', 'schien', 'schienst', 'schienen', 'schient', 'schienen', 'geschienen', 'scheinest', 'scheinet',
         # 'schiene', 'schienest', 'schienet',
         'drohe', 'drohst', 'droht', 'drohen', 'drohte', 'drohtest', 'drohten', 'drohtet',
         # 'gedroht', 'drohest', 'drohet',
         'verspreche', 'versprichst', 'verspricht', 'versprechen', 'versprecht', 'versprach', 'versprachst', 'versprachen', 'verspracht', 'versprochen', 'versprechest', 'versprechet', 'verspräche',
         # 'versprächest', 'versprächst', 'versprächen', 'versprächet', 'versprächt'
        }
    ],
    'fr': {
        'peux', 'peut', 'pouvons', 'pouvez', 'peuvent', 'pouvais', 'pouvait', 'pouvions', 'pouviez', 'pouvaient', 'pourrai', 'pourras', 'pourra', 'pourrons', 'pourrez', 'pourront', 'pourrais', 'pourrait', 'pourrions', 'pourriez', 'pourraient', 'puisse', 'puisses', 'puissions', 'puissiez', 'puissent', 'pu',
        'trouve', 'trouves', 'trouvons', 'trouvez', 'trouvent', 'trouvé', 'trouvais', 'trouvait', 'trouvions', 'trouviez', 'trouvaient', 'trouverais', 'trouverait', 'trouverions', 'trouveriez', 'trouveraient',
        'crois', 'croit', 'croyons', 'croyez', 'croient', 'croyais', 'croyait', 'croyions', 'croyiez', 'croyaient', 'croirai', 'croiras', 'croira', 'croirons', 'croirez', 'croiront', 'cru', 'crus', 'crut', 'crûmes', 'crûtes', 'crurent', 'croie', 'croies', 'croient', 'crusse', 'crusses', 'crût', 'crussions', 'crussiez', 'crussent', 'croirais', 'croirait', 'croirions', 'croiriez', 'croiraient', 'croyant',
        'sans doute'
    },
    'ja': {'よう', 'みたい', 'らしい'},
    'ko': {
        ('책무', re.compile(r'이\w*다?'), True),
        ('허가', re.compile(r'(있\w*다?)|(없\w*다?)|(얻\w*다?)|(받\w*다?)|(되\w*다?)'), True),
        ('허락', re.compile(r'(있\w*다?)|(없\w*다?)|(얻\w*다?)|(받\w*다?)|(되\w*다?)'), True),
        ('허용', re.compile(r'(있\w*다?)|(없\w*다?)|(얻\w*다?)|(받\w*다?)|(되\w*다?)'), True),
        ('면', re.compile(r'\w+면 좋\w*다?'), False),
        ('필요', re.compile(r'(있\w*다?)|(없\w*다?)|(하다)'), True),
        ('도', re.compile(r'\w+도 좋\w*다?'), False),
        ('야', re.compile(r'\w+야 하다'), False),
        ('추측', re.compile(r'추측'), False),
        ('추정', re.compile(r'추정'), False),
        ('걸', re.compile(r'\w+걸\W+'), False),
        ('것 같다', re.compile(r' 것 같다\W+'), False),
        ('것다', re.compile(r'\w+것다'), False),
        ('판단', re.compile(r'판단으로'), False),
        ('생각', re.compile(r'생각으로'), False),
        ('상상', re.compile(r'\W+상상\W+'), False),
        ('의견으로', re.compile(r'의견으로'), False),
        ('군', re.compile(r'\w+군\W+'), False),
        ('네', re.compile(r'\w+네\W+'), False),
        ('다고', re.compile(r'\w+다고 하\w*다?'), False),
    },
}


def flatten(l: list):
    """
    Takes a list and concatenates and flattens all sub-lists.
    :param l: list of sub-lists
    :return: single list containing the sub-lists.
    """
    return [item for sublist in l for item in sublist]
