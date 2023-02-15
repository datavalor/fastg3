# %%
import time
import timeit
import tqdm
import numpy as np

import init
from constants import N_REPEATS, N_STEPS, RES_FOLDER
from dataset_utils import AVAILABLE_DATASETS, load_dataset
from bench_utils import gen_file_infos, gen_result_df, save_result

MAX_SYN = 100000000

from sql_utils import sql_available
print(f'SQL available: {sql_available}')

def gen_setup(dataset_name, f):
    return f'''
import init
import fastg3.crisp as g3crisp
from sql_utils import g3_sql_bench
from dataset_utils import load_dataset

df, X, Y = load_dataset('{dataset_name}', n_tuples_syn={MAX_SYN})
df = df.sample(frac={str(f)}, replace=False, random_state=27)
'''

def time_test(dataset_name, frac_samples):
    to_benchmark, labels = init.gen_time_benchmark()
    for f in tqdm.tqdm(frac_samples):
        setup=gen_setup(dataset_name, f)
        for cmd in to_benchmark:
            if cmd != 'G3_SQL':
                duration_mean = timeit.timeit(cmd, setup=setup, number=N_REPEATS)/N_REPEATS*1000
                to_benchmark[cmd].append(duration_mean)
            else:
                exec(setup)
                to_benchmark[cmd].append(1000*eval(f'g3_sql_bench(df, X, Y, n_repeats={N_REPEATS})'))
    y_label=f"Average time on {str(N_REPEATS)} runs (ms)"
    return to_benchmark, labels, y_label

def approx_test(dataset_name, frac_samples):
    to_benchmark, labels = init.gen_sampling_benchmark()
    for f in tqdm.tqdm(frac_samples):
        setup=gen_setup(dataset_name, f)
        exec(setup)
        true_g3=eval('g3crisp.g3_hash(df, X, Y)')
        for cmd in to_benchmark:
            to_benchmark[cmd].append(abs(true_g3-eval(cmd)))
    y_label=f"Absolute error"# mean on {str(N_REPEATS)} runs"
    return to_benchmark, labels, y_label

if __name__ == '__main__':    
    STEP=1/N_STEPS
    frac_samples = list(np.arange(STEP, 1+STEP, STEP))
    print(f'Available datasets: {AVAILABLE_DATASETS}')
    for dataset_name in AVAILABLE_DATASETS:
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
            res_df = gen_result_df(frac_samples, benchmark_res, y_legends)
            dataset_size = MAX_SYN if dataset_name=='syn' else len(load_dataset(dataset_name)[0].index)

            # save results
            save_result(
                res_df, 
                'Number of tuples',
                y_label,
                bench_duration,
                file_path
            )