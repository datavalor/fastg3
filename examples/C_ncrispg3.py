from pydataset import data
import time

import sys
sys.path.insert(1, '../')
import fastg3.ncrisp as g3ncrisp

df = data("diamonds")#.sample(n=100, random_state=27)

xparams = {
    'carat':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
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
        'predicate': 'absolute_distance',
        'params': [10]
    }

}

if __name__ == '__main__':
    # Creates an interface with C++ object; errors will be return if any parameter is wrong
    VPE = g3ncrisp.create_vpe_instance(df, 
        xparams, 
        yparams, 
        blocking=True,
        join_type="auto",
        verbose=False)

    return_cover=False

    print(f'Diamond dataset contains {len(df.index)} rows.')
    print(len(VPE.enum_vps()), "violating pairs.")

    start=time.time()
    rg3 = g3ncrisp.RSolver(VPE, precompute=True)
    print(f'Initialisation in {1000*(time.time()-start)}ms')

    # Exact
    print("-> Exact computation")
    start=time.time()
    wgyc = rg3.exact(method="wgyc", return_cover=return_cover)
    print(f'WeGotYouCovered value computed in {time.time()-start}s')


    # Lower bound
    print("-> Lower bound")
    start=time.time()
    maximal_matching = rg3.lower_bound(method="maxmatch")
    print(f'Maximal matching computed in {1000*(time.time()-start)}ms')
    # start=time.time()
    # maximum_matching = rg3.lower_bound(method="mvmatch")
    # print(f'Maximum matching computed in {1000*(time.time()-start)}ms')

    # Upper bound
    print("-> Upper bound")
    start=time.time()
    approx2 = rg3.upper_bound(method="2approx", return_cover=return_cover)
    print(f'Greedy 2-approximation algorithm computed in {1000*(time.time()-start)}ms')
    start=time.time()
    gic = rg3.upper_bound(method="gic", return_cover=return_cover)
    print(f'Greedy independent Cover upper bound computed in {1000*(time.time()-start)}ms')
    start=time.time()
    numvc = rg3.upper_bound(method="numvc", return_cover=return_cover)
    print(f'Numvc tight heuristic computed in {time.time()-start}s')

    if return_cover:
        print("Exact:", sorted(wgyc))
        print("NuMVC:", sorted(numvc))
        print("GIC:", sorted(gic))
        print("approx2:", sorted(gic))
    else:
        print(f'{"{:.2f}".format(maximal_matching)} <= g3={"{:.2f}".format(wgyc)} <= {"{:.2f}".format(numvc)} <= {"{:.2f}".format(gic)} <= {"{:.2f}".format(approx2)}')
    
    