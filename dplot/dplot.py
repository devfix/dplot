import enum
import math
import os.path
import shutil
import subprocess
import sys
import tempfile
from enum import Enum
from itertools import chain
from typing import Union, Literal, get_args, Collection, cast
import numpy as np

# import matplotlib
# matplotlib.use('gtk3agg')
import matplotlib.pyplot as plt

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


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyProtectedMember
class Figure:
    def __init__(self, name: str, title: str = '', width: str = '5cm', height: str = '5cm', basic_thickness: PlotThickness = 'thick',
                 background_color: PlotColor = 'white',
                 legend_setup: LegendSetup = LegendSetup()):
        self.name: str = name
        self.title: str = title
        self.width: str = width
        self.height: str = height
        self.basic_thickness: PlotThickness = basic_thickness
        self.background_color: PlotColor = background_color
        self.legend_setup = legend_setup
        self.axes = cast(dict[Union[XAxis, YAxis], AxisSetup], dict([(axis, None) for axis in get_args(XAxis) + get_args(YAxis)]))
        self.plot_data: list[Data] = []
        self._data_counter = 0

    def add(self, data: Data):
        data._id = self._data_counter
        self._data_counter += 1
        self.plot_data.append(data)

    def plot(
            self,
            ax: XAxis,
            ay: YAxis,
            dx: TypeData,
            dy: TypeData,
            label: str = '',
            ls: Union[LineSetup, None] = None
    ) -> Data:
        data = Data(ax=ax, ay=ay, dx=dx, dy=dy, label=label, ls=ls)
        self.add(data)
        return data

    def get_latex_code(self) -> list[str]:
        self._validate()
        return _LatexOutput(self).exec()

    def export(self, path_out_dir: str, *types, quiet=True):
        types: list[ExportType] = list(types)
        if len(types) == 0:
            raise RuntimeError('at least one output type is required')
        for t in types:
            assert isinstance(t, ExportType)
        required_types = set(types)
        if ExportType.SVG in required_types:
            required_types.add(ExportType.PDF)
        if ExportType.PDF in required_types:
            required_types.add(ExportType.LATEX)

        path_out_dir = os.path.abspath(path_out_dir)
        path_latex = os.path.join(path_out_dir, self.name + '.tex')
        path_pdf = os.path.join(path_out_dir, self.name + '.pdf')
        path_svg = os.path.join(path_out_dir, self.name + '.svg')
        os.makedirs(path_out_dir, exist_ok=True)

        if ExportType.LATEX in required_types:
            with open(path_latex, 'w') as fp:
                fp.write('\n'.join(self.get_latex_code()))
        if ExportType.PDF in required_types:
            self._cvt_latex_to_pdf(path_latex, path_pdf, quiet)
        if ExportType.SVG in required_types:
            self._cvt_pdf_to_svg(path_pdf, path_svg, quiet)

        if ExportType.LATEX not in types and os.path.exists(path_latex):
            os.remove(path_latex)
        if ExportType.PDF not in types and os.path.exists(path_pdf):
            os.remove(path_pdf)
        if ExportType.SVG not in types and os.path.exists(path_svg):
            os.remove(path_svg)

        type_map = {
            ExportType.LATEX: path_latex,
            ExportType.PDF: path_pdf,
            ExportType.SVG: path_svg
        }
        return tuple([type_map[t] for t in types])

    def show(self):
        _MatplotlibView(self).show()

    def _cvt_latex_to_pdf(self, path_latex: str, path_pdf: str, quiet=True):
        if shutil.which(Environment.PATH_PDFLATEX) is None:
            raise FileNotFoundError(Environment.PATH_PDFLATEX)

        path_tmp_dir = tempfile.mkdtemp()
        cmd = [Environment.PATH_PDFLATEX, '-synctex=1', '-interaction=nonstopmode', path_latex]

        # 1st latex compilation run
        proc = subprocess.Popen(cmd, cwd=path_tmp_dir, stdout=subprocess.PIPE, stderr=sys.stdout.buffer)
        if not quiet:
            for line in proc.stdout:
                print(line.decode('utf-8'), end='')
        proc.wait()

        # 2nd latex compilation run
        proc2 = subprocess.Popen(cmd, cwd=path_tmp_dir, stdout=subprocess.PIPE, stderr=sys.stdout.buffer)
        if not quiet:
            for line in proc2.stdout:
                print(line.decode('utf-8'), end='')
        proc2.wait()

        path_tmp_pdf = os.path.join(path_tmp_dir, os.path.basename(path_pdf))
        if os.path.exists(path_tmp_pdf):
            shutil.copy(path_tmp_pdf, path_pdf)
        else:
            shutil.rmtree(path_tmp_dir)
            if quiet:  # if quiet, no output so far. Due to that we report all output now,
                for line in chain(proc.stdout, proc2.stdout):
                    print(line.decode('utf-8'), end='', flush=True, file=sys.stderr)
            raise RuntimeError('compilation failed')
        shutil.rmtree(path_tmp_dir)

    def _cvt_pdf_to_svg(self, path_pdf: str, path_svg: str, quiet: bool):
        if shutil.which(Environment.PATH_PDF2SVG) is None:
            raise FileNotFoundError(Environment.PATH_PDF2SVG)

        path_svg_tmp = path_svg + '.tmp.svg'
        cmd = [Environment.PATH_PDF2SVG, path_pdf, path_svg_tmp]
        subprocess.call(cmd, stdout=subprocess.DEVNULL if quiet else sys.stdout.buffer, stderr=subprocess.DEVNULL if quiet else sys.stderr.buffer)

        if shutil.which(Environment.PATH_SCOUR) is None:
            print('warning: scour not found, skipping svg optimization', file=sys.stderr)
            os.rename(path_svg_tmp, path_svg)
        else:
            cmd = [Environment.PATH_SCOUR, '-i', path_svg_tmp, '-o', path_svg]
            subprocess.call(cmd, stdout=subprocess.DEVNULL if quiet else sys.stdout.buffer, stderr=subprocess.DEVNULL if quiet else sys.stderr.buffer)
            os.remove(path_svg_tmp)

    @staticmethod
    def get_axis_pos(axis: Union[XAxis, YAxis]) -> Literal['top', 'left', 'right', 'bottom']:
        if axis == 't':
            return 'top'
        elif axis == 'l':
            return 'left'
        elif axis == 'r':
            return 'right'
        elif axis == 'b':
            return 'bottom'
        raise RuntimeError()

    @staticmethod
    def get_axis_kind(val: Union[XAxis, YAxis]) -> Literal['x', 'y']:
        return 'x' if val in get_args(XAxis) else ('y' if val in get_args(YAxis) else None)

    @staticmethod
    def get_opposite_axis_kind(axis_kind: Literal['x', 'y']) -> Literal['x', 'y']:
        return 'x' if axis_kind == 'y' else ('y' if axis_kind == 'x' else None)

    @staticmethod
    def get_opposite_axis(axis: Union[XAxis, YAxis]) -> Union[XAxis, YAxis]:
        if axis == 'l':
            return 'r'
        elif axis == 'r':
            return 'l'
        elif axis == 't':
            return 'b'
        elif axis == 'b':
            return 't'
        raise RuntimeError(f'invalid axis: {axis}')

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
        self.overscale_limit = 1e10

    def exec(self):
        out = self.__create_doc_begin()
        out += self.__create_padding()
        out += self.__create_background()
        for ax in get_args(XAxis):
            for ay in get_args(YAxis):
                out += self.__create_plot_group(ax, ay)
        out += self.__create_overlay()
        if self.fig.legend_setup.enable:
            out += self.__create_legend()
        out += self.__create_doc_end()
        return out

    def __get_y_domain(self, asy: AxisSetup):
        if asy.limits is None:
            return None
        if asy.log:  # y domain does somehow not work for logarithmic plots
            return None

        # pgfplot encounters a probem if values are way outside the limits
        # -> If we would just clip the data precisely to the limits, this can change the shape
        # of the plat drastically, especially for a low number of data points.
        # The overscale_limit is a workaround, setting it higher increases the quality
        # but at some point pgfplots just gives up does not render correctly.
        mn = asy.limits[0] / self.overscale_limit if asy.limits[0] > 0 else asy.limits[0] * self.overscale_limit
        mx = asy.limits[1] * self.overscale_limit if asy.limits[1] > 0 else asy.limits[1] / self.overscale_limit
        return mn, mx

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

    def __get_axis_param(self, axis_kind: Literal['x', 'y'], axis_setup: Union[AxisSetup, None], limits: Union[None, tuple[float, float]] = None) -> list[str]:
        if limits is None:
            assert axis_setup is not None
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
            axis_kind = Figure.get_axis_kind(axis)
            axis_kind_op = Figure.get_opposite_axis_kind(axis_kind)
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
                f'{axis_kind}ticklabel pos={Figure.get_axis_pos(axis)}',
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
            axis_kind = Figure.get_axis_kind(axis)
            axis_kind_op = Figure.get_opposite_axis_kind(axis_kind)
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
                f'{axis_kind}tick pos=' + (r'both' if axis_setup.tick.opposite else Figure.get_axis_pos(axis)),
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
        asy = cast(AxisSetup, self.fig.axes[ay])
        y_domain = self.__get_y_domain(asy)
        params_plot = [
            f'color=' + data.ls.plot_color,
            data.ls.line_style,
            f'line width={data.ls.line_width}',
            f'mark={data.ls.marker}',
            f'mark repeat={data.ls.marker_repeat}',
            f'mark phase={data.ls.marker_phase}',
            f'mark options={{solid}}',  # prevent dashed markers etc.
        ]
        if len(data.ls.line_style) == 0:
            params_plot += ['only marks']
        if len(data.ls.marker) == 0:
            params_plot += ['no markers']
        if y_domain is not None:
            params_plot += [f'restrict y to domain={{{self.__fmt_flt(y_domain[0])}:{self.__fmt_flt(y_domain[1])}}}']

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
        out += [f'\\label{{dplot:{data._id}}}']
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
                axis_kind = Figure.get_axis_kind(axis)
                axis_kind_op = Figure.get_opposite_axis_kind(axis_kind)
                params = self.__get_axis_param(axis_kind, axis_setup)
                params += [
                    f'{axis_kind_op}min=0',
                    f'{axis_kind_op}max=1',
                    f'{axis_kind}mode=' + ('log' if axis_setup.log else 'linear'),
                    f'log basis {axis_kind}={axis_setup.log_base}',
                    f'{axis_kind}tick style={{draw=none}}',
                    f'{axis_kind}tick distance=' + (self.__fmt_flt(axis_setup.tick.major_distance) if axis_setup.tick.major_distance is not None else r''),
                    f'hide {axis_kind_op} axis=true',
                    f'{axis_kind}ticklabel pos={Figure.get_axis_pos(axis)}',
                    r'axis on top=true',
                ]

                out += [r'\begin{axis}% ' + f'{axis}-axis', r'['] + [f'  {p},' for p in params] + [r']', r'\end{axis}']
        return out

    def __create_legend(self) -> list[str]:
        out = ['']
        out += ['%%%%%%%%%%']
        out += ['% legend %']
        out += ['%%%%%%%%%%']
        legend_style = [
            f'at={{({self.__fmt_flt(self.fig.legend_setup.at[0])},{self.__fmt_flt(self.fig.legend_setup.at[1])})}}',
            f'anchor={self.fig.legend_setup.anchor}',
            f'legend cell align={self.fig.legend_setup.cell_align}',
            f'align={self.fig.legend_setup.align}',
            f'nodes={{scale={self.__fmt_flt(self.fig.legend_setup.scale)}, transform shape}}'
        ]
        params = self.__get_axis_param('x', None, limits=(0, 1))
        params += [
            f'ymin=0',
            f'ymax=1',
            f'xmode=linear',
            f'hide x axis=true',
            f'hide y axis=true',
            r'axis on top=true',
            r'legend style={' + ', '.join(legend_style) + r'}'
        ]
        out += [
            r'\begin{axis}',
            r'['
        ]
        out += [f'  {p},' for p in params]
        out += [r']']
        for data in self.fig.plot_data:
            label = data.label if len(data.label) > 0 else str(data._id)
            out.append(r'\addlegendimage{/pgfplots/refstyle=dplot:' + str(data._id) + r'}\addlegendentry{' + label + r'}')
        out += [r'\end{axis}']
        return out

    def __create_doc_end(self) -> list[str]:
        return [
            r'\end{tikzpicture}',
            r'\end{document}',
        ]


