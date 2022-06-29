import matplotlib
from matplotlib import pyplot as plt

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['font.family'] = 'Times New Roman'


default_bar_hatches = [ 'xx','oo','\\','--' ]
default_bar_colors = [ '#ffb6b9', '#a1a499', '#fff1ac', '#50C1E9' ]
default_markers =['D', 'o', '^', 's']
default_line_styles = ['--','--','--','--']
default_line_colors = ['#515bd4','#dd2a7b','g','#716e77']
default_label_font = {
    'family': 'Times New Roman',
    'weight': 'normal',
    'size': 30,
}
default_legend_font = {
    'family': 'Times New Roman',
    'weight': 'normal',
    'size': 24,
}


class BasicPlotter:
    def __init__(self, algs,
                 specific_bar_colors=None, specific_bar_hatches=None,
                 specific_markers=None, specific_line_styles=None, specific_line_colors=None,
                 specific_label_font=None, specific_legend_font=None):

        self.algs = algs
        
        # for diagrams
        self.bar_colors = { alg: color for alg, color in zip(self.algs,specific_bar_colors) } \
            if specific_bar_colors is not None else { alg: color for alg, color in zip(self.algs,default_bar_colors) }  
        self.bar_hatches = { alg: hatch for alg, hatch in zip(self.algs,specific_bar_hatches) } \
            if specific_bar_hatches is not None else  { alg: hatch for alg, hatch in zip(self.algs,default_bar_hatches) }

        # for linegraph
        self.markers = {alg: marker for alg, marker in zip(self.algs, specific_markers)} \
            if specific_markers is not None else { alg: marker for alg, marker in zip(self.algs,default_markers)}
        self.line_styles = {alg: line_style for alg, line_style in zip(self.algs, specific_line_styles)} \
            if specific_line_styles is not None else { alg: line_style for alg, line_style in zip(self.algs,default_line_styles)}
        self.line_colors = {alg: line_color for alg, line_color in zip(self.algs, specific_line_colors)} \
            if specific_line_colors is not None else { alg: line_color for alg, line_color in zip(self.algs,default_line_colors)}
        
        self.legend = None
        self.legend_font = specific_legend_font if specific_label_font is not None else default_legend_font
        self.label_font = specific_label_font if specific_label_font is not None else default_label_font
        
    def plot_diagram(self, y_values, y_label, y_infos, x_label, x_infos, xlim, bar_pos, 
                     fig_size=(8, 5),bar_width=0.25,
                     save_file=False, file_name=None):

        fig, ax = plt.subplots(figsize=fig_size, constrained_layout=True)

        for i, alg in enumerate(self.algs):
            bars = ax.bar(bar_pos[i], width=bar_width,
                          color=self.bar_colors[alg], edgecolor="k",
                          height=y_values[alg], label=alg)
            for bar in bars:
                bar.set_hatch(self.bar_hatches[alg])

        self.legend = ax.legend(frameon=False, prop=self.legend_font,
                                labelspacing=0.1, borderpad=0.1, loc=2)

        self._plot(plt, ax, y_label, y_infos, x_label, x_infos, xlim, save_file, file_name)

    def plot_linegraph(self, y_values, y_infos, y_label, x_edges, x_label, x_infos,
                       fig_size=(8, 5), save_file=False, file_name=None):
        
        fig, ax = plt.subplots(figsize=fig_size, constrained_layout=True)

        for alg in self.algs:
            ax.plot(x_edges, y_values[alg], self.line_colors[alg], label=alg,
                    marker=self.markers[alg], markersize=20, markerfacecolor='none',
                    linestyle=self.line_styles[alg], linewidth=3)

        self.legend = ax.legend(frameon=False, prop=self.legend_font,
                                labelspacing=0.1, borderpad=0.1)

        xlim = (self.x_infos[0][0], self.x_infos[0][-1])

        self._plot(plt, ax, y_label, y_infos, x_label, x_infos, xlim, save_file, file_name)

    def plot_diagram_with_error(self,
                                y_max_values, y_mean_values, y_min_values, y_infos, y_label,
                                bar_width=0.25,
                                fig_size=(8, 5),
                                save_file=False, file_name=None,
                                x_pos=None, x_label=None, xlim=None, x_infos=None

                                ):
        fig, ax = plt.subplots(figsize=fig_size, constrained_layout=True)

        bar_pos = self.bar_pos
        if x_pos is not None:
            bar_pos = x_pos

        for i, alg in enumerate(self.algs):
            bars = ax.bar(x=bar_pos[i], height=y_mean_values[alg], width=bar_width,
                          color=self.bar_color[alg], edgecolor="k",
                          yerr=[
                              [y_max - y_mean for y_max, y_mean in zip(y_max_values[alg], y_mean_values[alg])],
                              [y_mean - y_min for y_mean, y_min in zip(y_mean_values[alg], y_min_values[alg])]
                          ],
                          error_kw={
                              'elinewidth': 3,
                              'capsize': 6,
                            'capthick': 3},
                          align='edge',
                          label=alg)
            for bar in bars:
                bar.set_hatch(self.bar_hatch[alg])

        self.legend = ax.legend(labelspacing=0.1, borderpad=0.1, frameon=False, prop=self.legend_font, ncol=2, loc=2)

        self._plot(plt, ax, y_label, y_infos, x_label, x_infos, xlim, save_file, file_name)

    def _plot(self, plt, ax, y_label, y_infos, x_label, x_infos, xlim, save_file, file_name):
        legend = self.legend

        frame = legend.get_frame()
        frame.set_alpha(1)
        frame.set_facecolor('none')

        ax.tick_params(labelsize=30)

        ax.set_ylabel(y_label, self.label_font)
        ax.set_yticks(y_infos[0], y_infos[1])
        ax.set_ylim(y_infos[0][0], y_infos[0][-1])

        ax.set_xlabel(x_label, self.label_font)
        ax.set_xlim(xlim)
        ax.set_xticks(x_infos[0], x_infos[1])

        if save_file:
            try:
                plt.savefig(file_name, format='pdf')
            except Exception as e:
                print(e)
                plt.savefig('unnamed_figure.pdf', format='pdf')
        else:
            plt.show()

class AccPlotter(BasicPlotter):
    def __init__(self, algs,
                 specific_bar_colors=None, specific_bar_hatches=None,
                 specific_markers=None, specific_line_styles=None, specific_line_colors=None,
                 specific_label_font=None, specific_legend_font=None):

        super().__init__(algs, specific_bar_colors, specific_bar_hatches,
                 specific_markers, specific_line_styles, specific_line_colors,
                 specific_label_font, specific_legend_font)

    def plot_linegraph(self, y_values, y_infos, y_label,x_edges, x_label, x_infos,
                       fig_size=(8, 5), save_file=False, file_name=None):
        
        fig, ax = plt.subplots(figsize=fig_size, constrained_layout=True)

        for alg in self.algs:
            ax.plot(x_edges[alg], y_values[alg], self.line_colors[alg], label=alg,
                    marker=self.markers[alg], markersize=20, markerfacecolor='none',
                    linestyle=self.line_styles[alg], linewidth=3)

        self.legend = ax.legend(frameon=False, prop=self.legend_font,
                                labelspacing=0.1, borderpad=0.1)
        xlim = (self.x_infos[0][0], self.x_infos[0][-1])

        self._plot(plt, ax, y_label, y_infos, x_label, x_infos, xlim, save_file, file_name)
