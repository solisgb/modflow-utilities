# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:49:25 2020

@author: solis
"""
import numpy as np


def plot_heads(org, lrc: list, ylabel: str, **kwargs):
    """
    it plots heads from bhd modflow 6 ourput files; heads can be plotted
        with stress periods or time steps in x axis
    now only structured grids can be used but unstructured grids will be
        addedd soon
    to read bhs fiel ir uses flopy

    https://modflowpy.github.io/flopydoc/binaryfile.html
    optional arguments
        date0 str: a str date representation as yyyy-mm-dd (it's not used yet)
        dir_out str: directory where png plots will be saved. If nor present
            plot is shown in the screen
        xlabel str: label in x axis -xlabel-
        time_step bool: if present and is True time steps are represented
    """
    import sqlite3
    import flopy.utils.binaryfile as bf
    create_db = \
    'create table t1 (fid integer, time_step integer, stress_period integer, ' +\
    'primary key (fid, time_step, stress_period) )'
    insert = \
    'insert into t1 (fid, time_step, stress_period) values (?, ?, ?)'
    select1 = 'select distinct stress_period from t1 order by stress_period'
    select2 = 'select max(fid) from t1 where stress_period=?'

    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    fi = bf.HeadFile(org)
    if 'time_steps' not in kwargs or \
    'time_steps' in kwargs and not kwargs['time_steps']:
        cur.execute(create_db)
        # Get a list of unique stress periods and time steps in the file
        kstpkper = fi.get_kstpkper()
        for i, item in enumerate(kstpkper):
            cur.execute(insert, (int(i), int(item[0]), int(item[1])))
        cur.execute(select1)
        stress_periods = [ row[0] for row in cur.fetchall()]
        ii = []
        for stress_period in stress_periods:
            cur.execute(select2, (stress_period,))
            ii1 = cur.fetchone()
            ii.append(ii1[0])

    hds = fi.get_ts(lrc)
    fi.close()

    if 'time_steps' in kwargs and kwargs['time_steps']:
        x = hds[:, 0]
        suffix = '_ts'
    else:
        x = np.array([i for i in range(len(stress_periods))], np.float32)
        suffix = '_sp'
        y = np.empty((len(stress_periods)), np.float32)

    for i in range(len(lrc)):
        title = f'Head in layer {lrc[i][0]:n}, row {lrc[i][1]:n}, ' +\
        f'col {lrc[i][2]:n}'
        if 'dir_out' in kwargs:
            kwargs['name_file'] = \
            f'L{lrc[i][0]:n}_R{lrc[i][1]:n}_C{lrc[i][2]:n}' + suffix
        print(title)

        ycol = i + 1
        if 'time_steps' in kwargs and kwargs['time_steps']:
            y = hds[:, ycol]
        else:
            for j, ii1 in enumerate(ii):
                y[j] = hds[ii1, ycol]

        xy_plot_1g(title, x, y, ylabel, kwargs)
    con.close()


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
    if 'xlabel' in kwargs:
        ax.set_xlabel(kwargs['xlabel'])

    if isinstance(x[0], date):
        fig.autofmt_xdate()

    ax.plot(x, y)

    if 'dir_out' not in kwargs:
        plt.show()
    else:
        fig.savefig(join(kwargs['dir_out'], kwargs['name_file']))

    plt.close('all')
    plt.rcdefaults()
