import os
import shutil
import subprocess
import sys
from typing import cast, get_args, Union, Collection

from .color import color_to_lilaq_color
from .common import *
from .figure import Figure


LILAQ_LINE_STYLE_MAP = {
    '': 'none',
    'solid': '"solid"',
    'dotted': '"dotted"',
    'densely dotted': '"dotted"',
    'loosely dotted': '"dotted"',
    'dashed': '"dashed"',
    'densely dashed': '"dashed"',
    'loosely dashed': '"dashed"',
    'dashdotted': '"dash-dotted"',
    'densely dashdotted': '"dash-dotted"',
    'loosely dashdotted': '"dash-dotted"',
    'dashdotdotted': '"dash-dotted"',
}

LILAQ_MARKER_MAP = {
    '': 'none',
    '*': '"o"',
    'o': '"o"',
    'circle': '"o"',
    'x': '"x"',
    '+': '"+"',
    '-': '"-"',
    '|': '"|"',
    'square': '"s"',
    'square*': '"s"',
    'triangle': '"^"',
    'triangle*': '"^"',
    'diamond': '"d"',
    'diamond*': '"d"',
    'asterisk': '"star"',
    'star': '"star"',
}

LILAQ_COLOR_MAP = {
    'darkgray': 'gray.darken(40%)',
    'lightgray': 'gray.lighten(40%)',
    'brown': 'rgb("a52a2a")',
    'lime': 'rgb("00ff00")',
    'olive': 'rgb("808000")',
    'orange': 'rgb("ffa500")',
    'pink': 'rgb("ffc0cb")',
    'purple': 'rgb("800080")',
    'teal': 'rgb("008080")',
    'violet': 'rgb("ee82ee")',
}


