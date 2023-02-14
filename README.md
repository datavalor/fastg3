# <img alt="fastg3" src="branding/logo_github_dark.png" height="80">

Introduced in [1], the g3 indicator is of primary interest for measuring the veracity of a functional dependency (FD) in a relation. The g3-error and its opposite the confidence are at the core of many types of relaxed FDs and allowed important advances in FD mining but also more recently in supervised learning. For a relation r and a FD phi, g3 measures the proportion of tuples to remove from r for phi to be satisfied in r.

This library aims to be a fast and reliable solution for computing g3 in Python for classic and relaxed FDs. Is has been designed to be used with Pandas and its underlying Cython implementation along with its integrated sampling schemes allow for fast analysis of large datasets.

# Installation

For building and relative import (you need to install Cython, Pandas and Numpy first):

``` bash
python3 setup.py build_ext
```
For installing:
``` bash
python3 setup.py install
```
# Usage

The examples/ folder contains an comprehensive example for each use case.

## References
<a id="1">[1]</a> 
Kivinen, J., & Mannila, H. (1995). Approximate inference of functional dependencies from relations. Theoretical Computer Science, 149(1), 129-149.

<a id="2">[2]</a> 
Armstrong, William Ward. "Dependency Structures of Data Base Relationships." IFIP congress. Vol. 74. 1974.

<a id="3">[3]</a> 
Cormode, Graham, et al. "Estimating the confidence of conditional functional dependencies." Proceedings of the 2009 ACM SIGMOD International Conference on Management of data. 2009.
