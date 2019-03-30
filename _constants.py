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
    'de': [],
    'fr': ['peux', 'peut', 'pouvons', 'pouvez', 'peuvent', 'pouvais', 'pouvait', 'pouvions', 'pouviez', 'pouvaient', 'pourrai', 'pourras', 'pourra', 'pourrons', 'pourrez', 'pourront', 'pourrais', 'pourrait', 'pourrions', 'pourriez', 'pourraient', 'puisse', 'puisses', 'puissions', 'puissiez', 'puissent', 'pu',
           'trouve', 'trouves', 'trouvons', 'trouvez', 'trouvent', 'trouvé', 'trouvais', 'trouvait', 'trouvions', 'trouviez', 'trouvaient', 'trouverais', 'trouverait', 'trouverions', 'trouveriez', 'trouveraient',
           'crois', 'croit', 'croyons', 'croyez', 'croient', 'croyais', 'croyait', 'croyions', 'croyiez', 'croyaient', 'croirai', 'croiras', 'croira', 'croirons', 'croirez', 'croiront', 'cru', 'crus', 'crut', 'crûmes', 'crûtes', 'crurent', 'croie', 'croies', 'croient', 'crusse', 'crusses', 'crût', 'crussions', 'crussiez', 'crussent', 'croirais', 'croirait', 'croirions', 'croiriez', 'croiraient', 'croyant'],
    'ja': ['よう', 'みたい'],
    'ko': [],
}


def flatten(l: list):
    """
    Takes a list and concatenates and flattens all sub-lists.
    :param l: list of sub-lists
    :return: single list containing the sub-lists.
    """
    return [item for sublist in l for item in sublist]
