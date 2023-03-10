import random

from algorithm import SampleAlg
from topology import LeafSpineGenerator

worker_num = 40
switch_num = 10
resource = {
    "comp_base": 3200,
    "ingress_band": 100,
}
computing_resource = [
    resource["comp_base"] + random.randint(-1000, 0) for _ in range(switch_num)
]

if __name__ == "__main__":
    topo = LeafSpineGenerator(30, 30, 10)
    alg = SampleAlg(topo)

    test_set = topo.generate_test_set(worker_num, switch_num, random_pick=True, seed=10)

    alg.run(test_set, computing_resource, resource["ingress_band"])
