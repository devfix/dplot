import os
import shutil
import subprocess
import sys
from typing import cast, Collection, Union
from .color import _resolve_color, AnyColor, Color
from .common import *
from .figure import Figure


class TypstGenerator:
    def __init__(self, fig: Figure):
        self.fig = fig

    def get_typst_code(self) -> list[str]:
        """Generates the complete Typst document string using Lilaq."""
        self.fig.validate()
        out = self.__create_doc_begin()
        out += self.__create_diagram_groups()
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

    # ==========================================
    # Formatting Helpers
    # ==========================================

    def __fmt_flt(self, x: float) -> str:
        """Formats floating point numbers cleanly."""
        return f'{x:.10g}'

    def __fmt_array(self, vals: Collection[float]) -> str:
        """Formats Python collections into Typst arrays, handling single-element syntax correctly."""
        formatted = [self.__fmt_flt(v) for v in vals]
        if len(formatted) == 0:
            return "()"
        if len(formatted) == 1:
            return f"({formatted[0]},)"
        return f"({', '.join(formatted)})"

    def __fmt_thickness(self, thickness: AnyThickness) -> str:
        """Converts Thickness enum or float to a Typst dimension string in points."""
        if isinstance(thickness, Thickness):
            val = thickness.value
        else:
            val = float(thickness)
        return f'{val:.3f}pt'

    def __fmt_linestyle(self, linestyle: LineStyle) -> str:
        """
        Returns the appropriate Typst stroke definition.
        Uses native shorthands for standard styles, and custom dash arrays for variants.
        """
        mapping = {
            # Native Lilaq/Typst shorthands
            LineStyle.SOLID: '"solid"',
            LineStyle.DOTTED: '"dotted"',
            LineStyle.DASHED: '"dashed"',
            LineStyle.DASH_DOTTED: '"dash-dotted"',

            # Custom patterns for variants
            LineStyle.DENSELY_DOTTED: '(array: (1pt, 1pt), phase: 0pt)',
            LineStyle.LOOSELY_DOTTED: '(array: (1pt, 4pt), phase: 0pt)',
            LineStyle.DENSELY_DASHED: '(array: (2pt, 2pt), phase: 0pt)',
            LineStyle.LOOSELY_DASHED: '(array: (6pt, 6pt), phase: 0pt)',
            LineStyle.DENSELY_DASH_DOTTED: '(array: (2pt, 1pt, 1pt, 1pt), phase: 0pt)',
            LineStyle.LOOSELY_DASH_DOTTED: '(array: (4pt, 2pt, 1pt, 2pt), phase: 0pt)',

            # Fallback for others
            LineStyle.NONE: 'none'
        }
        return mapping.get(linestyle, '"solid"')

    def __fmt__color(self, color: AnyColor) -> str:
        """
        Converts a Color enum, RGBAColor, tuple, or string name to a valid Typst/Lilaq color string.
        Example output: 'rgb(31, 119, 180)' or 'rgb(255, 0, 0, 50%)'
        """
        col = _resolve_color(color)
        if col.a < 1.0:
            alpha_pct = round(col.a * 100, 1)
            alpha_str = f"{int(alpha_pct)}%" if alpha_pct.is_integer() else f"{alpha_pct}%"
            return f'rgb({col.r}, {col.g}, {col.b}, {alpha_str})'
        return f'rgb({col.r}, {col.g}, {col.b})'

    def __fmt_marker(self, marker: Marker, color: AnyColor) -> str:
        """Returns the native Typst/Lilaq marker shorthand."""
        mapping = {
            Marker.NONE: 'mark: none',
            Marker.DOT: 'mark: "o", mark-fill: ' + self.__fmt__color(color),
            Marker.CIRCLE: 'mark: "o"',
            Marker.SQUARE: 'mark: "s"',
            Marker.TRIANGLE: 'mark: "^"',
            Marker.DIAMOND: 'mark: "d"',
            Marker.CROSS: 'mark: "x"',
            Marker.PLUS: 'mark: "+"',
            Marker.ASTERISK: 'mark: "star"',
        }
        if marker not in Marker:
            raise ValueError(marker)
        return cast(str, mapping.get(marker))

    # ==========================================
    # Document Construction
    # ==========================================

    def __create_doc_begin(self) -> list[str]:
        """Sets up page dimensions, zero page margin for exact cropping, and imports Lilaq."""
        out = [
            '// auto-generated using dplot (TypstGenerator - Lilaq)',
            '#import "@preview/lilaq:0.6.0" as lq',
            '',
            '#set page(',
            '  width: auto,',
            '  height: auto,',
            '  margin: 0mm,',  # FIXED: 0 page margin matches LaTeX standalone cropping!
            ')',
            ''
        ]
        return out

    def __create_diagram_groups(self) -> list[str]:
        """
        Handles multi-axis layouts by grouping data by (ax, ay) pairs.
        If multiple axis pairs are used (e.g., bottom-left and top-right), they are
        rendered as overlaid diagrams inside a Typst block container.
        """
        # Find all active (ax, ay) combinations in the plotted data
        active_pairs = []
        for data in self.fig.plot_data:
            pair = (data.ax, data.ay)
            if pair not in active_pairs:
                active_pairs.append(pair)

        # Fallback to bottom/left if no data sets are present
        if not active_pairs:
            active_pairs = [('b', 'l')]

        # If only one axis pair is needed, generate a single diagram cleanly
        if len(active_pairs) == 1:
            ax, ay = active_pairs[0]
            return self.__create_diagram(ax, ay, is_primary=True)

        # FIXED: Calculate total outer dimensions (plot size + margins)
        m = self.fig.margin
        total_w = self.fig.width + m["l"] + m["r"]
        total_h = self.fig.height + m["t"] + m["b"]

        # For multi-axis setups, wrap diagrams in an overlaid block container
        out = [
            f'#block(width: {total_w:.3f}mm, height: {total_h:.3f}mm, [',
        ]
        for idx, (ax, ay) in enumerate(active_pairs):
            is_primary = (idx == 0)
            out.append('  #place(top + left)[')
            diag_lines = self.__create_diagram(ax, ay, is_primary=is_primary)
            out += [f'    {line}' for line in diag_lines]
            out.append('  ]')
        out.append('])')
        return out

    def __create_diagram(self, ax: XAxis, ay: YAxis, is_primary: bool) -> list[str]:
        """Configures an individual lq.diagram container, axes, grids, and legend."""
        asx = cast(AxisSetup, self.fig.axes.get(ax))
        asy = cast(AxisSetup, self.fig.axes.get(ay))

        m = self.fig.margin
        args = [
            f'width: {self.fig.width:.3f}mm',
            f'height: {self.fig.height:.3f}mm',
            # FIXED: Pass margin directly into Lilaq diagram for exact padding around plot box!
            f'margin: (top: {m["t"]:.3f}mm, bottom: {m["b"]:.3f}mm, left: {m["l"]:.3f}mm, right: {m["r"]:.3f}mm)',
        ]

        # Apply title and background color only to the primary layer
        if is_primary:
            if self.fig.title:
                args.append(f'title: [{self.fig.title}]')
            if self.fig.background_color != Color.WHITE:
                args.append(f'fill: {self.__fmt__color(self.fig.background_color)}')
        else:
            args.append('fill: none')  # Transparent background for overlays

        # Configure X-Axis
        if asx:
            if asx.limits:
                args.append(f'xlim: ({self.__fmt_flt(asx.limits[0])}, {self.__fmt_flt(asx.limits[1])})')
            if asx.label and is_primary:
                args.append(f'xlabel: [{asx.label}]')
            if asx.log:
                args.append('xscale: "log"')
            if asx.tick.major_distance is not None:
                args.append(f'xticks: (step: {self.__fmt_flt(asx.tick.major_distance)})')

        # Configure Y-Axis
        if asy:
            if asy.limits:
                args.append(f'ylim: ({self.__fmt_flt(asy.limits[0])}, {self.__fmt_flt(asy.limits[1])})')
            if asy.label and is_primary:
                args.append(f'ylabel: [{asy.label}]')
            if asy.log:
                args.append('yscale: "log"')
            if asy.tick.major_distance is not None:
                args.append(f'yticks: (step: {self.__fmt_flt(asy.tick.major_distance)})')

        # Grid configuration (drawn on primary layer only)
        grid_enabled = is_primary and ((asx and asx.grid.major_enable) or (asy and asy.grid.major_enable))
        if grid_enabled:
            grid_stroke = self.__fmt_thickness(asx.grid.major_thickness if asx else Thickness.THIN)
            grid_color = self.__fmt__color(asx.grid.major_color if asx else Color.BLACK)
            args.append(f'grid: (stroke: {grid_stroke} + {grid_color})')
        else:
            args.append('grid: none')

        # Legend configuration
        if is_primary and self.fig.legend_setup.enable:
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

        # Inject plot data belonging to this specific axis group
        for data in self.fig.plot_data:
            if data.ax == ax and data.ay == ay:
                out += self.__create_plot_call(data, asx, asy)

        out.append(')')
        return out

    def __create_plot_call(self, data: Data, asx: Union[AxisSetup, None], asy: Union[AxisSetup, None]) -> list[str]:
        """Translates data arrays and LineSetup into lq.plot() calls, applying axis scaling."""
        # Apply axis scaling factor to raw coordinates
        scale_x = asx.scale if asx else 1.0
        scale_y = asy.scale if asy else 1.0
        scaled_dx = [x * scale_x for x in data.dx]
        scaled_dy = [y * scale_y for y in data.dy]

        xs_str = self.__fmt_array(scaled_dx)
        ys_str = self.__fmt_array(scaled_dy)

        plot_args = [
            f'{xs_str},',
            f'{ys_str},',
        ]

        if data.label:
            plot_args.append(f'label: [{data.label}],')

        # Configure Stroke (Color, Thickness, Dash Pattern)
        if data.ls.line_style == LineStyle.NONE:
            plot_args.append('stroke: none,')
        else:
            color_str = self.__fmt__color(data.ls.plot_color)
            thick_str = self.__fmt_thickness(data.ls.line_width)
            dash_str = self.__fmt_linestyle(data.ls.line_style)
            stroke_val = f'(paint: {color_str}, thickness: {thick_str}, dash: {dash_str})'
            plot_args.append(f'stroke: {stroke_val},')

        # Configure Markers and Repeat Step
        # Always emit the mark argument so Lilaq knows to disable it!
        marker_str = self.__fmt_marker(data.ls.marker, data.ls.plot_color)
        plot_args.append(f'{marker_str},')

        # Only emit mark-step if a valid marker is active and repeat is requested
        if data.ls.marker != Marker.NONE and data.ls.marker_repeat > 1:
            plot_args.append(f'mark-step: {data.ls.marker_repeat},')

        lines = ['  lq.plot(']
        for pa in plot_args:
            lines.append(f'    {pa}')
        lines.append('  ),')
        return lines
