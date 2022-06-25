from collections import defaultdict
from BasicAlg import BasicAlg
from utils.TopoGenerator import TopoGenerator


class DT(BasicAlg):
    def __init__(self, topo: TopoGenerator) -> None:
        super().__init__(topo)

    def run(self, test_set, resources):
        ps = test_set[0]
        worker_set = test_set[1]
        aggregation_node=defaultdict(list)
        
        for index_i, w in enumerate(worker_set):
            for index_j, l in enumerate(resources['layer_size']):
                aggregation_node[w].append(ps)

        return aggregation_node