import pandas as pd

import sys
sys.path.insert(1, '../')
import fastg3.crisp as g3crisp
import fastg3.ncrisp as g3ncrisp

rtoy=[
    [2.6, 10.1, 23.3],
    [2.5, 10.2, 22.9],
    [2.5, 10.2, 23.0],
    [2.6, 10.0, 23.4],
    [2.7, 10.0, 24.3],
    [2.7, 10.1, 24.5]
]
df = pd.DataFrame(rtoy, columns=['flow', 'elevation', 'power'])

xparams = {
    'flow':{
        'type': 'numerical',
        'predicate': 'abs_rel_uncertainties',
        'params': [0,0.05]
    },
    'elevation':{
        'type': 'numerical',
        'predicate': 'abs_rel_uncertainties',
        'params': [0.05,0]
    }
}

yparams = {
    'power':{
        'type': 'numerical',
        'predicate': 'abs_rel_uncertainties',
        'params': [0.01,0]
    }
}

if __name__ == '__main__':
    print("###### TOY DATASET ######")
    print(df)
    print("__CRISP__")
    crisp_vps = g3crisp.vpe(df, list(xparams.keys()), list(yparams.keys()))
    crisp_g3 =  g3crisp.g3_sort(df, list(xparams.keys()), list(yparams.keys()))
    print(f"Violating pairs: {crisp_vps}")
    print(f"g3: {'{:.2f}'.format(crisp_g3)}")

    print("__NON-CRISP__")
    VPE = g3ncrisp.create_vpe_instance(
        df, 
        xparams, 
        yparams,
        verbose=False)
    ncrisp_vps = VPE.enum_vps()
    rg3 = g3ncrisp.RSolver(VPE, precompute=True)
    ncrisp_g3 = rg3.exact(method="wgyc")
    print(f"Violating pairs: {ncrisp_vps}")
    print(f"g3: {'{:.2f}'.format(ncrisp_g3)}")