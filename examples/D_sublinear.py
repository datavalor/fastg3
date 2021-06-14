from pydataset import data
import time
import line_profiler

import sys
sys.path.insert(1, '../')
import fastg3.ncrisp as g3ncrisp

df = data("diamonds").sample(n=400000, replace=True, random_state=27).reset_index(drop=True)
# print(df.head())

xparams = {
    'carat':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.05
    },
    'cut':{
        'type': 'categorical',
        'predicate': 'equality'
    },
    'color':{
        'type': 'categorical',
        'predicate': 'equality'
    },
    'clarity':{
        'type': 'categorical',
        'predicate': 'equality'
    }
}

yparams = {
    'price':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 10
    }
}

if __name__ == '__main__':
    VPE = g3ncrisp.create_vpe_instance(
    df, 
    xparams, 
    yparams, 
    blocking=True,
    join_type="auto",
    opti_ordering=False,
    verbose=False)

    # print(len(VPE.enum_vps()), "violating pairs.")

    # Exact
    # start=time.time()
    # rg3 = g3ncrisp.RSolver(VPE, precompute=True)
    # gic = rg3.upper_bound(method="gic")
    # print(f'Greedy independent Cover upper bound computed in {1000*(time.time()-start)}ms')
    # print("GIC g3 is", gic)
    # print("-> Exact computation")
    # start=time.time()
    # wgyc = rg3.exact(method="wgyc")
    # print(f'WeGotYouCovered value computed in {time.time()-start}s')
    # print("Exact g3 is", wgyc)


    # print("-> Sublinear computation")
    # sub_solverY = g3ncrisp.Yoshida2009(g3ncrisp.VPEGraph(VPE))
    # start=time.time()
    # estimated_size = sub_solverY.estimate_mvc_size(2000)
    # print(f"Yoshida sublinear in {1000*(time.time()-start)}ms")
    # print(f"Estimation: {estimated_size}")
    sub_solverO = g3ncrisp.Onak2011(g3ncrisp.VPEGraph(VPE))
    start=time.time()
    estimated_size = sub_solverO.estimate_mvc_size(2000)
    print(f"Onak sublinear in {1000*(time.time()-start)}ms")
    print(f"Estimation: {estimated_size}")
