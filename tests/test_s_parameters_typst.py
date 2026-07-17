import os.path
from typing import cast
import numpy as np
import pandas
from pandas import DataFrame
from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_TYPST
from dplot import *


def test_s_parameters():
    fig_name = 's_parameters'
    path = os.path.join(os.path.dirname(__file__), 'via250.txt')
    df: DataFrame = pandas.read_csv(path, delimiter='\t')
    freqs_ghz = df['S(1,1) (GHz) Via Frequency'].to_numpy()
    s11 = df['S(1,1) Via Unitless data (Real)'].to_numpy() + 1j * df['S(1,1) Via Unitless data (Imag)'].to_numpy()

    fig = Figure(fig_name, margin={'t': 4, 'b': 12, 'l': 16, 'r': 16}, legend_setup=LegendSetup(anchor='south east', at=(0.6, 0.02)))

    # since we use the typst output, we use typst inline math commands
    fig.axes['b'] = AxisSetup(r'$f$ / $"GHz"$', label_shift=1.5,
                              tick=TickSetup(minor_num=1), grid=GridSetup(major_enable=True, minor_enable=True, minor_color=Color.LIGHTGRAY))
    fig.axes['l'] = AxisSetup(r'$abs(S) dot 10^2$', label_shift=1)
    fig.axes['r'] = AxisSetup(r'$angle S$ / $360^degree$', label_shift=5)

    fig.add('b', 'l', freqs_ghz, 10 ** 2 * 20 * np.log10(np.abs(s11)), label=r'$abs(S_11)$', ls=LineSetup(plot_color=Color.CADETBLUE, marker=Marker.DOT, marker_repeat=20))
    fig.add('b', 'r', freqs_ghz, cast(np.array, np.angle(s11)) * 360 / np.pi, ls=LineSetup(line_style=LineStyle.DASHED, marker=Marker.SQUARE, marker_repeat=20),
            label=r'$angle S_11$')

    path_typst, path_typst_pdf = TypstGenerator(fig).export(PATH_OUTPUT_DIR_TYPST)  # generate pdf via Typst
    assert check_identical_pdf(path_typst_pdf)  # check that pdf looks as expected
