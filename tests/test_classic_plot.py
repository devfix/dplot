import inspect
from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_LATEX
from dplot import *


def test_classic_plot():
    title = inspect.stack()[0][3]
    fig = Figure(title, margin={'t': 0, 'b': 0, 'l': 0, 'r': 0}, background_color=Color.LIGHTGRAY, legend_setup=LegendSetup(enable=False))
    ts = TickSetup(enable=True)
    fig.axes['b'] = AxisSetup('x', scale=1, tick=ts)
    fig.axes['l'] = AxisSetup('y', scale=1, tick=ts)
    fig.add(Data('b', 'l', [-2, -1, 0, 1, 2], [5, 1, 0, 1, 5]))

    path_latex, path_pdf = LatexGenerator(fig).export(PATH_OUTPUT_DIR_LATEX)
    assert check_identical_pdf(path_pdf)
    # TypstGenerator(fig).export(PATH_OUTPUT_DIR_TYPST)
