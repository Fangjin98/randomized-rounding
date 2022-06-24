from collections import defaultdict
import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, '../src')
print(SRC_DIR)
sys.path.append(SRC_DIR)

from utils.TopoGenerator import TopoGenerator
from GRID import GRID
from ATP import ATP
from DT import DT
from LINA import LINA

def worker_num_overhead(algs, topo: TopoGenerator, worker_num_set, switch_num, resources,delay_rate=0):
    
    overhead = defaultdict(list)

    for num in worker_num_set:
        test_set, flattern_test_set = topo.generate_test_set(num, switch_num, random_pick=True, seed=10)
        print("Test: \t{} workers.".format(str(num)))
        
        aggregation_policy, layer_depolyment=algs[3].run(flattern_test_set,resources)
        overhead['ingress']=algs[3].cal_ingress_overhead(flattern_test_set, resources, layer_depolyment)
        overhead['in-network']=algs[3].cal_innetwork_aggregation_overhead(flattern_test_set, resources, aggregation_policy)
        overhead['total']=algs[3].cal_total_overhead(flattern_test_set, resources, aggregation_policy, layer_depolyment)
        
        print(overhead)

    # for alg_result, alg in zip(res, ['GRID', 'ATP', 'SwitchML', 'Greyon']):
    #     print(alg)
    #     for i, suite_result in enumerate(alg_result):
    #         print("Worker num: {}".format(worker_num[i]))
    #         total_throughput = 0
    #         ps_throughput = 0
    #         agg_throughput = 0
    #         total_band = 0
    #         for key in suite_result[1].keys():
    #             if key[0] == 'h':  # worker
    #                 total_throughput += suite_result[1][key]
    #                 if suite_result[0][key][0] == 'v':  # aggregation node is switch
    #                     agg_throughput += suite_result[1][key]
    #                     total_band += MODEL_SIZE
    #                 else:  # aggregation node is the ps
    #                     ps_throughput += suite_result[1][key]
    #                     total_band += MODEL_SIZE * 3

    #             elif key[0] == 'v':  # switch
    #                 ps_throughput += suite_result[1][key]
    #                 total_band += MODEL_SIZE * 2

            # print('Avg worker sending rate: {}'.format(str(total_throughput / worker_num[i])))
            # print('PS ingress bandwidth: {}'.format(str(ps_throughput)))
            # print('In-network aggregation throughput: {}'.format(str(agg_throughput)))
            # print('Total throughput: {}'.format(str(total_band)))


if __name__ == "__main__":
    topo1 = TopoGenerator(json.load(open(os.path.join(BASE_DIR, '../topology/fattree80.json'))))
    algs=[DT(topo1),ATP(topo1),GRID(topo1),LINA(topo1)]
    worker_num_set = [20 + i * 5 for i in range(4)]  # 20 25 30 35
    switch_num = 5
    resources={
        'memory_size':60,
        'layer_size' : [15 for i in range(16)] # AlexNet, avg layer size of 15 MB, 16 layers
    }

    overhead=worker_num_overhead(algs, topo1, worker_num_set, switch_num,resources)