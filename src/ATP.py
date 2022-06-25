from collections import defaultdict
import random
from typing import List
from BasicAlg import BasicAlg
from utils.TopoGenerator import TopoGenerator


class ATP(BasicAlg):
    def __init__(self, topo: TopoGenerator) -> None:
        super().__init__(topo)

    def run(self, test_set, resources, **kwargs):
        ps = test_set[0]
        worker_set = test_set[1]
        switch_set = test_set[2]

        aggregation_node = defaultdict(list)
        MEM_SIZE=resources['memory_size']
        LAYER_SIZE=resources['layer_size']
        
        delayed_worker_num=int(len(worker_set)* kwargs['delay_ratio'])
        print("No. of delayed workers = {}".format(str(delayed_worker_num)))
        
        for w in worker_set[:delayed_worker_num]:
            for l in LAYER_SIZE:
                aggregation_node[w].append(ps)
        
        for w in worker_set[delayed_worker_num:]:
            node=self.topo.get_nearest_switch(w,specific_switch_set=switch_set)
            remained_mem=MEM_SIZE
            for index_l, l in enumerate(LAYER_SIZE):
                if remained_mem >= l:
                    remained_mem-=l
                    aggregation_node[w].append(node)
                else:
                    aggregation_node[w].append(ps)

        return aggregation_node

