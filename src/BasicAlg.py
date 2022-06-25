from abc import ABC, abstractmethod
from utils.TopoGenerator import TopoGenerator


class BasicAlg(ABC):
    def __init__(self, topo: TopoGenerator) -> None:
        self.topo = topo

    @abstractmethod
    def run(self, input):
        pass
    
    def _cal_aggregated_overhead(self, test_set, resources, aggregation_policy):
        ps=test_set[0]
        worker_set=test_set[1]
        aggregated_overhead = 0

        layer_deployment=[ set() for i in range(len(resources['layer_size']))]

        for w in worker_set:
            for index, node in enumerate(aggregation_policy[w]):
                layer_deployment[index].add(node)                

        for index, size in enumerate(resources['layer_size']):
            aggregated_overhead += sum([len(self.topo.get_shortest_path(node, ps)) * size for node in layer_deployment[index]]) 
        
        return aggregated_overhead

    def cal_ps_ingress_overhead(self,test_set,resources,aggregation_policy):
        ingress_overhead=0
        ps=test_set[0]
        # non-aggregated traffic, ie, worker to ps
        for w in test_set[1]:
            for size, node in zip(resources['layer_size'],aggregation_policy[w]):
                if node == ps:
                    ingress_overhead += size * len(self.topo.get_shortest_path(w, node))
        
        ingress_overhead+= self._cal_aggregated_overhead(test_set, resources, aggregation_policy)

        return ingress_overhead
        
    def cal_innetwork_aggregation_overhead(self, test_set, resources, aggregation_policy):
        ps=test_set[0]
        aggregation_amount=0
        for w in test_set[1]:
            for size, node in zip(resources['layer_size'],aggregation_policy[w]):
                if node != ps:
                    aggregation_amount += size
        return aggregation_amount

    def cal_total_overhead(self, test_set, resources, aggregation_policy):
        total_overhead=0
        
        # non-aggregated traffic, ie, worker to nodes
        for w in test_set[1]:
            for size, node in zip(resources['layer_size'],aggregation_policy[w]):
                total_overhead += size * len(self.topo.get_shortest_path(w, node))
        
        total_overhead+= self._cal_aggregated_overhead(test_set, resources, aggregation_policy)

        return total_overhead