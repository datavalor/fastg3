# %%
import timeit
import tqdm
from os import path
import inspect
import numpy as np
import dill

import init
import fastg3.crisp as g3crisp
from plot_utils import plot_bench
from constants import N_REPEATS, N_STEPS, DILL_FOLDER
from number_utils import format_number
from dataset_utils import AVAILABLE_DATASETS, load_dataset

MAX_SYN = 100000000

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
    yaxis_name=f"Average time on {str(N_REPEATS)} runs (ms)"
    return to_benchmark, labels, yaxis_name

def approx_test(dataset_name, frac_samples):
    to_benchmark, labels = init.gen_sampling_benchmark()
    for f in tqdm.tqdm(frac_samples):
        setup=gen_setup(dataset_name, f)
        exec(setup)
        true_g3=eval('g3crisp.g3_hash(df, X, Y)')
        for cmd in to_benchmark:
            to_benchmark[cmd].append(abs(true_g3-eval(cmd)))
    yaxis_name=f"Absolute error"# mean on {str(N_REPEATS)} runs"
    return to_benchmark, labels, yaxis_name

if __name__ == '__main__':    
    STEP=1/N_STEPS
    frac_samples = list(np.arange(STEP, 1+STEP, STEP))
    for dataset_name in AVAILABLE_DATASETS:
        for test_name in ['time', 'approx']:
            script_name = inspect.stack()[0].filename.split('.')[0]
            file_path = './'+path.join(DILL_FOLDER, f'{script_name}_{test_name}_{dataset_name}.d')
            if path.isfile(file_path): 
                print(f'{file_path} found! Skipping...')
                continue
            else:
                print(f'{file_path} in progress...')
            if test_name=='time':
                to_benchmark, labels, yaxis_name = time_test(dataset_name, frac_samples)
            else:
                to_benchmark, labels, yaxis_name = approx_test(dataset_name, frac_samples)
            fig, ax = plot_bench(to_benchmark, 
                frac_samples, 
                labels, 
                xlabel="Number of tuples", 
                ylabel=yaxis_name,
                logy=False,
                savefig=False
            )
            if dataset_name=='syn':
                dataset_size=MAX_SYN
            else:
                dataset_size = len(load_dataset(dataset_name)[0].index)
            ax.xaxis.set_major_formatter(lambda x, pos: format_number(x*dataset_size))
            dill.dump((fig, {"dataset_size": dataset_size}), open(file_path, "wb"))