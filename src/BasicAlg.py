from abc import ABC, abstractmethod
from utils.TopoGenerator import TopoGenerator


class BasicAlg(ABC):
    def __init__(self, topo: TopoGenerator) -> None:
        self.topo = topo

    @abstractmethod
    def run(self, input):
        pass
    
    def cal_ingress_overhead(self, test_set, resources, layer_deployment):
        overhead = 0
        
        for index, size in enumerate(resources['layer_size']):
            overhead += sum([len(self.topo.get_shortest_path(node, test_set[0])) * size for node in layer_deployment[index]]) 
        
        return overhead

    def cal_innetwork_aggregation_overhead(self, test_set, resources, aggregation_policy):
        aggregation_amount=0
        for w in test_set[1]:
            for size, node in zip(resources['layer_size'],aggregation_policy[w]):
                if node != test_set[0]:
                    aggregation_amount += size
        return aggregation_amount

    def cal_total_overhead(self, test_set, resources, aggregation_policy, layer_deployment):
        total_overhead=0
        for w in test_set[1]:
            for size, node in zip(resources['layer_size'],aggregation_policy[w]):
                total_overhead += size * len(self.topo.get_shortest_path(w, node))
        
        total_overhead+= self.cal_ingress_overhead(test_set, resources, layer_deployment)

        return total_overhead