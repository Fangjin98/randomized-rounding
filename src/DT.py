from collections import defaultdict
from BasicAlg import BasicAlg
from utils.TopoGenerator import TopoGenerator


class DT(BasicAlg):
    def __init__(self, topo: TopoGenerator) -> None:
        super().__init__(topo)

    def run(self, test_set, resources):
        ps = test_set[0]
        worker_set = test_set[1]
        LAYER_SIZE=resources['layer_size']
        
        layer_assigned_node=[[] for i in range(len(LAYER_SIZE))] # each layer aggregated by which switch
        aggregation_node=defaultdict(list)
        
        for index, l in enumerate(LAYER_SIZE):
            layer_assigned_node[index].append(ps)
        
        print(layer_assigned_node)

        for index_i, w in enumerate(worker_set):
            for index_j, l in enumerate(LAYER_SIZE):
                aggregation_node[w].append( ps )
        
        print(aggregation_node)

        return aggregation_node, layer_assigned_node