class TypstGenerator:
    def __init__(self, fig: Figure):
        self.fig = fig

    def get_typst_code(self) -> list[str]:
        """Generates the complete Typst document string using Lilaq."""
        self.fig.validate()
        out = self.__create_doc_begin()
        out += self.__create_diagram()
        return out

    def export(self, path_output_dir: str, create_pdf: bool = True, quiet: bool = True) -> tuple[str, str]:
        """
        Exports the Typst code to a .typ file and optionally compiles it to PDF.
        Mirrors the behavior of LatexGenerator.export().
        """
        os.makedirs(path_output_dir, exist_ok=True)
        path_typst = os.path.join(path_output_dir, self.fig.name + '.typ')
        path_pdf = os.path.join(path_output_dir, self.fig.name + '.pdf')

        with open(path_typst, 'w') as fp:
            fp.write('\n'.join(self.get_typst_code()))

        if not create_pdf:
            return path_typst, path_pdf

        typst_bin = shutil.which('typst')
        if typst_bin is None:
            raise FileNotFoundError('The "typst" executable was not found in PATH.')

        cmd = [typst_bin, 'compile', path_typst, path_pdf]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if quiet else sys.stdout,
            stderr=subprocess.PIPE if quiet else sys.stderr
        )
        proc.wait()

        if proc.returncode != 0:
            if quiet and proc.stderr:
                print(proc.stderr.read().decode('utf-8'), file=sys.stderr)
            raise RuntimeError('Typst compilation failed.')

        return path_typst, path_pdf

    def __fmt_flt(self, x: float) -> str:
        return f'{x:.10g}'

    def __fmt_array(self, vals: Collection[float]) -> str:
        """Formats Python collections into Typst arrays, handling single-element syntax cleanly."""
        formatted = [self.__fmt_flt(v) for v in vals]
        if len(formatted) == 1:
            return f'({formatted[0]},)'
        return f'({", ".join(formatted)})'

    def __fmt_thickness(self, thickness: AnyThickness) -> str:
        if isinstance(thickness, Thickness):
            thickness = thickness.value
        return f'{thickness:.3f}pt'

    def __fmt_linestyle(self, linestyle: LineStyle) -> str:
        return linestyle.value

    def __translate_style(self, style_str: LineStyle) -> str:
        return LILAQ_LINE_STYLE_MAP.get(style_str, '"solid"')

    def __translate_marker(self, marker_str: Marker) -> str:
        return LILAQ_MARKER_MAP.get(marker_str, 'none')

    def __create_doc_begin(self) -> list[str]:
        """Sets up page dimensions, margins, and imports Lilaq."""
        m = self.fig.margin
        out = [
            '// auto-generated using dplot (TypstGenerator - Lilaq)',
            '#import "@preview/lilaq:0.6.0" as lq',
            '',
            '#set page(',
            '  width: auto,',
            '  height: auto,',
            f'  margin: (top: {m["t"]}mm, bottom: {m["b"]}mm, left: {m["l"]}mm, right: {m["r"]}mm),',
            ')',
            ''
        ]
        return out

    def __create_diagram(self) -> list[str]:
        """Configures the lq.diagram container, axes, grids, and legend."""
        asx = cast(AxisSetup, self.fig.axes.get('b') or self.fig.axes.get('t'))
        asy = cast(AxisSetup, self.fig.axes.get('l') or self.fig.axes.get('r'))

        args = [
            f'width: {self.fig.width:.3f}mm',
            f'height: {self.fig.height:.3f}mm',
        ]

        if self.fig.title:
            args.append(f'title: [{self.fig.title}]')

        if self.fig.background_color != 'white':
            args.append(f'fill: {color_to_lilaq_color(self.fig.background_color)}')

        # X-Axis configuration
        if asx:
            if asx.limits:
                args.append(f'xlim: ({self.__fmt_flt(asx.limits[0])}, {self.__fmt_flt(asx.limits[1])})')
            if asx.label:
                args.append(f'xlabel: [{asx.label}]')
            if asx.log:
                args.append('xscale: "log"')

        # Y-Axis configuration
        if asy:
            if asy.limits:
                args.append(f'ylim: ({self.__fmt_flt(asy.limits[0])}, {self.__fmt_flt(asy.limits[1])})')
            if asy.label:
                args.append(f'ylabel: [{asy.label}]')
            if asy.log:
                args.append('yscale: "log"')

        # Grid configuration
        grid_enabled = (asx and asx.grid.major_enable) or (asy and asy.grid.major_enable)
        if grid_enabled:
            args.append('grid: (stroke: 0.5pt + luma(80%))')
        else:
            args.append('grid: none')

        # Legend configuration
        if self.fig.legend_setup.enable:
            anchor_map = {
                'north east': 'top + right',
                'north west': 'top + left',
                'south east': 'bottom + right',
                'south west': 'bottom + left',
            }
            pos = anchor_map.get(self.fig.legend_setup.anchor, 'top + right')
            args.append(f'legend: (position: {pos})')
        else:
            args.append('legend: none')

        out = ['#lq.diagram(']
        for arg in args:
            out.append(f'  {arg},')

        # Add data plots
        for data in self.fig.plot_data:
            out += self.__create_plot_call(data)

        out.append(')')
        return out

    def __create_plot_call(self, data: Data) -> list[str]:
        """Translates data arrays and LineSetup into lq.plot() calls."""
        color = color_to_lilaq_color(data.ls.plot_color)
        style = self.__translate_style(data.ls.line_style)
        marker = self.__translate_marker(data.ls.marker)

        xs_str = self.__fmt_array(data.dx)
        ys_str = self.__fmt_array(data.dy)

        plot_args = [
            f'{xs_str},',
            f'{ys_str},',
        ]

        if data.label:
            plot_args.append(f'label: [{data.label}]')

        if style != 'none':
            plot_args.append(f'stroke: (paint: {color}, thickness: {self.__fmt_thickness(data.ls.line_width)}, dash: {style})')
        else:
            plot_args.append('stroke: none')

        if marker != 'none':
            plot_args.append(f'mark: {marker}')

        lines = ['  lq.plot(']
        for pa in plot_args:
            lines.append(f'    {pa},')
        lines.append('  ),')
        return lines