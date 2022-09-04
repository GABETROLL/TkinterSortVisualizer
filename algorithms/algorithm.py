from algorithms.playground import SortPlayground
from dataclasses import dataclass


@dataclass
class Algorithm:
    playground: SortPlayground

    def run(self):
        raise NotImplementedError("Algorithm is abstract.")
