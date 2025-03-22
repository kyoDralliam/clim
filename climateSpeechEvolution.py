import json
import re
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load all the speeches
with open('speechs_data.json') as f:
  speechs = json.load(f)['speechs']

# Ratification date of Kyoto's protocol
kyoto_protocol = datetime(1997,12,12, tzinfo=timezone.utc)

# Regexp to match climate change keywords
climate_words = r'climat|planéte|pollution|réchauffement|écolog|ZAD|zad'
climate_regexp = re.compile(climate_words)

# Process each entry to parse the datetime and adds an integer valued column `match` (containing 0 or 1)
# indicating whether the entry has some references to climate change keywords in its text
def process(x):
  d = datetime.fromisoformat(x['datetime'])
  x['datetime'] = d
  if kyoto_protocol < d and x['text']:
    x['match'] = int(bool(5 < len (climate_regexp.findall(x['text']))))
  else:
    x['match'] = 0
  return x

# Apply the process function to all data, filter out entries before Kyoto's protocol (remove text as well)
df = pd.DataFrame.from_records((x for x in map(process, after_kyoto) if kyoto_protocol < x['datetime']), index=['datetime'], exclude=['text'])


# Group the data per quarter
quarterly = df.groupby(pd.Grouper(freq="QE")).agg(
  # creates 3 new columns ratio, climate and all from the matches
  ratio=('match', 'mean'),
  climate=('match','sum'),
  all=('match', 'count')
  ).reset_index()
# Remove the first and last quarter that are incomplete
quarterly.drop([0,quarterly.shape[0] - 1], inplace=True)
# Change the representation for the climate and all columns to plot on a single figure
quarterly_sum_all = quarterly.melt(id_vars=['datetime'],value_vars=['climate','all'])

# Create 2 subplots and plot climate, all on the first, ratio on the second
fig,axs=plt.subplots(ncols=2)
sns.lineplot(data=quarterly_sum_all, x='datetime', y='value', hue='variable',ax=axs[0])
sns.lineplot(data=quarterly, x='datetime', y='ratio',ax=axs[1])
# Do not forget to show the underlying matplotlib.pyplot buffer !!
plt.show()