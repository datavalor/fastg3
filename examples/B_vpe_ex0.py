import pandas as pd
from pydataset import data

import sys
sys.path.insert(1, '../')
import fastg3.ncrisp as g3ncrisp

df = data("iris")

xparams = {
    'Sepal.Length':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
    },
    'Sepal.Width':{
        'type': 'numerical',
        'predicate': 'absolute_distance',
        'params': [0.05]
    }
}

yparams = {
    'Species':{
        'type': 'categorical',
        'predicate': 'equality'
    }
}

if __name__ == '__main__':
    # Creates an interface with C++ object; errors will be return if any parameter is wrong
    VPE = g3ncrisp.create_vpe_instance(
        df, 
        xparams, 
        yparams, 
        blocking=True, #unused as there is no equality predicate on the LHS of the FD
        opti_ordering=True,
        join_type="auto",
        verbose=True)
    
    # Finds all violating pairs in the form of vp list
    print(VPE.enum_vps())