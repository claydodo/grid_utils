# -*- coding:utf-8 -*-

# TODO: still draft.

from dt_utils import T
from grid_utils.dimension.grid_dim import GridDim

__all__ = ['DatetimeDim']


class DatetimeDim(GridDim):
    parser = T
    serializer = "{:%Y-%m-%d %H:%M:%S}"

    def __getitem__(self, key):
        if np.isscalar(key):
            return nearest_i(self.values, key)  # TODO


