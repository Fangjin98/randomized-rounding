from collections import defaultdict
import numpy as np
import pulp as pl

from BasicAlg import BasicAlg
from utils.TopoGenerator import TopoGenerator


class LINA(BasicAlg):
    def __init__(self, topo: TopoGenerator) -> None:
        super().__init__(topo)

    def run(self, test_set, resources, solver=None):
        ps = test_set[0]
        worker_set = test_set[1]
        switch_set = test_set[2]

        optimal_results = self._solve_lp(worker_set, switch_set, resources, solver)

        return self._knapsack_based_random_rounding(optimal_results, ps, worker_set, switch_set, resources)

    
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
        
    def _solve_lp(self, ps, worker_set, switch_set, resources, solver):

        lp_problem = pl.LpProblem("LINA", pl.LpMaximize)

        MEM_SIZE=resources['memory_size']
        LAYER_SIZE=resources['layer_size']

        layer_num=len(LAYER_SIZE)
        worker_num = len(worker_set)
        switch_num = len(switch_set)

        
        x_ps = [pl.LpVariable('x_l' + str(i) + 'ps', lowBound=0, upBound=1)
                for i in range(layer_num)]

        x_s = [[pl.LpVariable('x_l' + str(i) + 's' + str(j), lowBound=0, upBound=1)
                for j in range(switch_num)]
               for i in range(layer_num)]


        y_ps = [[pl.LpVariable('y_n' + str(i) +'l'+ str(j) + 'ps', lowBound=0, upBound=1)
             for j in range(layer_num)]
             for i in range(worker_num)]

        y_s = [[[pl.LpVariable('y_n' + str(i) +'l'+ str(j) + 's'+str(k), lowBound=0, upBound=1)
             for k in range(switch_num)]
             for j in range(layer_num)]
             for i in range(worker_num)]

        lp_problem += pl.lpSum(
            [ pl.lpSum([y_s[i][j][k] for i in range(worker_num)]) - x_s[j][k] * len(self.topo.get_shortest_path(switch_set[k], ps)) * LAYER_SIZE[j] for j in range(layer_num) for k in range(switch_num)]
            ) 

        for i in range(layer_num):
            lp_problem += pl.lpSum([x_ps[i]] + [x_s[i][j] for j in range(switch_num)]) >= 1

        for i in range(worker_num):
            for j in range(layer_num):
                lp_problem += pl.lpSum([y_ps[i][j]] + [y_s[i][j][k] for k in range(switch_num)]) == 1

        for i in range(worker_num):
            for j in range(layer_num):
                    lp_problem += y_ps[i][j] <= x_ps[j]
        
        for i in range(worker_num):
            for j in range(layer_num):
                for k in range(switch_num):
                    lp_problem += y_s[i][j][k] <= x_s[j][k]

        for i in range(switch_num):
            lp_problem += pl.lpSum([x_s[j][i] * LAYER_SIZE[j] for j in range(layer_num)]) <= MEM_SIZE[i]


        if solver is not None:
            try:
                lp_problem.solve(pl.get_solver(solver))
                print("Using solver: " + solver)
            except Exception as e:
                print(e)
                lp_problem.solve()
        else:
            lp_problem.solve()

        print('objective =', pl.value(lp_problem.objective))

        return np.asarray([x_ps[i].value() for i in range(worker_num)]), \
               np.asarray([[x_s[i][j].value() for j in range(switch_num)] for i in range(worker_num)]), \
               np.asarray([[y_ps[i][j].value() for j in range(layer_num)] for i in range(worker_num)]), \
                np.asarray([[[y_s[i][j][k] for k in range(switch_num)] for j in range(layer_num)] for i in range(worker_num)])

    @staticmethod
    def _knapsack_based_random_rounding(optimal_results, ps, worker_set, switch_set, resources):
        x_ps = optimal_results[0]
        x_s = optimal_results[1]
        y_ps=optimal_results[2]
        y_s=optimal_results[3]
        
        LAYER_SIZE=resources['layer_size']

        layer_assigned_node=[[] for i in range(len(LAYER_SIZE))] # each layer aggregated by which switch
        aggregation_node=defaultdict(list)

        for index, l in enumerate(LAYER_SIZE):
            knapsack_num=np.sum(x_s[index])
            if knapsack_num != 0:
                knapsack_element_num=len(switch_set)/knapsack_num
                remained_element_num= len(switch_set) % knapsack_num
                offset=0
                for k in range(knapsack_num):
                    if k == knapsack_num-1: # the last knapsack
                        l_res = np.random.choice([i for i in range(offset,knapsack_element_num+offset+remained_element_num)], p=[x_s[index][i]/knapsack_num for i in range(offset,knapsack_element_num+offset+remained_element_num)])
                        layer_assigned_node[index].append(switch_set[l_res])
                    else:
                        l_res = np.random.choice([i for i in range(offset,knapsack_element_num+offset)], p=[x_s[index][i]/knapsack_num for i in range(offset,knapsack_element_num+offset+remained_element_num)])
                        layer_assigned_node[index].append(switch_set[l_res])
            else: layer_assigned_node[index].append(ps)
        
        print(layer_assigned_node)

        for index_i, w in enumerate(worker_set):
            for index_j, l in enumerate(LAYER_SIZE):
                if layer_assigned_node.count()==0:
                    aggregation_node[w].append(ps)
                else:
                    prob=[]
                    for s in layer_assigned_node[index_j]:
                        prob.append[y_s[index_i][index][s]/x_s[index][s]]
                    prob.append(1-sum(prob))
                    node=np.random.choice([switch_set[i] for i in layer_assigned_node[index]]+[ps], prob=prob)
                    aggregation_node[w].append(node)
        
        print(aggregation_node)

        return aggregation_node, layer_assigned_node