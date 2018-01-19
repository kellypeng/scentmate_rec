import csv
import pandas as pd

def gender_dict():
    return {u'男香': 'Male', u'女香': 'Female', u'中性香': 'Unisex'}

def brand_dict():
    """Get brand name dictionary, Chinese names as key, English names as value"""
    reader = csv.reader(open('../cn_en/brand_names.csv', 'r'))
    brand_dict = {}
    for row in reader:
       k, v = row
       brand_dict[k] = v
    return brand_dict

def note_dict():
    """Takes in two csv files, one contains all CN names, another all EN names.
    Returns note dictionary, Chinese names as key, English names as value"""
    note_cn = pd.read_csv('../cn_en/notes_cn.csv', encoding='utf-8')
    note_en = pd.read_csv('../cn_en/notes_en.csv', encoding='utf-8')
    joined = note_cn.join(note_en, how='inner', lsuffix='_l', rsuffix='_r')
    joined.drop(['Unnamed: 0_l', 'Unnamed: 0_r'], axis=1, inplace=True)
    joined.rename(columns={'0':'note_cn'}, inplace=True)
    joined.rename(columns={' 0':'note_en'}, inplace=True)
    joined.set_index('note_cn', inplace=True)
    joined = joined.to_dict(orient='dict') # dict (default) : dict like {column -> {index -> value}}
    joined = list(joined.values())[0] # access dict inside dict
    return joined

def tag_dict():
    """Takes in two csv files, one contains all CN names, another all EN names.
    Returns tag dictionary, Chinese names as key, English names as value"""
    note_cn = pd.read_csv('../cn_en/tags_cn.csv', encoding='utf-8')
    note_en = pd.read_csv('../cn_en/tags_en.csv', encoding='utf-8')
    joined = note_cn.join(note_en, how='inner', lsuffix='_l', rsuffix='_r')
    joined.drop(['Unnamed: 0_l', 'Unnamed: 0_r'], axis=1, inplace=True)
    joined.rename(columns={'0':'tag_cn'}, inplace=True)
    joined.rename(columns={' 0':'tag_en'}, inplace=True)
    joined.set_index('tag_cn', inplace=True)
    joined = joined.to_dict(orient='dict')
    joined = list(joined.values())[0] # access dict inside dict
    return joined

def theme_dict():
    """Takes in csv file with two columns: CN and EN themes.
    Convert into dictionary for visualization
    """
    theme = pd.read_csv('../cn_en/themes.csv', encoding='utf-8')
    theme.set_index('CN', inplace=True)
    theme = theme.to_dict(orient='dict')
    theme = list(theme.values())[0]
    return theme


if __name__ == '__main__':
    brand_dict = brand_dict()
    note_dict = note_dict()
    tag_dict = tag_dict()
    gender_dict = gender_dict()
    theme_dict = theme_dict()
