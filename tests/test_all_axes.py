import inspect

from dplot import color
from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_LATEX
from dplot import *


def test_all_axes():
    title = inspect.stack()[0][3]
    fig = Figure(title, margin={'t': 10, 'b': 10, 'l': 10, 'r': 10}, legend_setup=LegendSetup(enable=False))
    fig.axes['b'] = AxisSetup(
        'bottom', scale=1,
        tick=TickSetup(enable=True, minor_thickness='very thin', major_thickness='very thick', minor_color=Color.LIGHTGRAY, minor_num=4),
        grid=GridSetup(major_enable=True, major_thickness='very thick', minor_enable=True, minor_color=Color.LIGHTGRAY, minor_thickness='thin'),
        label_shift=2
    )
    fig.axes['l'] = AxisSetup('left', log=True, tick=TickSetup(enable=True), label_shift=7)
    fig.axes['r'] = AxisSetup('right', tick=TickSetup(enable=True), label_shift=4)
    fig.axes['t'] = AxisSetup(
        'top', scale=1,
        tick=TickSetup(enable=True, minor_thickness='thin', major_thickness='thick', minor_num=1),
        grid=GridSetup(major_enable=False),
        label_shift=2
    )

    fig.add('b', 'l', [0, 1, 2, 3, 4, 5], [4, 5, 4, 5, 4, 5], ls=LineSetup(plot_color=Color.RED))
    fig.add('b', 'r', [0, 1, 2, 3, 4, 5], [1, 1, 2, 1, 1, 1], ls=LineSetup(plot_color=Color.LIMEGREEN, line_style='dotted', line_width='2'))
    fig.add('t', 'l', [-2, -1, 0], [4, 6, 4], ls=LineSetup(plot_color=Color.BLUEVIOLET, line_style='solid', marker='square', marker_repeat=2, marker_phase=2))
    fig.add('t', 'r', [-2, -1, 0], [0, 1, 0], ls=LineSetup(plot_color=Color.ROSYBROWN, line_width='0.5'))

    path_latex, path_pdf = LatexGenerator(fig).export(PATH_OUTPUT_DIR_LATEX)  # generate pdf via LaTex
    assert check_identical_pdf(path_pdf)  # check that pdf looks as expected
