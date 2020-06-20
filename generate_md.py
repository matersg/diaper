import re
import pandas as pd

SIZE_DICT = {
    'XXXL': {
        'enum': 6,
        'expressions': ['XXXL'],
    },
    'XXL': {
        'enum': 5,
        'expressions': ['XXL','XXLarge','Extra Extra Large'],
    },
    'XL': {
        'enum': 4,
        'expressions': ['XL','XLarge','X-Large','Extra Large'],
    },
    'L': {
        'enum': 3,
        'expressions': ['L','Large'],
    },
    'M': {
        'enum': 2,
        'expressions': ['M','Medium'],
    },
    'S': {
        'enum': 1,
        'expressions': ['S','Small'],
    },
    'NB': {
        'enum': 0,
        'expressions': ['NB','Newborn','New Born'],
    },
}

def az_parse_size(product_name):
    for k, definition in SIZE_DICT.items():
        for e in definition['expressions']:
            if f' {e},' in product_name:
                return k

def parse_type(product_name):
    if 'Tape' in product_name:
        return 'Tape'
    elif 'Pants' in product_name:
        return 'Pants'
    else:
        return '-'

def az_parse_count(product_name):
    cts = re.findall(r'\s(\d+)\s?c', product_name, re.IGNORECASE)
    return int(cts[0]) if cts else None

def az_parse_packs(product_name):
    pks = re.findall(r'Pack of (\d)', product_name, re.IGNORECASE)
    return int(pks[0]) if pks else 1

def fp_parse_size(product_name):
    sz = product_name.split('-')[1].split('(')[0].strip()
    for k, definition in SIZE_DICT.items():
        for e in definition['expressions']:
            if e in sz:
                return k

def fp_parse_count(units_str):
    matches = re.findall(r'\A(\d+) \+ free (\d+) per pack', units_str, re.IGNORECASE)
    if len(matches) == 1 and len(matches[0]) == 2:
        return int(matches[0][0]) + int(matches[0][1])
    matches = re.findall(r'(\d+)\s?per pack', units_str, re.IGNORECASE)
    if len(matches) == 1:
        return int(matches[0])
    else:
        return None

def fp_parse_packs(units_str):
    matches = re.findall(r'\A(\d+) x (\d+) per pack', units_str, re.IGNORECASE)
    if len(matches) == 1 and len(matches[0]) == 2:
        return int(matches[0][0])
    else:
        return 1

def get_df_amazon():
    return pd.read_csv(
        'amazon.csv',
        parse_dates=['date_crawled'],
    ).query(
        'availability != "Temporarily out of stock."'
    ).assign(
        size=lambda x: x.name.apply(az_parse_size),
        cts=lambda x: x.name.apply(az_parse_count),
        pks=lambda x: x.name.apply(az_parse_packs),
        site='amazon.sg',
    )

def get_df_fairprice():
    return pd.read_csv(
        'fairprice.csv',
        parse_dates=['date_crawled'],
    ).query(
        'availability != "Out of stock"'
    ).assign(
        size=lambda x: x.name.apply(fp_parse_size),
        pks=lambda x: x.units.apply(fp_parse_packs),
        cts=lambda x: x.units.apply(fp_parse_count),
        site='FairPrice',
    )

def get_name_jp(product_name):
    name_lower = product_name.lower()
    if 'mamypoko' in name_lower:
        if 'air fit' in name_lower:
            return 'ムーニー'
        else:
            return 'マミーポコ'
    elif 'merries' in name_lower:
        return 'メリーズ'
    elif 'moony' in name_lower:
        return 'ムーニー'
    elif 'pampers' in name_lower:
        if 'premium care' in name_lower:
            return 'パンパースプレミアム'
        else:
            return 'パンパース'

def get_size_enum(size_str):
    return SIZE_DICT[size_str]['enum']

if __name__=='__main__':
    az_df = get_df_amazon()
    fp_df = get_df_fairprice()

    df = pd.concat([
        az_df[~az_df.name.str.contains('Wipe')],
        fp_df[~fp_df.name.str.contains('Wipe')],
    ]).dropna(
        subset=['size','cts','pks']
    ).drop_duplicates(
        subset=['url'],
        keep='last',
    ).assign(
        type=lambda x: x.name.apply(parse_type),
        per_diaper=lambda x: (x['price'] / x['cts'] / x['pks']),
        name_jp=lambda x: x.name.apply(get_name_jp),
        size_enum=lambda x: x['size'].apply(get_size_enum),
    )

    name_jp_links_str = ' / '.join([f'[{x}](#{x.lower()})' for x in sorted(df.name_jp.unique())])
    size_links_str = ' / '.join([f'[{x}](#{x.lower()})' for x in reversed(list(SIZE_DICT.keys()))])
    lines = [
        f'サイズ別: {size_links_str}\n',
        f'ブランド別: {name_jp_links_str}\n',
        '※MamyPoko Air Fitの中身はムーニー(マン)なのでムーニーに分類しています\n',
    ]

    lines.append('# サイズ別 (1枚あたりの価格順)')
    for sz in reversed(list(SIZE_DICT.keys())):
        rows = df.query(f'size == "{sz}"').sort_values(
            by=['per_diaper','price']
        )
        last_updated_jp = rows.date_crawled.min().strftime('%Y年%m月%d日 %I%p')
        lines.append(f'\n## {sz}\n')
        lines.append(f'最終更新 {last_updated_jp}\n')
        lines.append('商品名 |   | 販売 | 価格 | 1枚あたり')
        lines.append('----- | - | ---- | --- | ------')
        for r in rows.itertuples():
            cols = [
                f'[{r.name}]({r.url})',
                r.type,
                r.site,
                f'S${r.price:.2f}',
                f'S${r.per_diaper:.3f}',
            ]
            line = ' | '.join(cols)
            lines.append(line)

    lines.append('# ブランド別 (サイズ順、1枚あたりの価格順)')
    for njp in sorted(df.name_jp.unique()):
        rows = df.query(f'name_jp == "{njp}"').sort_values(
            by=['size_enum','per_diaper','price']
        )
        last_updated_jp = rows.date_crawled.min().strftime('%Y年%m月%d日 %I%p')
        lines.append(f'\n## {njp}\n')
        lines.append(f'最終更新 {last_updated_jp}\n')
        lines.append('商品名 |   |   | 販売 | 価格 | 1枚あたり')
        lines.append('----- | - | - | ---- | --- | ------')
        for r in rows.itertuples():
            cols = [
                f'[{r.name}]({r.url})',
                r.type,
                r.size,
                r.site,
                f'S${r.price:.2f}',
                f'S${r.per_diaper:.3f}',
            ]
            line = ' | '.join(cols)
            lines.append(line)

    fname = 'README.md'
    with open(fname, mode='w') as f:
        f.write('\n'.join(lines))

    print(f'Saved {fname}')