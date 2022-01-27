"""
Allows a more user-friendly experience with violating pair enumeraiton.
Checks, correct and raise errors dependending on the users parameters.
Auto choice of the type of join and blocking attributes.
Returns a VPE object.

Author: Pierre Faure--Giovagnoli, 2021
"""

import numpy as np
import pandas as pd
from pandas.api.types import is_string_dtype, is_categorical_dtype, is_numeric_dtype
import logging
from typing import Tuple

logger = logging.getLogger('fastg3_vpe')
logging.basicConfig(level=logging.DEBUG)

from .VPE import VPE

PREDICATES = {
    'equality': {
        'params': 0,
        'monotonic': True
    },
    'absolute_distance': {
        'params': 1, #[thresold]
        'monotonic': True
    },
    'abs_rel_uncertainties': {
        'params': 2, #[abs_uncertainty, rel_uncertainty]
        'monotonic': True
    },
    'edit_distance': {
        'params': 1 #[thresold]
    }

}
AUTHORIZED_JOINS = ['auto', 'brute_force', 'ordered'] 
CONSTRAINTS = {
    'numerical': {
        'predicates': ['equality', 'absolute_distance', 'abs_rel_uncertainties'],
        'check_type': 'not is_string_dtype(df[attr])'
    },
    'categorical': {
        'predicates': ['equality', 'edit_distance'],
        'check_type': 'True'
    },
    'datetime': {
        'predicates': ['equality', 'absolute_distance'],
        'check_type': 'np.issubdtype(df[attr].dtype, np.datetime64)'
    }
}

def _check_attr(attr, attr_params, df):
    prefix = f"[{attr}]: "
    if attr not in df.columns:
        logger.warning(f'{prefix}Attribute not in provided dataframe. Attribute ignored.')
        return False, None
    authorized_types = list(CONSTRAINTS.keys())
    if 'type' not in attr_params or attr_params['type'] not in authorized_types:
        logger.warning(f'{prefix}No type or invalid type provided. Avalaible types are {authorized_types}. Attribute ignored.')
        return False, None
    attr_type = CONSTRAINTS[attr_params['type']]
    if not eval(attr_type['check_type']):
        logger.warning(f'{prefix}Should be {attr_params["type"]} but invalid Pandas column type! Should respect: {attr_type["check_type"]}')
        return False, None
    authorized_predicates = attr_type['predicates']
    if "predicate" not in  attr_params or attr_params['predicate'] not in authorized_predicates:
        logger.warning(f'{prefix}No or invalid predicate. Avalaible predicates are {authorized_predicates}. Attribute ignored.')
        return False, None
    if 'params' not in attr_params: attr_params['params']=[]
    n_required_params = PREDICATES[attr_params['predicate']]['params']
    if len(attr_params['params'])!=n_required_params:
        logger.warning(f'{prefix}Invalid number of parameters. Exactly {n_required_params} required params for {attr_params["predicate"]}. Attribute ignored.')
        return False, None
    return True, attr_params

def _clean_params(
    params: dict, 
    df: dict
) -> dict:
    for attr in params.copy():
        to_keep, modified_params = _check_attr(attr, params[attr], df)
        if to_keep:
            params[attr] = modified_params
        else:
            del params[attr]
    return params

def _handle_join(
    join_type: str, 
    join_attr: str, 
    xjoin_candidates: list
) -> Tuple[str, str]:
    if join_type=="auto" or join_type is None:
        if xjoin_candidates:
            join_type="ordered"
        else:
            join_type="brute_force"
        logger.info(f'Join type [{join_type}] chosen automatically.')
    if join_type=="ordered" and not xjoin_candidates:
        logger.warning("Ordered join requested but no ordered attribute found. Brute force join applied.")
        join_type="brute_force"
    if join_type=="ordered" and join_attr is not None and join_attr not in xjoin_candidates:
        logger.warning(f"Join attribute [{join_attr}] specified for ordered join but it does not seem to be an ordered attribute. Join attribute chosen automatically.")
        join_attr=None
    if join_type not in AUTHORIZED_JOINS:
        logger.warning(f"Requested join [{join_type}] not authorized. Available joins are {AUTHORIZED_JOINS}. Brute force join applied.")
        join_type="brute_force"
    return join_type, join_attr

