import logging
logging.basicConfig(level=logging.WARNING)

import sys
sys.path.insert(1, '../utils/')
sys.path.insert(1, '../')
sys.path.insert(1, '../../')

COLORMAP = [
    {'color': 'k', 'marker': '', 'dash': (None,None)},
    {'color': 'k', 'marker': '', 'dash': [1,1]},
    {'color': 'k', 'marker': '', 'dash': [3,1]},
    {'color': 'k', 'marker': 'o', 'dash': [1,1]},
    {'color': 'k', 'marker': '', 'dash': [4,1,1,1]}
][::-1]

def gen_time_benchmark():
    to_benchmark = {
        "g3crisp.g3_sort(df, X, Y)":[],
        "g3crisp.g3_hash(df, X, Y)":[],
        # "G3_SQL": [],
        "g3crisp.g3_srsi(df, X, Y, conf=0.95, error=0.01)":[],
        "g3crisp.g3_srs(df, X, Y, conf=0.95, error=0.01)":[],
        "g3crisp.g3_urs(df, X, Y, conf=0.95, error=0.01, algo=g3crisp.g3_sort)":[],
    }
    labels = [
        'G3_MEMOPT',
        'G3_TIMEOPT',
        # 'G3_SQL',
        'G3_SRSI',
        'G3_SRS',
        'G3_URS',
    ]
    return to_benchmark, labels

def gen_sampling_benchmark():
    to_benchmark = {
        "g3crisp.g3_srsi(df, X, Y, conf=0.95, error=0.01)":[],
        "g3crisp.g3_srs(df, X, Y, conf=0.95, error=0.01)":[],
        "g3crisp.g3_urs(df, X, Y, conf=0.95, error=0.01, algo=g3crisp.g3_sort)":[],
    }
    labels = [
        'G3_SRSI',
        'G3_SRS',
        'G3_URS',
    ]
    return to_benchmark, labels