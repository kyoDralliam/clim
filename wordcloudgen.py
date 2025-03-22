import json
import pandas as pd
from datetime import datetime, timezone
import re
import numpy as np
from  wordcloud import WordCloud
import matplotlib.pyplot as plt
import itertools

with open('freqwordlist.txt') as f:
  freqreg = re.compile(f.read(), re.I)

wordreg = re.compile(r"\w+")

def getFrequencyDictForText(sentence):
  freqs = {}

  # making dict for counting frequencies
  for match in wordreg.finditer(sentence):
    text = match.group().lower()
    if freqreg.fullmatch(text) or len(text) < 5:
      continue
    val = freqs.get(text, 0)
    freqs[text] =  val + 1
  return freqs


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

for i in range(yearly_df.shape[0]):
  makeImage("wc" + str(yearly_df['datetime'][i].year)+".png", getFrequencyDictForText(yearly_df['text'][i]))
