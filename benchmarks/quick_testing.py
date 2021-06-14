import time
import sys
sys.path.insert(1, 'utils/')
sys.path.insert(1, '../')
from dataset_utils import load_dataset
import fastg3.ncrisp as g3ncrisp

if __name__ == '__main__':
    df, xparams, yparams = load_dataset('hydroturbine', ncrisp=True)
    df = df.sample(100000)#.reset_index(drop=True)

    start = time.time()
    VPE = g3ncrisp.create_vpe_instance(
        df, 
        xparams, 
        yparams, 
        blocking=True,
        opti_ordering=True,
        join_type="auto",
        verbose=True)
    print(len(VPE.enum_vps()))
    print("Init: ", time.time() - start)
    start = time.time()
    rg3 = g3ncrisp.RSolver(VPE, precompute=True)
    print("VPE: ", time.time() - start)
    gic = rg3.upper_bound(method="gic")
    print("gic:",gic)
    wgyc = rg3.exact(method="wgyc")
    print("g3:", wgyc)