class _MatplotlibView:
    def __init__(self, fig: Figure):
        self.fig = fig

    def show(self):
        custom_params = {
            'text.usetex': True,
            'font.family': 'serif',
            'text.latex.preamble': r'''
                \usepackage{siunitx}
                \usepackage{amsmath}
            '''
        }
        with plt.rc_context(custom_params):
            self._show_pyplot()

    def _show_pyplot(self):
        plt_fig, plot_initial = plt.subplots(figsize=(10, 6))
        plt.get_current_fig_manager().set_window_title(self.fig.title if len(self.fig.title) > 0 else self.fig.name)

        required_axes = {axis: axis_setup for axis, axis_setup in self.fig.axes.items() if axis_setup is not None}
        plots = {'t': {'l': None, 'r': None}, 'b': {'l': None, 'r': None}}

        # create initial x-y relation
        x_side: XAxis = 'b'
        y_side: YAxis = 'l'
        if 'l' not in required_axes:
            # move y-axis to right side
            y_side = 'r'
            plot_initial.yaxis.set_label_position("right")
            plot_initial.yaxis.tick_right()
        if 'b' not in required_axes:
            # move axis to top
            x_side = 't'
            plot_initial.xaxis.set_ticks_position('top')

        plots[x_side][y_side] = plot_initial  # initial relation (plot)
        axes = {x_side: plot_initial, y_side: plot_initial}

        x_side_opp = Figure.get_opposite_axis(x_side)
        y_side_opp = Figure.get_opposite_axis(y_side)
        if y_side_opp in required_axes:
            plots[x_side][y_side_opp] = plot_initial.twinx()
            axes[y_side_opp] = plots[x_side][y_side_opp]
        if x_side_opp in required_axes:
            plots[x_side_opp][y_side] = plot_initial.twiny()
            axes[x_side_opp] = plots[x_side_opp][y_side]
        if x_side_opp in required_axes and y_side_opp in required_axes:
            plots[x_side_opp][y_side_opp] = plots[x_side][y_side_opp].twiny()

        for data in self.fig.plot_data:
            ax: plt.Axes = plots[data.ax][data.ay]
            plot_color = data.ls.plot_color if data.ls is not None else 'black'
            line_style = data.ls.line_style if data.ls is not None else '-'
            label = data.label if len(data.label) > 0 else None
            ax.plot(data.dx, data.dy, color=plot_color, linestyle=line_style, label=label)

        for axis, axis_setup in required_axes.items():
            if axis_setup.limits is not None:
                getattr(axes[axis], f'set_{Figure.get_axis_kind(axis)}lim')(axis_setup.limits)
            if axis_setup.label is not None:
                getattr(axes[axis], f'set_{Figure.get_axis_kind(axis)}label')(axis_setup.label)
            if axis_setup.log:
                getattr(axes[axis], f'set_{Figure.get_axis_kind(axis)}scale')('log', base=float(axis_setup.log_base))

        if self.fig.legend_setup.enable:
            plot_initial.legend()

        plt.tight_layout()
        plt.show(block=True)

        # plot_initial.tick_params(axis='y', colors='blue')
        # ax_br.tick_params(axis='y', colors='red')
        # plot_initial.tick_params(axis='x', colors='blue')
        # ax_tl.tick_params(axis='x', colors='green')
