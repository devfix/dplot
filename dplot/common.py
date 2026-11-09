import math
from enum import Enum
from typing import Union, Literal, Collection, Optional
from dataclasses import dataclass
from itertools import repeat
from .color import Color, AnyColor, WongColorblindPalette


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
    DASHED = 'dashed'
    DASH_DOTTED = 'dashdotted'
    DASH_DOT_DOTTED = 'dashdotdotted'
    DENSELY_DOTTED = 'densely dotted'
    LOOSELY_DOTTED = 'loosely dotted'
    DENSELY_DASHED = 'densely dashed'
    LOOSELY_DASHED = 'loosely dashed'
    DENSELY_DASH_DOTTED = 'densely dashdotted'
    LOOSELY_DASH_DOTTED = 'loosely dashdotted'
    DENSELY_DASH_DOT_DOTTED = 'densely dashdotdotted'
    LOOSELY_DASH_DOT_DOTTED = 'loosely dashdotdotted'


LineStylePalette = [
    LineStyle.SOLID,
    LineStyle.DOTTED,
    LineStyle.DASHED,
    LineStyle.DASH_DOTTED,
    LineStyle.DENSELY_DOTTED,
    LineStyle.DASH_DOT_DOTTED,
    LineStyle.LOOSELY_DASHED,
    LineStyle.DENSELY_DASH_DOT_DOTTED
]

class Marker(Enum):
    NONE = 'none'
    DOT = 'dot'  # filled circle
    CIRCLE = 'circle'
    SQUARE = 'square'
    TRIANGLE = 'triangle'
    DIAMOND = 'diamond'
    CROSS = 'cross'
    PLUS = 'plus'
    ASTERISK = 'asterisk'
    SQUARE_FILLED = 'square_filled'
    TRIANGLE_FILLED = 'triangle_filled'

MarkerPalette = [Marker.CIRCLE, Marker.TRIANGLE, Marker.SQUARE, Marker.ASTERISK, Marker.DIAMOND, Marker.CROSS, Marker.PLUS, Marker.DOT, Marker.SQUARE_FILLED, Marker.TRIANGLE_FILLED]


# list() is required to enforce that an iteration always starts at the beginning of LineFormattingPalette
FormattingPalette = list(zip(WongColorblindPalette, LineStylePalette, MarkerPalette))
FormattingPaletteGrayscale = list(zip(repeat(Color.BLACK), LineStylePalette, MarkerPalette))


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
            major_values: Union[None, TypeData] = None,  # create axis values automatically (None) or specify them
            major_thickness: AnyThickness = Thickness.THIN,  # in pt
            major_color: AnyColor = Color.BLACK,
            major_distance: Union[float, None] = None,
            minor_thickness: AnyThickness = Thickness.THIN,  # in pt
            minor_color: AnyColor = Color.GRAY,
            minor_num: int = 0
    ):
        self.enable = enable
        self.opposite = opposite
        self.major_values = major_values
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


@dataclass(frozen=True)
class LineSetup:
    plot_color: AnyColor = Color.BLACK
    line_style: LineStyle = LineStyle.SOLID
    line_width: AnyThickness = Thickness.SEMITHICK
    marker: Marker = Marker.NONE
    marker_count: float = 5  # total number of markers to be shown, might be one additional if zero phase
    marker_phase: float = 0  # fraction of the marker distance by which the markers are shiftet to the right
    # marker_count is of type float since it will be converted to a discrete number of data points
    # during output generation and float allows the user fine-tuning if wished


@dataclass(frozen=True)
class CurveCompression:
    dpmm: float = 0
    n_min: int = 11


class Data:
    def __init__(
            self,
            ax: XAxis,
            ay: YAxis,
            dx: TypeData,
            dy: TypeData,
            *,
            step: Union[str, none] = None,
            label: str = '',
            ls: Union[LineSetup, None] = None,
            cc: Union[CurveCompression, None] = None
    ):
        """
        Construct new data set.
        :param ax: axis of type x
        :param ay: axis of type y
        :param dx: data for x-axis
        :param dy: data for y-axis
        :param label: label string, supports latex
        :param ls: line-setup
        :param dpmm: dots per mm for curve optimization, zero means disabled
        """
        assert len(dx) == len(dy)
        self.ax = ax
        self.ay = ay
        self.dx = dx
        self.dy = dy
        self.step = step
        self.label = label
        self.ls = LineSetup() if ls is None else ls
        self.cc = CurveCompression() if cc is None else cc
        self._id = None

@dataclass(frozen=True)
class Placement:
    ax: XAxis
    ay: YAxis
    x: float
    y: float
    body: str
    halign: HAlign = HAlign.CENTER
    valign: VAlign = VAlign.CENTER
    clip: bool = False
    z_index = 21
