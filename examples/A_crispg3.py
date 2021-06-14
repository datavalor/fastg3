from pydataset import data

import sys
sys.path.insert(1, '../')
import fastg3.crisp as g3crisp

df = data("diamonds").sample(n=50000, replace=True)
X = ['carat', 'cut', 'clarity', 'color']
Y = ['price']

if __name__ == '__main__':
    # violating pairs enumeration for crisp FDs
    print(len(g3crisp.vpe(df, X, Y)))

    # based on sorting, less time efficient O(nlog(n)) in theory but more memory friendly
    print(g3crisp.g3_sort(df, X, Y))
    # based on hashing, efficient O(n) but less memory friendly
    print(g3crisp.g3_hash(df, X, Y))
    # based uniquely on pandas (no c++)
    print(g3crisp.g3_pandas(df, X, Y))

    # uses uniform random sampling for large datasets p(|g3-urs_g3|<=error)=conf
    print(g3crisp.g3_urs(df, X, Y, conf=0.95, error=0.01, algo=g3crisp.g3_hash, verbose=True))
    # uses stratified random sampling for large datasets p(|g3-srs_g3|<=error)=conf
    print(g3crisp.g3_srs(df, X, Y, conf=0.95, error=0.01, verbose=True))
    print(g3crisp.g3_srsi(df, X, Y, conf=0.95, error=0.01, verbose=True))

    
