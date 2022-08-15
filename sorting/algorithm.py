from sorting.playground import SortPlayground
from dataclasses import dataclass


@dataclass
class Algorithm:
    playground: SortPlayground

    def run(self):
        raise NotImplementedError("Algorithm is abstract.")

    def reversal(self, array_index: int):
        array_length = len(self.playground.arrays[array_index])

        for i in range(array_length // 2):
            left, right = (array_index, i), (array_index, array_length - i - 1)
            self.playground.swap(left, right)
            yield
