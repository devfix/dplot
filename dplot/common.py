import enum
import math
from typing import Union, Literal, Collection

# https://tikz.dev/pgfplots/reference-markers


TypeData = Collection  # requires type to be sized and iterable
XAxis = Literal['t', 'b']  # top, bottom
YAxis = Literal['l', 'r']  # left, right
LineStyle = Literal['', 'solid', 'dotted', 'densely dotted', 'loosely dotted', 'dashed', 'densely dashed', 'loosely dashed', 'dashdotted',
'densely dashdotted', 'loosely dashdotted', 'dashdotdotted', 'densely dashdotdotted', 'loosely dashdotdotted']
PlotColor = Union[str, Literal['black', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'gray', 'white', 'darkgray', 'lightgray', 'brown',
'lime', 'olive', 'orange', 'pink', 'purple', 'teal', 'violet']]
PlotThickness = Literal['very thin', 'thin', 'thick', 'very thick']
LineWidth = str
Marker = Literal[
    '', '*', 'x', '+', '-', '|', 'o', 'asterisk', 'star', '10-pointed star', 'oplus', 'oplus*', 'otimes', 'otimes*', 'square', 'square*', 'triangle',
    'triangle*', 'diamond', 'diamond*', 'halfdiamond*', 'halfsquare*', 'halfsquare left*', 'halfsquare right*', 'Mercedes star', 'Mercedes star flipped',
    'halfcircle', 'halfcircle*', 'pentagon', 'pentagon*', 'ball', 'cube', 'cube*', '']


class Environment:
    PATH_PDFLATEX = 'pdflatex'
    PATH_PDF2SVG = 'pdf2svg'
    PATH_SCOUR = 'scour'


class ExportType(enum.Enum):
    LATEX = enum.auto()
    PDF = enum.auto()
    SVG = enum.auto()


class GridSetup:
    def __init__(
            self,
            major_enable: bool = False,
            major_thickness: PlotThickness = 'thin',
            major_color: PlotColor = 'black',
            minor_enable: bool = False,
            minor_color: PlotColor = 'black',
            minor_thickness: PlotThickness = 'very thin'
    ):
        self.major_enable = major_enable
        self.major_thickness = major_thickness
        self.major_color = major_color
        self.minor_enable = minor_enable
        self.minor_color = minor_color
        self.minor_thickness = minor_thickness


class TickSetup:
    def __init__(
            self,
            enable: bool = True,  # enable / disable tick
            opposite: bool = False,  # enable ticks on opposite axis
            major_thickness: PlotThickness = 'thin',
            major_color: PlotColor = 'black',
            major_distance: Union[float, None] = None,
            minor_thickness: PlotThickness = 'thin',
            minor_color: PlotColor = 'gray',
            minor_num: int = 0
    ):
        self.enable = enable
        self.opposite = opposite
        self.major_thickness = major_thickness
        self.major_color = major_color
        self.major_distance = major_distance
        self.minor_thickness = minor_thickness
        self.minor_color = minor_color
        self.minor_num = minor_num


class LegendSetup:
    def __init__(
            self,
            enable: bool = True,
            anchor: str = 'north east',
            align: str = 'left',
            cell_align: str = 'left',
            at: tuple[float, float] = (0.98, 0.98),
            scale: float = 0.8
    ):
        """
        Create new legend setup.
        :param enable: show / hide legend
        :param anchor: based on which corner of the legend it gets positioned
        :param align:
        :param cell_align:
        :param at: position of legend anchor, x and y value in range 0...1
        :param scale: legend scale (size)
        """
        self.enable = enable
        self.anchor = anchor
        self.align = align
        self.cell_align = cell_align
        self.at = at
        self.scale = scale


class AxisSetup:
    def __init__(
            self,
            label: str = '',
            label_shift: str = '0cm',
            scale: float = 1,
            log: bool = False,
            log_base: str = '10',  # no float, otherwise the number of digits is not clear
            limits: Union[None, tuple[float, float]] = None,
            padding: float = 0,
            grid: GridSetup = GridSetup(),
            tick: TickSetup = TickSetup(),
    ):
        self.label = label
        self.label_shift = label_shift
        self.scale = scale
        self.log = log
        self.log_base = log_base
        self.limits = limits
        self.padding = padding
        self.grid = grid
        self.tick = tick


class LineSetup:
    def __init__(self, plot_color: PlotColor = 'black', line_style: LineStyle = 'solid', line_width: LineWidth = '1pt',
                 marker: Marker = '', marker_repeat: int | float = 1, marker_phase: int = 0):
        self.plot_color: PlotColor = plot_color
        self.line_style: LineStyle = line_style
        self.line_width: LineWidth = line_width
        self.marker: Marker = marker
        self.marker_repeat: int = int(marker_repeat)
        self.marker_phase: int = int(marker_phase)


class Data:
    def __init__(
            self,
            ax: XAxis,
            ay: YAxis,
            dx: TypeData,
            dy: TypeData,
            label: str = '',
            ls: Union[LineSetup, None] = None
    ):
        """
        Construct new data set.
        :param ax: axis of type x
        :param ay: axis of type y
        :param dx: data for x-axis
        :param dy: data for y-axis
        :param label: label string, supports latex
        :param ls: line-setup
        """
        assert len(dx) == len(dy)
        if ls is None:
            ls = LineSetup()  # apply default line setup
        self.ax = ax
        self.ay = ay
        self.dx = dx
        self.dy = dy
        self.label = label
        self.ls = ls
        self._id = None

    def cfg_marker(self, phase_frac: float = 0.0, n_samples=0, n_markers: int = 5) -> 'Data':
        if n_samples == 0:
            n_samples = len(self.dx)
        self.ls.marker_repeat = math.floor(n_samples / n_markers)
        self.ls.marker_phase = round((phase_frac % 1) * n_samples / n_markers)
        return self
