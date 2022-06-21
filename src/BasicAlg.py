from abc import ABC, abstractmethod
from utils.TopoGenerator import TopoGenerator


class BasicAlg(ABC):
    def __init__(self, topo: TopoGenerator) -> None:
        self.topo = topo

    @abstractmethod
    def run(self, input):
        pass
