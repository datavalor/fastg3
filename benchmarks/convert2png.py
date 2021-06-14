import dill
import os
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, './utils/')
from number_utils import format_number

dill_files = []
for root, dirs, files in os.walk("./"):
    for file in files:
        if file.endswith(".d"):
             dill_files.append(os.path.join(root, file))

for f in dill_files:
    png_path = f.replace("dill", "graphs")
    png_path = png_path[:-1]
    png_path += "png"

    t = dill.load(open(f, "rb"))
    if isinstance(t,tuple):
        fig = t[0]
        if len(t)>1:
            params=t[1]
            for k in params:
                exec(f"{k}={params[k]}")
    else:
        fig = t
    fig.set_size_inches(5.4, 3.8)
    plt.gcf().set_dpi(300)
    if "vpe_diamonds" in f:
        ax = fig.axes[0]
        ax.set_yscale('log')
        # ax.legend(bbox_to_anchor=(0.1,0.5))
        # fig.tight_layout(pad=500)
        plt.subplots_adjust(left=0.1, top=0.8, bottom=0.11)
        ax.legend(frameon=False, loc='upper center', handlelength=4, ncol=2, bbox_to_anchor=(0.45, 1.3))
    if "nrows_time_hydroturbine" in f:
        ax = fig.axes[0]
        ax.set_yscale('log')
        # ax.legend(bbox_to_anchor=(0.1,0.5))
        # fig.tight_layout(pad=500)
        plt.subplots_adjust(left=0.1)
    fig.savefig(png_path)