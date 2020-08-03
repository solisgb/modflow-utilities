# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:49:25 2020

@author: solis
"""
import numpy as np


def plot_heads(org, lrc: list, ylabel: str, **kwargs):
    """
    https://modflowpy.github.io/flopydoc/binaryfile.html
    optional arguments
        date0: a str date representation as yyyy-mm-dd (it's not used yet)
        dir_out: directory where png plots will be saved. If nor present
            plot is shown in the screen
    """
    import flopy.utils.binaryfile as bf

    fi = bf.HeadFile(org)
    # Get a list of unique stress periods and time steps in the file
    kstpkper = fi.get_kstpkper()
    print('stress periods and time steps')
    print(kstpkper)

    hds = fi.get_ts(lrc)
    fi.close()
    for i in range(len(lrc)):
        title = f'layer {lrc[i][0]:n}, row {lrc[i][1]:n}, col {lrc[i][2]:n}'
        if 'dir_out' in kwargs:
            kwargs['name_file'] = \
            f'l{lrc[i][0]:n}_r{lrc[i][1]:n}_c{lrc[i][2]:n}'
        print(title)

        if 'date0' not in kwargs:
            x = np.array([i for i in range(hds.shape[0])], np.float32)
            ycol = i + 1
            xy_plot_1g(title, x, hds[:, ycol], ylabel, kwargs)
        else:
            break


def xy_plot_1g(title: str, x: list, y: list, ylabel: str, kwargs: dict):
    """
    Dibuja una figura con 1 gráfico (axis) xy
    args
    title: título de la figura
    x: lista de objetos date
    y: lista de valores interpolados float
    dst: nombre fichero destino (debe incluir la extensión png)
    """
    from datetime import date
    from os.path import join
    import warnings
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    # parámetros específicos
    warnings.simplefilter(action='ignore', category=FutureWarning)
    mpl.rc('font', size=8)
    mpl.rc('axes', labelsize=8, titlesize= 10, grid=True)
    mpl.rc('axes.spines', right=False, top=False)
    mpl.rc('xtick', direction='out', top=False)
    mpl.rc('ytick', direction='out', right=False)
    mpl.rc('lines', linewidth=0.8, linestyle='-', marker='.', markersize=4)
    mpl.rc('legend', fontsize=8, framealpha=0.5, loc='best')

    fig, ax = plt.subplots()

    plt.suptitle(title)
    ax.set_ylabel(ylabel)

    if isinstance(x[0], date):
        fig.autofmt_xdate()

    ax.plot(x, y)

    if 'dir_out' not in kwargs:
        plt.show()
    else:
        fig.savefig(join(kwargs['dir_out'], kwargs['name_file']))

    plt.close('all')
    plt.rcdefaults()
