import time
import timeit
from pydataset import data
import tqdm
from os import path
import inspect
import numpy as np

import init
from constants import N_REPEATS, N_STEPS, RES_FOLDER
from dataset_utils import AVAILABLE_DATASETS, load_dataset
from bench_utils import gen_file_infos, gen_result_df, save_result

def gen_setup(dataset_name, f, blocking=True, join_type="brute_force", opti_ordering=True, footer=True):
    header_str = f'''
import sys
sys.path.insert(1, '../')
import fastg3.ncrisp as g3ncrisp
from dataset_utils import load_dataset

df, xparams, yparams = load_dataset('{dataset_name}', ncrisp=True, n_tuples_syn=300000)
'''
    footer_str=f'''
df = df.sample(frac={str(f)}, replace=False, random_state=27)

VPE = g3ncrisp.create_vpe_instance(
    df, 
    xparams, 
    yparams, 
    blocking={str(blocking)},
    opti_ordering={str(opti_ordering)},
    join_type="{join_type}", 
    verbose=False)
rg3 = g3ncrisp.RSolver(VPE, precompute=True)
''' 
    if footer:
        return header_str+footer_str
    else: 
        return header_str

if __name__ == '__main__':
    STEP=1/N_STEPS
    frac_samples = list(np.arange(STEP, 1+STEP, STEP))
    for dataset_name in ['diamonds']:
        print(f'Current test: {dataset_name}')

        benchmark_res = {
            (False, "brute_force", False):[],
            (False, "brute_force", True):[],
            (True, "brute_force", False):[],
            (False, "ordered", False):[],
            (True, "ordered", True):[],
        }
        y_legends = [
            "VPE_BF",
            "VPE_COMPOPT",
            "VPE_BLOCKOPT",
            "VPE_ORDEROPT",
            "VPE_ALL",
        ]

        # handle file
        file_path, exists = gen_file_infos('time', dataset_name, RES_FOLDER)
        if exists: continue
        script_name = inspect.stack()[0].filename.split('.')[0]

        # execute tests
        start = time.time()
        for f in tqdm.tqdm(frac_samples):
            for cmd in benchmark_res:
                s=gen_setup(dataset_name, f, blocking=cmd[0], join_type=cmd[1], opti_ordering=cmd[2])
                duration_mean = timeit.timeit("VPE.enum_vps()", setup=s, number=N_REPEATS)/N_REPEATS*1000
                benchmark_res[cmd].append(duration_mean)
        bench_duration = time.time()-start

        # create df from results
        dataset_size = len(load_dataset(dataset_name)[0].index)
        ntuples = np.array(dataset_size*np.array(frac_samples), dtype=np.int64)
        res_df = gen_result_df(ntuples, benchmark_res, y_legends)
        
        # save results
        save_result(
            res_df, 
            'Number of tuples',
            f'Average time on {str(N_REPEATS)} runs (ms)',
            bench_duration,
            file_path
        )