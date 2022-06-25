from collections import defaultdict
import os
import sys
import json
import pandas as pd

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
    
    total_overhead=pd.DataFrame(columns=worker_num_set, index=['Geryon','ATP','ATP+','LINA'])
    print(total_overhead)

    for num in worker_num_set:
        test_set, flattern_test_set = topo.generate_test_set(num, switch_num, random_pick=True, seed=10)
        results=[]

        print("Test: \t{} workers.".format(str(num)))

        print("----------------Geryon--------------")   
        aggregation_policy,layer_depolyment=algs[0].run(flattern_test_set,resources)
        results.append(algs[0].cal_total_overhead(flattern_test_set, resources, aggregation_policy, layer_depolyment))
        
        print("-----------------ATP-----------------")
        aggregation_policy,layer_depolyment=algs[1].run(flattern_test_set,resources,delay_ratio=0.2)
        results.append(algs[1].cal_total_overhead(flattern_test_set, resources, aggregation_policy, layer_depolyment))

        print("-----------------ATP+Geryon--------------")
        results.append(0)
        print("----------------LINA---------------")
        aggregation_policy, layer_depolyment=algs[3].run(flattern_test_set,resources)
        results.append(algs[3].cal_total_overhead(flattern_test_set, resources, aggregation_policy, layer_depolyment))
        
        total_overhead[num]=results
        # overhead['ingress']=algs[3].cal_ingress_overhead(flattern_test_set, resources, layer_depolyment)
        # overhead['in-network']=algs[3].cal_innetwork_aggregation_overhead(flattern_test_set, resources, aggregation_policy)

        print(total_overhead)
        

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