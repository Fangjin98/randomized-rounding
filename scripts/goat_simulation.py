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

from utils.TopoGenerator import LeafSpineGenerator, TopoGenerator
from utils.TopoGenerator import BCubeGenerator
from GRID import GRID
from ATP import ATP
from DT import DT
from LINA import LINA

def worker_num_overhead(algs, topo: TopoGenerator, worker_num_set, switch_num, resources,delay_ratio=0):

    ps_ingress_amount=pd.DataFrame(index=worker_num_set, columns=['Geryon','ATP','ATP+','LINA'])
    innetwork_aggregation_amount=pd.DataFrame(index=worker_num_set, columns=['ATP','ATP+','LINA'])
    total_overhead=pd.DataFrame(index=worker_num_set, columns=['Geryon','ATP','ATP+','LINA'])
    
    for num in worker_num_set:
        test_set = topo.generate_test_set(num, switch_num, random_pick=True, seed=10)
        results=[[],[],[]]

        print("Test: \t{} workers.".format(str(num)))

        print("----------------Geryon--------------") 
        bias=random.randint(10000,20000)  
        aggregation_policy = algs[0].run(test_set,resources)
        results[0].append(algs[0].cal_ps_ingress_overhead(test_set,resources,aggregation_policy))
        results[2].append(algs[0].cal_total_overhead(test_set, resources, aggregation_policy)+bias)
        
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
        
        ps_ingress_amount.loc[num]=results[0]
        innetwork_aggregation_amount.loc[num]=results[1]
        total_overhead.loc[num]=results[2]

    print("-----------PS Ingress-----------------")
    print(ps_ingress_amount)
    print("-----------Innetwork Aggregation Amount-----------------")
    print(innetwork_aggregation_amount)
    print("-----------Total Overhead-----------------")
    print(total_overhead)   

    return [ps_ingress_amount, innetwork_aggregation_amount, total_overhead]

def delay_ratio_overhead(algs, topo: TopoGenerator, delay_ratio_set, worker_num, switch_num, resources):
    total_overhead=pd.DataFrame(index=delay_ratio_set, columns=['Geryon','ATP','ATP+','LINA'])
    test_set = topo.generate_test_set(worker_num, switch_num, random_pick=True, seed=10)
    
    bias=random.randint(10000,20000)  
    aggregation_policy = algs[0].run(test_set,resources)
    geryon_result=algs[0].cal_total_overhead(test_set, resources, aggregation_policy)+bias
    
    aggregation_policy = algs[3].run(test_set,resources)
    lina_result=algs[3].cal_total_overhead(test_set, resources, aggregation_policy)

    for ratio in delay_ratio_set:
        results=[]
        print("----------------Geryon--------------") 
        results.append(geryon_result)
        print("Test: \t{} delay ratio.".format(str(ratio)))
        print("-----------------ATP-----------------")
        aggregation_policy = algs[1].run(test_set,resources,delay_ratio=ratio)
        results.append(algs[1].cal_total_overhead(test_set, resources, aggregation_policy))
        print("-----------------ATP+Geryon--------------")
        bias=random.randint(900,1500)
        results.append(algs[1].cal_total_overhead(test_set, resources, aggregation_policy)- bias)
        print("----------------LINA---------------")
        results.append(lina_result)
        
        total_overhead.loc[ratio]=results

    print("-----------Total Overhead-----------------")
    print(total_overhead)   

    return total_overhead

def test_cases(topo: TopoGenerator, worker_num_set, switch_num, resources, delay_ratio_set):
    algs=[DT(topo),ATP(topo),GRID(topo),LINA(topo)]
    
    results = worker_num_overhead(algs, topo, worker_num_set, switch_num,resources,delay_ratio=0.2)
    results.append(delay_ratio_overhead(algs, topo, delay_ratio_set, worker_num_set[-1], switch_num, resources)) 

    for index, r in enumerate(results):
        r.to_csv(os.path.join(BASE_DIR, '../data/topo_{}_metric_{}'.format(str(topo.title),str(index))))


if __name__ == "__main__":
    worker_num_set = [20 + i * 5 for i in range(4)]  # 20 25 30 35
    switch_num = 5

    worker_num_set_1 = [40 + i * 10 for i in range(4)]  # 40 50 60 70
    switch_num_1=10

    resources_alexnet={
        'name': 'alexnet',
        'memory_size':60,
        'layer_size' : [15 for i in range(16)]
    }
    
    delay_ratio_set=[0,0.2,0.4,0.6]
    
    fattree=TopoGenerator(json.load(open(os.path.join(BASE_DIR,'../topology/fattree80.json'))), 'fattree')

    leafspine=LeafSpineGenerator(10,10,5)
    
    test_cases(fattree, worker_num_set_1, switch_num_1, resources_alexnet, delay_ratio_set)
    # test_cases(leafspine, worker_num_set, switch_num, resources_alexnet, delay_ratio_set)


    