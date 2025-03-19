import unittest

from dplot import Figure, AxisSetup, LineSetup


class DPlotTest(unittest.TestCase):

    def test_all_axes(self):
        fig = Figure('test-figure', background_color='gray!30')
        fig.axes['b'] = AxisSetup('freq', scale=1, tick_enable=True, tick_minor_thickness='very thin', tick_major_thickness='very thick', tick_minor_num=4,
                                  grid_major_enable=True, grid_major_thickness='very thick', grid_minor_enable=True, grid_minor_color='blue', grid_minor_thickness='thin', tick_minor_color='blue')
        fig.axes['l'] = AxisSetup('magnitude', tick_enable=True, log=True)
        fig.axes['r'] = AxisSetup('phase', tick_enable=False)
        fig.axes['t'] = AxisSetup('Test', scale=1, tick_enable=True, grid_major_enable=False, tick_minor_thickness='thin', tick_major_thickness='thick', tick_minor_num=1)
        fig.add_data('b', 'l', [0, 1, 2, 3, 4, 5], [4, 5, 4, 5, 4, 5])
        fig.add_data('b', 'r', [0, 1, 2, 3, 4, 5], [1, 1, 2, 1, 1, 1], LineSetup(line_style='dotted', line_width='2'))
        fig.add_data('t', 'l', [-2, -1, 0], [4, 6, 4], LineSetup(line_style='solid', marker='square', marker_repeat=2, marker_phase=2))
        fig.add_data('t', 'r', [-2, -1, 0], [0, 1, 0], LineSetup(plot_color='black', line_width='0.5'))
        fig.create_latex('test-file.tex', build=True, quiet=True)

        self.assertTrue(True)
