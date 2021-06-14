import numpy as np
import math

import logging
logger = logging.getLogger('fastg3_crisp')
logging.basicConfig(level=logging.DEBUG)

from . import cg3_hash
from . import cg3_sort
from . import cg3_srs
from . import cvpe

def _handle_verbose(verbose):
    if verbose: logger.setLevel(level=logging.DEBUG)
    else: logger.setLevel(level=logging.WARNING)

def _check_args(df, attrs):
    for attr in attrs:
        if attr not in df.columns:
            attrs.remove(attr)
            logging.warning(f'Attribute [{attr}] not in provided dataframe. Attribute ignored.')

def _preprocess(df, X, Y, label_encode=False):
    _check_args(df, X)
    _check_args(df, Y)
    try:
        assert len(X)>0 
        assert len(Y)>0
    except AssertionError:
        logging.exception("At least one attribute must be specified on each side of the df!")
        raise
    if label_encode: return df[X+Y].dropna().apply(lambda x: x.astype('category').cat.codes)
    else: return df[X+Y].dropna()

def vpe(df, X, Y):
    df = _preprocess(df, X, Y, label_encode=True)
    dfX = np.ascontiguousarray(df[X], dtype=np.int32)
    dfY = np.ascontiguousarray(df[Y], dtype=np.int32)
    return  cvpe.vpe(df.index.to_numpy(dtype=np.uint), dfX, dfY)

def g3_sort(df, X, Y):
    df = _preprocess(df, X, Y, label_encode=True)
    df = df.sort_values(X+Y, ascending=True, kind='quicksort')
    dfX = np.ascontiguousarray(df[X], dtype=np.int32)
    dfY = np.ascontiguousarray(df[Y], dtype=np.int32)
    return cg3_sort.sort_based(dfX, dfY)
    # return cg3_sort.sort_based(df[X].to_numpy(dtype=np.int32), df[Y].to_numpy(dtype=np.int32))

def g3_hash(df, X, Y):
    df = _preprocess(df, X, Y, label_encode=True)
    dfX = np.ascontiguousarray(df[X], dtype=np.int32)
    dfY = np.ascontiguousarray(df[Y], dtype=np.int32)
    return cg3_hash.hash_based(dfX, dfY)

def g3_pandas(df, X, Y):
    df = _preprocess(df, X, Y, label_encode=False)
    data_grouped = df.groupby(X+Y).size() \
                .to_frame('count').reset_index() \
                .sort_values('count', ascending=False) \
                .drop_duplicates(subset=X)
    # line below also works but slower...
    # g3 = (len(df.index)-df.groupby(X).apply(lambda x: x[Y].value_counts(sort=False, normalize=False).max()).sum())/len(df.index)
    return (len(df.index)-data_grouped['count'].sum())/len(df.index)

def hoeffding_sample_size(error, conf, n_total):
    if error==0 or conf==1: return n_total
    m = math.ceil(0.5*error**(-2)*math.log(2/(1-conf)))
    return min(n_total, m)

def g3_urs(
    df, 
    X, 
    Y, 
    conf=0.95, 
    error=0.05, 
    m=None, 
    algo=g3_hash, 
    seed=None,
    verbose=False
):
    _handle_verbose(verbose)
    df = _preprocess(df, X, Y, label_encode=False)
    if m is None:
        m = hoeffding_sample_size(error, conf, len(df.index))
    if m<len(df.index): s = df.sample(m, replace=False, random_state=seed)
    else: s = df
    logger.info(f'Sampling {len(s.index)} tuples over {len(df.index)}.')
    return algo(s, X, Y)

def g3_srs(df, X, Y, conf=0.95, error=0.05, t=None, verbose=False):
    _handle_verbose(verbose)
    df = _preprocess(df, X, Y, label_encode=True)
    if t is None:
        t=hoeffding_sample_size(error, conf, len(df.index))
    z=100
    logger.info(f't={t}, z={z}')
    dfX = np.ascontiguousarray(df[X], dtype=np.int32)
    dfY = np.ascontiguousarray(df[Y], dtype=np.int32)
    return cg3_srs.srs_based(dfX, dfY, t, z)

def g3_srsi(df, X, Y, conf=0.95, error=0.05, t=None, verbose=False):
    _handle_verbose(verbose)
    df = _preprocess(df, X, Y, label_encode=True)
    if t is None:
        t=hoeffding_sample_size(error, conf, len(df.index))
    logger.info(f't={t}')
    dfX = np.ascontiguousarray(df[X], dtype=np.int32)
    dfY = np.ascontiguousarray(df[Y], dtype=np.int32)
    # return cg3_srs.srs_based(dfX, dfY, t, auto_z=True, confidence=0.95, error=0.06)
    return cg3_srs.srs_based(dfX, dfY, t, auto_z=True, confidence=0.5, error=0.05)
