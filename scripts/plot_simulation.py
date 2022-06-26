import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
from MyPlotter import BasicPlotter

bar_pos_1 = [
        [1.7, 2.95, 4.2, 5.45],
        [1.9, 3.15, 4.4, 5.65],
        [2.1, 3.35, 4.6, 5.85],
        [2.3, 3.55, 4.8, 6.05]]

bar_pos_2 = [
        [1.75, 3, 4.25, 5.5],
        [2, 3.25, 4.5, 5.75],
        [2.25, 3.5, 4.75, 6]
]

xlim = [1.25, 6.5]
x_index_pos = [2, 3.25, 4.5, 5.75]

if __name__ == '__main__':
    plotter = BasicPlotter( ["LINA","ATP+", "ATP", "Geryon"] )
    
    ps_ingress_amount=pd.read_csv(os.path.join(BASE_DIR,'../data/topo_fattree_metric_0'),index_col=0)
    innetwork_aggregation_amount=pd.read_csv(os.path.join(BASE_DIR,'../data/topo_fattree_metric_1'),index_col=0)
    total_overhead=pd.read_csv(os.path.join(BASE_DIR,'../data/topo_fattree_metric_2'),index_col=0)
    total_overhead_ratio=pd.read_csv(os.path.join(BASE_DIR,'../data/topo_fattree_metric_3'),index_col=0)

    plotter.plot_diagram(ps_ingress_amount, 'Amount (GB)', 
        ([0, 10000, 20000, 30000, 40000, 50000, 60000], ['0', '10', '20', '30', '40', '50', '60']) , 
        'No. of Workers', 
        (x_index_pos, ps_ingress_amount.index), xlim, bar_pos_1, bar_width=0.2, save_file=True, file_name=os.path.join(BASE_DIR, "../figures/fattree_figure_0.pdf"))

    plotter.plot_diagram(total_overhead, 'Amount (GB)', 
        ([0, 10000, 20000, 30000, 40000, 50000, 60000], ['0', '10', '20', '30', '40', '50', '60']) , 
        'No. of Workers', 
        (x_index_pos, total_overhead.index), xlim, bar_pos_1, bar_width=0.2, save_file=True, file_name=os.path.join(BASE_DIR, "../figures/fattree_figure_2.pdf"))

    plotter.plot_diagram(total_overhead_ratio, 'Amount (GB)', 
        ([0, 20000, 40000, 60000, 80000, 100000 ], ['0', '20', '40', '60', '80', '100']) , 
        'Distribution', 
        (x_index_pos, total_overhead_ratio.index), xlim, bar_pos_1, bar_width=0.2, save_file=True, file_name=os.path.join(BASE_DIR, "../figures/fattree_figure_3.pdf"))
    
    plotter.algs=plotter.algs[:-1]
    plotter.plot_diagram(innetwork_aggregation_amount, 'Amount (GB)', 
        ([0, 2000, 4000, 6000, 8000, 10000], ['0', '2', '4', '6', '8', '10']) , 
        'No. of Workers', 
        (x_index_pos, innetwork_aggregation_amount.index), xlim, bar_pos_2, bar_width=0.25, save_file=True, file_name=os.path.join(BASE_DIR, "../figures/fattree_figure_1.pdf"))