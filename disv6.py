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


    def get_layer_definition(self, end_line=b'\r\n'):
        """
        returns mode_top
        """
        dim = self.get_dimensions()
        hs = np.empty((dim['NLAY'] + 1, dim['NCPL']), np.float64)

        start_block = ('BEGIN GRIDDATA', 'TOP', 'BOTM LAYERED')
        end_block = ('IDOMAIN' , 'END GRIDDATA')
        with open(self.file, mode="r", encoding="utf-8") as fr:
            with mmap.mmap(fr.fileno(), length=0,
                           access=mmap.ACCESS_READ) as obj:

                nb1 = self.__find_label(obj, start_block[0], posn=0)
                nb1 = self.__find_label(obj, start_block[1], posn=nb1)
                nb1 = self.__move_start_next_line(obj, nb1)

                line, nb1 = self.__read_line(obj, nb1)
                if b'CONSTANT' in line:
                    hs[0, :] = float(line.decode('utf-8').split()[-1])
                else:
                    nb2 = self.__find_label(obj, start_block[2], nb1)
                    tmp = obj[nb1:nb2].decode('utf-8').split()
                    tmp = np.array(tmp, np.float64)
                    hs[0, :] = tmp

                for ilay in range(dim['NLAY']):
                    nb1 = self.__move_start_next_line(obj, nb2)
                    line, nb1 = self.__read_line(obj, nb1)
                    if b'CONSTANT' in line:
                        hs[ilay+2, :] = float(line.decode('utf-8').split()[-1])
                    else:
                        if ilay + 1 < dim['NLAY']:
                            nb0 = nb1
                            while True:
                                line, nb1 = self.__read_line(obj, nb1)
                                if b'INTERNAL IPRN' in line or \
                                b'CONSTANT' in line


                        else:
                            pass


#                for i in range(dim['NLAY']):
#                    if i < dim['NLAY'] - 1:
#                        x1 = obj.find(start_block[2])
#                        obj.seek(x1)
#                        item = obj.readline()
#                        x1 = x1 + len(item)
#                        obj.seek(x1)
#                        x2 = obj.find(start_block[2])
#                    else:
#                        x1 = obj.find(start_block[2])
#                        obj.seek(x1)
#                        item = obj.readline()
#                        x1 = x1 + len(item)
#                        obj.seek(x1)
#                        x2 = obj.find(end_block[2])
#                    if x2 <= x1:
#                        msg = end_block[0].decode("utf-8")
#                        raise ValueError(f'No se encontra {msg}')
#                    arr = obj[x1:x2].decode('utf-8').split()
#                    arr = np.array(arr, np.float64)
#                    obj.seek(x2)
        return True


    def __find_label(self, obj, label, posn = None):
        """
        search for label in obj and positions cursor at he beguining of the
            line
        if label is not found raises a ValueError error
        """
        if posn is None:
            posn = obj.tell()
        x1 = obj.find(label.encode('utf-8'), posn)
        if x1 < 0:
            raise ValueError(f'No se ha encontrado {label}')
        obj.seek(posn)
        return x1


    def __move_start_next_line(self, obj, posn = None):
        """
        move to start of the next line
        returns the position of the beguining end of this line
        """
        if posn is None:
            posn = obj.tell()
        x1 = obj.find(b'\n', posn) + 1
        obj.seek(x1)
        return x1


    def __move_start_prev_line(self, obj, posn = None):
        """
        move to the start of the previous line
        returns the position of the beguining of this line
        """
        if posn is None:
            posn = obj.tell()
        for i in range(2):
            posn = obj.rfind(b'\n', posn)
            obj.seek(x1)
        x1 = self.__move_start_next_line(obj, posn)
        return x1


    def __read_line(self, obj, posn):
        """
        read current line and moves to the start of the next line
        """
        obj.seek(posn)
        line = obj.readline()
        new_posn = self.__move_start_next_line(obj, posn)
        return (line, new_posn)

