import re
import pandas as pd

def _parse_count(product_name):
    cts = re.findall(r'\s(\d+)\s?c', product_name, re.IGNORECASE)
    return int(cts[0]) if cts else None

def _parse_packs(product_name):
    pks = re.findall(r'Pack of (\d)', product_name, re.IGNORECASE)
    return int(pks[0]) if pks else 1

def get_df():
    return pd.read_csv(
        'amazon.csv',
        parse_dates=['date_crawled'],
    ).query(
        'availability != "Temporarily out of stock."'
    ).assign(
        cts=lambda x: x.name.apply(_parse_count),
        pks=lambda x: x.name.apply(_parse_packs),
        site='amazon.sg',
    )