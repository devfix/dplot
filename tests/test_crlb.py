import inspect
import numpy as np
from numpy import pi
from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_LATEX
from dplot import *


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

    fig = Figure(title, margin={'t': 0, 'b': 0, 'l': 10, 'r': 10}, background_color=Color.LIGHTGRAY, legend_setup=LegendSetup(enable=True))
    ts = TickSetup(enable=True)
    fig.axes['b'] = AxisSetup(r'$f_0$', scale=1, tick=ts)
    fig.axes['l'] = AxisSetup(r'$\mathrm{CRLB} \ /\  (\sigma^2 / A^2)$', scale=1, tick=ts, limits=(y_min, y_max), log=True)
    fig.axes['r'] = AxisSetup('')
    fig.add(Data('b', 'l', f0s, crlb_exact, label='exact'))
    fig.add(Data('b', 'l', np.array([f0_min, f0_max]), np.ones(2) * crlb_approx, label='approx', ls=LineSetup(line_style='dotted')))

    path_latex, path_pdf = LatexGenerator(fig).export(PATH_OUTPUT_DIR_LATEX)
    assert check_identical_pdf(path_pdf)
