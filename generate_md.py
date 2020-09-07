import re
import pandas as pd

import amazon as az
import fairprice as fp
import redmart as rm

SIZE_DICT = {
    'NB': ['NB','Newborn','New Born'],
    'S': ['S','Small'],
    'M': ['M','Medium'],
    'L': ['L','Large'],
    'XL': ['XL','XLarge','X-Large','Extra Large'],
    'XXL': ['XXL','XXLarge','Extra Extra Large'],
    'XXXL': ['XXXL'],
}

def parse_size(product_name):
    for k, variations in reversed(list(SIZE_DICT.items())):
        for v in variations:
            if re.findall(f'\W{v}\W', product_name, re.IGNORECASE):
                return k

def parse_type(product_name):
    if 'tape' in product_name.lower():
        return 'Tape'
    elif 'pants' in product_name.lower():
        return 'Pants'
    else:
        return '-'

def remove_kg_range(product_name):
    return re.sub('\s?\(\d+\s?-\s?\d+kg\)', '', product_name).strip()

def remove_packaging_may_vary(product_name):
    return re.sub('\s?\(?[Pp]ackag?ing may vary\)?', '', product_name)

def get_name_jp(product_name):
    name_lower = product_name.lower()
    if 'moony' in name_lower:
        return 'ムーニー'
    elif 'mamypoko' in name_lower:
        if 'air fit' in name_lower:
            return 'ムーニー'
        else:
            return 'マミーポコ'
    elif 'merries' in name_lower:
        return 'メリーズ'
    elif 'pampers' in name_lower:
        if 'premium care' in name_lower:
            return 'パンパースプレミアムケア'
        else:
            return 'パンパース'
    elif 'goo.n' in name_lower:
        return 'GOO.N (グ〜ン)'

def get_df():
    az_df = az.get_df()
    fp_df = fp.get_df()
    rm_df = rm.get_df()

    return pd.concat([
        az_df[~az_df.name.str.contains('Wipe')],
        fp_df[~fp_df.name.str.contains('Wipe')],
    ]).dropna(
        subset=['cts', 'pks']
    ).drop_duplicates(
        subset=['url'],
        keep='last',
    ).assign(
        size=lambda x: x.name.apply(parse_size),
        name=lambda x: x.name.apply(remove_kg_range),
        type=lambda x: x.name.apply(parse_type),
    ).append(
        rm_df,
        ignore_index=True
    ).assign(
        name=lambda x: x.name.apply(remove_packaging_may_vary),
        per_diaper=lambda x: (x['price'] / x['cts'] / x['pks']),
        name_jp=lambda x: x.name.apply(get_name_jp),
    ).dropna(
        subset=['name_jp']
    )

if __name__=='__main__':
    df = get_df()

    size_links = [f'[{x}](#{x.lower()})' for x in SIZE_DICT.keys()]
    lines = [
        f'サイズ {" / ".join(size_links)}\n',
        '注: MamyPoko Air Fitの中身はムーニー(マン)なのでムーニーに分類しています\n',
    ]

    for sz in SIZE_DICT.keys():
        lines.append(f'\n# {sz}\n')
        df_per_size = df.query(f'size == "{sz}"')
        if len(df_per_size) == 0:
            continue

        oldest_date_crawled = df_per_size.date_crawled.min()
        last_updated_jp = oldest_date_crawled.strftime('%Y年%m月%d日 %I%p')
        lines.append(f'最終更新 {last_updated_jp}\n')

        for i, njp in enumerate(sorted(df_per_size.name_jp.unique())):
            rows = df_per_size.query(f'name_jp == "{njp}"').sort_values(
                by=['per_diaper','price','name']
            )
            lines.append(f'**{njp} {sz}** |   |   | **1枚あたり**')
            if i == 0:
                lines.append(':---------- | - | - | ------')
            for r in rows.itertuples():
                cols = [
                    f'[{r.name}]({r.url})',
                    r.type,
                    f'S${r.price:.2f} {r.site}',
                    f'S${r.per_diaper:.3f}',
                ]
                line = ' | '.join(cols)
                lines.append(line)

    fname = 'README.md'
    with open(fname, mode='w') as f:
        f.write('\n'.join(lines))

    print(f'Saved {fname}')
