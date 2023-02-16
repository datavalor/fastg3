import os
import inspect
import platform
import datetime
from pathlib import Path
import pandas as pd
from os import path

def gen_file_infos(test_name, dataset_name, result_folder):
    script_name = inspect.stack()[1].filename.split('.')[0].split('/')[-1]
    file_name = f'{script_name}_{test_name}_{dataset_name}.csv'
    folder = path.join('./', result_folder, test_name+'/')
    file_path = path.join(folder, file_name)
    exists = True if path.isfile(file_path) else False

    return file_path, exists

def gen_result_df(x_data, benchmark_res, y_legends):
    res_data = { 'x': x_data }
    for i, d in enumerate(benchmark_res):
        res_data[f'y_{y_legends[i]}'] = benchmark_res[d]
    return pd.DataFrame(res_data)

def save_result(df,  x_label, y_label, bench_duration, file_path, log=False):
    folder = os.path.dirname(file_path) 
    Path(folder).mkdir(parents=True, exist_ok=True)
    f = open(file_path, "a")
    f.write(f'#date,{datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")}\n')
    f.write(f'#host,{platform.node()}\n')
    f.write(f'#benchmark_duration,{round(bench_duration,2)}s\n')
    f.write(f'#x_label,{x_label}\n')
    f.write(f'#y_label,{y_label}\n')
    if log: f.write(f'#log,1\n')
    else: f.write(f'#log,0\n')
    # f.write(f'#dataset_size,{dataset_size}\n')
    df.to_csv(f, index=False)
    f.close()