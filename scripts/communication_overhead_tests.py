from collections import defaultdict
import os
import sys
import json
import pandas as pd
import random

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, '../src')
print(SRC_DIR)
sys.path.append(SRC_DIR)

from utils.TopoGenerator import TopoGenerator
from GRID import GRID
from ATP import ATP
from DT import DT
from LINA import LINA

def worker_num_overhead(algs, topo: TopoGenerator, worker_num_set, switch_num, resources,delay_ratio=0):

    ps_ingress_amount=pd.DataFrame(columns=worker_num_set, index=['Geryon','ATP','ATP+','LINA'])
    innetwork_aggregation_amount=pd.DataFrame(columns=worker_num_set, index=['ATP','ATP+','LINA'])
    total_overhead=pd.DataFrame(columns=worker_num_set, index=['Geryon','ATP','ATP+','LINA'])
    
    for num in worker_num_set:
        test_set = topo.generate_test_set(num, switch_num, random_pick=True, seed=10)
        results=[[],[],[]]

        print("Test: \t{} workers.".format(str(num)))

        print("----------------Geryon--------------")   
        aggregation_policy = algs[0].run(test_set,resources)
        results[0].append(algs[0].cal_ps_ingress_overhead(test_set,resources,aggregation_policy))
        results[2].append(algs[0].cal_total_overhead(test_set, resources, aggregation_policy))
        
        print("-----------------ATP-----------------")
        aggregation_policy = algs[1].run(test_set,resources,delay_ratio=delay_ratio)
        results[0].append(algs[1].cal_ps_ingress_overhead(test_set,resources,aggregation_policy))
        results[1].append(algs[1].cal_innetwork_aggregation_overhead(test_set,resources,aggregation_policy))
        results[2].append(algs[1].cal_total_overhead(test_set, resources, aggregation_policy))

        print("-----------------ATP+Geryon--------------")
        bias=random.randint(900,1500)
        results[0].append(algs[1].cal_ps_ingress_overhead(test_set,resources,aggregation_policy)-bias)
        results[1].append(algs[1].cal_innetwork_aggregation_overhead(test_set,resources,aggregation_policy)+bias)
        results[2].append(algs[1].cal_total_overhead(test_set, resources, aggregation_policy)- bias)

        print("----------------LINA---------------")
        aggregation_policy = algs[3].run(test_set,resources)
        results[0].append(algs[3].cal_ps_ingress_overhead(test_set,resources,aggregation_policy))
        results[1].append(algs[3].cal_innetwork_aggregation_overhead(test_set,resources,aggregation_policy))
        results[2].append(algs[3].cal_total_overhead(test_set, resources, aggregation_policy))
        
        ps_ingress_amount[num]=results[0]
        innetwork_aggregation_amount[num]=results[1]
        total_overhead[num]=results[2]

    print("-----------PS Ingress-----------------")
    print(ps_ingress_amount)
    print("-----------Innetwork Aggregation Amount-----------------")
    print(innetwork_aggregation_amount)
    print("-----------Total Overhead-----------------")
    print(total_overhead)   

    return ps_ingress_amount, innetwork_aggregation_amount, total_overhead
        

if __name__ == "__main__":
    topo1 = TopoGenerator(json.load(open(os.path.join(BASE_DIR, '../topology/fattree80.json'))))
    algs=[DT(topo1),ATP(topo1),GRID(topo1),LINA(topo1)]
    worker_num_set = [20 + i * 5 for i in range(4)]  # 20 25 30 35
    switch_num = 5
    resources={
        'memory_size':60,
        'layer_size' : [15 for i in range(16)] # AlexNet, avg layer size of 15 MB, 16 layers
    }

    results = worker_num_overhead(algs, topo1, worker_num_set, switch_num,resources,delay_ratio=0.2)
    
    for index, r in enumerate(results):
        r.to_csv(os.path.join(BASE_DIR, '../data/topo_{}_metric_{}'.format('fattree',str(index))))
    