import heapq
import json
import random
import sys
from collections import defaultdict


def get_link_array(paths: list, topo_dict: dict):
    link_index = defaultdict(dict)
    link_num = 0
    band = []

    for p in paths:
        weight_p = p.get_link_weight(topo_dict)
        for l in p.link_list:
            if l[1] not in link_index[l[0]].keys():
                link_index[l[0]][l[1]] = link_num
                link_num += 1
                band.append(weight_p[l[0]][l[1]])

    return link_index, band, link_num


class TopoGenerator(object):
    def __init__(self, topo_dict=dict(), topo_title=None):
        self.topo_dict = dict(topo_dict)
        self.host_set = []
        self.switch_set = []
        self.title = topo_title if topo_title is not None else "default"

        for key in topo_dict.keys():
            for value in topo_dict[key]:
                try:
                    if key not in self.topo_dict[value]:  # add reverse links
                        self.add_edge(value, key, topo_dict[key][value])
                except KeyError as e:
                    print(e)
                    self.topo_dict[value] = dict()
                    self.add_edge(value, key, topo_dict[key][value])

        for key in self.topo_dict.keys():
            if key[0] == "v" and (key not in self.switch_set):
                self.switch_set.append(key)
            elif key[0] == "h" and (key not in self.host_set):
                self.host_set.append(key)

    def __str__(self) -> str:
        return type(self).__name__

    def add_edge(self, src, dst, weight):
        self.topo_dict[src][dst] = weight

    def add_edges(self, edge_list):
        for e in edge_list:
            self.add_edge(e[0], e[1], e[2])

    def remove_edge(self, src, dst):
        if self.topo_dict[src]:
            for node in self.topo_dict[dst]:
                if node.keys()[0] is dst:
                    self.topo_dict[src].remove(node)
                    break

    def get_shortest_path(self, src, dst):
        distances = {}  # Distance from start to node
        previous = {}  # Previous node in optimal path from source
        nodes = []  # Priority queue of all nodes in Graph

        # init
        for node in self.topo_dict.keys():
            if node == src:  # Set root node as distance of 0
                distances[node] = 0
                heapq.heappush(nodes, [0, node])
            else:
                distances[node] = sys.maxsize
                heapq.heappush(nodes, [sys.maxsize, node])
            previous[node] = None

        while nodes:
            nearest = heapq.heappop(nodes)[1]
            if nearest == dst:
                p = []
                while previous[nearest]:
                    p.append(nearest)
                    nearest = previous[nearest]
                return Path(p)

            if distances[nearest] == sys.maxsize:
                raise RecursionError("Error: path not found.")

            for neighbor in self.topo_dict[nearest]:
                alt = distances[nearest] + self.topo_dict[nearest][neighbor]
                if alt < distances[neighbor]:
                    distances[neighbor] = alt
                    previous[neighbor] = nearest
                    for n in nodes:
                        if n[1] == neighbor:
                            n[0] = alt
                            break
                    heapq.heapify(nodes)

        raise RecursionError("Error: path not found.")

    def get_nearest_switch(self, worker, specific_switch_set=None):
        min_distance = sys.maxsize
        nearest_switch = None

        if specific_switch_set == None:
            specific_switch_set = self.switch_set

        for s in specific_switch_set:
            distance = len(self.get_shortest_path(worker, s))
            if distance == 1:
                return s
            else:
                if distance < min_distance:
                    nearest_switch = s
                    min_distance = distance
        return nearest_switch

    def construct_path_set(self, src_set, dst_set, max_len=8):
        path = defaultdict(dict)
        for s in src_set:
            for d in dst_set:
                path[s][d] = [Path(p) for p in self._get_feasible_path(s, d, max_len)]
        return path

    def _get_feasible_path(self, src, dst, max_len=None, path=[]):
        path = path + [src]

        if src == dst:
            return [path]

        if max_len is not None:
            if len(path) > max_len:
                return

        paths = []

        for node in self.topo_dict[src].keys():
            if node not in path:
                results = self._get_feasible_path(node, dst, max_len, path)
                if results is not None:
                    for p in results:
                        paths.append(p)

        return paths

    def generate_json(self, json_file):
        json_str = json.dumps(self.topo_dict, indent=4)
        with open(json_file, "w") as f:
            f.write(json_str)

    def generate_test_set(self, worker_num, switch_num, random_pick=False, seed=None):
        temp_host_set = list(self.host_set)
        temp_switch_set = list(self.switch_set)

        if random_pick:
            if not seed:
                random.seed(seed)
            random.shuffle(temp_host_set)
            random.shuffle(temp_switch_set)

        worker_set = []
        switch_set = []
        ps = temp_host_set[0]

        for i in range(1, worker_num + 1):
            worker_set.append(temp_host_set[i])

        for i in range(switch_num):
            switch_set.append(temp_switch_set[i])

        return [ps, worker_set, switch_set]


