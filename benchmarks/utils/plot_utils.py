# Plotting
import seaborn
import matplotlib.pyplot as plt
plt.style.use('default')
seaborn.set_palette('gray')

import inspect
from init import COLORMAP

from constants import MARKERSIZE

def plot_bench(
    data_dict, 
    xlabels, 
    labels, 
    xlabel="", 
    ylabel="", 
    logy=False, 
    savefig=False
):
    fig, ax = plt.subplots()

    for i, d in enumerate(data_dict):
        ax.plot(xlabels, data_dict[d], marker='o', label=labels[i])

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    setFigLinesBW(fig)

    if logy: ax.set_yscale('log')
    plt.legend(frameon=False, loc='best', handlelength=4)
    seaborn.despine(bottom=True)
    fig.tight_layout()
    if savefig:
        plt.savefig(f"./{inspect.stack()[1].filename.split('.')[0]}.png", bbox_inches='tight')
    return fig, ax

def setAxLinesBW(ax):
    """
    Take each Line2D in the axes, ax, and convert the line style to be 
    suitable for black and white viewing.
    """
    lines_to_adjust = ax.get_lines()
    try:
        lines_to_adjust += ax.get_legend().get_lines()
    except AttributeError:
        pass

    for i, line in enumerate(lines_to_adjust[::-1]):
        line.set_color('black')
        line.set_dashes(COLORMAP[i]['dash'])
        line.set_marker(COLORMAP[i]['marker'])
        line.set_markersize(MARKERSIZE)

def setFigLinesBW(fig):
    """
    Take each axes in the figure, and for each line in the axes, make the
    line viewable in black and white.
    """
    for ax in fig.get_axes():
        setAxLinesBW(ax)