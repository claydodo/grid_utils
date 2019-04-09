from unittest import TestCase

from grid_utils.tiler.xy_tiler import *


class TestXYTiler(TestCase):
    def gen_tiler(self):
        return XYTiler(1.0, 1.0, 10, 10)

    def gen_tiler_with_x0y0(self):
        return XYTiler(1.0, 1.0, 10, 10, 100.0, 30.0)

    def gen_tiler_with_margin(self):
        return XYTiler(1.0, 1.0, 10, 10, margin=2)

    def test_full_nx_ny(self):
        tiler1 = self.gen_tiler()
        tiler2 = self.gen_tiler_with_margin()

        self.assertEqual(tiler1.full_nx, 10)
        self.assertEqual(tiler1.full_ny, 10)
        self.assertEqual(tiler2.full_nx, 14)
        self.assertEqual(tiler2.full_ny, 14)

    def test_xy2tile(self):
        tiler1 = self.gen_tiler()

        self.assertEqual(tiler1.xy2tile(93.501, 34.301), (93, 34, 5, 3))
        self.assertEqual(tiler1.xy2tile(93.499, 34.301), (93, 34, 4, 3))

        tiler2 = self.gen_tiler_with_x0y0()
        self.assertEqual(tiler2.xy2tile(93.501, 34.301), (-7, 4, 5, 3))

        tiler3 = self.gen_tiler_with_margin()
        self.assertEqual(tiler3.xy2tile(93.501, 34.301), (93, 34, 7, 5))
        self.assertEqual(tiler3.xy2tile(93.501, 34.301, margin=False), (93, 34, 5, 3))
        self.assertEqual(tiler3.xy2tile(93.001, 34.999), (93, 34, 2, 11))

