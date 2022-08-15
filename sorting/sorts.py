from sorting.algorithm import *
from itertools import count


@dataclass
class BubbleSort(Algorithm):
    optimized: bool = True

    def __str__(self):
        return ("Optimized" if self.optimized else "") + "Bubble Sort"

    def run(self):
        nums = self.playground.arrays[0]

        for sorted_elements in range(len(nums)):
            for index in range(len(nums) - sorted_elements - 1):

                if self.playground.compare((0, index), ">", (0, index + 1)):
                    yield

                    self.playground.swap((0, index), (0, index + 1))
                    yield


@dataclass
class InsertionSort(Algorithm):
    binary_search: bool = False

    def run(self):
        for unsorted_start_index in range(1, len(self.playground.arrays[0])):
            index = unsorted_start_index

            while 0 < index and self.playground.compare((0, index - 1), ">", (0, index)):
                yield

                self.playground.swap((0, index - 1), (0, index))
                yield

                index -= 1


@dataclass
class SelectionSort(Algorithm):
    double: bool = False

    def run(self):
        for unsorted_start_index in range(len(self.playground.main_array)):
            smallest = None

            for i in range(unsorted_start_index, len(self.playground.main_array)):

                if not smallest or self.playground.compare((0, i), "<", smallest):
                    smallest = (0, i)
                yield

            self.playground.swap(smallest, (0, unsorted_start_index))
            yield


@dataclass
class HeapSort(Algorithm):
    mode: str = "min"

    def run(self):
        # Heapify.
        if self.mode == "min":
            comparison = ">"
        elif self.mode == "max":
            comparison = "<"
        else:
            raise ValueError("Invalid HeapSort mode.")

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

        # Once heap is done:
        for sorted_index in range(len(self.playground.main_array) - 1, -1, -1):
            self.playground.swap((0, 0), (0, sorted_index))

            index = 0
            while (left_child_index := index * 2 + 1) < sorted_index:
                right_child_index = left_child_index + 1

                if right_child_index < sorted_index:

                    left_child = self.playground.read((0, left_child_index))
                    yield
                    right_child = self.playground.read((0, right_child_index))
                    yield

                    child_index = left_child_index if eval(f"{right_child}{comparison}{left_child}") else right_child_index
                    # must swap with its smallest child if mode is min;
                    # must swap with its biggest child if mode is max.
                else:
                    # If right child index is in out of bounds,
                    # left child is the only choice.
                    child_index = left_child_index

                should_swap = self.playground.compare((0, index), comparison, (0, child_index))
                yield

                if should_swap:
                    self.playground.swap((0, index), (0, child_index))
                    yield

                    index = child_index
                else:
                    break
                    # Done bubbling.

        if self.mode == "min":
            for _ in self.reversal(0):
                yield


@dataclass
class MergeSort(Algorithm):
    in_place: bool = False

    def out_of_place(self, start=0, end=0):
        if end == 0:
            end = len(self.playground.main_array)

        section_length = end - start

        if section_length > 1:
            midpoint = start + section_length // 2

            for _ in self.out_of_place(start, midpoint):
                yield
            for _ in self.out_of_place(midpoint, end):
                yield

            left_index = start
            right_index = midpoint

            merge_index = start

            while left_index < midpoint and right_index < end:
                if self.playground.compare((0, left_index), "<", (0, right_index)):
                    yield

                    self.playground.write(self.playground.read((0, left_index)), (1, merge_index))
                    yield

                    left_index += 1
                else:
                    yield

                    self.playground.write(self.playground.read((0, right_index)), (1, merge_index))
                    yield

                    right_index += 1
                merge_index += 1

            while left_index < midpoint:
                self.playground.write(self.playground.read((0, left_index)), (1, merge_index))
                yield

                left_index += 1
                merge_index += 1
            while right_index < end:
                self.playground.write(self.playground.read((0, right_index)), (1, merge_index))
                yield

                right_index += 1
                merge_index += 1

            for copy_index in range(start, merge_index):
                self.playground.write(self.playground.read((1, copy_index)), (0, copy_index))
                yield

    def run(self):
        yield

        if self.in_place:
            pass
        else:
            self.playground.spawn_new_array(len(self.playground.main_array))
            yield

            for _ in self.out_of_place():
                yield

            self.playground.delete_array(1)
            yield


class RadixSort(Algorithm):
    mode: str = "LSD"
    base: int = 10

    def lsd_digit(self, num: int, place: int):
        digit = 0
        for _ in range(place):
            digit = num % self.base
            num = num // self.base

        return digit, num

    def lsd(self):
        self.playground.spawn_new_array(self.playground.capacity)
        copy_array_index = 1
        yield
        # nums copy

        for digit_index in count(1, 1):

            self.playground.spawn_new_array(self.base)
            count_array_index = 2
            yield
            # counts array

            all_zeroes = True

            for index, num in enumerate(self.playground.array_iter(0)):
                yield
                self.playground.write(num, (copy_array_index, index))
                yield

                digit, division = self.lsd_digit(num, digit_index)

                if digit or division:
                    all_zeroes = False

                self.playground.increment(1, (count_array_index, digit))
                yield
            # copy array

            if all_zeroes:
                break

            prefix_sum = 0
            for count_index in range(self.base):
                current_count = self.playground.read((count_array_index, count_index))
                yield

                self.playground.write(prefix_sum, (count_array_index, count_index))
                yield

                prefix_sum += current_count
            # prefix sum

            for copy_index, num in enumerate(self.playground.array_iter(copy_array_index)):
                digit, division = self.lsd_digit(num, digit_index)

                new_index = self.playground.read((count_array_index, digit))
                yield

                self.playground.write(num, (0, new_index))
                yield

                self.playground.increment(1, (count_array_index, digit))
                yield
            # re-write array

            self.playground.delete_array(count_array_index)

        self.playground.delete_array(2)
        self.playground.delete_array(copy_array_index)

    def run(self):
        if self.mode == "LSD":
            return self.lsd()
        elif self.mode == "MSD":
            pass
        else:
            raise ValueError("Invalid Radix Sort mode.")
