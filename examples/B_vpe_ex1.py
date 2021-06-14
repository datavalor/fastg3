from pydataset import data
import time

import sys
sys.path.insert(1, '../')
import fastg3.ncrisp as g3ncrisp

df = data("diamonds")

xparams = {
    'carat':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.05
    },
    'x':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.05
    },
    'y':{
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
    # Creates an interface with C++ object; errors will be return if any parameter is wrong
    VPE = g3ncrisp.create_vpe_instance(df, 
        xparams, 
        yparams, 
        blocking=True,
        opti_ordering=True,
        join_type="auto",
        verbose=True)
    
    # Finds all violating pairs
    start = time.time()
    vps = VPE.enum_vps()
    ellapsed = time.time()-start
    print(f'Diamond dataset contains {len(df.index)} rows.')
    print(f'{len(vps)} violating pairs found in {"{:.3f}".format(ellapsed)}s.')