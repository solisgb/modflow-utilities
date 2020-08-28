# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:48:59 2020

@author: solis

it plot heads from modflow 6 binary files .bhd

if the model has a regular grid you must use plot_heads_sg: in this case you
    must supply a list with rows and columns to be plotted
else you must pass a list with the cell numbers

if each case you must pass the .bhd file path and the directory where the
    plots (.png files) will be saved

Both functions have optional arguments: look at function definition in m6
    module
"""
import littleLogging as logging

org = r'H:\modflow\course\Session_2\Exercise_2\myEx2\myEx2_transient.bhd'
rows_cols = [[10,4], [10,9]]
cells = (28, 3719)
dir_out = r'H:\modflow\course\Session_2\Exercise_2\myEx2\xy'

if __name__ == "__main__":

    try:
        from datetime import datetime
        from time import time
        import traceback
        import m6

        now = datetime.now()

        startTime = time()

        m6.plot_heads_sg(org, rows_cols, dir_out)

#        m6.plot_heads_ug(org, cells, dir_out)

        xtime = time() - startTime
        msg = f'El script tardó {xtime:0.1f} s'

    except ValueError:
        msg = traceback.format_exc()
        logging.append(f'ValueError exception\n{msg}')
    except ImportError:
        msg = traceback.format_exc()
        logging.append(f'ImportError exception\n{msg}')
    except Exception:
        msg = traceback.format_exc()
        logging.append(f'Exception\n{msg}')
    finally:
        logging.dump()
        print(f'{msg}')
