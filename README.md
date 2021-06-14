# <img alt="fastg3" src="branding/logo_github_dark.png" height="80">

Introduced in [1], the g3 indicator is of primary interest for measuring the veracity of a functionnal dependency (FD) in a relation. The g3-error and its opposite the confidence are at the core of many types of relaxed FDs and allowed important advances in FD mining but also more recently in supervised learning. For a relation r and a FD phi, g3 measures the proportion of tuples to remove from r for phi to be satisfied in r.

This library aims to be a fast and reliable solution for computing g3 in Python for classic and relaxed FDs. Is has been desgined to be used with Pandas and its underlying Cython implementation along with its integrated sampling schemes allow for fast analysis of large datasets.

# Installation

For building and relative import (you need to install cython, pandas and numpy first):

``` bash
python3 setup.py build_ext
```
For installing:
``` bash
python3 setup.py install
```
In the future:

``` bash
pip install fastg3
```

# Crisp functionnal dependencies

We propose several algorithms for computing g3 in the case of classic FDs as defined by Armstrong [2]. Algorithms are pretty similar in terms of performance and fast overall (eg. in the magnitude of milliseconds for 30000 tuples). For very large datasets, random sampling approaches can be considered. Uniform RS is easier to use, faster, and as good as stratified RS in most cases.

``` python
import pandas as pd
from pydataset import data
import fastg3.crisp as g3crisp

df = data("iris")
X = ['Sepal.Length', 'Sepal.Width']
Y = ['Species']

# violating pairs enumeration for crisp FDs
print(len(g3crisp.vpe(df, X, Y)))

# based on sorting, less time efficient O(nlog(n)) in theory but more memory friendly
print(g3crisp.g3_sort(df, X, Y))
# based on hashing, efficient O(n) but less memory friendly
print(g3crisp.g3_hash(df, X, Y))
# based uniquely on pandas (no c++)
print(g3crisp.g3_pandas(df, X, Y))

# uses uniform random sampling for large datasets p(|g3-urs_g3|<=error)=conf
print(g3crisp.g3_urs(df, X, Y, conf=0.99, error=0.01, algo=g3crisp.g3_hash, verbose=True))
# uses stratified random sampling for large datasets p(|g3-srs_g3|<=error)=conf [3]
print(g3crisp.g3_srs(df, X, Y, conf=0.95, error=0.05))
```

# Relaxed functionnal dependencies (RFD)

We consider the class of functional dependencies relaxed on attributes values comparison. In that case, the problem of computing g3 comes back to computing the minimum vertex cover (MVC) and has been proven to be NP-Complete. 

## Violating pairs enumeration (VPE)

VPE consists in finding all pairs of tuples which are similar for the left-hand side of the RFD and dissimilar on the right-hand side. Firstly, each attribute has to be defined according to the following dict:

``` python
{
    'attribute_name':{
        'type': <'numerical', 'categorical', 'datetime'>,
         # only equality can be chosen for categorical for now
        'predicate': <'equality', 'metric'>,
        # if predicate is metric
        # absolute distance for numerical attributes and 
        # edit ditance (levenshtein) for textual attributes but this is pretty slow for now...
        'metric': <'absolute', 'edit_distance'>, 
        # if predicate is metric
        # thresold under which attributes are considered similar under the given metric
        # for datetime, thresold is given in ns
        'thresold': float, 
    }
}
```

Here is a fully working example:

``` python
import pandas as pd
import fastg3.ncrisp as g3ncrisp
from pydataset import data

data = data("iris")

xparams = {
    'Sepal.Length':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.05
    },
    'Sepal.Width':{
        'type': 'numerical',
        'predicate': 'metric',
        'metric': 'absolute',
        'thresold': 0.05
    }
}

yparams = {
    'Species':{
        'type': 'categorical',
        'predicate': 'equality'
    }
}

# Creates an interface with C++ object; errors will be return if any parameter is wrong
VPE = g3ncrisp.create_vpe_instance(df, 
    xparams, 
    yparams, 
    blocking=True, #unused as there is no equality predicate on the LHS of the FD
    join_type="auto", #chooses automatically between brute_force join O(n*2) and ordered join o(nlog(n))
    n_jobs=3, 
    verbose=True)

# Finds all violating pairs
print(VPE.enum_vps())

# Finds all tuples in violation with a given tuple
print(VPE.enum_neighboring_vps(68))
```
VPE can be very fast (centiseconds for tenth of thousands of tuples) if blocking and ordered join can be applied.

## Computing g3

``` python
import pandas as pd
import fastg3.ncrisp as g3ncrisp
from pydataset import data

df = data("diamonds")

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

VPE = g3ncrisp.create_vpe_instance(df, 
    xparams, 
    yparams, 
    blocking=True,
    join_type="auto", 
    n_jobs=3, 
    verbose=False)

rg3 = g3ncrisp.RSolver(VPE, precompute=True)
lower_bound = rg3.maximal_matching()
upper_bound = rg3.mvc_2_approx()
numvc = rg3.numvc(2)
```

## References
<a id="1">[1]</a> 
Kivinen, J., & Mannila, H. (1995). Approximate inference of functional dependencies from relations. Theoretical Computer Science, 149(1), 129-149.

<a id="2">[2]</a> 
Armstrong, William Ward. "Dependency Structures of Data Base Relationships." IFIP congress. Vol. 74. 1974.

<a id="3">[3]</a> 
Cormode, Graham, et al. "Estimating the confidence of conditional functional dependencies." Proceedings of the 2009 ACM SIGMOD International Conference on Management of data. 2009.