class BCubeGenerator(TopoGenerator):
    """
    This topology is defined as a recursive structure. A :math:`Bcube_0` is
    composed of n hosts connected to an n-port switch. A :math:`Bcube_1` is
    composed of n :math:`Bcube_0` connected to n n-port switches. A :math:`Bcube_k` is
    composed of n :math:`Bcube_{k-1}` connected to :math:`n^k` n-port switches.
    This topology comprises:
     * :math:`n^(k+1)` hosts, each of them connected to :math:`k+1` switches
     * :math:`n*(k+1)` switches, each of them having n ports
    Parameters
    ----------
    k : int
    The level of Bcube

    n : int
        The number of host per :math:`Bcube_0`
    """

    def __init__(self, k=1, n=4):
        if not isinstance(n, int) or not isinstance(k, int):
            raise TypeError("k and n arguments must be of int type")
        if n < 1:
            raise ValueError("Invalid n parameter. It should be >= 1")
        if k < 0:
            raise ValueError("Invalid k parameter. It should be >= 0")

        self.topo_dict = defaultdict(dict)
        self.host_set = ["h" + str(i) for i in range(n ** (k + 1))]
        self.switch_set = []

        for level in range(k + 1):
            sid = 0
            arg1 = n**level
            arg2 = n ** (level + 1)
            # i is the horizontal position of a switch a specific level
            for i in range(n**k):
                # add switch at given level
                sw = "s{}_{}".format(level, sid)
                self.switch_set.append(sw)
                sid += 1
                # add links between hosts and switch
                m = int(i % arg1 + i / arg1 * arg2)
                for index in range(m, m + arg2, arg1):
                    try:
                        self.add_edge(sw, self.host_set[index], 1)
                        self.add_edge(self.host_set[index], sw, 1)
                    except IndexError as e:
                        print(index)
                        break


class LeafSpineGenerator(TopoGenerator):
    """
    spine_num: number of spine switches
    leaf_num: number of leaf switches
    host_num: number of hosts per leaf switch
    """

    def __init__(self, spine_num, leaf_num, host_num, topo_title=None):
        if (
            not isinstance(spine_num, int)
            or not isinstance(leaf_num, int)
            or not isinstance(host_num, int)
        ):
            raise TypeError("arguments must be of int type")
        if spine_num < 1:
            raise ValueError("Invalid spine_num parameter. It should be >= 1.")
        if leaf_num < 1:
            raise ValueError("Invalid leaf_num parameter. It should be >= 1.")
        if host_num < 1:
            raise ValueError("Invalid host_num parameter. It should be >= 1.")

        self.title = topo_title if topo_title is not None else "leafspine"
        self.topo_dict = defaultdict(dict)
        self.host_set = []
        spine_switches = ["s" + str(i) for i in range(spine_num)]
        leaf_switches = ["s" + str(i) for i in range(spine_num, spine_num + leaf_num)]
        self.switch_set = spine_switches + leaf_switches

        for spine in spine_switches:
            for leaf in leaf_switches:
                self.add_edge(spine, leaf, 1)
                self.add_edge(leaf, spine, 1)

        count = 0
        for leaf in leaf_switches:
            for num in range(host_num):
                host = "h{}" + str(count)
                count += 1
                self.host_set.append(host)
                self.add_edge(host, leaf, 1)
                self.add_edge(leaf, host, 1)


class Path(object):
    def __init__(self, node_list, link_list=None):
        self.node_list = node_list
        if link_list == None:
            self.link_list = []
            for i in range(len(self.node_list) - 1):
                node1 = self.node_list[i]
                node2 = self.node_list[i + 1]
                self.link_list.append((node1, node2))
        else:
            self.link_list = link_list

    def __repr__(self):
        p_str = self.node_list[0]
        for node in self.node_list[1:]:
            p_str = p_str + "->" + node
        return p_str

    def __len__(self):
        return len(self.link_list)

    def get_link_weight(self, topo_dict):
        link_weight = defaultdict(dict)
        for i in range(len(self.node_list) - 1):
            node1 = self.node_list[i]
            node2 = self.node_list[i + 1]
            link_weight[node1][node2] = topo_dict[node1][node2]
        return link_weight
