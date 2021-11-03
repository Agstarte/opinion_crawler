import pickle

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
    # czyszczenie tekstu ze wszystkiego poza literami i emotikonami
    emoticons = re.findall(r'(?::|;|=)(?:-)?(?:\)|\(|\(|D|P)', new_text)
    new_text = re.sub(r'(#[^ ]+?$)|(#[^ ]+? )', '', new_text)
    new_text = re.sub(r'([^a-z]+)', ' ', new_text.lower().replace('\\n', ' ')) \
               + ' ' + ' '.join(emoticons).replace('-', '')

    return new_text


docs = [preprocessor(text) for text in docs]

# lematyzacja wyrazów i tokenizacja
import spacy
nlp = spacy.load("pl_core_news_sm")

# python -m spacy download pl_core_news_sm
def lem_tok_docs(docs):
    docs = [[word.lemma_ for word in nlp(text)] for text in docs]

    print(docs)

    pickle.dump(docs, open('lem_tok_docs.pkl', 'wb'), protocol=4)


def load_lem_tok_docs():
    return pickle.load(open('lem_tok_docs.pkl', 'rb'))


docs = load_lem_tok_docs()
print(docs)

# stopwords

stopwords = nlp.Defaults.stop_words
stopwords.add(' ')

docs = [[word for word in text if word not in stopwords] for text in docs if text]
print(docs)


#
# # wektory cech
#
# from sklearn.feature_extraction.text import CountVectorizer
#
# count = CountVectorizer()  # unigramowe, można zwiększyć ngram_range=2
# #
# # # print(docs)
# bag = count.fit_transform(docs)
#
# # print(count.vocabulary_)
# #
# # # ważenie TF-IDF
# #
# from sklearn.feature_extraction.text import TfidfTransformer
#
# tf_idf = TfidfTransformer(use_idf=True,
#                           norm='l2',
#                           smooth_idf=True)
# print(tf_idf.fit_transform(bag).toarray())
