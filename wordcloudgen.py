import json
import pandas as pd
from datetime import datetime, timezone
import re
import numpy as np
from  wordcloud import WordCloud
import matplotlib.pyplot as plt
import itertools
from collections import Counter
import spacy

nlp = spacy.load('fr_core_news_md')

nlp.max_length = 14000000

with open('freqwordlist.txt') as f:
  freqreg = re.compile(f.read(), re.I)

def getFrequencyDictForText(sentence):
  return Counter(w.lemma_ for w in nlp(sentence) if w.is_alpha and not w.is_stop)
  # words = map(lambda m: m.group().lower(), wordreg.finditer(sentence))
  # return nltk.FreqDist(w for w in words if len(w) > 4 and not freqreg.fullmatch(w))


def makeImage(filename, text):
    wc = WordCloud(background_color="white", max_words=1000)
    # generate word cloud
    wc.generate_from_frequencies(text)
    wc.to_file(filename)

with open('climate.json') as f:
  data = json.load(f)

def process(x):
  x['datetime'] = datetime.fromisoformat(x['datetime'])
  if not x['text']:
    x['text'] = ''
  return x

df = pd.DataFrame.from_records(map(process, data), index=['datetime'], exclude=list(data[0].keys() - {'text'}))
yearly_df = df.groupby(pd.Grouper(freq="YE"))['text'].apply(' '.join).reset_index()

# l = list(len(yearly_df['text'][i]) for i in range(yearly_df.shape[0]))
# print(max(l), l)

for i in [0,3,5,9]: #range(yearly_df.shape[0]):
  makeImage("wc" + str(yearly_df['datetime'][i].year)+".png", getFrequencyDictForText(yearly_df['text'][i]))
