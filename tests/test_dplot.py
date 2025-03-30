import inspect
import os.path
import unittest
from typing import cast

import numpy as np
import pandas
from pandas import DataFrame
from dplot import Figure, AxisSetup, LineSetup
from dplot.dplot import TickSetup, GridSetup, Data
from tests.tools import check_identical_pdf


class DPlotTest(unittest.TestCase):
    def test_classic_bl(self):
        fig = Figure('test-figure', background_color='gray!30')
        ts = TickSetup(enable=True)
        fig.axes['b'] = AxisSetup('x', scale=1, tick=ts)
        fig.axes['l'] = AxisSetup('y', scale=1, tick=ts)
        fig.add(Data('b', 'l', [-2, -1, 0, 1, 2], [5, 1, 0, 1, 5]))

        _, path_pdf = fig.create_latex(f'{inspect.stack()[0][3]}.tex', build=True)
        self.assertTrue(check_identical_pdf(path_pdf))

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

        fig.add(Data('b', 'l', [0, 1, 2, 3, 4, 5], [4, 5, 4, 5, 4, 5]))
        fig.add(Data('b', 'r', [0, 1, 2, 3, 4, 5], [1, 1, 2, 1, 1, 1], LineSetup(line_style='dotted', line_width='2')))
        fig.add(Data('t', 'l', [-2, -1, 0], [4, 6, 4], LineSetup(line_style='solid', marker='square', marker_repeat=2, marker_phase=2)))
        fig.add(Data('t', 'r', [-2, -1, 0], [0, 1, 0], LineSetup(plot_color='black', line_width='0.5')))

        _, path_pdf = fig.create_latex(f'{inspect.stack()[0][3]}.tex', build=True)
        self.assertTrue(check_identical_pdf(path_pdf))

    def test_s_par(self):
        path = os.path.join(os.path.dirname(__file__), 'via250.txt')
        df: DataFrame = pandas.read_csv(path, delimiter='\t')
        freqs_ghz = df['S(1,1) (GHz) Via Frequency'].to_numpy()
        s11 = df['S(1,1) Via Unitless data (Real)'].to_numpy() + 1j * df['S(1,1) Via Unitless data (Imag)'].to_numpy()

        fig = Figure('Test S-parameters')
        fig.axes['t'] = AxisSetup(padding='0cm')
        fig.axes['b'] = AxisSetup(r'$f$ / $\si{\giga\hertz}$', label_shift='0.5em', padding='0.8cm',
                                  tick=TickSetup(minor_num=1), grid=GridSetup(major_enable=True, minor_enable=True, minor_color='lightgray'))
        fig.axes['l'] = AxisSetup(r'$|S(1,1)| \cdot 10^2$', label_shift='0.1em', padding='1.5cm')
        fig.axes['r'] = AxisSetup(r'$\angle S(1,1)$ / $\num{360}^\circ$', label_shift='1.5em', padding='1.5cm')
        fig.add(Data('b', 'l', freqs_ghz, 10**2 * 20*np.log10(np.abs(s11))))
        fig.add(Data('b', 'r', freqs_ghz, cast(np.array, np.angle(s11)) * 360 / np.pi, LineSetup(line_style='dashed')))

        _, path_pdf = fig.create_latex(f'{inspect.stack()[0][3]}.tex', build=True)
        self.assertTrue(check_identical_pdf(path_pdf))
