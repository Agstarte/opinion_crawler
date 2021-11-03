import pandas as pd

labels = {
    'positive': 1,
    'negative': 0
}


def transform_csv():
    rates = pd.read_csv('csv/ceneo.csv')

    for index, rate in enumerate(rates['rate']):
        if float(rate.split('/')[0].replace(',', '.')) >= 4:
            rates['rate'][index] = 1
        else:
            rates['rate'][index] = 0

    out_dict = {
        'text': list(rates['text']),
        'sentiment': list(rates['rate']),
    }

    dataframe = pd.DataFrame.from_dict(out_dict)
    dataframe.to_csv('csv/out_ceneo.csv', quoting=1, encoding='utf-8', index=False)


# czyszczenie tekstu
import numpy as np
import re

docs = np.array(list(pd.read_csv('csv/out_ceneo.csv')['text']))


def preprocessor(text):
    # zamiana polskich znaków na zwykle
    polish_characters = {'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ś': 's',
                         'ó': 'o', 'ń': 'n', 'ż': 'z', 'ź': 'z'}
    new_text = ''
    for char in text:
        if char in polish_characters:
            new_text += polish_characters[char]
        else:
            new_text += char

    emoticons = re.findall(r'(?::|;|=)(?:-)?(?:\)|\(|\(|D|P)', new_text)
    new_text = re.sub(r'[^\w ]+', ' ', new_text.lower()) + " ".join(emoticons).replace('-', '')

    return new_text


print(preprocessor('fbdhasuj dfśąfółśą 1321 nfui456... ?? :) :*'))

#
# # wektory cech
#
# from sklearn.feature_extraction.text import CountVectorizer
#
# count = CountVectorizer()  # unigramowe, można zwiększyć ngram_range=2
#
# # print(docs)
# # bag = count.fit_transform(docs)
# #
# # print(count.vocabulary_)
#
# # ważenie TF-IDF
#
# from sklearn.feature_extraction.text import TfidfTransformer
#
# tf_idf = TfidfTransformer(use_idf=True,
#                           norm='l2',
#                           smooth_idf=True)
# print(tf_idf.fit_transform(count.fit_transform(docs)).toarray())
