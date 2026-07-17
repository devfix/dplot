class MatplotlibView:
    _initialized = False

    def __init__(self, fig: Figure):
        self.fig = fig
        if not _MatplotlibView._initialized:
            # import matplotlib
            # matplotlib.use('gtk3agg')
            import matplotlib.pyplot as plt
            _MatplotlibView._initialized = True

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
