# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:48:59 2020

@author: solis

plot_heads uses optional arguments
    look the function definition

"""
import littleLogging as logging

org = r'H:\modflow\exercises\session04\ex1\ex1_1.bhd'
layer_row_col = [[0,7,16], [0,34,7]]
ylabel = 'MASL'
dir_out = r'H:\modflow\exercises\session04\ex1\xy_1'


if __name__ == "__main__":

    try:
        from datetime import datetime
        from time import time
        import traceback
        import m6

        now = datetime.now()

        startTime = time()

        m6.plot_heads(org, layer_row_col, ylabel, xlabel='stress period',
                      dir_out=dir_out, time_steps=False)

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
