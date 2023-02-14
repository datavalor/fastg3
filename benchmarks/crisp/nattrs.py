import time
import timeit
import tqdm
import numpy as np

import init
from constants import N_REPEATS, N_STEPS, RES_FOLDER
from dataset_utils import AVAILABLE_DATASETS, MAX_ATTRS_DATASETS, load_dataset
from bench_utils import gen_file_infos, gen_result_df, save_result

from sql_utils import sql_available
print(f'SQL available: {sql_available}')

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
    y_label=f"Average time on {str(N_REPEATS)} runs (ms)"
    return to_benchmark, labels, y_label

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
    y_label='Absolute error'
    return to_benchmark, labels, y_label

if __name__ == '__main__':
    print(f'Available datasets: {AVAILABLE_DATASETS}')
    for dataset_name in AVAILABLE_DATASETS:
        for side in [(False, 'ants')]:#, (True, 'cons')]:
            for test_name in ['time', 'approx']:
                print(f'Current test: {dataset_name}, {test_name}')

                # handle file
                file_path, folder, exists = gen_file_infos(test_name, dataset_name, RES_FOLDER)
                if exists: continue

                # execute tests
                start = time.time()
                max_attrs = MAX_ATTRS_DATASETS[dataset_name]
                step=round(max_attrs/N_STEPS)
                if step<1: step=1
                n_attrs = list(range(step, max_attrs, step))
                if test_name=='time':
                    benchmark_res, y_legends, y_label = time_test(dataset_name, n_attrs, side[0])
                else:
                    benchmark_res, y_legends, y_label = approx_test(dataset_name, n_attrs, side[1])
                bench_duration = time.time()-start

                # create df from results
                res_df = gen_result_df(n_attrs, benchmark_res, y_legends)
        
                # save results
                x_label="Number of consequents" if side[0] else "Number of antecedents"
                save_result(
                    res_df, 
                    x_label,
                    y_label,
                    bench_duration,
                    folder,
                    file_path
                )