import os.path
import shutil
import subprocess
import sys
import tempfile
from enum import Enum
from typing import Union, Literal, get_args, Collection, cast
import numpy as np

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

LatexCmdsDocClass = [r'\documentclass[class=IEEEtran]{standalone}']
LatexCmdsAfterDocClass = [
    r'\usepackage{tikz,amsmath,siunitx}',
    r'\sisetup{range-units=repeat, list-units=repeat, binary-units, exponent-product = \cdot, print-unity-mantissa=false}',
    r'\usetikzlibrary{arrows,snakes,backgrounds,patterns,matrix,shapes,fit,calc,shadows,plotmarks}',
    r'\usepackage[graphics,tightpage,active]{preview}',
    r'\usepackage{pgfplots}',
    r'\pgfplotsset{compat=newest}',
    r'\usetikzlibrary{shapes.geometric}',
    r'\PreviewEnvironment{tikzpicture}',
    r'\PreviewEnvironment{equation}',
    r'\PreviewEnvironment{equation*}',
    r'\newlength\figurewidth',
    r'\newlength\figureheight',
]


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


class AxisSetup:
    def __init__(
            self,
            label: str = '',
            label_shift: str = '0cm',
            scale: float = 1,
            log: bool = False,
            log_base: str = '10',  # no float, otherwise the number of digits is not clear
            limits: Union[None, tuple[float, float]] = None,
            padding: str = '0cm',
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
                 marker: Marker = '', marker_repeat: int = 1, marker_phase: int = 0):
        self.plot_color: PlotColor = plot_color
        self.line_style: LineStyle = line_style
        self.line_width: LineWidth = line_width
        self.marker: Marker = marker
        self.marker_repeat: int = marker_repeat
        self.marker_phase: int = marker_phase


