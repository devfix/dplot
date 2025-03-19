import os.path
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sized
from dataclasses import dataclass
from enum import Enum
from typing import Union, Literal, get_args, Collection, cast
import numpy as np

TypeData = Collection  # requires type to be sized and iterable
XAxis = Literal['t', 'b']  # top, bottom
YAxis = Literal['l', 'r']  # left, right
# https://tikz.dev/pgfplots/reference-markers
LineStyle = Literal['', 'solid', 'dotted', 'densely dotted', 'loosely dotted', 'dashed', 'densely dashed', 'loosely dashed', 'dashdotted',
'densely dashdotted', 'loosely dashdotted', 'dashdotdotted', 'densely dashdotdotted', 'loosely dashdotdotted']
PlotColor = Union[str, Literal['black', 'red', 'green', 'blue', 'cyan', 'magenta', 'yellow', 'gray', 'white', 'darkgray', 'lightgray', 'brown',
'lime', 'olive', 'orange', 'pink', 'purple', 'teal', 'violet']]
PlotThickness = Literal['very thin', 'thin', 'thick', 'very thick']
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


@dataclass
class AxisSetup:
    name: str = ''
    scale: float = 1
    log: bool = False
    limits: Union[None, tuple[float, float]] = None
    grid_major_enable: bool = False
    grid_major_color: PlotColor = 'black'
    grid_major_thickness: PlotThickness = 'thin'
    grid_minor_enable: bool = False
    grid_minor_color: PlotColor = 'black'
    grid_minor_thickness: PlotThickness = 'very thin'
    tick_enable: bool = True  # enable / disable tick
    tick_opposite: bool = False  # enable ticks on opposite axis
    tick_major_thickness: PlotThickness = 'thin'
    tick_major_color: PlotColor = 'black'
    tick_major_distance: Union[float, None] = None
    tick_minor_thickness: PlotThickness = 'thin'
    tick_minor_color: PlotColor = 'gray'
    tick_minor_num: int = 0


