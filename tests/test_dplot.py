import inspect
import os.path
import unittest
from typing import cast
import numpy as np
from numpy import pi
import pandas
from pandas import DataFrame
from dplot import *
from tests.tools import check_identical_pdf

PATH_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def test_classic_bl():
    title = inspect.stack()[0][3]
    fig = Figure(title, background_color='gray!30', legend_setup=LegendSetup(enable=False))
    ts = TickSetup(enable=True)
    fig.axes['b'] = AxisSetup('x', scale=1, tick=ts)
    fig.axes['l'] = AxisSetup('y', scale=1, tick=ts)
    fig.add(Data('b', 'l', [-2, -1, 0, 1, 2], [5, 1, 0, 1, 5]))

    path_pdf, = fig.export(PATH_OUTPUT_DIR, ExportType.PDF)
    assert check_identical_pdf(path_pdf)


def test_all_axes():
    title = inspect.stack()[0][3]
    fig = Figure(title, background_color='gray!30', legend_setup=LegendSetup(enable=False))
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
    fig.add(Data('b', 'r', [0, 1, 2, 3, 4, 5], [1, 1, 2, 1, 1, 1], ls=LineSetup(line_style='dotted', line_width='2')))
    fig.add(Data('t', 'l', [-2, -1, 0], [4, 6, 4], ls=LineSetup(line_style='solid', marker='square', marker_repeat=2, marker_phase=2)))
    fig.add(Data('t', 'r', [-2, -1, 0], [0, 1, 0], ls=LineSetup(plot_color='black', line_width='0.5')))

    path_pdf, = fig.export(PATH_OUTPUT_DIR, ExportType.PDF)
    assert check_identical_pdf(path_pdf)


def test_s_par():
    title = inspect.stack()[0][3]
    path = os.path.join(os.path.dirname(__file__), 'via250.txt')
    df: DataFrame = pandas.read_csv(path, delimiter='\t')
    freqs_ghz = df['S(1,1) (GHz) Via Frequency'].to_numpy()
    s11 = df['S(1,1) Via Unitless data (Real)'].to_numpy() + 1j * df['S(1,1) Via Unitless data (Imag)'].to_numpy()

    fig = Figure(title, legend_setup=LegendSetup(anchor='south east', at=(0.6, 0.02)))
    fig.axes['t'] = AxisSetup(padding='0cm')
    fig.axes['b'] = AxisSetup(r'$f$ / $\si{\giga\hertz}$', label_shift='0.5em', padding='0.8cm',
                              tick=TickSetup(minor_num=1), grid=GridSetup(major_enable=True, minor_enable=True, minor_color='lightgray'))
    fig.axes['l'] = AxisSetup(r'$|S| \cdot 10^2$', label_shift='0.1em', padding='1.5cm')
    fig.axes['r'] = AxisSetup(r'$\angle S$ / $\num{360}^\circ$', label_shift='1.5em', padding='1.5cm')

    fig.add(Data('b', 'l', freqs_ghz, 10 ** 2 * 20 * np.log10(np.abs(s11)), label=r'$|S_{11}|$',
                 ls=LineSetup(marker='*', marker_repeat=20)))
    fig.add(Data('b', 'r', freqs_ghz, cast(np.array, np.angle(s11)) * 360 / np.pi,
                 ls=LineSetup(line_style='dashed', marker='*', marker_repeat=20), label=r'$\angle S_{11}$'))

    path_pdf, = fig.export(PATH_OUTPUT_DIR, ExportType.PDF)
    assert check_identical_pdf(path_pdf)


def test_crlb():
    #  N: number of samples for the estimator
    N = 10
    phi = 0
    n_f0s = 51  # number of f0s for the plot
    f0_min = 0
    f0_max = 0.5
    title = f'{inspect.stack()[0][3]}_{N}'

    n = np.array(range(N))
    f0s = np.linspace(f0_min, f0_max, n_f0s)

    # calculate the value in the sum of the denominator, i.e. for every f0 x n
    # then sum over the n -> 2nd axis i.e. axis=1
    # use np.clip to prevent dividing by zero
    den = 2 * pi ** 2 * np.sum(n ** 2 - n ** 2 * np.cos(4 * pi * np.outer(f0s, n) + 2 * phi), axis=1)
    crlb_exact = 1 / np.clip(den, a_min=1e-100, a_max=None)

    crlb_approx = 3 / (pi ** 2 * (N - 1) * N * (2 * N - 1))

    crlb_min = np.min(crlb_exact)
    crlb_max = 2 * crlb_approx - crlb_min

    y_min = 10 ** np.floor(np.log10(crlb_min))
    y_max = 10 ** np.ceil(np.log10(crlb_max))
    # print(f'{title}: y_min={y_min}, y_max={y_max} crlb_approx={crlb_approx}')

    fig = Figure(title, background_color='gray!30', legend_setup=LegendSetup(enable=True))
    ts = TickSetup(enable=True)
    fig.axes['b'] = AxisSetup(r'$f_0$', scale=1, tick=ts)
    fig.axes['l'] = AxisSetup(r'$\mathrm{CRLB} \ /\  (\sigma^2 / A^2)$', scale=1, tick=ts, limits=(y_min, y_max), padding='1cm', log=True)
    fig.axes['r'] = AxisSetup('', padding='1cm')
    fig.add(Data('b', 'l', f0s, crlb_exact, label='exact'))
    fig.add(Data('b', 'l', np.array([f0_min, f0_max]), np.ones(2) * crlb_approx, label='approx', ls=LineSetup(line_style='dotted')))

    path_pdf, = fig.export(PATH_OUTPUT_DIR, ExportType.PDF)
    assert check_identical_pdf(path_pdf)
