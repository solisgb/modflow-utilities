# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:48:59 2020

@author: solis

the package has two modules

module m6 plot heads from modflow 6 binary files .bhd in structured or
    disv grids
    if the model has a structured grid you must use plot_heads_sg: in this case
        you must supply a list with rows and columns to be plotted
    else you must pass a list with the cell numbers
    if each case you must pass the .bhd file path and the directory where the
        plots (.png files) will be saved
    Both functions have optional arguments: look at function definition in m6
        module

module disv gets topo model & bottom layers heights from a disv file

module m6_tests has several tests:
    adjust file & directoriy names before running
"""
import littleLogging as logging


if __name__ == "__main__":

    try:
        from datetime import datetime
        from time import time
        import traceback
        import m6_tests as test

        now = datetime.now()

        startTime = time()

#        test.test01()

        test.test02()

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
