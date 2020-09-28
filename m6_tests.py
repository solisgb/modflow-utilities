# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 10:13:50 2020

@author: solis
"""

def all_tests():
    test01()
    test02()
    test03()


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


def test02(disv_file: str):
    """
    gets top model and bottom layers heights
    """
    import disv6
    print('gets layer definition ')
    grd = disv6.DISV(disv_file)
    hs, idomain = grd.get_layer_definition()
    print('test02 ok')


def test03(disv_file: str):
    """
    gets vertices coordinates and cells centroids & vertices
    """
    import disv6

    print('gets vertices coordinates and cells centroids & vertices')
    grd = disv6.DISV(disv_file)
    centroids, cell_verts = grd.read_cells()

    print('test03 ok')
