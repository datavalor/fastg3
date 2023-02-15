import os
import numpy as np
import pandas as pd
from itertools import takewhile
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'serif'

# from utils.constants import RES_FOLDER

import sys
sys.path.insert(1, './utils/')
from number_utils import format_number

csv_files = []
for root, dirs, files in os.walk("./crisp"):
    for file in files:
        if file.endswith(".csv"):
             csv_files.append(os.path.join(root, file))

if __name__ == "__main__":
    # print(csv_files)
    for csv_path in [csv_files[0]]:
        # converts to svg path
        svg_path = csv_path.replace("csv", "svg")
        svg_path = svg_path[:-3]
        svg_path += "svg"

        # creates folder if does not exists
        svg_folder = os.path.dirname(svg_path) 
        Path(svg_folder).mkdir(parents=True, exist_ok=True)

        # reading csv
        df=pd.read_csv(csv_path, comment='#')
        
        # getting metadata
        header = []
        with open(csv_path, 'r') as fobj:
            headiter = takewhile(lambda s: s.startswith('#'), fobj)
            header = list(headiter)
        metadata = {}
        for meta in header:
            clean_head = meta.replace('#','').replace('\n','').split(',')
            metadata[clean_head[0]] = clean_head[1:] if len(clean_head) > 2 else clean_head[1]

        fig, ax = plt.subplots()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set(xlabel=metadata['x_label'])
        ax.set(ylabel=metadata['y_label'])

        print(df.columns)
        x = df['x']
        df = df.drop(columns=['x'])
        min_y, max_y = np.inf, -np.inf
        for column in df.columns:
            y = df[column]
            tmp_min, tmp_max = y.min(), y.max()
            if tmp_min < min_y: min_y = tmp_min
            if tmp_max > max_y: max_y = tmp_max
            ax.scatter(
                x, df[column],
                color='black', alpha=1, s=25, zorder=99
            )
        ax.spines['left'].set_bounds(min_y, max_y)
            

        fig.set_size_inches(5, 4)

        plt.savefig(svg_path, bbox_inches='tight') 


