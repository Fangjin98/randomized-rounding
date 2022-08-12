from ATP import ATP
from utils.TopoGenerator import TopoGenerator


class SwitchML(ATP):
    def __init__(self, topo: TopoGenerator) -> None:
        super().__init__(topo)

    def run(self, test_set, resources, **kwargs):
        worker_set = test_set[1]
        switch_set = test_set[2]

        aggregation_node = dict()

        for w in worker_set:
            aggregation_node[w] = self.topo.get_nearest_switch(w,specific_switch_set=switch_set)

        return aggregation_node
