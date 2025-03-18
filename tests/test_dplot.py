import unittest

from dplot import Figure, AxisSetup


class DPlotTest(unittest.TestCase):

    def test_all_axes(self):
        fig = Figure('test-figure')
        fig.axes['b'] = AxisSetup('freq', scale=1e9)
        fig.axes['l'] = AxisSetup('magnitude')
        fig.axes['r'] = AxisSetup('phase')
        fig.axes['t'] = AxisSetup('Test')
        fig.add_data('b', 'l', [0, 1, 2, 3, 4, 5], [4, 5, 4, 5, 4, 5])
        fig.add_data('b', 'r', [0, 1, 2, 3, 4, 5], [1, 1, 2, 1, 1, 1])
        fig.add_data('t', 'l', [-2, -1, 0], [4, 6, 4])
        fig.add_data('t', 'r', [-2, -1, 0], [0, 1, 0])
        fig.create_latex('test-file.tex', build=True)

        self.assertTrue(True)
