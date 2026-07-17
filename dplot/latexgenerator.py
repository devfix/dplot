import os.path
import shutil
import subprocess
import sys
import tempfile
from enum import Enum
from itertools import chain
from typing import cast, get_args

from .color import color_to_pgfplots_color, color_to_pgfplots_options
from .common import *
from .figure import Figure

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


# noinspection PyShadowingNames,PyMethodMayBeStatic,PyProtectedMember
class LatexGenerator:
    class AxisMode(Enum):
        HIDE = 0,  # draw nothing
        SINGLE = 1,  # only init one side, e.g. left
        BOTH = 2  # init one side and the opposite, e.g. left explicitly and right implicitly

    def __init__(self, fig: Figure):
        self.fig = fig
        self.overscale_limit = 1e10

    def get_latex_code(self) -> list[str]:
        self.fig.validate()
        out = self.__create_doc_begin()
        out += self.__create_plot_margin()
        out += self.__create_background()
        for ax in get_args(XAxis):
            for ay in get_args(YAxis):
                out += self.__create_plot_group(ax, ay)
        out += self.__create_overlay()
        if self.fig.legend_setup.enable:
            out += self.__create_legend()
        out += self.__create_doc_end()
        return out

    def export(self, path_output_dir: str, create_pdf: bool = True, quiet: bool = True) -> tuple[str, str]:
        os.makedirs(path_output_dir, exist_ok=True)
        path_latex = os.path.join(path_output_dir, self.fig.name + '.tex')
        path_pdf = os.path.join(path_output_dir, self.fig.name + '.pdf')
        with open(path_latex, 'w') as fp:
            fp.write('\n'.join(self.get_latex_code()))

        if shutil.which(Environment.PATH_PDFLATEX) is None:
            raise FileNotFoundError(Environment.PATH_PDFLATEX)

        if not create_pdf:
            return path_latex, path_pdf

        path_tmp_dir = tempfile.mkdtemp()
        cmd = [Environment.PATH_PDFLATEX, '-synctex=1', '-interaction=nonstopmode', path_latex]

        proc1 = subprocess.Popen(cmd, cwd=path_tmp_dir, stdout=subprocess.PIPE, stderr=sys.stdout.buffer)
        if not quiet:
            for line in proc1.stdout:
                print(line.decode('utf-8'), end='')
        proc1.wait()

        proc2 = subprocess.Popen(cmd, cwd=path_tmp_dir, stdout=subprocess.PIPE, stderr=sys.stdout.buffer)
        if not quiet:
            for line in proc2.stdout:
                print(line.decode('utf-8'), end='')
        proc2.wait()

        path_tmp_pdf = os.path.join(path_tmp_dir, os.path.basename(path_pdf))
        if os.path.exists(path_tmp_pdf):
            shutil.copy(path_tmp_pdf, path_pdf)
        else:
            if quiet:  # if quiet, no output so far. Due to that we report all output now,
                for line in chain(proc1.stdout, proc2.stdout):
                    print(line.decode('utf-8'), end='', flush=True, file=sys.stderr)
            raise RuntimeError('compilation failed')
        shutil.rmtree(path_tmp_dir)

        return path_latex, path_pdf

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

    def __fmt_thickness(self, thickness: AnyThickness) -> str:
        if isinstance(thickness, Thickness):
            thickness = thickness.value
        return f'{thickness:.3f}pt'

    def __fmt_linestyle(self, linestyle: LineStyle) -> str:
        return linestyle.value

    def __create_doc_begin(self) -> list[str]:
        out = ['%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%']
        out += ['% auto-generated using dplot %']
        out += ['%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%']
        out += LatexCmdsDocClass
        out += LatexCmdsAfterDocClass
        out += [r'\begin{document}']
        out += [r'\setlength\figurewidth{' + f'{self.fig.width:.3f}' + r'mm}']
        out += [r'\setlength\figureheight{' + f'{self.fig.height:.3f}' + r'mm}']
        out += [r'\begin{tikzpicture}[font=\normalsize]']
        out += [r'\pgfplotsset{every axis/.append style={line width=' + self.__fmt_thickness(self.fig.basic_thickness) + r'},compat=1.18},']
        return out

    def __get_axis_param(self, axis_kind: Literal['x', 'y'], axis_setup: Union[AxisSetup, None], limits: Union[None, tuple[float, float]] = None) -> list[str]:
        if limits is None:
            assert axis_setup is not None
            limits = axis_setup.limits
        return [
            f'scale only axis',
            f'width={self.fig.width:.3f}mm',
            f'height={self.fig.height:.3f}mm',
            f'{axis_kind}min={self.__fmt_flt(limits[0])}',
            f'{axis_kind}max={self.__fmt_flt(limits[1])}',
        ]

    def __create_plot_margin(self) -> list[str]:
        out = ['']
        out += ['%%%%%%%%%%%%%%%%%']
        out += ['% figure margin %']
        out += ['%%%%%%%%%%%%%%%%%']
        for axis in get_args(XAxis) + get_args(YAxis):
            axis_kind = Figure.get_axis_kind(axis)
            axis_kind_op = Figure.get_opposite_axis_kind(axis_kind)
            params = [
                f'scale only axis',
                f'width={self.fig.width:.3f}mm',
                f'height={self.fig.height:.3f}mm',
                f'{axis_kind}min=0',
                f'{axis_kind}max=1',
                f'{axis_kind_op}min=0',
                f'{axis_kind_op}max=1',
                r'xtick=\empty',
                r'ytick=\empty',
                f'hide {axis_kind_op} axis=true',
                f'{axis_kind}tick style={{draw=none}}',
                f'{axis_kind}label=' + (r'{\hphantom{-}}' if axis_kind == 'y' else r'{\vphantom{-}}'),
                f'{axis_kind}label shift={self.fig.margin[axis]:.3f}mm',
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
                params += [f'axis background/.style={{fill={color_to_pgfplots_color(self.fig.background_color)}}}']
                background_color_applied = True
            params += [
                f'{axis_kind}mode=' + ('log' if axis_setup.log else 'linear'),
                f'log basis {axis_kind}={axis_setup.log_base}',
                f'{axis_kind_op}min=0',
                f'{axis_kind_op}max=1',
                f'{axis_kind}label={{{axis_setup.label}}}',
                f'{axis_kind}label shift={{{axis_setup.label_shift:.3f}mm}}',
                r'xticklabel=\empty',
                r'yticklabel=\empty',
                f'{axis_kind}majorgrids={str(axis_setup.grid.major_enable).lower()}',
                f'major grid style={{line width={self.__fmt_thickness(axis_setup.grid.major_thickness)},{color_to_pgfplots_options(axis_setup.grid.major_color)}}}',
                f'{axis_kind}minorgrids={str(axis_setup.grid.minor_enable).lower()}',
                f'minor grid style={{line width={self.__fmt_thickness(axis_setup.grid.minor_thickness)},{color_to_pgfplots_options(axis_setup.grid.minor_color)}}}',
                f'{axis_kind}tick=' + ('' if axis_setup.tick.enable else r'\empty'),  # enable / disable major tick
                f'{axis_kind_op}tick=\\empty',  # disable tick of adjacent axes
                f'{axis_kind}tick pos=' + (r'both' if axis_setup.tick.opposite else Figure.get_axis_pos(axis)),
                f'{axis_kind}tick distance=' + (self.__fmt_flt(axis_setup.tick.major_distance) if axis_setup.tick.major_distance is not None else r''),
                f'major {axis_kind} tick style={{line width={self.__fmt_thickness(axis_setup.tick.major_thickness)},{color_to_pgfplots_options(axis_setup.tick.major_color)}}}',
                f'minor {axis_kind} tick style={{line width={self.__fmt_thickness(axis_setup.tick.minor_thickness)},{color_to_pgfplots_options(axis_setup.tick.minor_color)}}}',
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
            color_to_pgfplots_options(data.ls.plot_color),
            self.__fmt_linestyle(data.ls.line_style),
            f'line width={data.ls.line_width}',
            f'mark={data.ls.marker}',
            f'mark repeat={data.ls.marker_repeat}',
            f'mark phase={data.ls.marker_phase}',
            f'mark options={{solid}}',  # prevent dashed markers etc.
        ]
        if data.ls.line_style == LineStyle.NONE:
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
