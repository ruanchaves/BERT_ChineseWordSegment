import pandas as pd
import csv
import os
import pathlib

def read_results(filename):
    df = pd.read_csv(filename)
    column_dict = dict(zip([x for x in df.columns], ['index', 'timestamp', 'identifier', 'token', 'ori_seg', 'des_seg']))
    df = df.rename(columns=column_dict)
    df.sample(5)
    df = df.sort_values('index')
    return df

def read_original(filename):
    df = pd.read_csv(filename, sep='\t', header=None)
    df = df.rename(columns={0: 'token'})
    return df
    
def identifier_filter(df, identifier):
    return df[df['identifier'].str.contains(identifier)]

def merge_frames(original, results):
    return pd.merge(original, results, on='token', how='left')

def get_nan_rows(df):
    df = df[df.isna().any(axis=1)]
    df = df[['token', 1]]
    df['token'] = df['token'].str.replace('\t', ' ')
    df[1] = df[1].str.replace('\t', ' ')
    return df

def save_df(df, destination):
    folder = os.path.split(destination)[0]
    pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    df.to_csv(
            destination,
            sep='\t',
            index=False,
            header=False,
            # quoting=csv.QUOTE_NONE
        )

    
def check_equality(s1, s2):
    if len(s1) == len(s2):
        return True
    else:
        s1 = s1.replace(" ", "X")
        s1 = s1.replace("\t", "X")
        print(len(s1), len(s2) )
        return False

def check_df(filename):
    df = pd.read_csv(filename, sep='\t', header=None)
    df['test'] = df[0].combine(df[1], check_equality)
    if (df['test']==False).any():
        raise Exception('Values do not match.')

if __name__ == '__main__':
    tables = [
        {
            "source": "results.csv",
            "identifier": "./corpora/wiki/en/processed_20200319155305799110",
            "original": "./corpora/wiki/en/processed/test.txt",
            "target": "./corpora/wiki/en/remainder/test.txt"
        },
        # {
        #     "source": "results.csv",
        #     "identifier": "",
        #     "original": "corpora/wiki/pt/processed/test.txt",
        #     "target": "./corpora/wiki/pt/remainder/test.txt"
        # }
    ]
    for item in tables:
        df = read_results(item['source'])
        df = identifier_filter(df, item['identifier'])
        original = read_original(item['original'])
        merged = merge_frames(original, df)
        nan_merged = get_nan_rows(merged)
        save_df(nan_merged, item['target'])
        check_df(item['target'])