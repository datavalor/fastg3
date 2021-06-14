import tqdm
import matplotlib.pyplot as plt
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
        script_name = inspect.stack()[0].filename.split('.')[0]
        file_path = './'+path.join(DILL_FOLDER, f'{script_name}_{dataset_name}.d')
        if path.isfile(file_path): 
            print(f'{file_path} found! Skipping...')
            continue
        else:
            print(f'{file_path} in progress...')
        exec(gen_setup(dataset_name))
        dataset_n_tuples = eval('len(df.index)')
        true_g3 = eval('g3crisp.g3_hash(df, X, Y)')
        # print(dataset_name, dataset_n_tuples, exact_val)
        step=round(dataset_n_tuples/N_STEPS)
        sample_sizes=range(step, dataset_n_tuples+step, step)
        to_benchmark, labels = gen_to_benchmark()
        for ss in tqdm.tqdm(sample_sizes):
            for cmd in to_benchmark:
                errors = []
                for _ in range(N_REPEATS):
                    cmd_modified = cmd.replace(STRING_TO_REPLACE, str(ss))
                    exec(gen_setup(dataset_name))
                    errors.append(abs(true_g3-eval(cmd_modified)))
                to_benchmark[cmd].append(np.mean(errors))

        fig, ax = plot_bench(
            to_benchmark,
            sample_sizes, 
            labels, 
            xlabel="Number of sampled tuples", 
            ylabel=f"Absolute error",# mean on {str(N_REPEATS)} runs",
            savefig=False
        )
        ax.xaxis.set_major_formatter(lambda x, pos: format_number(x))
        dill.dump((fig), open(file_path, "wb"))