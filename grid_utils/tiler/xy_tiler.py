# -*- coding:utf-8 -*-

import six
import numpy as np

__all__ = ['XYTiler']


class XYTiler(object):
    _offset_dict = {
        "center": (0.5, 0.5),
        "lowerleft": (0.0, 0.0),
        "lowerright": (1.0, 0.0),
        "upperleft": (0.0, 1.0),
        "upperright": (1.0, 1.0)
    }

    def __init__(self, x_size, y_size, nx, ny, x0=0.0, y0=0.0, margin=0, **kwargs):
        self.x_size = x_size
        self.y_size = y_size

        self.nx = nx
        self.ny = ny

        self.x0 = x0
        self.y0 = y0

        self.dx = self.x_size / self.nx
        self.dy = self.y_size / self.ny

        self.margin = margin

    @property
    def full_nx(self):
        return self.nx + self.margin * 2

    @property
    def full_ny(self):
        return self.ny + self.margin * 2

    def xy2tile(self, x, y, margin=True):
        tile_i, i = self._to_tile_1d(x, self.x0, self.x_size, self.nx)
        tile_j, j = self._to_tile_1d(y, self.y0, self.y_size, self.ny)
        if margin:
            i += self.margin
            j += self.margin
        return tile_i, tile_j, i, j

    def tile2xy(self, tile_i, tile_j, i, j, pos='center', margin=True):
        i_offset, j_offset = self._offset_dict.get(pos, (0.5, 0.5))
        if margin:
            i -= self.margin
            j -= self.margin
        x = self._to_xy_1d(tile_i, i, self.x0, self.x_size, self.nx, i_offset)
        y = self._to_xy_1d(tile_j, j, self.y0, self.y_size, self.ny, j_offset)
        return x, y

    def get_tile_xys(self, tile_i, tile_j, pos='center', margin=True):
        i_offset, j_offset = self._offset_dict.get(pos, (0.5, 0.5))
        if margin:
            ii = np.arange(-self.margin, self.nx+self.margin)
            jj = np.arange(-self.margin, self.ny+self.margin)
        else:
            ii = np.arange(self.nx)
            jj = np.arange(self.ny)
        xs = self._to_xy_1d(tile_i, ii, self.x0, self.x_size, self.nx, i_offset)
        ys = self._to_xy_1d(tile_j, jj, self.y0, self.y_size, self.ny, j_offset)
        return xs, ys

    def get_tile_bbox(self, tile_i, tile_j):
        x1 = self.x0 + self.x_size * tile_i
        y1 = self.y0 + self.y_size * tile_j
        x2 = x1 + self.x_size
        y2 = y1 + self.y_size
        return (x1, y1, x2, y2)

    def get_covered_tiles(self, x1, y1, x2, y2, padding=0, detail=False, margin=True):
        # margin is considered only when generating each tile's details.
        tile_i1, tile_j1, i1, j1 = self.xy2tile(x1, y1, margin=False)
        tile_i2, tile_j2, i2, j2 = self.xy2tile(x2, y2, margin=False)

        x2_, y2_ = self.tile2xy(tile_i2, tile_j2, i2, j2, pos='lowerleft', margin=False)
        if i2 == 0:
            if x2 < x2_ + (self.x_size / self.nx) / 10.0:
                tile_i2 -= 1
                i2 = self.nx - 1
        if j2 == 0:
            if y2 < y2_ + (self.y_size / self.ny) / 10.0:
                tile_j2 -= 1
                j2 = self.ny - 1

        # Add padding
        i1 -= padding
        i2 += padding
        j1 -= padding
        j2 += padding

        tile_i1 += i1 // self.nx
        tile_i2 += i2 // self.nx
        tile_j1 += j1 // self.ny
        tile_j2 += j2 // self.ny

        i1 %= self.nx
        i2 %= self.nx
        j1 %= self.ny
        j2 %= self.ny

        tile_list = []
        for tj in range(tile_j1, tile_j2 + 1):
            for ti in range(tile_i1, tile_i2 + 1):
                tile_list.append((ti, tj))

        if detail:
            i_beg_dict = {}
            i_end_dict = {}
            i_offset_dict = {}
            j_beg_dict = {}
            j_end_dict = {}
            j_offset_dict = {}

            j_offset = 0
            for tj in range(tile_j1, tile_j2+1):
                j_beg = j1 if tj == tile_j1 else 0
                j_end = j2 + 1 if (tj == tile_j2 and j2 < self.ny) else self.ny
                if margin:
                    j_beg += self.margin
                    j_end += self.margin
                j_size = j_end - j_beg
                j_beg_dict[tj] = j_beg
                j_end_dict[tj] = j_end
                j_offset_dict[tj] = j_offset
                j_offset += j_size
            total_nj = j_offset

            i_offset = 0
            for ti in range(tile_i1, tile_i2+1):
                i_beg = i1 if ti == tile_i1 else 0
                i_end = i2 + 1 if (ti == tile_i2 and i2 < self.nx) else self.nx
                if margin:
                    i_beg += self.margin
                    i_end += self.margin
                i_size = i_end - i_beg
                i_beg_dict[ti] = i_beg
                i_end_dict[ti] = i_end
                i_offset_dict[ti] = i_offset
                i_offset += i_size
            total_ni = i_offset

            x_beg, y_beg = self.tile2xy(tile_i1, tile_j1, i1, j1, margin=False)
            x_end, y_end = self.tile2xy(tile_i2, tile_j2, i2, j2, margin=False)
            total_xs = np.linspace(x_beg, x_end, total_ni)
            total_ys = np.linspace(y_beg, y_end, total_nj)

            return {
                "ni": total_ni,
                "nj": total_nj,
                "xs": total_xs,
                "ys": total_ys,
                "i_beg_dict": i_beg_dict,
                "i_end_dict": i_end_dict,
                "i_offset_dict": i_offset_dict,
                "j_beg_dict": j_beg_dict,
                "j_end_dict": j_end_dict,
                "j_offset_dict": j_offset_dict,
                "tile_list": tile_list
            }
        else:
            return tile_list

    def _to_tile_1d(self, x, orig, block_size, pixel_num):
        x_ = x - orig
        tile_i = int(np.floor(x_ / block_size))
        i = int(np.floor((x_ - block_size * tile_i) / (block_size / pixel_num)))
        if i == pixel_num:
            tile_i += 1
            i = 0
        return tile_i, i

    def _to_xy_1d(self, tile_i, i, orig, block_size, pixel_num, offset=0.5):
        return orig + tile_i * block_size + (i + offset) * block_size / pixel_num

    def get_surrounding_pixels(self, tile_i, tile_j, i, j, length=1, margin=True):
        size = length * 2 + 1
        tile_I = np.full((size, size), tile_i, dtype='i')
        tile_J = np.full((size, size), tile_j, dtype='i')
        J, I = np.mgrid[-length:length+1, -length:length+1]

        if margin:
            i -= self.margin
            j -= self.margin

        J += j
        I += i

        tile_I += I // self.nx
        tile_J += J // self.ny
        I = I % self.nx
        J = J % self.ny

        if margin:
            I += self.margin
            J += self.margin

        return tile_I, tile_J, I, J

    def __repr__(self):
        return "<{} size: {}, n_pixel: {}, orig: {}, margin: {}>".format(self.__class__.__name__, (self.x_size, self.y_size), (self.nx, self.ny), (self.x0, self.y0), self.margin)