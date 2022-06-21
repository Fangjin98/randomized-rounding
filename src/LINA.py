from collections import defaultdict
from distutils.log import Log
from email.policy import default
from operator import mod
import resource
import numpy as np
import pulp as pl

from BasicAlg import BasicAlg
from utils.TopoGenerator import TopoGenerator


class GRID(BasicAlg):
    def __init__(self, topo: TopoGenerator) -> None:
        super().__init__(topo)

    def run(self, test_set, resources, solver=None):
        ps = test_set[0]
        worker_set = test_set[1]
        switch_set = test_set[2]

        optimal_results = self._solve_lp(worker_set, switch_set, resources, solver)

        aggregation_node = self._knapsack_based_random_rounding(optimal_results, ps, worker_set, switch_set, resources)

        sending_rate = dict()
        switch = {s: 0 for s in switch_set}
        count = 0 
        
        # for index, w in enumerate(worker_set):
        #     if aggregation_node[w] != ps:  # aggregate on PS
        #         if switch[aggregation_node[w]] == 0:
        #             count += 1
        #         switch[aggregation_node[w]] += 1

        # for w in worker_set:
        #     if aggregation_node[w] == ps:
        #         sending_rate[w] = band / len(worker_set)

        # for index, s in enumerate(switch_set):
        #     if switch[s] == 0:
        #         continue
        #     tmp_rate = band * switch[s] / len(worker_set)
        #     for w in worker_set:
        #         if aggregation_node[w] == s:
        #             sending_rate[w] = tmp_rate
        #     sending_rate[s] = tmp_rate

        return aggregation_node, sending_rate

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
                        layer_assigned_node[index].append(l_res)
                    else:
                        l_res = np.random.choice([i for i in range(offset,knapsack_element_num+offset)], p=[x_s[index][i]/knapsack_num for i in range(offset,knapsack_element_num+offset+remained_element_num)])
                        layer_assigned_node[index].append(l_res)
        
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

        return aggregation_node