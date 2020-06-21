import re
import pandas as pd

def _parse_count(units_str):
    matches = re.findall(r'\A(\d+) \+ free (\d+) per pack', units_str, re.IGNORECASE)
    if len(matches) == 1 and len(matches[0]) == 2:
        return int(matches[0][0]) + int(matches[0][1])
    matches = re.findall(r'(\d+)\s?per pack', units_str, re.IGNORECASE)
    if len(matches) == 1:
        return int(matches[0])
    else:
        return None

def _parse_packs(units_str):
    matches = re.findall(r'\A(\d+) x (\d+) per pack', units_str, re.IGNORECASE)
    if len(matches) == 1 and len(matches[0]) == 2:
        return int(matches[0][0])
    else:
        return 1

def get_df():
    return pd.read_csv(
        'fairprice.csv',
        parse_dates=['date_crawled'],
    ).query(
        'availability != "Out of stock"'
    ).assign(
        pks=lambda x: x.units.apply(_parse_packs),
        cts=lambda x: x.units.apply(_parse_count),
        site='FairPrice',
    )