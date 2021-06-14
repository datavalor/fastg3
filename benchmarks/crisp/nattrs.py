import timeit
import tqdm
import numpy as np
import inspect
from os import path
import dill

import init
import fastg3.crisp as g3crisp
from plot_utils import plot_bench
from constants import N_REPEATS, N_STEPS, DILL_FOLDER
from dataset_utils import AVAILABLE_DATASETS, MAX_ATTRS_DATASETS, load_dataset

def gen_setup(dataset_name, n, cons=False):
    if cons: load=f"df, X, Y = load_dataset('{dataset_name}', n_antecedents=1, n_consequents={n})"
    else: load=f"df, X, Y = load_dataset('{dataset_name}', n_antecedents={n}, n_consequents=1)"
    return f'''
import init
import fastg3.crisp as g3crisp
from sql_utils import g3_sql_bench
from dataset_utils import load_dataset
'''+load

def time_test(dataset_name, n_attrs, cons=False):
    to_benchmark, labels = init.gen_time_benchmark()
    for n in tqdm.tqdm(n_attrs):
        setup=gen_setup(dataset_name, n, cons)
        for cmd in to_benchmark:
            if cmd != 'G3_SQL':
                duration_mean = timeit.timeit(cmd, setup=setup, number=N_REPEATS)/N_REPEATS*1000
                to_benchmark[cmd].append(duration_mean)
            else:
                exec(setup)
                to_benchmark[cmd].append(1000*eval(f'g3_sql_bench(df, X, Y, n_repeats={N_REPEATS})'))
    yaxis_name=f"Average time on {str(N_REPEATS)} runs (ms)"
    return to_benchmark, labels, yaxis_name

def approx_test(dataset_name, frac_samples, cons=False):
    to_benchmark, labels = init.gen_sampling_benchmark()
    for f in tqdm.tqdm(frac_samples):
        setup=gen_setup(dataset_name, f, cons)
        exec(setup)
        true_g3=eval('g3crisp.g3_hash(df, X, Y)')
        for cmd in to_benchmark:
            errors = []
            for _ in range(N_REPEATS):
                exec(setup)
                errors.append(abs(true_g3-eval(cmd)))
            to_benchmark[cmd].append(np.mean(errors))
    yaxis_name=f"Absolute error"# mean on {str(N_REPEATS)} runs"
    return to_benchmark, labels, yaxis_name

if __name__ == '__main__':
    for dataset_name in AVAILABLE_DATASETS:
        for side in [(False, 'ants')]:#, (True, 'cons')]:
            for test_name in ['time', 'approx']:
                script_name = inspect.stack()[0].filename.split('.')[0]
                file_path = './'+path.join(DILL_FOLDER, f'{script_name}_{test_name}_{side[1]}_{dataset_name}.d')
                if path.isfile(file_path): 
                    print(f'{file_path} found! Skipping...')
                    continue
                else:
                    print(f'{file_path} in progress...')
                max_attrs = MAX_ATTRS_DATASETS[dataset_name]
                step=round(max_attrs/N_STEPS)
                if step<1: step=1
                n_attrs = list(range(step, max_attrs, step))
                if test_name=='time':
                    to_benchmark, labels, yaxis_name = time_test(dataset_name, n_attrs, side[0])
                else:
                    to_benchmark, labels, yaxis_name = approx_test(dataset_name, n_attrs, side[1])
                xaxis_name="Number of antecedents"
                if side[0]: xaxis_name="Number of consequents"
                fig, ax  = plot_bench(to_benchmark, 
                    n_attrs, 
                    labels, 
                    xlabel=xaxis_name, 
                    ylabel=yaxis_name,
                    logy=False,
                    savefig=False
                )
                ax.set_xticks(n_attrs)
                dill.dump((fig), open(file_path, "wb"))