import os.path
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sized
from dataclasses import dataclass
from typing import Union, Literal, get_args, Collection, cast
import numpy as np

TypeData = Collection  # requires type to be sized and iterable
XAxis = Literal['t', 'b']  # top, bottom
YAxis = Literal['l', 'r']  # left, right
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


class LineSetup:
    pass


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyProtectedMember
class Figure:
    def __init__(self, name: str, width: str = '5.5cm', height: str = '5.5cm'):
        self._name: str = name
        self._width: str = width
        self._height: str = height
        self._axes = {'t': None, 'b': None, 'l': None, 'r': None}
        self._data: list[dict[str, Union[XAxis, YAxis, TypeData, TypeData, LineSetup]]] = []

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def axes(self):
        return self._axes

    def add_data(self, ax: XAxis, ay: YAxis, dx: TypeData, dy: TypeData, ls: Union[LineSetup, None] = None):
        assert len(dx) == len(dy)
        if ls is None:
            ls = LineSetup()  # apply default line setup
        self._data.append({'ax': ax, 'ay': ay, 'dx': dx, 'dy': dy, 'ls': ls})

    def create_latex(self, path_latex: str, build: bool = True, quiet=False):
        path_latex = os.path.abspath(path_latex)
        self._validate()
        out = _LatexOutput(self).exec()
        print('\n'.join(out))
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

    def _get_axis_by_val(self, val: Union[XAxis, YAxis]):
        return 'ax' if val in get_args(XAxis) else ('ay' if val in get_args(YAxis) else None)

    # noinspection PyTypeChecker
    def _validate(self):

        for data in self._data:
            # check for unset but referenced axes
            assert self._axes[data['ax']] is not None
            assert self._axes[data['ay']] is not None

            # check for empty data sets
            assert len(data['dx']) > 0
            assert len(data['dy']) > 0

        for axis in self._axes.keys():
            # check for illegal axis keys
            assert axis in get_args(XAxis) or axis in get_args(YAxis)

            # check for empty axis limits and auto-detect them
            axis_setup: AxisSetup = self._axes[axis]
            if axis_setup is not None and axis_setup.limits is None:
                mx = sys.float_info.min
                mn = sys.float_info.max
                for data in self._data:
                    if data['ax'] == axis:
                        mx = max(mx, axis_setup.scale * np.max(data['dx']))
                        mn = min(mn, axis_setup.scale * np.min(data['dx']))
                    if data['ay'] == axis:
                        mx = max(mx, axis_setup.scale * np.max(data['dy']))
                        mn = min(mn, axis_setup.scale * np.min(data['dy']))
                axis_setup.limits = (mn, mx)


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyProtectedMember
class _LatexOutput:
    def __init__(self, fig: Figure):
        self.fig = fig

    def exec(self):
        out = self.__create_doc_begin()

        data_bl, data_br, data_tl, data_tr = self.__get_wrapped_data()

        # each axis (b,t,l,r) is only prepared if the first data set using this axis occurred
        # the same holds if the last data set occurs and the axis should be ended
        for data, init_x_axis, init_y_axis in [data_bl, data_br, data_tl, data_tr]:
            ax: XAxis = cast(XAxis, data[0]['ax'])
            ay: YAxis = cast(YAxis, data[0]['ay'])
            out += self.__create_axis_begin(ax, ay)
            for d in data:
                out += self.__create_plot(self.fig._axes[d['ax']], self.fig._axes[d['ay']], d['dx'], d['dy'])
            out += self.__create_axis_end()
        out += self.__create_doc_end()
        return out

    def __fmt_flt(self, x: float) -> str:
        return f'{x:.20e}'

    def __create_doc_begin(self) -> list[str]:
        out = LatexCmdsDocClass
        out += LatexCmdsAfterDocClass
        out += [r'\begin{document}']
        out += [r'\setlength\figurewidth{' + self.fig._width + r'}']
        out += [r'\setlength\figureheight{' + self.fig._height + r'}']
        out += [r'\begin{tikzpicture}[font=\normalsize]']
        out += [r'\pgfplotsset{every axis/.append style={very thick},compat=1.18},']
        return out

    def __get_wrapped_data(self):
        def get_first_idx(axis: Union[XAxis, YAxis]):
            return next((idx for idx, data in enumerate(self.fig._data) if data[self.fig._get_axis_by_val(axis)] == axis), -1)

        def get_last_idx(axis: Union[XAxis, YAxis]):
            return next((idx for idx, data in reversed(list(enumerate(self.fig._data))) if data[self.fig._get_axis_by_val(axis)] == axis), -1)

        # wrapping each data entry is associated with the start and/or begin of an x or y-axis
        def wrap_data(idxs: dict[str, tuple[int, int]], ax: XAxis, ay: YAxis):
            data_idxs = [idx for idx, d in enumerate(self.fig._data) if d['ax'] ==ax and d['ay'] == ay]
            data = [d for d in self.fig._data if d['ax'] ==ax and d['ay'] == ay]
            return data, idxs[ax][1] in data_idxs, idxs[ay][1] in data_idxs
            # return [(tup, ( == idx, idxs[ax][1] == idx, idxs[ay][0] == idx, idxs[ay][1] == idx))
            #         for idx, tup in enumerate(self.fig._data) if tup['ax'] == ax and tup['ay'] == ay]

        self.fig._data.sort(key=lambda data: data['ax'] + data['ay'])  # sort by b/t, l/r

        idxs = {
            'b': (get_first_idx('b'), get_last_idx('b')),
            't': (get_first_idx('t'), get_last_idx('t')),
            'l': (get_first_idx('l'), get_last_idx('l')),
            'r': (get_first_idx('r'), get_last_idx('r')),
        }

        return wrap_data(idxs, 'b', 'l'), wrap_data(idxs, 'b', 'r'), wrap_data(idxs, 't', 'l'), wrap_data(idxs, 't', 'r')

    def __create_axis_begin(self, ax: XAxis, ay: YAxis) -> list[str]:
        asx: AxisSetup = self.fig._axes[ax]
        asy: AxisSetup = self.fig._axes[ay]
        params = [
            f'scale only axis',
            f'width={self.fig._width}',
            f'height={self.fig._height}',
            f'xmin={self.__fmt_flt(asx.limits[0])}',
            f'xmax={self.__fmt_flt(asx.limits[1])}',
            f'axis x line*=' + ('bottom' if ax == 'b' else 'top'),
            f'axis y line*=' + ('left' if ay == 'l' else 'right'),
            f'xlabel={asx.name},'
            f'ylabel={asy.name},'
        ]
        return [r'\begin{axis}', r'['] + [f'  {p},' for p in params] + [r']']

    def __create_plot(self, asx: AxisSetup, asy: AxisSetup, dx: TypeData, dy: TypeData) -> list[str]:
        params_plot = [
            f'color=black',
            f'dotted',
            f'mark phase=0'
        ]
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
