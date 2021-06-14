import tqdm
import matplotlib.pyplot as plt
from os import path
import inspect
import numpy as np
import dill

import init
import fastg3.crisp as g3crisp
from number_utils import format_number
from plot_utils import plot_bench
from constants import N_REPEATS, N_STEPS, DILL_FOLDER
from dataset_utils import AVAILABLE_DATASETS, load_dataset

STRING_TO_REPLACE='g3frvr'

def gen_setup(dataset_name, f=1, footer=True, precompute=True):
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
rg3 = g3ncrisp.RSolver(VPE, precompute="{str(precompute)}")
''' 
    if footer: return header_str+footer_str
    else: return header_str

def gen_to_benchmark():
    to_benchmark = {
        f'g3ncrisp.Yoshida2009(g3ncrisp.VPEGraph(VPE)).estimate_mvc_size({STRING_TO_REPLACE})':[],
        f'g3ncrisp.Onak2011(g3ncrisp.VPEGraph(VPE)).estimate_mvc_size({STRING_TO_REPLACE})':[]
    }
    labels = [
        'NCG3_SUB09',
        'NCG3_SUB11',
    ]
    return to_benchmark, labels

if __name__ == '__main__':
    for dataset_name in ['diamonds', 'hydroturbine']:
        script_name = inspect.stack()[0].filename.split('.')[0]
        file_path = './'+path.join(DILL_FOLDER, f'{script_name}_{dataset_name}.d')
        if path.isfile(file_path): 
            print(f'{file_path} found! Skipping...')
            continue
        else:
            print(f'{file_path} in progress...')
        exec(gen_setup(dataset_name, 1, footer=True))
        dataset_size = eval('len(df.index)')

        true_g3 = eval('rg3.exact(method="wgyc")')
        print(f"{dataset_name}: {dataset_size} tuples, g3={dataset_name}")
        if dataset_size>100000:
            dataset_size=100000
        step=round(dataset_size/N_STEPS)
        sample_sizes=range(step, dataset_size+step, step)
        to_benchmark, labels = gen_to_benchmark()
        for ss in tqdm.tqdm(sample_sizes):
            for cmd in to_benchmark:
                cmd_modified = cmd.replace(STRING_TO_REPLACE, str(ss))
                exec(gen_setup(dataset_name, precompute=False))
                to_benchmark[cmd].append(eval(cmd_modified)/true_g3)

        fig, ax = plot_bench(
            to_benchmark,
            sample_sizes, 
            labels, 
            xlabel="Number of sampled tuples", 
            ylabel=f"Relative error",# mean on {str(N_REPEATS)} runs",
            savefig=False
        )
        ax.xaxis.set_major_formatter(lambda x, pos: format_number(x*dataset_size))
        dill.dump((fig, {'dataset_size':dataset_size}), open(file_path, "wb"))