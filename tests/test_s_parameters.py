import inspect
import os.path
from typing import cast
import numpy as np
import pandas
from pandas import DataFrame
from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_LATEX
from dplot import *


def test_s_parameters():
    title = inspect.stack()[0][3]
    path = os.path.join(os.path.dirname(__file__), 'via250.txt')
    df: DataFrame = pandas.read_csv(path, delimiter='\t')
    freqs_ghz = df['S(1,1) (GHz) Via Frequency'].to_numpy()
    s11 = df['S(1,1) Via Unitless data (Real)'].to_numpy() + 1j * df['S(1,1) Via Unitless data (Imag)'].to_numpy()

    fig = Figure(title, margin={'t': 5, 'b': 5, 'l': 10, 'r': 10}, legend_setup=LegendSetup(anchor='south east', at=(0.6, 0.02)))
    fig.axes['b'] = AxisSetup(r'$f$ / $\si{\giga\hertz}$', label_shift=1.5,
                              tick=TickSetup(minor_num=1), grid=GridSetup(major_enable=True, minor_enable=True, minor_color=Color.LIGHTGRAY))
    fig.axes['l'] = AxisSetup(r'$|S| \cdot 10^2$', label_shift=1)
    fig.axes['r'] = AxisSetup(r'$\angle S$ / $\num{360}^\circ$', label_shift=5)

    fig.add('b', 'l', freqs_ghz, 10 ** 2 * 20 * np.log10(np.abs(s11)), label=r'$|S_{11}|$', ls=LineSetup(marker=Marker.DOT, marker_repeat=20))
    fig.add('b', 'r', freqs_ghz, cast(np.array, np.angle(s11)) * 360 / np.pi, ls=LineSetup(line_style=LineStyle.DASHED, marker=Marker.DOT, marker_repeat=20),
            label=r'$\angle S_{11}$')

    path_latex, path_pdf = LatexGenerator(fig).export(PATH_OUTPUT_DIR_LATEX)  # generate pdf via LaTex
    assert check_identical_pdf(path_pdf)  # check that pdf looks as expected
