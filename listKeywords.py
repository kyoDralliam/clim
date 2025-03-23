import json
import re
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import tee

# Load all the speeches
with open('speechs_data.json') as f:
  speechs = json.load(f)['speechs']

s = set(kwd for x in speechs for kwd in x['keywords'])
print(len(s))

with open("keywords", "w") as f:
  json.dump(list(s), f, ensure_ascii=False,indent=2)