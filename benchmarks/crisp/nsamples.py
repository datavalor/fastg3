import time
import tqdm
import numpy as np

import init
from constants import N_REPEATS, N_STEPS, RES_FOLDER
from dataset_utils import AVAILABLE_DATASETS
from bench_utils import gen_file_infos, gen_result_df, save_result

STRING_TO_REPLACE='g3frvr'

def gen_setup(dataset_name):
    return f'''
import init
import fastg3.crisp as g3crisp
from dataset_utils import load_dataset

df, X, Y = load_dataset('{dataset_name}')
'''

def gen_to_benchmark():
    to_benchmark = {
        f"g3crisp.g3_srsi(df, X, Y, t={STRING_TO_REPLACE})":[],
        f"g3crisp.g3_srs(df, X, Y, t={STRING_TO_REPLACE})":[],
        f"g3crisp.g3_urs(df, X, Y, m={STRING_TO_REPLACE})":[],
    }
    labels = [
        'G3_SRSI',
        'G3_SRS',
        'G3_URS',
    ]
    return to_benchmark, labels

if __name__ == '__main__':
    for dataset_name in AVAILABLE_DATASETS:
        print(f'Current test: {dataset_name}')

        # handle file
        file_path, exists = gen_file_infos('approx', dataset_name, RES_FOLDER)
        if exists: continue

        # execute tests
        start = time.time()
        exec(gen_setup(dataset_name))
        dataset_n_tuples = eval('len(df.index)')
        true_g3 = eval('g3crisp.g3_hash(df, X, Y)')
        step=round(dataset_n_tuples/N_STEPS)
        sample_sizes=range(step, dataset_n_tuples+step, step)
        benchmark_res, y_legends = gen_to_benchmark()
        for ss in tqdm.tqdm(sample_sizes):
            for cmd in benchmark_res:
                errors = []
                for _ in range(N_REPEATS):
                    cmd_modified = cmd.replace(STRING_TO_REPLACE, str(ss))
                    exec(gen_setup(dataset_name))
                    errors.append(abs(true_g3-eval(cmd_modified)))
                benchmark_res[cmd].append(np.mean(errors))
        bench_duration = time.time()-start

        # create df from results
        res_df = gen_result_df(sample_sizes, benchmark_res, y_legends)

        # save results
        save_result(
            res_df, 
            'Number of sampled tuples',
            'Absolute error',
            bench_duration,
            file_path
        )