class Data:
    def __init__(self, ax: XAxis, ay: YAxis, dx: TypeData, dy: TypeData, ls: Union[LineSetup, None] = None):
        assert len(dx) == len(dy)
        if ls is None:
            ls = LineSetup()  # apply default line setup
        self.ax = ax
        self.ay = ay
        self.dx = dx
        self.dy = dy
        self.ls = ls


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyProtectedMember
class Figure:
    def __init__(self, title: str, width: str = '5cm', height: str = '5cm', basic_thickness: PlotThickness = 'thick', background_color: PlotColor = 'white'):
        self.title: str = title
        self.width: str = width
        self.height: str = height
        self.basic_thickness: PlotThickness = basic_thickness
        self.background_color: PlotColor = background_color
        self.axes = cast(dict[Union[XAxis, YAxis], AxisSetup], dict([(axis, None) for axis in get_args(XAxis) + get_args(YAxis)]))
        self.plot_data: list[Data] = []

    def add(self, data: Data):
        self.plot_data.append(data)

    def get_latex_code(self) -> list[str]:
        self._validate()
        return _LatexOutput(self).exec()

    def create_latex(self, path_latex: str, build: bool = True, quiet=True) -> tuple[str, str]:
        path_latex = os.path.abspath(os.path.realpath(path_latex))
        name_pdf = os.path.splitext(os.path.basename(path_latex))[0] + '.pdf'
        path_pdf = os.path.join(os.path.dirname(path_latex), name_pdf)
        with open(path_latex, 'w') as fp:
            fp.write('\n'.join(self.get_latex_code()))
        if build:
            path_tmp_dir = tempfile.mkdtemp()
            cmd = ['pdflatex', '-halt-on-error', path_latex]
            proc = subprocess.Popen(cmd, cwd=path_tmp_dir, stdout=subprocess.PIPE, stderr=sys.stdout.buffer)
            if not quiet:
                for line in proc.stdout:
                    print(line.decode('utf-8'), end='')
            proc.wait()
            path_tmp_pdf = os.path.join(path_tmp_dir, name_pdf)
            if os.path.exists(path_tmp_pdf):
                shutil.copy(path_tmp_pdf, path_pdf)
            else:
                shutil.rmtree(path_tmp_dir)
                if quiet:
                    for line in proc.stdout:
                        print(line.decode('utf-8'), end='', flush=True, file=sys.stderr)
                raise RuntimeError('compilation failed')
            shutil.rmtree(path_tmp_dir)
        return path_latex, path_pdf

    def get_axis_pos(self, val: Union[XAxis, YAxis]) -> Literal['top', 'left', 'right', 'bottom']:
        if val == 't':
            return 'top'
        elif val == 'l':
            return 'left'
        elif val == 'r':
            return 'right'
        elif val == 'b':
            return 'bottom'
        raise RuntimeError()

    def get_axis_kind(self, val: Union[XAxis, YAxis]) -> Literal['x', 'y']:
        return 'x' if val in get_args(XAxis) else ('y' if val in get_args(YAxis) else None)

    def get_opposite_axis_kind(self, axis_kind: Literal['x', 'y']) -> Literal['x', 'y']:
        return 'x' if axis_kind == 'y' else ('y' if axis_kind == 'x' else None)

    # noinspection PyTypeChecker
    def _validate(self):
        for data in self.plot_data:
            # check for unset but referenced axes
            assert self.axes[data.ax] is not None
            assert self.axes[data.ay] is not None

            # check for empty data sets
            assert len(data.dx) > 0
            assert len(data.dy) > 0

        for axis in self.axes.keys():
            # check for illegal axis keys
            assert axis in get_args(XAxis) or axis in get_args(YAxis)

            # check for empty axis limits and auto-detect them
            axis_setup: AxisSetup = self.axes[axis]
            if axis_setup is not None and axis_setup.limits is None:
                mx = -sys.float_info.min
                mn = sys.float_info.max
                for data in self.plot_data:
                    if data.ax == axis:
                        mx = max(mx, axis_setup.scale * np.max(data.dx))
                        mn = min(mn, axis_setup.scale * np.min(data.dx))
                    if data.ay == axis:
                        mx = max(mx, axis_setup.scale * np.max(data.dy))
                        mn = min(mn, axis_setup.scale * np.min(data.dy))
                axis_setup.limits = (mn, mx)

                if axis_setup.grid.major_enable and not axis_setup.tick.enable:
                    raise RuntimeError('grid_major requires ticks to be enabled')


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyProtectedMember
class _LatexOutput:
    class AxisMode(Enum):
        HIDE = 0,  # draw nothing
        SINGLE = 1,  # only init one side, e.g. left
        BOTH = 2  # init one side and the opposite, e.g. left explicitly and right implicitly

    def __init__(self, fig: Figure):
        self.fig = fig

    def exec(self):
        out = self.__create_doc_begin()
        out += self.__create_padding()
        out += self.__create_background()
        for ax in get_args(XAxis):
            for ay in get_args(YAxis):
                out += self.__create_plot_group(ax, ay)
        out += self.__create_overlay()
        out += self.__create_doc_end()
        return out

    def __fmt_flt(self, x: float) -> str:
        return f'{x:.20e}'

    def __create_doc_begin(self) -> list[str]:
        out = ['%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%']
        out += ['% auto-generated using dplot %']
        out += ['%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%']
        out += LatexCmdsDocClass
        out += LatexCmdsAfterDocClass
        out += [r'\begin{document}']
        out += [r'\setlength\figurewidth{' + self.fig.width + r'}']
        out += [r'\setlength\figureheight{' + self.fig.height + r'}']
        out += [r'\begin{tikzpicture}[font=\normalsize]']
        out += [r'\pgfplotsset{every axis/.append style={' + self.fig.basic_thickness + r'},compat=1.18},']
        return out

    def __get_axis_param(self, axis_kind: Literal['x', 'y'], axis_setup: AxisSetup, limits: Union[None, tuple[float, float]] = None) -> list[str]:
        if limits is None:
            limits = axis_setup.limits
        return [
            f'scale only axis',
            f'width={self.fig.width}',
            f'height={self.fig.height}',
            f'{axis_kind}min={self.__fmt_flt(limits[0])}',
            f'{axis_kind}max={self.__fmt_flt(limits[1])}',
        ]

    def __create_padding(self) -> list[str]:
        out = ['']
        out += ['%%%%%%%%%%%']
        out += ['% padding %']
        out += ['%%%%%%%%%%%']
        for axis in get_args(XAxis) + get_args(YAxis):
            axis_setup = self.fig.axes[axis]
            if axis_setup is None:
                continue
            axis_kind = self.fig.get_axis_kind(axis)
            axis_kind_op = self.fig.get_opposite_axis_kind(axis_kind)
            params = self.__get_axis_param(axis_kind, axis_setup, limits=(0, 1))
            params += [
                f'{axis_kind}mode=linear',
                f'log basis {axis_kind}={axis_setup.log_base}',
                f'{axis_kind_op}min=0',
                f'{axis_kind_op}max=1',
                r'xtick=\empty',
                r'ytick=\empty',
                f'hide {axis_kind_op} axis=true',
                f'{axis_kind}tick style={{draw=none}}',
                f'{axis_kind}label=' + (r'{\hphantom{-}}' if axis_kind == 'y' else r'{\vphantom{-}}'),
                f'{axis_kind}label shift={axis_setup.padding}',
                f'{axis_kind}ticklabel pos={self.fig.get_axis_pos(axis)}',
            ]
            out += [r'\begin{axis}% ' + f'{axis}-axis', r'['] + [f'  {p},' for p in params] + [r']', r'\end{axis}']
        return out

    def __create_background(self) -> list[str]:
        out = ['']
        out += ['%%%%%%%%%%%%%%']
        out += ['% background %']
        out += ['%%%%%%%%%%%%%%']
        background_color_applied = False
        for axis, axis_setup in self.fig.axes.items():
            if axis_setup is None:
                continue
            axis = cast(Union[XAxis, YAxis], axis)
            axis_setup = cast(AxisSetup, axis_setup)
            axis_kind = self.fig.get_axis_kind(axis)
            axis_kind_op = self.fig.get_opposite_axis_kind(axis_kind)
            params = self.__get_axis_param(axis_kind, axis_setup)
            if not background_color_applied:
                params += [f'axis background/.style={{fill={self.fig.background_color}}}']
                background_color_applied = True
            params += [
                f'{axis_kind}mode=' + ('log' if axis_setup.log else 'linear'),
                f'log basis {axis_kind}={axis_setup.log_base}',
                f'{axis_kind_op}min=0',
                f'{axis_kind_op}max=1',
                f'{axis_kind}label={{{axis_setup.label}}}',
                f'{axis_kind}label shift={{{axis_setup.label_shift}}}',
                r'xticklabel=\empty',
                r'yticklabel=\empty',
                f'{axis_kind}majorgrids={str(axis_setup.grid.major_enable).lower()}',
                f'major grid style={{{axis_setup.grid.major_thickness},color={axis_setup.grid.major_color}}}',
                f'{axis_kind}minorgrids={str(axis_setup.grid.minor_enable).lower()}',
                f'minor grid style={{{axis_setup.grid.minor_thickness},color={axis_setup.grid.minor_color}}}',
                f'{axis_kind}tick=' + ('' if axis_setup.tick.enable else r'\empty'),  # enable / disable major tick
                f'{axis_kind_op}tick=\\empty',  # disable tick of adjacent axes
                f'{axis_kind}tick pos=' + (r'both' if axis_setup.tick.opposite else self.fig.get_axis_pos(axis)),
                f'{axis_kind}tick distance=' + (self.__fmt_flt(axis_setup.tick.major_distance) if axis_setup.tick.major_distance is not None else r''),
                f'major {axis_kind} tick style={{{axis_setup.tick.major_thickness},color={axis_setup.tick.major_color}}}',
                f'minor {axis_kind} tick style={{{axis_setup.tick.minor_thickness},color={axis_setup.tick.minor_color}}}',
                f'minor {axis_kind} tick num={axis_setup.tick.minor_num}',
            ]
            out += [r'\begin{axis}% ' + f'{axis}-axis', r'['] + [f'  {p},' for p in params] + [r']', r'\end{axis}']
        return out

    def __create_plot_group(self, ax: XAxis, ay: YAxis) -> list[str]:
        out = ['']
        out += ['%%%%%%%%%%%%%%%%%%']
        out += [f'% plot group {ax}/{ay} %']
        out += ['%%%%%%%%%%%%%%%%%%']
        data_selected = [data for data in self.fig.plot_data if data.ax == ax and data.ay == ay]
        if len(data_selected) > 0:
            out += self.__create_plot_begin(ax, ay)
            for data in data_selected:
                out += self.__create_plot_content(ax, ay, data)
            out += self.__create_plot_end()
        return out

    def __create_plot_begin(self, ax: XAxis, ay: YAxis) -> list[str]:
        asy = cast(AxisSetup, self.fig.axes[ay])
        axis_setup = self.fig.axes[ax]
        params = self.__get_axis_param('x', axis_setup)
        params += [
            f'ymin={self.__fmt_flt(asy.limits[0])}',
            f'ymax={self.__fmt_flt(asy.limits[1])}',
            f'xmode=' + ('log' if axis_setup.log else 'linear'),
            f'log basis x={axis_setup.log_base}',
            f'ymode=' + ('log' if asy.log else 'linear'),
            f'log basis y={asy.log_base}',
            r'hide x axis=true',
            r'hide y axis=true',
            r'xtick=\empty',
            r'ytick=\empty',
        ]
        return [r'\begin{axis}', r'['] + [f'  {p},' for p in params] + [r']']

    def __create_plot_content(self, ax: XAxis, ay: YAxis, data: Data) -> list[str]:
        params_plot = [
            f'color=' + data.ls.plot_color,
            data.ls.line_style,
            f'line width={data.ls.line_width}',
            f'mark={data.ls.marker}',
            f'mark repeat={data.ls.marker_repeat}',
            f'mark phase={data.ls.marker_phase}',
        ]
        if len(data.ls.line_style) == 0:
            params_plot += ['only marks']
        if len(data.ls.marker) == 0:
            params_plot += ['no markers']

        asx = cast(AxisSetup, self.fig.axes[ax])
        asy = cast(AxisSetup, self.fig.axes[ay])
        params_table = [
            f'row sep=newline',
            f'x expr=\\thisrowno{{0}}*{self.__fmt_flt(asx.scale)}',
            f'y expr=\\thisrowno{{1}}*{self.__fmt_flt(asy.scale)}',
        ]
        out = [r'\addplot [']
        out += [f'  {p},' for p in params_plot]
        out += [r'] table [']
        out += [f'  {p},' for p in params_table]
        out += [r']{']
        for x, y in zip(data.dx, data.dy):
            out.append(f'  {self.__fmt_flt(x)} {self.__fmt_flt(y)}')
        out += [r'};']
        return out

    def __create_plot_end(self) -> list[str]:
        return [r'\end{axis}']

    def __create_overlay(self) -> list[str]:
        out = ['']
        out += ['%%%%%%%%%%%']
        out += ['% overlay %']
        out += ['%%%%%%%%%%%']
        for axis, axis_setup in self.fig.axes.items():
            if axis_setup is not None:
                axis_kind = self.fig.get_axis_kind(axis)
                axis_kind_op = self.fig.get_opposite_axis_kind(axis_kind)
                params = self.__get_axis_param(axis_kind, axis_setup)
                params += [
                    f'{axis_kind_op}min=0',
                    f'{axis_kind_op}max=1',
                    f'{axis_kind}mode=' + ('log' if axis_setup.log else 'linear'),
                    f'log basis {axis_kind}={axis_setup.log_base}',
                    f'{axis_kind}tick style={{draw=none}}',
                    f'hide {axis_kind_op} axis=true',
                    f'{axis_kind}ticklabel pos={self.fig.get_axis_pos(axis)}',
                    r'axis on top=true',
                ]
                out += [r'\begin{axis}% ' + f'{axis}-axis', r'['] + [f'  {p},' for p in params] + [r']', r'\end{axis}']
        return out

    def __create_doc_end(self) -> list[str]:
        return [
            r'\end{tikzpicture}',
            r'\end{document}',
        ]
