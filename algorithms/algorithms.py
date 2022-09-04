from algorithms.inputs import *


class Shuffle(Algorithm):
    """Shuffle"""
    def run(self):
        nums_len = self.playground.capacity - 1
        for index in range(nums_len):
            self.playground.swap((0, index), (0, randint(index + 1, nums_len)))
            yield


class Reversal(Algorithm):
    """Reversal"""
    def reverse_array(self, array_index: int):
        array_length = len(self.playground.arrays[array_index])

        for i in range(array_length // 2):
            left, right = (array_index, i), (array_index, array_length - i - 1)
            self.playground.swap(left, right)
            yield

    def run(self):
        for _ in self.reverse_array(0):
            yield


class Heapify(Algorithm):
    """Heap"""
    def heapify(self, mode="min"):
        if mode == "max":
            comparison = "<"
        elif mode == "min":
            comparison = ">"
        else:
            raise ValueError("Invalid Heap Sort mode.")

        for index in range(1, len(self.playground.main_array)):

            while 0 < index:
                parent_index = (index - 1) >> 1

                should_bubble = self.playground.compare((0, parent_index), comparison, (0, index))
                yield

                if should_bubble:
                    self.playground.swap((0, parent_index), (0, index))
                    yield
                else:
                    break

                index = parent_index

    def run(self):
        raise NotImplementedError


algorithms = [Shuffle, Reversal, Heapify]


@dataclass
class Verify(Algorithm):
    sorted: bool = True

    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums) - 1):
            check = self.playground.compare((0, index), ">", (0, index + 1))
            yield

            if check:
                self.sorted = False
                break
