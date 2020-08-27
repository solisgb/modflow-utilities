# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:49:25 2020

@author: solis

module uses flopy extensively
https://modflowpy.github.io/flopydoc
"""
import numpy as np


def plot_heads(org, lrc: list, ylabel: str, **kwargs):
    """
    This function as candidate to be refactored

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


def plot_heads_ug(org: str, cells: tuple, dir_out: str, **kwargs):
    """
    Unstructured grid
    Function plots heads. Heads are read from a bhd file in a unstructured grid
    args:
        org: bhd file
        cells: list o cells to be plotted
        dir_out str: directory where png plots will be saved. If not present
            plot is shown in the screen
        xlabel str: label in x axis -xlabel-
    optional args
        layers tuple: list of layers to be plotted; is not present all layers
            will bel plotted
    """
    from os.path import join

    if 'ylabel' in kwargs:
        ylabel = kwargs['ylabel']
    else:
        ylabel = 'm asl'

    icells = [item-1 for item in cells]
    hds = get_heads_ug(org, icells, **kwargs)
    x = np.array([i for i in range(hds.shape[2])], np.float32)
    if 'layers' in kwargs:
        ilayers = [item-1 for item in kwargs['layers']]
    else:
        ilayers = hds.shape[0]
    for i in icells:
        for j in ilayers:
            title = f'Head in cell {i}, layer {j}'
            dst = join(dir_out, f'hd_cell_{i:n}_ly_{j:n}.png')
            y = hds[i, j, :]
            xy_plot_1g(title, x, y, ylabel, dst, kwargs)


def get_disv_dimension(org):
    """
    it returns grid dimension as a tuple with 3 items by reading disv file:
        nlay: layers number
        ncpl: cell per layer number
        nvert: vertex number
    """
    import os.path

    ext = os.path.splitext(org)[1]
    if ext.lower() != '.disv':
        raise ValueError('org must have disv extension')

    i = 0
    kwords = ('NLAY', 'NCPL', 'NVERT')
    disvd = []
    fi = open(org)
    for line in fi:
        if kwords[i] in line:
            disvd.append(int(line.split()[1]))
            if len(disvd) == 3:
                return tuple(disvd)
            i += 1
    raise ValueError(f'missed key words in {org}')


def get_heads_ug(org: str, cells: list, **kwargs):
    """
    it returns a np.array with the heads in the last time_step of each stress
        period for cells in cells. The heads are read from org, that is a file
        with .bhd extension.
    """
    import flopy.utils.binaryfile as bf

    fi = bf.HeadFile(org)
    ts_sp = get_last_ts_sp(fi, **kwargs)

    for i, item in enumerate(ts_sp):
        hds = fi.get_data(kstpkper=item)
        if i == 0:
            nlays = hds.shape[0]
            hd_ts = np.array((len(cells), nlays, len(ts_sp)), np.float32)

        for j in cells:
            for ilay in range(nlays):
                hd_ts[j, ilay, i] = ts_sp[j, ilay, item[1]]


def get_last_ts_sp(fi, **kwargs):
    """
    it returns stress periods and their las time step
    args
    bi: object heads binary file
    """
    import sqlite3

    create_db = \
    'create table t1 (time_step integer, stress_period integer, ' +\
    'primary key (time_step, stress_period) )'
    insert = \
    'insert into t1 (time_step, stress_period) values (?, ?)'
    select1 = 'select distinct stress_period from t1 order by stress_period'
    select2 = 'select max(time_step) from t1 where stress_period=?'

    con = sqlite3.connect(':memory:')
    cur = con.cursor()

    ts_sp = fi.get_kstpkper()  # time steps & stress periods

    if 'time_steps' not in kwargs or \
    'time_steps' in kwargs and not kwargs['time_steps']:
        cur.execute(create_db)

        for i, item in enumerate(ts_sp):
            cur.execute(insert, (int(item[0]), int(item[1])))
        cur.execute(select1)
        stress_periods = [ row[0] for row in cur.fetchall()]
        tsl_sp = []
        for stress_period in stress_periods:
            cur.execute(select2, (stress_period,))
            row = cur.fetchone()
            tsl_sp.append((row[0], row[1]))
        return tuple(tsl_sp)
    else:
        return ts_sp


def xy_plot_1g(title: str, x: list, y: list, ylabel: str, dst: str,
               kwargs: dict):
    """
    plot a png file
    args
        title: figure title
        x: list of stress periods
        y: list of heads
        ylabel: y axis label
        dst: output file name
    optional args
        xlabel: x axis label, default str 'stress periods'
        to_screen: figures are show in the screen, default bool False
    returns
        None
    """
    from datetime import date
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

    if 'to_screen' in kwargs and  kwargs['to_screen']:
        plt.show()

    fig.savefig(dst)

    plt.close('all')
    plt.rcdefaults()
