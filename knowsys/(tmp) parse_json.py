from knowsys_utils.file_utils import load_json
import pandas as pd


data = load_json('cached_data/knowsys.json')

for table in data:
    if table['type'] == 'table':
        t = pd.DataFrame(table['data'])
        t.to_csv(f'cached_data/knowsys_table_{table["name"]}.csv')