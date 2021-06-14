# Test different known values of g3
import timeit
import tqdm
from os import path
import numpy as np
import dill

import init
import fastg3.crisp as g3crisp
from plot_utils import plot_bench
from constants import N_REPEATS, N_STEPS, DILL_FOLDER

SYN_N_TUPLES=1000000
N_REPEATS=1

def gen_setup(variable='g3', value=0.5):
    if variable=='g3':
        suffix=f'df, X, Y = load_syn(n_tuples={SYN_N_TUPLES}, target_g3={str(value)})'
    elif variable=='nec': # Number of equivalence classes
        suffix=f'df, X, Y = load_syn(n_tuples={SYN_N_TUPLES}, n_groups={str(value)})'
    elif variable=='pdiff': # Proportion of different consequent values in each equivalence class
        suffix=f'df, X, Y = load_syn(n_tuples={SYN_N_TUPLES}, percent_classes_per_group={str(value)})'
    prefix=f'''
import init
import fastg3.crisp as g3crisp
from sql_utils import g3_sql_bench
from dataset_utils import load_syn
'''
    return prefix + suffix

def time_test(variable_parameter, parameter_values):
    to_benchmark, labels = init.gen_time_benchmark()
    for p in tqdm.tqdm(parameter_values):
        setup=gen_setup(variable=variable_parameter, value=p)
        for cmd in to_benchmark:
            if cmd != 'G3_SQL':
                duration_mean = timeit.timeit(cmd, setup=setup, number=N_REPEATS)/N_REPEATS*1000
                to_benchmark[cmd].append(duration_mean)
            else:
                exec(setup)
                to_benchmark[cmd].append(1000*eval(f'g3_sql_bench(df, X, Y, n_repeats={N_REPEATS})'))
    yaxis_name=f"Average time on {str(N_REPEATS)} runs (ms)"
    return to_benchmark, labels, yaxis_name

def approx_test(variable_parameter, parameter_values):
    to_benchmark, labels = init.gen_sampling_benchmark()
    for p in tqdm.tqdm(parameter_values):
        setup=gen_setup(variable=variable_parameter, value=p)
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

MAX_NEC = 5000
NEC_STEP = round(MAX_NEC/N_STEPS)
PDIFF_STEP = 1/N_STEPS
variables_settings = {
    'g3':{
        'range': list(np.arange(0,1,1/N_STEPS)),
        'xlabel': f"Known $g_3$ value"
    },
    'nec':{
        'range': list(range(NEC_STEP,MAX_NEC+NEC_STEP,NEC_STEP)),
        'xlabel': f"Number of equivalence classes"
    },
    'pdiff':{
        'range': list(np.arange(0,1+PDIFF_STEP,PDIFF_STEP)),
        'xlabel': f"Percentage of unique consequents in each equivalence class"
    }
}

if __name__ == '__main__':
    for variable_parameter in ['g3', 'nec', 'pdiff']:
        for test_name in ['approx']:#['time', 'approx']:
            file_path = './'+path.join(DILL_FOLDER, f'syn_{variable_parameter}_{test_name}.d')
            if path.isfile(file_path): 
                print(f'{file_path} found! Skipping...')
                continue
            else:
                print(f'{file_path} in progress...')
            param_range = variables_settings[variable_parameter]['range']
            if test_name=='time':
                to_benchmark, labels, yaxis_name = time_test(variable_parameter, param_range)
            else:
                to_benchmark, labels, yaxis_name = approx_test(variable_parameter, param_range)
            fig, ax  = plot_bench(
                to_benchmark, 
                param_range, 
                labels, 
                xlabel=variables_settings[variable_parameter]['xlabel'], 
                ylabel=yaxis_name,
                logy=False,
                savefig=False
            )
            dill.dump((fig), open(file_path, "wb"))