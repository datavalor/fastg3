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
from number_utils import format_number
from constants import N_REPEATS, N_STEPS, DILL_FOLDER
from dataset_utils import AVAILABLE_DATASETS, load_dataset

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
    yaxis_name=f"Average time on {str(N_REPEATS)} runs (ms)"
    return to_benchmark, labels, yaxis_name

def approx_test(dataset_name, frac_samples):
    to_benchmark, labels = init.gen_approx_benchmark()
    for f in tqdm.tqdm(frac_samples):
        setup=gen_setup(dataset_name, f)
        exec(setup)
        true_g3=eval("rg3.exact(method='wgyc')")
        for cmd in to_benchmark:
            exec(setup)
            to_benchmark[cmd].append(eval(cmd)/true_g3)
    yaxis_name=f"Relative error"
    return to_benchmark, labels, yaxis_name

if __name__ == '__main__':    
    STEP=1/N_STEPS
    frac_samples = list(np.arange(STEP, 1+STEP, STEP))
    for dataset_name in ['diamonds', 'hydroturbine']:#, 'syn']:
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
            fig, ax = plot_bench(
                to_benchmark, 
                frac_samples, 
                labels, 
                xlabel="Number of tuples", 
                ylabel=yaxis_name,
                logy=False,
                savefig=False
            )
            exec(gen_setup(dataset_name, 1, footer=False))
            dataset_size = eval('len(df.index)')
            ax.xaxis.set_major_formatter(lambda x, pos: format_number(x*dataset_size))
            dill.dump((fig, {'dataset_size':dataset_size}), open(file_path, "wb"))