import os
import numpy as np
import pandas as pd
from itertools import takewhile
from pathlib import Path
# from matplotlib2tikz import matplotlib2tikz

import matplotlib
import matplotlib.pyplot as plt
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'text.usetex': True,
    'text.latex.preamble': r'\usepackage[libertine,cmintegrals,cmbraces,vvarbb]{newtxmath}'
})
# sudo apt-get install dvipng texlive-latex-extra texlive-fonts-recommended cm-super texlive-fonts-extra

# from utils.constants import RES_FOLDER
MARKERSIZE = 3
LINEWIDTH = 1
THEME = {
    'G3_MEMOPT': {'label': 'g3_memopt', 'color': 'k', 'marker': '', 'dash': (None,None)},
    'G3_TIMEOPT': {'label': 'g3_timeopt', 'color': 'k', 'marker': '', 'dash': [1,1]},
    'G3_SRSI': {'label': 'g3_srsi', 'color': 'k', 'marker': '', 'dash': [3,1]},
    'G3_SRS': {'label': 'g3_srs', 'color': 'k', 'marker': 'o', 'dash': [1,1]},
    'G3_URS': {'label': 'g3_urs', 'color': 'k', 'marker': '', 'dash': [4,1,1,1]},
}

import sys
sys.path.insert(1, './utils/')
from number_utils import format_number

def human_format(num, pos):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return f'{num:.1f}'.rstrip('0').rstrip('.') + ['', 'K', 'M', 'G', 'T', 'P'][magnitude]

csv_files = []
for root, dirs, files in os.walk("./crisp"):
    for file in files:
        if file.endswith(".csv"):
             csv_files.append(os.path.join(root, file))

if __name__ == "__main__":
    # print(csv_files)
    for csv_path in csv_files:
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
            algo_name = '_'.join(column.split('_')[1:])
            y = df[column]
            tmp_min, tmp_max = y.min(), y.max()
            if tmp_min < min_y: min_y = tmp_min
            if tmp_max > max_y: max_y = tmp_max
            theme = THEME[algo_name]
            ax.plot(
                x, df[column],
                label='\\textsc{'+theme['label']+'}',
                color=theme['color'],
                marker=theme['marker'],
                markersize=MARKERSIZE,
                linewidth=LINEWIDTH,
                dashes=theme['dash']
                # color='black', alpha=1, s=25, zorder=99
            )
            ax.xaxis.set_major_formatter(human_format)
            # if 'error' in metadata['y_label']: 
            #     def perc_format(num, pos):
            #         # print(f'{num*100:.0f}'+'%')
            #         return f'{num*100:.0f}'+'%'
            #     ax.yaxis.set_major_formatter(perc_format)

        plt.legend(frameon=False)
        ax.spines['left'].set_bounds(min_y, max_y)
            

        fig.set_size_inches(4.5, 3.5)

        plt.savefig(svg_path, bbox_inches='tight') 


