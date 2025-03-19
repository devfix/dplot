import unittest

from dplot import Figure, AxisSetup, LineSetup


class DPlotTest(unittest.TestCase):

    def test_all_axes(self):
        fig = Figure('test-figure')
        fig.axes['b'] = AxisSetup('freq', scale=1e9, grid_major=False, ticks=False)
        fig.axes['l'] = AxisSetup('magnitude', grid_major=True, ticks=True)
        fig.axes['r'] = AxisSetup('phase')
        fig.axes['t'] = AxisSetup('Test', scale=1e-18)
        fig.add_data('b', 'l', [0, 1, 2, 3, 4, 5], [4, 5, 4, 5, 4, 5])
        fig.add_data('b', 'r', [0, 1, 2, 3, 4, 5], [1, 1, 2, 1, 1, 1], LineSetup(line_style='dotted', line_width=2))
        fig.add_data('t', 'l', [-2, -1, 0], [4, 6, 4], LineSetup(line_style='', marker='square', marker_repeat=2, marker_phase=2))
        fig.add_data('t', 'r', [-2, -1, 0], [0, 1, 0], LineSetup(plot_color='black', line_width=0.5))
        fig.create_latex('test-file.tex', build=True, quiet=True)

        self.assertTrue(True)