def _prepare_data(
    df: pd.DataFrame, 
    xparams: dict, 
    yparams: dict, 
    blocking: bool=True, 
    opti_ordering: bool=True,
    join_type: str="auto", 
    join_attr: str=None, 
    verbose: bool=False
) -> Tuple[pd.DataFrame, dict, dict, str, str, list]:
    # Verifying user parameters
    xparams = _clean_params(xparams.copy(), df)
    yparams = _clean_params(yparams.copy(), df)
    global_params = {**xparams, **yparams}

    # First filtering
    try:
        assert len(xparams.keys())>0 
        assert len(yparams.keys())>0
    except AssertionError:
        logger.exception("At least one attribute must be specified on each side of the df!")
        raise
    df_clean = df[list(global_params.keys())].dropna()
    n_rows = len(df_clean.index)

    # Converting dates to long with ns unit
    for attr in df_clean.columns:
        if global_params[attr]["type"] == "datetime":
            df_clean[attr]=df_clean[attr].astype("datetime64[ns]").astype("int64")

    # Handling X side
    xblocking=[]
    xjoin_candidates = []
    for attr in xparams.copy():
        if xparams[attr]['predicate']=='equality':
            if blocking:
                xblocking.append(attr)
                del xparams[attr]
            elif is_string_dtype(df_clean[attr]) or is_categorical_dtype(df_clean[attr]):
                df_clean[attr] = df_clean[attr].astype('category').cat.codes.astype('int64')
        elif is_numeric_dtype(df_clean[attr]):
            xjoin_candidates.append(attr)

    # Handling Y side
    for attr in yparams:
        if yparams[attr]['predicate']=='equality' and (is_string_dtype(df[attr]) or is_categorical_dtype(df[attr])):
            df_clean[attr] = df_clean[attr].astype('category').cat.codes.astype('int64')

    # Choosing best ordering for antecedents and handling join
    join_type, join_attr = _handle_join(join_type, join_attr, xjoin_candidates)
    if opti_ordering and len(xjoin_candidates) > 1 and n_rows>2000:
        attrs_with_score = {}
        for attr in xparams:
            tmp_join_type = "brute_force"
            if attr in xjoin_candidates: tmp_join_type = "ordered"
            V = VPE(verbose=False)
            V.prepare_enumeration(
                    df_clean.sample(1000), 
                    {attr:xparams[attr]},
                    yparams,
                    pjoin_type=tmp_join_type, 
                    join_attr=attr)
            attrs_with_score[attr]=len(V.enum_vps())
        if verbose: logger.setLevel(level=logging.DEBUG)
        # Handling join
        if join_type=="ordered":
            if join_attr is not None:
                attrs_with_score[attr]=-1
            else:
                xjoin_candidates = sorted(xjoin_candidates, key=lambda x: attrs_with_score[x])
                join_attr=xjoin_candidates[0]
                attrs_with_score[join_attr]=-1
        sorted_attrs = sorted(list(attrs_with_score), key=lambda x: attrs_with_score[x])
        for i,attr in enumerate(sorted_attrs):
            xparams[attr]["position"]=i
        logger.info(f"Attributes order optimized in the following way: {sorted_attrs}") 
    else:
        if len(xjoin_candidates)==0:
            join_type="brute_force"
            join_attr=None
        else:
            join_attr = xjoin_candidates[0]
            for i, attr in enumerate(xparams):
                if attr==join_attr:
                    xparams[attr]["position"]=0
                else:
                    xparams[attr]["position"]=i+1
            sorted_attrs = sorted(list(xparams), key=lambda x: xparams[x]["position"])
            logger.info(f"Non-optimized attribute order: {sorted_attrs}") 

    if join_attr is not None:
        logger.info(f"[{join_attr}] chosen for ordered join among following candidates {xjoin_candidates}.") 

    return df_clean, xparams, yparams, join_type, join_attr, xblocking

def create_vpe_instance(
    df: pd.DataFrame, 
    xparams: dict, 
    yparams: dict, 
    blocking: bool=True, 
    opti_ordering: bool=True,
    join_type: str="auto", 
    join_attr: str=None, 
    verbose: bool=False
) -> VPE:
    """
    Returns a VPE object based on user parameters.
    VPE: Violating Pair Enumeration
    FD: Functionnal Dependency

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe on which VPE needs to be performed.
    xparams : dict
        Parameters for the left side of the FD.
    yparams : dict
        Parameters for the right side of the FD.
    blocking : bool
        If True, blocking will be performed if possible.
    opti_ordering : bool
        If True, attributes will be ordered for comparison in optimized way.
    join_type :  {'auto', 'brute_force', 'ordered'}
        Chooses the join type. Auto will automatically choose between brute_force and ordered.
    join_attr : str
        If ordered join is selected, forces the attribute to join on.
    blocking : bool
        If True, verbose will be activated.
    n_jobs : int
        Number of threads used to perform the join.
    Returns
    -------
    out : VPE object
        VPE object according to user's parameters.

    """
    if verbose: logger.setLevel(level=logging.DEBUG)
    else: logger.setLevel(level=logging.WARNING)
    
    df_clean, xparams, yparams, join_type, join_attr, xblocking = _prepare_data(
        df, 
        xparams, 
        yparams, 
        blocking, 
        opti_ordering,
        join_type, 
        join_attr, 
        verbose)
    V = VPE(verbose=verbose)
    V.prepare_enumeration(
        df_clean, 
        xparams, 
        yparams, 
        blocking_attrs=xblocking, 
        pjoin_type=join_type, 
        join_attr=join_attr)

    return V

