# %%
import time
import timeit
import tqdm
import numpy as np

import init
from constants import N_REPEATS, N_STEPS, RES_FOLDER
from dataset_utils import AVAILABLE_DATASETS, load_dataset
from bench_utils import gen_file_infos, gen_result_df, save_result

SELECTED_DATASETS = AVAILABLE_DATASETS.copy()
SELECTED_DATASETS.remove('syn')
MAX_SYN = 10000000

def gen_setup(dataset_name, f, footer=True):
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
    blocking=True,
    opti_ordering=True,
    join_type='auto', 
    verbose=False)
rg3 = g3ncrisp.RSolver(VPE, precompute=True)
''' 
    if footer: return header_str+footer_str
    else: return header_str

def time_test(dataset_name, frac_samples):
    to_benchmark, labels = init.gen_time_benchmark()
    for f in tqdm.tqdm(frac_samples):
        setup=gen_setup(dataset_name, f)
        exec(setup)
        vpe_time = timeit.timeit('VPE.enum_vps()', setup=setup, number=1)*1000
        for cmd in to_benchmark:
            if cmd != 'G3_SQL':
                duration_mean = timeit.timeit(cmd, setup=setup, number=N_REPEATS)/N_REPEATS*1000
                if 'estimate_mvc_size' not in cmd:
                    to_benchmark[cmd].append(duration_mean+vpe_time)
                else:
                    to_benchmark[cmd].append(duration_mean)
            else:
                # exec(setup)
                to_benchmark[cmd].append(1000*eval(f'g3_sql_bench(df, X, Y, n_repeats={N_REPEATS})'))
    y_label=f"Average time on {str(N_REPEATS)} runs (ms)"
    return to_benchmark, labels, y_label

def approx_test(dataset_name, frac_samples):
    to_benchmark, labels = init.gen_approx_benchmark()
    for f in tqdm.tqdm(frac_samples):
        setup=gen_setup(dataset_name, f)
        exec(setup)
        true_g3=eval("rg3.exact(method='wgyc')")
        for cmd in to_benchmark:
            exec(setup)
            to_benchmark[cmd].append(eval(cmd)/true_g3)
    y_label='Relative error'
    return to_benchmark, labels, y_label

if __name__ == '__main__':    
    STEP=1/N_STEPS
    frac_samples = list(np.arange(STEP, 1+STEP, STEP))
    for dataset_name in SELECTED_DATASETS:
        for test_name in ['time', 'approx']:
            print(f'Current test: {dataset_name}, {test_name}')

            # handle file
            file_path, exists = gen_file_infos(test_name, dataset_name, RES_FOLDER)
            if exists: continue
            
            # execute tests
            start = time.time()
            bench_func = time_test if test_name=='time' else approx_test
            benchmark_res, y_legends, y_label = bench_func(dataset_name, frac_samples)
            bench_duration = time.time()-start

            # create df from results
            dataset_size = len(load_dataset(dataset_name)[0].index)
            ntuples = np.array(dataset_size*np.array(frac_samples), dtype=np.int64)
            res_df = gen_result_df(ntuples, benchmark_res, y_legends)
            
            # save results
            save_result(
                res_df, 
                'Number of tuples',
                y_label,
                bench_duration,
                file_path
            )