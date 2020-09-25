# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 10:13:50 2020

@author: solis
"""

def all_tests():
    test01()
    test02()


def test01():
    """
    plots xy heads using a structured or disv grid
    """
    import m6

    org = r'H:\modflow\exam1\v01\v01.bhd'
    rows_cols = [[10,4], [10,9]]
    cells = (2834, 9935, 9984)
    dir_out = r'H:\modflow\exam1\v01\xy'

    print('xy heads in selected cells of a structured grid')
    m6.plot_heads_sg(org, rows_cols, dir_out)

    print('xy heads cells in selected cells of a disv grid')
    m6.plot_heads_ug(org, cells, dir_out)

    print('test01 ok')


def test02():
    """
    gets top model and bottom layers heights
    """
    import disv6
    org = r'H:\off\chs\m6_cc_chunk_03\v03\qcc_v03.disv'

    print('get layer definition ')
    disv = disv6.DISV(org)
    layer_def = disv.get_layer_definition()

    print('test02 ok')
