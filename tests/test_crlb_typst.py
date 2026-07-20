import numpy as np
from numpy import pi
from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_LATEX, PATH_OUTPUT_DIR_TYPST, check_embedded_typst_export
from dplot import *


def test_crlb_typst():
    #  N: number of samples for the estimator
    N = 10
    phi = 0
    n_f0s = 201  # number of f0s for the plot
    f0_min = 0
    f0_max = 0.5
    fig_name = f'crlb_{N}'

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

    fig = Figure(fig_name, margin={'t': 8, 'b': 12, 'l': 14, 'r': 14}, background_color=Color.GAINSBORO, legend_setup=LegendSetup(enable=True, h_align=HAlign.CENTER))
    ts = TickSetup(enable=True)

    # since we use the typst output, we use typst inline math commands
    fig.axes['b'] = AxisSetup(r'$f_0$', scale=1, tick=ts, label_shift=0)
    fig.axes['l'] = AxisSetup(r'$"CRLB" thick \/ thick (sigma^2 \/ A^2)$', scale=1, tick=ts, limits=(y_min, y_max), log=True, label_shift=0, grid=GridSetup(major_enable=True, minor_enable=True))
    fig.axes['r'] = AxisSetup('')
    fig.add('b', 'l', f0s, crlb_exact, label='exact')
    fig.add('b', 'l', np.array([f0_min, f0_max]), np.ones(2) * crlb_approx, label='approx', ls=LineSetup(line_style=LineStyle.DOTTED))

    # check standalone export, create pdf
    path_typst, path_typst_pdf = TypstGenerator(fig).export(PATH_OUTPUT_DIR_TYPST)  # generate pdf via Typst
    assert check_identical_pdf(path_typst_pdf)  # check that pdf looks as expected

    # check embedded (non-standalone) export
    assert check_embedded_typst_export(fig)
