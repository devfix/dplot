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
        """Returns the native Typst/Lilaq marker closure bound to the plot line color."""
        mapping = {
            Marker.NONE: ('none', 'none'),
            Marker.DOT: ('lq.marks.o', 'fill'),  # Filled circle
            Marker.CIRCLE: ('lq.marks.o', 'none'),  # Open circle
            Marker.SQUARE: ('lq.marks.s', 'none'),  # Open square
            Marker.TRIANGLE: ('lq.marks.^', 'none'),  # Open triangle
            Marker.DIAMOND: ('lq.marks.d', 'none'),  # Open diamond
            Marker.CROSS: ('lq.marks.x', 'none'),
            Marker.PLUS: ('lq.marks.+', 'none'),
            Marker.ASTERISK: ('lq.marks.asterisk', 'none'),
        }
        if marker not in Marker:
            raise ValueError(marker)
        if marker == Marker.NONE:
            return 'mark: none'

        mark_func, inner_fill = mapping.get(marker, ('lq.marks.circle', 'none'))
        col_str = self.__fmt__color(color)

        return f'mark: ((mark, fill: {col_str}, stroke: {col_str}) => ({mark_func})((size: mark.size, stroke: stroke, fill: {inner_fill})))'

    # ==========================================
    # Document Construction
    # ==========================================

    def __create_doc_begin(self) -> list[str]:
        """Sets up page dimensions, margins around the data-area, and imports Lilaq."""
        m = self.fig.margin
        out = [
            '// auto-generated using dplot (TypstGenerator - Lilaq)',
            '#import "@preview/lilaq:0.6.0" as lq',
            '',
            '#set page(',
            '  width: auto,',
            '  height: auto,',
            f'  margin: (top: {m["t"]:.3f}mm, bottom: {m["b"]:.3f}mm, left: {m["l"]:.3f}mm, right: {m["r"]:.3f}mm),',
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
        active_pairs = []
        for data in self.fig.plot_data:
            pair = (data.ax, data.ay)
            if pair not in active_pairs:
                active_pairs.append(pair)

        if not active_pairs:
            active_pairs = [('b', 'l')]

        if len(active_pairs) == 1:
            ax, ay = active_pairs[0]
            return self.__create_diagram(ax, ay, is_primary=True, draw_x=True, draw_y=True)

        out = [
            f'#block(width: {self.fig.width:.3f}mm, height: {self.fig.height:.3f}mm, [',
        ]

        # Track which axis kinds have already been drawn to prevent double-rendering on overlays
        drawn_x = set()
        drawn_y = set()

        for idx, (ax, ay) in enumerate(active_pairs):
            is_primary = (idx == 0)
            draw_x = ax not in drawn_x
            draw_y = ay not in drawn_y
            drawn_x.add(ax)
            drawn_y.add(ay)

            out.append('  #place(top + left)[')
            diag_lines = self.__create_diagram(ax, ay, is_primary=is_primary, draw_x=draw_x, draw_y=draw_y)
            out += [f'    {line}' for line in diag_lines]
            out.append('  ]')
        out.append('])')
        return out

    def __create_diagram(self, ax: XAxis, ay: YAxis, is_primary: bool, draw_x: bool = True, draw_y: bool = True) -> list[str]:
        """Configures an individual lq.diagram container, axes, grids, ticks, and legend."""
        asx = cast(AxisSetup, self.fig.axes.get(ax))
        asy = cast(AxisSetup, self.fig.axes.get(ay))

        args = [
            'bounds: "data-area"',
            f'width: {self.fig.width:.3f}mm',
            f'height: {self.fig.height:.3f}mm',
        ]

        if is_primary:
            if self.fig.title:
                args.append(f'title: [{self.fig.title}]')
            if self.fig.background_color != Color.WHITE:
                args.append(f'fill: {self.__fmt__color(self.fig.background_color)}')
        else:
            args.append('fill: none')

        # ==========================================
        # X-Axis & Ticks Configuration
        # ==========================================
        if asx:
            if asx.limits:
                args.append(f'xlim: ({self.__fmt_flt(asx.limits[0])}, {self.__fmt_flt(asx.limits[1])})')
            # FIXED: Check draw_x instead of is_primary so new top axes ('t') get their labels
            if asx.label and draw_x:
                args.append(f'xlabel: [{asx.label}]')
            if asx.log:
                args.append('xscale: "log"')

            x_tick_opts = []
            # FIXED: Add explicit position mapping for top axes ('t' / XAxis.TOP)
            if ax in ('t', getattr(XAxis, 'TOP', 't')):
                x_tick_opts.append('position: top')

            # Suppress ticks if the axis was already drawn by an earlier diagram group
            if not draw_x or not asx.tick.enable:
                x_tick_opts.append('ticks: none')
                x_tick_opts.append('subticks: none')
            else:
                if asx.tick.major_distance is not None:
                    x_tick_opts.append(f'ticks: (step: {self.__fmt_flt(asx.tick.major_distance)})')
                if asx.tick.minor_num > 0:
                    x_tick_opts.append(f'subticks: {asx.tick.minor_num}')
                else:
                    x_tick_opts.append('subticks: none')
                if asx.tick.opposite:
                    x_tick_opts.append('mirror: (ticks: true, tick-labels: false)')
                else:
                    x_tick_opts.append('mirror: (ticks: false)')
            if x_tick_opts:
                args.append(f'xaxis: ({", ".join(x_tick_opts)})')

        # ==========================================
        # Y-Axis & Ticks Configuration
        # ==========================================
        if asy:
            if asy.limits:
                args.append(f'ylim: ({self.__fmt_flt(asy.limits[0])}, {self.__fmt_flt(asy.limits[1])})')
            # FIXED: Check draw_y instead of is_primary so right axes ('r') get their labels!
            if asy.label and draw_y:
                args.append(f'ylabel: [{asy.label}]')
            if asy.log:
                args.append('yscale: "log"')

            y_tick_opts = []
            # FIXED: Add explicit position mapping for right axes ('r' / YAxis.RIGHT)
            if ay in ('r', getattr(YAxis, 'RIGHT', 'r')):
                y_tick_opts.append('position: right')

            # Suppress ticks if the axis was already drawn by an earlier diagram group
            if not draw_y or not asy.tick.enable:
                y_tick_opts.append('ticks: none')
                y_tick_opts.append('subticks: none')
            else:
                if asy.tick.major_distance is not None:
                    y_tick_opts.append(f'ticks: (step: {self.__fmt_flt(asy.tick.major_distance)})')
                if asy.tick.minor_num > 0:
                    y_tick_opts.append(f'subticks: {asy.tick.minor_num}')
                else:
                    y_tick_opts.append('subticks: none')
                if asy.tick.opposite:
                    y_tick_opts.append('mirror: (ticks: true, tick-labels: false)')
                else:
                    y_tick_opts.append('mirror: (ticks: false)')
            if y_tick_opts:
                args.append(f'yaxis: ({", ".join(y_tick_opts)})')

        # ==========================================
        # Comprehensive Grid Configuration
        # ==========================================
        prefix_rules = []

        def get_grid_stroke(axis_setup: Union[AxisSetup, None], is_major: bool, enabled: bool) -> str:
            if not axis_setup or not enabled:
                return "none"
            is_enabled = axis_setup.grid.major_enable if is_major else axis_setup.grid.minor_enable
            if not is_enabled:
                return "none"
            thickness = self.__fmt_thickness(axis_setup.grid.major_thickness if is_major else axis_setup.grid.minor_thickness)
            color = self.__fmt__color(axis_setup.grid.major_color if is_major else axis_setup.grid.minor_color)
            return f"{thickness} + {color}"

        # Grid lines are governed exclusively by active, non-duplicate drawn axes
        x_maj = get_grid_stroke(asx, is_major=True, enabled=draw_x)
        y_maj = get_grid_stroke(asy, is_major=True, enabled=draw_y)
        x_min = get_grid_stroke(asx, is_major=False, enabled=draw_x)
        y_min = get_grid_stroke(asy, is_major=False, enabled=draw_y)

        if x_maj == y_maj and x_min == y_min:
            args.append(f'grid: (stroke: {x_maj}, stroke-sub: {x_min})')
        else:
            prefix_rules.append(f'#show: lq.cond-set(lq.grid.with(kind: "x"), stroke: {x_maj}, stroke-sub: {x_min})')
            prefix_rules.append(f'#show: lq.cond-set(lq.grid.with(kind: "y"), stroke: {y_maj}, stroke-sub: {y_min})')

        # ==========================================
        # Comprehensive Tick Styling
        # ==========================================
        def get_tick_stroke(axis_setup: Union[AxisSetup, None], is_major: bool, enabled: bool) -> str:
            if not axis_setup or not axis_setup.tick.enable or not enabled:
                return "none"
            if not is_major and axis_setup.tick.minor_num <= 0:
                return "none"
            ref_tick = axis_setup.tick
            thickness = self.__fmt_thickness(ref_tick.major_thickness if is_major else ref_tick.minor_thickness)
            color = self.__fmt__color(ref_tick.major_color if is_major else ref_tick.minor_color)
            return f"{thickness} + {color}"

        x_tick_maj = get_tick_stroke(asx, is_major=True, enabled=draw_x)
        y_tick_maj = get_tick_stroke(asy, is_major=True, enabled=draw_y)
        x_tick_min = get_tick_stroke(asx, is_major=False, enabled=draw_x)
        y_tick_min = get_tick_stroke(asy, is_major=False, enabled=draw_y)

        if x_tick_maj == y_tick_maj and x_tick_min == y_tick_min:
            if x_tick_maj != "none":
                prefix_rules.append(f'#show: lq.cond-set(lq.tick.with(sub: false), stroke: {x_tick_maj})')
            if x_tick_min != "none":
                prefix_rules.append(f'#show: lq.cond-set(lq.tick.with(sub: true), stroke: {x_tick_min})')
        else:
            if x_tick_maj != "none":
                prefix_rules.append(f'#show: lq.cond-set(lq.tick.with(kind: "x", sub: false), stroke: {x_tick_maj})')
            if x_tick_min != "none":
                prefix_rules.append(f'#show: lq.cond-set(lq.tick.with(kind: "x", sub: true), stroke: {x_tick_min})')
            if y_tick_maj != "none":
                prefix_rules.append(f'#show: lq.cond-set(lq.tick.with(kind: "y", sub: false), stroke: {y_tick_maj})')
            if y_tick_min != "none":
                prefix_rules.append(f'#show: lq.cond-set(lq.tick.with(kind: "y", sub: true), stroke: {y_tick_min})')

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

        out = prefix_rules + ['#lq.diagram(']
        for arg in args:
            out.append(f'  {arg},')

        for data in self.fig.plot_data:
            if data.ax == ax and data.ay == ay:
                out += self.__create_plot_call(data, asx, asy)

        out.append(')')
        return out

    def __create_plot_call(self, data: Data, asx: Union[AxisSetup, None], asy: Union[AxisSetup, None]) -> list[str]:
        """Translates data arrays and LineSetup into lq.plot() calls, applying axis scaling."""
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

        if data.ls.line_style == LineStyle.NONE:
            plot_args.append('stroke: none,')
        else:
            color_str = self.__fmt__color(data.ls.plot_color)
            thick_str = self.__fmt_thickness(data.ls.line_width)
            dash_str = self.__fmt_linestyle(data.ls.line_style)
            stroke_val = f'(paint: {color_str}, thickness: {thick_str}, dash: {dash_str})'
            plot_args.append(f'stroke: {stroke_val},')

        marker_str = self.__fmt_marker(data.ls.marker, data.ls.plot_color)
        plot_args.append(f'{marker_str},')

        if data.ls.marker != Marker.NONE and data.ls.marker_repeat > 1:
            plot_args.append(f'every: {data.ls.marker_repeat},')

        lines = ['  lq.plot(']
        for pa in plot_args:
            lines.append(f'    {pa}')
        lines.append('  ),')
        return lines