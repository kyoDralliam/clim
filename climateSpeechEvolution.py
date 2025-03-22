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

# Ratification date of Kyoto's protocol
kyoto_protocol = datetime(1997,12,12, tzinfo=timezone.utc)

# Regexp to match climate change keywords
climate_words = r'[Cc]limat|[Pp]ollution|[Rr]échauffement|[Éé]colog|[Ee]ffet de serre|[Cc]arbone|[Aa]ccord de Paris|[Bb]iodiversité|COP 21|[Tt]ransition énergétique|CO2'
climate_regexp = re.compile(climate_words)

def match_kwd(l):
  return any(k in l for k in ['Climat', 'Ecologie', 'Developpement durable'])

# Process each entry, return a new dictionnary with parsed datetime and adds an integer valued field `match` (containing 0 or 1)
# indicating whether the entry has some references to climate change keywords in its text
def process(x):
  d = datetime.fromisoformat(x['datetime'])
  y = { 'datetime' : d }
  if kyoto_protocol < d and x['text']:
    l = climate_regexp.findall(x['title']) + climate_regexp.findall(x['text'])
    x['distr_match'] = { k : l.count(k) for k in set(l) }
    y['match'] = int(bool(len(l) > 2))
  else:
    y['match'] = 0
  y['climate_kwd'] = int(match_kwd(x['keywords']))
  return x, y

cutoff = datetime(2003,12,12, tzinfo=timezone.utc)

# Apply the process function to all data, filter out entries before Kyoto's protocol
speechs_after_kyoto = (x for x in map(process, speechs) if kyoto_protocol < x[1]['datetime'] ) #< cutoff)

# If we want to check the articles tagged Climat that we did not keep
# l = list(x[0] for x in speechs_after_kyoto if not match_kwd(x[0]['keywords']) and x[1]['match'])
# print(len(l))
# with open("climate_no_kwd.json", "w") as f:
#   json.dump(l, f, ensure_ascii=False,indent=2)

# Split the generators in two, one for saving the data, the other for plotting
speechs_after_kyoto1, speechs_after_kyoto2 = tee(speechs_after_kyoto)

# Save the entries that refers to climate
with open("climate.json", "w") as f:
  json.dump(list(x[0] for x in speechs_after_kyoto1 if x[1]['match']), f, ensure_ascii=False,indent=2)

# Transform to a panda dataframe removing all fields but 'match'
df = pd.DataFrame.from_records((x[1] for x in speechs_after_kyoto2), index=['datetime'])

# Group the data per quarter
quarterly = df.groupby(pd.Grouper(freq="QE")).agg(
  # creates 3 new columns ratio, climate and all from the matches
  ratio=('match', 'mean'),
  climate=('match','sum'),
  kwd=('climate_kwd','sum'),
  all=('match', 'count')
  ).reset_index()
# Remove the first and last quarter that are incomplete
quarterly.drop([0,quarterly.shape[0] - 1], inplace=True)
# Change the representation for the climate and all columns to plot on a single figure
quarterly_sum_all = quarterly.melt(id_vars=['datetime'],value_vars=['climate','kwd', 'all'])

# Create 2 subplots and plot climate, all on the first, ratio on the second
fig,axs=plt.subplots(ncols=2)
sns.lineplot(data=quarterly_sum_all, x='datetime', y='value', hue='variable',ax=axs[0])
sns.lineplot(data=quarterly, x='datetime', y='ratio',ax=axs[1])
# Do not forget to show the underlying matplotlib.pyplot buffer !!
plt.show()