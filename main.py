# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:48:59 2020

@author: solis

to plot_heads from modflow 6 binary files .bhd

if the model has a regular grid you can use plot_heads: in this case you
    must supply a list with rows and columns to be plotted
else you must pass a list with the cell numbers

if each case you must pass the .bhd file path and the directory where the
    plots (.png files) will be saved

Both functions have optional arguments: look at function definition in m6
    module
"""
import littleLogging as logging

org = r'H:\modflow\Exam2\v03\v03.bhd'
#layer_row_col = [[0,7,16], [0,34,7]]
cells = (28, 3719)
dir_out = r'H:\modflow\Exam2\v03\xy'

if __name__ == "__main__":

    try:
        from datetime import datetime
        from time import time
        import traceback
        import m6

        now = datetime.now()

        startTime = time()

#        m6.plot_heads(org, layer_row_col, ylabel, xlabel='stress period',
#                      dir_out=dir_out, time_steps=False)

        m6.plot_heads_ug(org, cells, dir_out)

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
