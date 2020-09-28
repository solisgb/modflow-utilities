# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 13:46:41 2020

@author: solis

read disv files
"""
import mmap
import numpy as np


class DISV():

    block_type = (b'CONSTANT', b'INTERNAL IPRN')


    def __init__(self, file: str):
        self.file = file


    def get_dimensions(self):
        """
        returns a dict with keys: NCPL -num. cell per layer-;
            NLAY -num layers; NVERT -num. vertex
        function can be improved; however items ared read at the begining
            of the file and the improvement will be small
        """
        start_block = b'BEGIN DIMENSIONS'
        n = len(start_block)
        end_block = b'END DIMENSIONS'
        with open(self.file, mode="r", encoding="utf-8") as file_obj:
            with mmap.mmap(file_obj.fileno(), length=0,
                           access=mmap.ACCESS_READ) as obj:
                x1 = obj.find(start_block)
                x2 = obj.find(end_block)
                a = obj[x1+n:x2].decode('utf-8').split()
        t = [(a[i], int(a[i+1])) for i in range(0, len(a), 2)]
        return dict(t)


    def get_layer_definition(self):
        """
        returns 2 arrays
            hs: heights of model top and layer bottoms, with shape = (n + 1, m)
                n is num layers; row 1 is model top, then layer bottoms
                m is num cells per layer
            idomain: active cell indicator (n, m)
        """
        dim = self.get_dimensions()
        hs = np.empty((dim['NLAY'] + 1, dim['NCPL']), np.float64)
        idomain = np.empty((dim['NLAY'], dim['NCPL']), np.int32)

        labels = ('BEGIN GRIDDATA', 'TOP', 'BOTM LAYERED', 'IDOMAIN')
        flags = (b'INTERNAL IPRN', b'CONSTANT', b'IDOMAIN', b'END GRIDDATA')
        with open(self.file, mode="r", encoding="utf-8") as fr:
            with mmap.mmap(fr.fileno(), length=0,
                           access=mmap.ACCESS_READ) as obj:

                nb1 = self.__find_label(obj, labels[0], posn=0)
                nb1 = self.__find_label(obj, labels[1], posn=nb1)
                nb1 = self.__move_start_next_line(obj, nb1)

                # reads model top
                line, nb1 = self.__read_line(obj, nb1)
                if b'CONSTANT' in line:
                    hs[0, :] = float(line.decode('utf-8').split()[-1])
                else:
                    nb2 = self.__find_label(obj, labels[2], nb1)
                    tmp = obj[nb1:nb2].decode('utf-8').split()
                    tmp = np.array(tmp, hs.dtype)
                    hs[0, :] = tmp

                # reads layer bottoms
                nb1 = self.__move_start_next_line(obj, nb2)
                nb1 = self.__read_data_chunk(dim['NLAY'], obj, nb1, hs, 1,
                                             flags)

                nb1 = self.__find_label(obj, labels[3], nb1)

                # reads cell status (0 inactive, 1 active)
                nb1 = self.__move_start_next_line(obj, nb1)
                nb1 = self.__read_data_chunk(dim['NLAY'], obj, nb1,
                                             idomain, 0, flags)

        return (hs, idomain)


    def __read_data_chunk(self, nlayers: int, obj, nb1: int, arr,
                          row_shift: int, flags: tuple):
        """
        reads  a data chunk from get_layer_definition method
        args:
            nlayers: model layers number
            obj: mmap objet pointing to a disv file
            nb1: byte in obj where the ponter is located
            arr: array to be filled
            row_shift: displacement of row index related to layer number
                if arr has the heights of model top and bottom layers, the
                heights of the first layer corresponds with the first row
                in arr, so layer bottom heights are located in ilayer + 1;
                in this case row_shit is equal to 1; other cases row_shit
                is equal to 0
            flags: labels that can signal the end of heights to be read for
                a layer
        """
        for ilay in range(nlayers):
            line, nb1 = self.__read_line(obj, nb1)
            if b'CONSTANT' in line:
                arr[ilay+row_shift, :] = \
                arr.fill(line.decode('utf-8').split()[1])
                nb1 = self.__move_start_prev_line(obj, nb1)
            else:
                nb2 = nb1
                while True:
                    line, nb2 = self.__read_line(obj, nb2)
                    if self.__any_item_in_line(flags, line):
                        nb2 = self.__move_start_prev_line(obj, nb2)
                        break
                tmp = obj[nb1:nb2].decode('utf-8').split()
                tmp = np.array(tmp, arr.dtype)
                arr[ilay+row_shift, :] = tmp
                nb1 = nb2
        return nb1


    def __find_label(self, obj, label, posn = None, move_cursor = True):
        """
        searches for label in obj and returns the position of in the
            first character of the label; if move_cursos is True moves the
            cursor to this position
        if label is not found raises a ValueError error
        """
        if posn is None:
            posn = obj.tell()
        x1 = obj.find(label.encode('utf-8'), posn)
        if x1 < 0:
            raise ValueError(f'No se ha encontrado {label}')
        if move_cursor:
            obj.seek(x1)
        return x1


    def __move_start_current_line(self, obj, posn = None):
        """
        moves to start of the current line
        returns the position of the beguining of the current line
        """
        if posn is None:
            posn = obj.tell()
        x1 = obj.rfind(b'\n', 0, posn) + 1
        obj.seek(x1)
        return x1


    def __move_start_next_line(self, obj, posn = None):
        """
        moves to start of the next line
        returns the position of the beguining end of this line
        """
        if posn is None:
            posn = obj.tell()
        x1 = obj.find(b'\n', posn) + 1
        obj.seek(x1)
        return x1


    def __move_start_prev_line(self, obj, posn = None):
        """
        moves to the start of the previous line
        returns the position of the beguining of this line
        """
        if posn is None:
            posn = obj.tell()
        for i in range(2):
            posn = obj.rfind(b'\n', 0, posn)
            obj.seek(posn)
        x1 = self.__move_start_next_line(obj, posn)
        return x1


    def __move_end_prev_line(self, obj, posn = None):
        """
        moves to the end of the previous line
        returns the position of the end of this line
        """
        if posn is None:
            posn = obj.tell()
        posn = obj.rfind(b'\n', posn)
        obj.seek(posn)
        return posn


    def __read_line(self, obj, posn):
        """
        reads current line and moves to the start of the next line
        it mimics readline function in text files
        """
        obj.seek(posn)
        line = obj.readline()
        new_posn = self.__move_start_next_line(obj, posn)
        return (line, new_posn)


    def __any_item_in_line(self, flags, line):
        """
        returns True if an item in flags is in line
        """
        for item in flags:
            if item in line:
                return True
        return False


    def read_vertices(self):
        """
        reads vertex coordinates from a disv file
        returns an array with the vertices coordinates
        """
        dim = self.get_dimensions()
        xys = np.empty((dim['NVERT'], 2), np.float64)

        label = 'BEGIN VERTICES'
        with open(self.file, mode="r", encoding="utf-8") as fr:
            with mmap.mmap(fr.fileno(), length=0,
                           access=mmap.ACCESS_READ) as obj:

                nb1 = self.__find_label(obj, label, posn=0)
                nb1 = self.__move_start_next_line(obj, nb1)
                nb2 = nb1
                for i in range(dim['NVERT']):
                    line, nb2 = self.__read_line(obj, nb2)
                    words = line.split()
                    xys[i, :] = (words[1], words[2])
        return xys


    def read_cells(self):
        """
        reads cells from a disv file
        returns 2 arrays:
            cell centroid coordinates
            vertices in each cell
        """
        dim = self.get_dimensions()
        centroids = np.empty((dim['NCPL'], 2), np.float64)
        cell_verts = []

        label = 'BEGIN CELL2D'
        with open(self.file, mode="r", encoding="utf-8") as fr:
            with mmap.mmap(fr.fileno(), length=0,
                           access=mmap.ACCESS_READ) as obj:

                nb1 = self.__find_label(obj, label, posn=0)
                nb1 = self.__move_start_next_line(obj, nb1)
                nb2 = nb1
                for i in range(dim['NCPL']):
                    line, nb2 = self.__read_line(obj, nb2)
                    words = line.split()
                    centroids[i, :] = (words[1], words[2])
                    nv = int(words[3])
                    vertices = [int(words[j]) for j in range(4, 4+nv)]
                    cell_verts.append(vertices)
        return (centroids, cell_verts)


# DEPRECATED
#                for ilay in range(dim['NLAY']):
#                    line, nb1 = self.__read_line(obj, nb1)
#                    if b'CONSTANT' in line:
#                        hs[ilay+1, :] = int(line.decode('utf-8').split()[1])
#                        nb1 = self.__move_start_prev_line(obj, nb1)
#                    else:
#                        nb2 = nb1
#                        while True:
#                            line, nb2 = self.__read_line(obj, nb2)
#                            if self.__any_item_in_line(flags, line):
#                                nb2 = self.__move_start_prev_line(obj, nb2)
#                                break
#                        tmp = obj[nb1:nb2].decode('utf-8').split()
#                        tmp = np.array(tmp, np.float64)
#                        hs[ilay+1, :] = tmp
#                        nb1 = nb2

#                for ilay in range(dim['NLAY']):
#                    line, nb1 = self.__read_line(obj, nb1)
#                    if b'CONSTANT' in line:
#                        active_cells[ilay, :] = \
#                        int(line.decode('utf-8').split()[1])
#                        nb1 = self.__move_start_prev_line(obj, nb1)
#                    else:
#                        nb2 = nb1
#                        while True:
#                            line, nb2 = self.__read_line(obj, nb2)
#                            if self.__any_item_in_line(flags, line):
#                                nb2 = self.__move_start_prev_line(obj, nb2)
#                                break
#                        tmp = obj[nb1:nb2].decode('utf-8').split()
#                        tmp = np.array(tmp, np.int32)
#                        active_cells[ilay, :] = tmp
#                        nb1 = nb2