from algorithms.inputs import *
from itertools import chain


class Nothing(Algorithm):
    """Nothing"""
    def run(self):
        yield


class Shuffle(Algorithm):
    """Shuffle"""
    def run(self):
        nums_len = self.playground.main_array_len - 1
        for index in range(nums_len):
            self.playground.swap((0, index), (0, randint(index + 1, nums_len)))
            yield


class Reversal(Algorithm):
    """Reversal"""
    def reverse_array(self, array_index: int, start: int, end: int):
        for i in range((end - start) // 2):
            left, right = (array_index, start + i), (array_index, end - i - 1)
            self.playground.swap(left, right)
            yield

    def run(self):
        for _ in self.reverse_array(0, 0, self.playground.main_array_len):
            yield


class RecursiveReversal(Reversal):
    """Recursive Reversal"""
    def _run(self, start: int, section_len: int):
        if section_len < 2:
            return

        for _ in self.reverse_array(0, start, start + section_len):
            yield

        for _ in chain(self._run(start, section_len // 2), self._run(start + section_len // 2, section_len // 2)):
            yield

    def run(self):
        for _ in self._run(0, self.playground.main_array_len):
            yield


class HalfRotation(Algorithm):
    """Half Rotation"""
    def run(self):
        half_len = self.playground.main_array_len // 2
        self.playground.spawn_new_array(half_len)
        yield

        main_array_index = 0
        copy_array_index = 1

        for index in range(half_len):
            left_side_num = self.playground.read((main_array_index, index))
            yield

            self.playground.write(left_side_num, (copy_array_index, index))
            yield
        # Copy left half of array

        for index in range(half_len, self.playground.main_array_len):
            right_side_num = self.playground.read((main_array_index, index))
            yield

            self.playground.write(right_side_num, (main_array_index, index - half_len))
            yield
        # Write right half of array in left side

        for index in range(half_len):
            copied_left_side_num = self.playground.read((copy_array_index, index))
            yield

            self.playground.write(copied_left_side_num, (main_array_index, half_len + index))
            yield
        # Write copied left side into right side of array.

        self.playground.delete_array(copy_array_index)
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

        for index in range(1, self.playground.main_array_len):

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


class MaxHeap(Heapify):
    """Max Heap"""
    def run(self):
        for _ in self.heapify("max"):
            yield


class MinHeap(Heapify):
    """Min Heap"""
    def run(self):
        for _ in self.heapify("min"):
            yield


shuffles = [Nothing, Shuffle, Reversal, RecursiveReversal, HalfRotation, MaxHeap, MinHeap]
algorithms = shuffles + inputs


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
