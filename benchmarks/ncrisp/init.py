import logging
logging.basicConfig(level=logging.WARNING)

import sys
sys.path.insert(1, '../utils/')
sys.path.insert(1, '../')
sys.path.insert(1, '../../')

COLORMAP = [
        {'color': 'k', 'marker': '', 'dash': (None,None)},
        {'color': 'k', 'marker': 'o', 'dash': [1,1]},
        {'color': 'k', 'marker': '', 'dash': [3,1]},
        {'color': 'k', 'marker': '', 'dash': [1,1]},
        {'color': 'k', 'marker': 'o', 'dash': [4,1,1,1]}
    ][::-1]

def gen_time_benchmark():
    to_benchmark = {
        "rg3.exact(method='wgyc')":[],
        "rg3.upper_bound(method='gic')":[],
        # "rg3.upper_bound(method='2approx')":[],
        # "g3ncrisp.Yoshida2009(g3ncrisp.VPEGraph(VPE)).estimate_mvc_size(2000)": [],
        "g3ncrisp.SubGIC(g3ncrisp.VPEGraph(VPE)).estimate_mvc_size(2000)": [],
        "g3ncrisp.Onak2011(g3ncrisp.VPEGraph(VPE)).estimate_mvc_size(2000)": [],
        # "rg3.lower_bound(method='maxmatch')": [],
    }
    labels = [
        'VPE+NCG3_EXACT',
        'VPE+NCG3_GIC',
        # 'VPE+NCG3_2APPROX',
        # 'NCG3_SUB09',
        'SubGIC',
        'NCG3_SUB11',
        # 'NCG3_MAXMATCH',
    ]
    return to_benchmark, labels

def gen_approx_benchmark():
    to_benchmark = {
        "rg3.upper_bound(method='numvc', numvc_time=1)":[],
        "rg3.upper_bound(method='gic')":[],
        # "rg3.upper_bound(method='2approx')":[],
        # "g3ncrisp.Yoshida2009(g3ncrisp.VPEGraph(VPE)).estimate_mvc_size(2000)": [],
        "g3ncrisp.SubGIC(g3ncrisp.VPEGraph(VPE)).estimate_mvc_size(2000)": [],
        "g3ncrisp.Onak2011(g3ncrisp.VPEGraph(VPE)).estimate_mvc_size(2000)": [],
        # "rg3.lower_bound(method='maxmatch')": [],
    }
    labels = [
        "VPE+NCG3_HEUR(1s)",
        'VPE+NCG3_GIC',
        # 'VPE+NCG3_2APPROX',
        # 'NCG3_SUB09',
        'SubGIC',
        'NCG3_SUB11',
        # 'VPE+NCG3_MAXMATCH',
    ]
    return to_benchmark, labels