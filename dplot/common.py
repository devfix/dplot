from enum import Enum
import math
from typing import Union, Literal, Collection
from .color import Color, AnyColor


# https://tikz.dev/pgfplots/reference-markers


class HAlign(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VAlign(Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class Thickness(Enum):
    ULTRA_THIN = 0.1
    VERY_THIN = 0.2
    THIN = 0.4
    SEMITHICK = 0.6
    THICK = 0.8
    VERY_THICK = 1.2
    ULTRA_THICK = 1.6


AnyThickness = Union[Thickness, float]


TypeData = Collection  # requires type to be sized and iterable
XAxis = Literal['t', 'b']  # top, bottom
YAxis = Literal['l', 'r']  # left, right


class LineStyle(Enum):
    NONE = 'none'
    SOLID = 'solid'
    DOTTED = 'dotted'
    DENSELY_DOTTED = 'densely dotted'
    LOOSELY_DOTTED = 'loosely dotted'
    DASHED = 'dashed'
    DENSELY_DASHED = 'densely dashed'
    LOOSELY_DASHED = 'loosely dashed'
    DASH_DOTTED = 'dashdotted'
    DENSELY_DASH_DOTTED = 'densely dashdotted'
    LOOSELY_DASH_DOTTED = 'loosely dashdotted'
    DASH_DOT_DOTTED = 'dashdotdotted'
    DENSELY_DASH_DOT_DOTTED = 'densely dashdotdotted'
    LOOSELY_DASH_DOT_DOTTED = 'loosely dashdotdotted'


class Marker(Enum):
    NONE = 'none'
    DOT = 'dot'
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'
    DIAMOND = 'diamond'
    CROSS = 'cross'
    PLUS = 'plus'
    ASTERISK = 'asterisk'


class Environment:
    PATH_PDFLATEX = 'pdflatex'
    PATH_PDF2SVG = 'pdf2svg'
    PATH_SCOUR = 'scour'


class GridSetup:
    def __init__(
            self,
            major_enable: bool = False,
            major_thickness: AnyThickness = Thickness.THIN,  # in pt
            major_color: AnyColor = Color.BLACK,
            minor_enable: bool = False,
            minor_color: AnyColor = Color.BLACK,
            minor_thickness: AnyThickness = Thickness.VERY_THIN  # in pt
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
            major_thickness: AnyThickness = Thickness.THIN,  # in pt
            major_color: AnyColor = Color.BLACK,
            major_distance: Union[float, None] = None,
            minor_thickness: AnyThickness = Thickness.THIN,  # in pt
            minor_color: AnyColor = Color.GRAY,
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


class AxisSetup:
    def __init__(
            self,
            label: str = '',
            label_shift: float = 0,  # in mm
            scale: float = 1,
            log: bool = False,
            log_base: str = '10',  # must be string. Use calc.e in the typst generator for euler's number
            limits: Union[None, tuple[float, float]] = None,
            grid: GridSetup = GridSetup(),
            tick: TickSetup = TickSetup(),
    ):
        self.label = label
        self.label_shift = label_shift
        self.scale = scale
        self.log = log
        self.log_base = log_base
        self.limits = limits
        self.grid = grid
        self.tick = tick


class LineSetup:
    def __init__(self, plot_color: AnyColor = Color.BLACK, line_style: LineStyle = LineStyle.SOLID, line_width: AnyThickness = 1,
                 marker: Marker = Marker.NONE, marker_repeat: int | float = 1, marker_phase: int = 0):
        self.plot_color: AnyColor = plot_color
        self.line_style: LineStyle = line_style
        self.line_width: AnyThickness = line_width
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
        self.ax = ax
        self.ay = ay
        self.dx = dx
        self.dy = dy
        self.label = label
        self.ls = LineSetup() if ls is None else ls
        self._id = None

    def cfg_marker(self, phase_frac: float = 0.0, n_samples=0, n_markers: int = 5) -> 'Data':
        if n_samples == 0:
            n_samples = len(self.dx)
        self.ls.marker_repeat = math.floor(n_samples / n_markers)
        self.ls.marker_phase = round((phase_frac % 1) * n_samples / n_markers)
        return self