class LineSetup:
    def __init__(self, plot_color: PlotColor = 'black', line_style: LineStyle = 'solid', line_thickness: PlotThickness = 'thin',
                 marker: Marker = '', marker_repeat: int = 1, marker_phase: int = 0):
        self.plot_color: PlotColor = plot_color
        self.line_style: LineStyle = line_style
        self.line_thickness: PlotThickness = line_thickness
        self.marker: Marker = marker
        self.marker_repeat: int = marker_repeat
        self.marker_phase: int = marker_phase


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyProtectedMember
class Figure:
    def __init__(self, title: str, width: str = '5cm', height: str = '5cm', basic_thickness: PlotThickness = 'thick', background_color: PlotColor = 'white'):
        self.title: str = title
        self.width: str = width
        self.height: str = height
        self.basic_thickness: PlotThickness = basic_thickness
        self.background_color: PlotColor = background_color
        self.axes = dict([(axis, None) for axis in get_args(XAxis) + get_args(YAxis)])
        self.data: list[dict[str, Union[XAxis, YAxis, TypeData, TypeData, LineSetup]]] = []

    def add_data(self, ax: XAxis, ay: YAxis, dx: TypeData, dy: TypeData, ls: Union[LineSetup, None] = None):
        assert len(dx) == len(dy)
        if ls is None:
            ls = LineSetup()  # apply default line setup
        self.data.append({'ax': ax, 'ay': ay, 'dx': dx, 'dy': dy, 'ls': ls})

    def create_latex(self, path_latex: str, build: bool = True, quiet=False):
        path_latex = os.path.abspath(path_latex)
        self._validate()
        out = _LatexOutput(self).exec()
        with open(path_latex, 'w') as fp:
            fp.write('\n'.join(out))

        if build:
            path_tmp_dir = tempfile.mkdtemp()
            cmd = ['pdflatex', '-halt-on-error', path_latex]
            sout = subprocess.DEVNULL if quiet else sys.stdout.buffer
            subprocess.call(cmd, cwd=path_tmp_dir, stdout=sout, stderr=sout)
            name_pdf = os.path.splitext(os.path.basename(path_latex))[0] + '.pdf'
            path_tmp_pdf = os.path.join(path_tmp_dir, name_pdf)
            path_pdf = os.path.join(os.path.dirname(path_latex), name_pdf)
            if os.path.exists(path_tmp_pdf):
                shutil.copy(path_tmp_pdf, path_pdf)
            else:
                shutil.rmtree(path_tmp_dir)
                raise RuntimeError('compilation failed')
            shutil.rmtree(path_tmp_dir)

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

        for data in self.data:
            # check for unset but referenced axes
            assert self.axes[data['ax']] is not None
            assert self.axes[data['ay']] is not None

            # check for empty data sets
            assert len(data['dx']) > 0
            assert len(data['dy']) > 0

        for axis in self.axes.keys():
            # check for illegal axis keys
            assert axis in get_args(XAxis) or axis in get_args(YAxis)

            # check for empty axis limits and auto-detect them
            axis_setup: AxisSetup = self.axes[axis]
            if axis_setup is not None and axis_setup.limits is None:
                mx = sys.float_info.min
                mn = sys.float_info.max
                for data in self.data:
                    if data['ax'] == axis:
                        mx = max(mx, axis_setup.scale * np.max(data['dx']))
                        mn = min(mn, axis_setup.scale * np.min(data['dx']))
                    if data['ay'] == axis:
                        mx = max(mx, axis_setup.scale * np.max(data['dy']))
                        mn = min(mn, axis_setup.scale * np.min(data['dy']))
                axis_setup.limits = (mn, mx)

                if axis_setup.grid_major_enable and not axis_setup.tick_enable:
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
        out += self.__create_background()

        # data_bl, data_br, data_tl, data_tr = self.__get_wrapped_data()
        #
        # # each axis (b,t,l,r) is only prepared if the first data set using this axis occurred
        # # the same holds if the last data set occurs and the axis should be ended
        # for data, ax_mode, ay_mode in [data_bl, data_br, data_tl, data_tr]:
        #     if len(data) == 0:
        #         continue
        #     ax: XAxis = cast(XAxis, data[0]['ax'])
        #     ay: YAxis = cast(YAxis, data[0]['ay'])
        #     out += self.__create_axis_begin(ax, ay, ax_mode, ay_mode)
        #     for d in data:
        #         out += self.__create_plot(self.fig.axes[d['ax']], self.fig.axes[d['ay']], cast(TypeData, d['dx']), cast(TypeData, d['dy']),
        #                                   cast(LineSetup, d['ls']))
        #     out += self.__create_axis_end()
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

    def __get_axis_param(self, axis_type: Literal['x', 'y'], axis_setup: AxisSetup) -> list[str]:
        return [
            f'scale only axis',
            f'width={self.fig.width}',
            f'height={self.fig.height}',
            f'{axis_type}min={self.__fmt_flt(axis_setup.limits[0])}',
            f'{axis_type}max={self.__fmt_flt(axis_setup.limits[1])}',
        ]

    def __create_background(self) -> list[str]:
        out = []
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
                f'{axis_kind_op}min=0',
                f'{axis_kind_op}max=1',
                r'xticklabel=\empty',
                r'yticklabel=\empty',
                f'{axis_kind}majorgrids={str(axis_setup.grid_major_enable).lower()}',
                f'major grid style={{{axis_setup.grid_major_thickness},color={axis_setup.grid_major_color}}}',
                f'{axis_kind}minorgrids={str(axis_setup.grid_minor_enable).lower()}',
                f'minor grid style={{{axis_setup.grid_minor_thickness},color={axis_setup.grid_minor_color}}}',
                f'{axis_kind}tick=' + ('' if axis_setup.tick_enable else r'\empty'),  # enable / disable major tick
                f'{axis_kind_op}tick=\\empty',  # disable tick of adjacent axes
                f'{axis_kind}tick pos=' + (r'both' if axis_setup.tick_opposite else self.fig.get_axis_pos(axis)),
                f'{axis_kind}tick distance=' + (str(axis_setup.tick_major_distance) if axis_setup.tick_major_distance is not None else r''),
                f'major {axis_kind} tick style={{{axis_setup.tick_major_thickness},color={axis_setup.tick_major_color}}}',
                f'minor {axis_kind} tick style={{{axis_setup.tick_minor_thickness},color={axis_setup.tick_minor_color}}}',
                f'minor {axis_kind} tick num={axis_setup.tick_minor_num}',
            ]
            out += [r'\begin{axis}', r'['] + [f'  {p},' for p in params] + [r']', r'\end{axis}']
        return out

    def __get_wrapped_data(self):
        def get_first_idx(axis: Union[XAxis, YAxis]):
            return next((idx for idx, data in enumerate(self.fig.data) if data[self.fig.get_axis_kind(axis)] == axis[1]), -1)

        def get_last_idx(axis: Union[XAxis, YAxis]):
            return next((idx for idx, data in reversed(list(enumerate(self.fig.data))) if data[self.fig.get_axis_kind(axis)] == axis[1]), -1)

        # wrapping each data entry is associated with the start and/or begin of an x or y-axis
        def wrap_data(idxs: dict[str, tuple[int, int]], ax: XAxis, ay: YAxis):
            data_idxs = [idx for idx, d in enumerate(self.fig.data) if d['ax'] == ax and d['ay'] == ay]
            data = [d for d in self.fig.data if d['ax'] == ax and d['ay'] == ay]
            return data, idxs[ax][1] in data_idxs, idxs[ay][1] in data_idxs

        def get_axis_mode(init: bool, multiple: bool):
            return _LatexOutput.AxisMode.HIDE if not init else (_LatexOutput.AxisMode.SINGLE if multiple else _LatexOutput.AxisMode.BOTH)

        self.fig.data.sort(key=lambda data: data['ax'] + data['ay'])  # sort by b/t, l/r

        idxs = {
            'b': (get_first_idx('b'), get_last_idx('b')),
            't': (get_first_idx('t'), get_last_idx('t')),
            'l': (get_first_idx('l'), get_last_idx('l')),
            'r': (get_first_idx('r'), get_last_idx('r')),
        }

        datas = [wrap_data(idxs, 'b', 'l'), wrap_data(idxs, 'b', 'r'), wrap_data(idxs, 't', 'l'), wrap_data(idxs, 't', 'r')]
        multiple_init_x = len([init_x for data, init_x, init_y in datas if init_x]) > 1
        multiple_init_y = len([init_y for data, init_x, init_y in datas if init_y]) > 1
        return [(data, get_axis_mode(init_x, multiple_init_x), get_axis_mode(init_y, multiple_init_y)) for data, init_x, init_y in datas]

    def __create_axis_begin(self, ax: XAxis, ay: YAxis, ax_mode: AxisMode, ay_mode: AxisMode) -> list[str]:
        asx = cast(AxisSetup, self.fig.axes[ax])
        asy = cast(AxisSetup, self.fig.axes[ay])
        params = [
            f'scale only axis',
            f'width={self.fig.width}',
            f'height={self.fig.height}',
            f'xmin={self.__fmt_flt(asx.limits[0])}',
            f'xmax={self.__fmt_flt(asx.limits[1])}',
            f'ymin={self.__fmt_flt(asy.limits[0])}',
            f'ymax={self.__fmt_flt(asy.limits[1])}',
            f'xlabel={{{asx.name}}}',
            f'ylabel={{{asy.name}}}',
        ]
        if ax_mode == _LatexOutput.AxisMode.SINGLE:
            params += [f'axis x line*=' + ('bottom' if ax == 'b' else 'top')]
        elif ax_mode == _LatexOutput.AxisMode.HIDE:
            params += ['hide x axis=true']
        if ay_mode == _LatexOutput.AxisMode.SINGLE:
            params += [f'axis y line*=' + ('left' if ay == 'l' else 'right')]
        elif ay_mode == _LatexOutput.AxisMode.HIDE:
            params += ['hide y axis=true']

        if asx.grid_major_enable:
            params += ['xmajorgrids']
        if asy.grid_major_enable:
            params += ['ymajorgrids']

        return [r'\begin{axis}', r'['] + [f'  {p},' for p in params] + [r']']

    def __create_plot(self, asx: AxisSetup, asy: AxisSetup, dx: TypeData, dy: TypeData, ls: LineSetup) -> list[str]:
        params_plot = [
            f'color=' + ls.plot_color,
            ls.line_style,
            f'line width={ls.line_thickness}pt',
            f'mark={ls.marker}',
            f'mark repeat={ls.marker_repeat}',
            f'mark phase={ls.marker_phase}',
        ]
        if len(ls.line_style) == 0:
            params_plot += ['only marks']
        if len(ls.marker) == 0:
            params_plot += ['no markers']

        params_table = [
            f'row sep=newline',
            f'x expr=\\thisrowno{{0}}*{self.__fmt_flt(asx.scale)}',
            f'y expr=\\thisrowno{{1}}*{self.__fmt_flt(asy.scale)}',
        ]
        out = (
                [r'\addplot ['] +
                [f'  {p},' for p in params_plot] +
                [r'] table ['] +
                [f'  {p},' for p in params_table] +
                [r']{']
        )
        for idx, (x, y) in enumerate(zip(dx, dy)):
            out.append(f'  {self.__fmt_flt(x)} {self.__fmt_flt(y)}')
        out += [r'};']
        return out

    def __create_axis_end(self) -> list[str]:
        return [r'\end{axis}']

    def __create_doc_end(self):
        return [
            r'\end{tikzpicture}',
            r'\end{document}',
        ]
