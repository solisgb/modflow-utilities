# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:48:59 2020

@author: solis

plot_heads uses optional arguments
    look the function definition

"""
import littleLogging as logging

org = r'H:\modflow\exercises\session02\ex2\ex2_2.bhd'
layer_row_col = [[0,4,4], [0,5,5]]
ylabel = 'CNP m s.n.m.'
dir_out = r'H:\modflow\exercises\session02\ex2\xy'


if __name__ == "__main__":

    try:
        from datetime import datetime
        from time import time
        import traceback
        import m6

        now = datetime.now()

        startTime = time()

        m6.plot_heads(org, layer_row_col, ylabel, dir_out=dir_out)

        xtime = time() - startTime
        print(f'El script tardó {xtime:0.1f} s')

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
        print('\nFin')
