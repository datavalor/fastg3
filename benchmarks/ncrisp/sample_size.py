import time
import tqdm
from os import path
import inspect
import numpy as np

import init
from constants import N_REPEATS, N_STEPS, RES_FOLDER
from dataset_utils import AVAILABLE_DATASETS, load_dataset
from bench_utils import gen_file_infos, gen_result_df, save_result


SELECTED_DATASETS = AVAILABLE_DATASETS.copy()
SELECTED_DATASETS.remove('syn')

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
    for dataset_name in SELECTED_DATASETS:
        print(f'Current test: {dataset_name}')

        # handle file
        file_path, exists = gen_file_infos('approx', dataset_name, RES_FOLDER)
        if exists: continue

        # execute tests
        start = time.time()
        exec(gen_setup(dataset_name, 1, footer=True))
        dataset_size = eval('len(df.index)')

        true_g3 = eval('rg3.exact(method="wgyc")')
        print(f"{dataset_name}: {dataset_size} tuples, g3={dataset_name}")
        if dataset_size>100000:
            dataset_size=100000
        step=round(dataset_size/N_STEPS)
        sample_sizes=range(step, dataset_size+step, step)
        benchmark_res, y_legends = gen_to_benchmark()
        for ss in tqdm.tqdm(sample_sizes):
            for cmd in benchmark_res:
                cmd_modified = cmd.replace(STRING_TO_REPLACE, str(ss))
                exec(gen_setup(dataset_name, precompute=False))
                benchmark_res[cmd].append(eval(cmd_modified)/true_g3)
        bench_duration = time.time()-start

        # create df from results
        res_df = gen_result_df(sample_sizes, benchmark_res, y_legends)

        # save results
        save_result(
            res_df, 
            'Number of sampled tuples',
            'Relative error',
            bench_duration,
            file_path
        )