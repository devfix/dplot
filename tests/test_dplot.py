import unittest

from dplot import Figure, AxisSetup, LineSetup
from dplot.dplot import TickSetup, GridSetup


class DPlotTest(unittest.TestCase):

    def test_classic_bl(self):
        fig = Figure('test-figure', background_color='gray!30')
        ts = TickSetup(enable=True)
        fig.axes['b'] = AxisSetup('x', scale=1, tick=ts)
        fig.axes['l'] = AxisSetup('y', scale=1, tick=ts)
        fig.add_data('b', 'l', [-2, -1, 0, 1, 2], [5, 1, 0, 1, 5])
        fig.create_latex('test-classic-bl')
        self.assertTrue(True)

    def test_all_axes(self):
        fig = Figure('test-figure', background_color='gray!30')
        fig.axes['b'] = AxisSetup(
            'bottom', scale=1,
            tick=TickSetup(enable=True, minor_thickness='very thin', major_thickness='very thick', minor_color='blue', minor_num=4),
            grid=GridSetup(major_enable=True, major_thickness='very thick', minor_enable=True, minor_color='blue', minor_thickness='thin'))
        fig.axes['l'] = AxisSetup('left', log=True, tick=TickSetup(enable=True))
        fig.axes['r'] = AxisSetup('right', tick=TickSetup(enable=True))
        fig.axes['t'] = AxisSetup(
            'top', scale=1,
            tick=TickSetup(enable=True, minor_thickness='thin', major_thickness='thick', minor_num=1),
            grid=GridSetup(major_enable=False)
        )
        fig.add_data('b', 'l', [0, 1, 2, 3, 4, 5], [4, 5, 4, 5, 4, 5])
        fig.add_data('b', 'r', [0, 1, 2, 3, 4, 5], [1, 1, 2, 1, 1, 1], LineSetup(line_style='dotted', line_width='2'))
        fig.add_data('t', 'l', [-2, -1, 0], [4, 6, 4], LineSetup(line_style='solid', marker='square', marker_repeat=2, marker_phase=2))
        fig.add_data('t', 'r', [-2, -1, 0], [0, 1, 0], LineSetup(plot_color='black', line_width='0.5'))
        fig.create_latex('test-all-axes.tex', build=True, quiet=True)

        self.assertTrue(True)
