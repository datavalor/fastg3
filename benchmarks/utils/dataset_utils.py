#%%
import pandas as pd
from pydataset import data
from generate_syn import generate_syn
from pathlib import Path

from diamonds_params import DIAMONDS_XPARAMS, DIAMONDS_YPARAMS
from hydro_params import HYDRO_XPARAMS, HYDRO_YPARAMS

try:
    path = Path(__file__).parent / "../hydroturbine.csv"
    df = pd.read_csv(path)
    AVAILABLE_DATASETS = ['diamonds', 'hydroturbine', 'syn']
except:
    AVAILABLE_DATASETS = ['diamonds', 'syn']
MAX_ATTRS_DATASETS = {
    'diamonds': 10,
    'hydroturbine': 6,
    'syn': 50
}


def _check_args(df, n_antecedents, n_consequents):
    try:
        assert n_antecedents+n_consequents<=len(df.columns)
        assert n_antecedents>0
        assert n_consequents>0
    except ValueError:
        print("Invalid parameters")
        raise

def _balance_XY(
    all_attributes,
    main_antecedent, 
    main_consequent, 
    n_antecedents, 
    n_consequents
):
    antecedents = [main_antecedent]
    consequents = [main_consequent]
    all_attributes.remove(main_antecedent)
    all_attributes.remove(main_consequent)
    antecedents += all_attributes[:n_antecedents-1]
    consequents += all_attributes[n_antecedents-1:n_antecedents+n_consequents-2]
    return antecedents, consequents

def load_diamonds(n_antecedents=5, n_consequents=1, ncrisp=False):
    df = data("diamonds").dropna()
    _check_args(df, n_antecedents, n_consequents)
    antecedents, consequents = _balance_XY(
        list(df.columns),
        'carat', 
        'price', 
        n_antecedents, 
        n_consequents
    )
    if ncrisp:
        return df, DIAMONDS_XPARAMS, DIAMONDS_YPARAMS
    else:
        return df, antecedents, consequents

def load_hydroturbine(n_antecedents=3, n_consequents=1, ncrisp=False):
    path = Path(__file__).parent / "../hydroturbine.csv"
    df = pd.read_csv(path).dropna()
    _check_args(df, n_antecedents, n_consequents)
    antecedents, consequents = _balance_XY(
        list(df.columns),
        'flow', 
        'power',
        n_antecedents, 
        n_consequents
    )
    if ncrisp:
        df = df.sample(100000, random_state=27)
        return df, HYDRO_XPARAMS, HYDRO_YPARAMS
    else:
        return df, antecedents, consequents

def load_syn(
    n_tuples=1000000, 
    target_g3=0.5, 
    n_antecedents=2, 
    n_consequents=1, 
    n_groups=300, 
    percent_classes_per_group=0,
    ncrisp=False
):
    df, antecedents, consequents = generate_syn(
        target_g3 = target_g3,
        n_tuples=n_tuples,
        n_groups=n_groups,
        percent_classes_per_group=percent_classes_per_group,
        n_antecedents = n_antecedents,
        n_consequents = n_consequents,
    )
    if ncrisp:
        xparams = {}
        yparams = {}
        for attr in antecedents:
            xparams[attr] = {
                'type': 'numerical',
                'predicate': 'metric',
                'metric': 'absolute',
                'thresold': 0
            }
        for attr in consequents:
            yparams[attr] = {
                'type': 'numerical',
                'predicate': 'metric',
                'metric': 'absolute',
                'thresold': 0
            }
        return df, xparams, yparams
    else:
        return df, antecedents, consequents

def load_dataset(name, n_antecedents=None, n_consequents=None, n_tuples_syn=1000000, ncrisp=False):
    assert name in AVAILABLE_DATASETS, f'Unknown dataset {name}!'

    if n_antecedents is None or n_consequents is None:
        if name=='diamonds':
            return load_diamonds(ncrisp=ncrisp)
        elif name=='hydroturbine':
            return load_hydroturbine(ncrisp=ncrisp)
        elif name=='syn':
            return load_syn(n_tuples=n_tuples_syn, ncrisp=ncrisp)
    else:
        if name=='diamonds':
            return load_diamonds(n_antecedents=n_antecedents, n_consequents=n_consequents, ncrisp=ncrisp)
        elif name=='hydroturbine':
            return load_hydroturbine(n_antecedents=n_antecedents, n_consequents=n_consequents, ncrisp=ncrisp)
        elif name=='syn':
            return load_syn(n_tuples=n_tuples_syn, n_antecedents=n_antecedents, n_consequents=n_consequents, ncrisp=ncrisp)


# %%
