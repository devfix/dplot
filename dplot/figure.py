import os.path
import shutil
import subprocess
import sys
from typing import cast, get_args
import numpy as np

from .common import *


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyProtectedMember
class Figure:
    def __init__(self, name: str, title: str = '', width: float = 50, height: float = 50, basic_thickness: PlotThickness = 'thick',
                 background_color: PlotColor = 'white', legend_setup: LegendSetup = LegendSetup()):
        self.name: str = name
        self.title: str = title
        self.width: float = width
        self.height: float = height
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
    def validate(self):
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
