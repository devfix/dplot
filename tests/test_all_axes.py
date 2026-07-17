import inspect
from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_LATEX
from dplot import *


def test_all_axes():
    title = inspect.stack()[0][3]
    fig = Figure(title, margin={'t': 0, 'b': 0, 'l': 0, 'r': 0}, background_color=Color.LIGHTGRAY, legend_setup=LegendSetup(enable=False))
    fig.axes['b'] = AxisSetup(
        'bottom', scale=1,
        tick=TickSetup(enable=True, minor_thickness='very thin', major_thickness='very thick', minor_color=Color.BLUE, minor_num=4),
        grid=GridSetup(major_enable=True, major_thickness='very thick', minor_enable=True, minor_color=Color.BLUE, minor_thickness='thin'))
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
    fig.add(Data('t', 'r', [-2, -1, 0], [0, 1, 0], ls=LineSetup(plot_color=Color.BLACK, line_width='0.5')))

    path_latex, path_pdf = LatexGenerator(fig).export(PATH_OUTPUT_DIR_LATEX)
    assert check_identical_pdf(path_pdf)
