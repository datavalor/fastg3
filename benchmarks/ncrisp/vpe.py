import timeit
from pydataset import data
import tqdm
from os import path
import inspect
import numpy as np
import dill

import init
from plot_utils import plot_bench
from number_utils import format_number
from constants import N_REPEATS, N_STEPS, DILL_FOLDER
from dataset_utils import AVAILABLE_DATASETS, load_dataset

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
    for dataset_name in ['diamonds', 'hydroturbine']:
        if dataset_name=='hydroturbine':
            labels = ["All optimisations"]
            to_benchmark = {
                (True, "ordered", True):[]
            }
        else:
            to_benchmark = {
                (False, "brute_force", False):[],
                (False, "brute_force", True):[],
                (True, "brute_force", False):[],
                (False, "ordered", False):[],
                (True, "ordered", True):[],
            }
            labels = [
                "VPE_BF (no optimisation)",
                "VPE_COMPOPT",
                "VPE_BLOCKOPT",
                "VPE_ORDEROPT",
                "All optimisations",
            ]
        script_name = inspect.stack()[0].filename.split('.')[0]
        file_path = './'+path.join(DILL_FOLDER, f'{script_name}_{dataset_name}.d')
        if path.isfile(file_path): 
            print(f'{file_path} found! Skipping...')
            continue
        else:
            print(f'{file_path} in progress...')
        for f in tqdm.tqdm(frac_samples):
            for cmd in to_benchmark:
                s=gen_setup(dataset_name, f, blocking=cmd[0], join_type=cmd[1], opti_ordering=cmd[2])
                duration_mean = timeit.timeit("VPE.enum_vps()", setup=s, number=N_REPEATS)/N_REPEATS*1000
                to_benchmark[cmd].append(duration_mean)
        fig, ax = plot_bench(
            to_benchmark, 
            frac_samples, 
            labels, 
            xlabel="Number of tuples", 
            ylabel=f"Average time on {str(N_REPEATS)} runs (ms)",
            savefig=False
        )
        exec(gen_setup(dataset_name, 1, footer=False))
        dataset_size = eval('len(df.index)')
        ax.xaxis.set_major_formatter(lambda x, pos: format_number(x*dataset_size))
        dill.dump((fig, {'dataset_size':dataset_size}), open(file_path, "wb"))