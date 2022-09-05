from algorithms.algorithms import *
from itertools import count, chain


class BubbleSort(Algorithm):
    """Bubble Sort"""
    def run(self):
        nums_len = len(self.playground.main_array)

        for sorted_elements in range(nums_len):
            for index in range(nums_len - 1):

                should_swap = self.playground.compare((0, index), ">", (0, index + 1))
                yield

                if should_swap:
                    self.playground.swap((0, index), (0, index + 1))
                    yield


class OptimizedBubbleSort(BubbleSort):
    """Optimized Bubble Sort"""
    def run(self):
        nums_len = len(self.playground.main_array)

        for sorted_elements in range(nums_len):

            all_sorted = True
            for index in range(nums_len - sorted_elements - 1):

                should_swap = self.playground.compare((0, index), ">", (0, index + 1))
                yield

                if should_swap:
                    self.playground.swap((0, index), (0, index + 1))
                    yield

                    all_sorted = False

            if all_sorted:
                break


class CocktailShakerSort(Algorithm):
    """Cocktail Shaker Sort"""
    def run(self):
        nums_len = len(self.playground.main_array)
        for sorted_elements in range(nums_len):
            for index in chain(range(sorted_elements, nums_len - sorted_elements - 1),
                               range(nums_len - sorted_elements - 2, sorted_elements - 1, -1)):

                should_swap = self.playground.compare((0, index), ">", (0, index + 1))
                yield

                if should_swap:
                    self.playground.swap((0, index), (0, index + 1))
                    yield


class OptimizedCocktailShakerSort(CocktailShakerSort):
    """Optimized Cocktail Shaker Sort"""
    def run(self):
        nums_len = len(self.playground.main_array)

        for sorted_elements in range(nums_len):

            all_sorted = True

            for index in chain(range(sorted_elements, nums_len - sorted_elements - 1),
                               range(nums_len - sorted_elements - 2, sorted_elements - 1, -1)):

                should_swap = self.playground.compare((0, index), ">", (0, index + 1))
                yield

                if should_swap:
                    self.playground.swap((0, index), (0, index + 1))
                    yield

                    all_sorted = False

            if all_sorted:
                break


class InsertionSort(Algorithm):
    """Insertion Sort"""
    def run(self):
        for unsorted_start_index in range(1, len(self.playground.arrays[0])):
            index = unsorted_start_index

            while 0 < index and self.playground.compare((0, index - 1), ">", (0, index)):
                yield

                self.playground.swap((0, index - 1), (0, index))
                yield

                index -= 1


class BinaryInsertionSort(InsertionSort):
    """Insertion Sort (Binary Search)"""
    def run(self):
        pass


class SelectionSort(Algorithm):
    """Selection Sort"""
    def run(self):
        for unsorted_start_index in range(len(self.playground.main_array)):
            smallest = None

            for i in range(unsorted_start_index, len(self.playground.main_array)):

                if not smallest or self.playground.compare((0, i), "<", smallest):
                    smallest = (0, i)
                yield

            self.playground.swap(smallest, (0, unsorted_start_index))
            yield


class DoubleSelectionSort(SelectionSort):
    """Double Selection Sort"""
    def run(self):
        pass


class HeapSort(Reversal):
    """Heap Sort"""
    def sort(self, mode="min"):
        if mode == "max":
            comparison = "<"
        elif mode == "min":
            comparison = ">"
        else:
            raise ValueError("Invalid Heap Sort mode.")

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

                    child_index = left_child_index if eval(
                        f"{right_child}{comparison}{left_child}") else right_child_index
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

        if mode == "min":
            for _ in self.reverse_array(0, 0, self.playground.capacity):
                yield

    def run(self):
        raise NotImplementedError


class MaxHeapSort(Heapify, HeapSort):
    """Max Heap Sort"""
    def run(self):
        for _ in chain(self.heapify("max"), self.sort("max")):
            yield


class MinHeapSort(Heapify, HeapSort):
    """Min Heap Sort"""
    def run(self):
        for _ in chain(self.heapify("min"), self.sort("min")):
            yield


class QuickSort(Algorithm):
    """Quick Sort"""
    def quick_sort(self, start=0, end=0):
        # [6, 8, 1, 7, 5, 9, 2, 0, 4, 3]
        # 6, 5, 3 -> median := 5
        # [6, 8, 1, 7, 5, 9, 2, 0, 4, 3]
        #  ^           p
        # [5, 8, 1, 7, 6, 9, 2, 0, 4, 3]
        #  p  ^
        #  p     ^
        # [5, 1, 8, 7, 6, 9, 2, 0, 4, 3]
        # [1, 5, 8, 7, 6, 9, 2, 0, 4, 3]
        #     p     ^
        #     p        ^
        #     p           ^
        #     p              ^
        # [1, 5, 2, 7, 6, 9, 8, 0, 4, 3]
        # [1, 2, 5, 7, 6, 9, 8, 0, 4, 3]
        #        p              ^
        # [1, 2, 5, 0, 6, 9, 8, 7, 4, 3]
        # [1, 2, 0, 5, 6, 9, 8, 7, 4, 3]
        #           p              ^
        # [1, 2, 0, 5, 4, 9, 8, 7, 6, 3]
        # [1, 2, 0, 4, 5, 9, 8, 7, 6, 3]
        #              p              ^
        # [1, 2, 0, 4, 5, 3, 8, 7, 6, 9]
        # [1, 2, 0, 4, 3, 5, 8, 7, 6, 9]
        # repeat again with left and right halves.
        if end == 0:
            end = len(self.playground.main_array)

        pivot_index = start
        pointer_index = start + 1

        while pointer_index < end:
            should_swap = self.playground.compare((0, pointer_index), "<", (0, pivot_index))
            yield

            if should_swap:
                self.playground.swap((0, pointer_index), (0, pivot_index + 1))
                yield

                self.playground.swap((0, pivot_index), (0, pivot_index + 1))
                yield

                pivot_index += 1

            pointer_index += 1

        # print(start, pivot_index, pivot_index + 1, end)

        if 1 < (pivot_index - start):
            for _ in self.quick_sort(start, pivot_index):
                yield
        if 1 < (end - (pivot_index + 1)):
            for _ in self.quick_sort(pivot_index + 1, end):
                yield

    def run(self):
        for _ in self.quick_sort():
            yield


class MergeSort(Algorithm):
    """Merge Sort"""
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
        self.playground.spawn_new_array(len(self.playground.main_array))
        yield

        for _ in self.out_of_place():
            yield

        self.playground.delete_array(1)
        yield


class MergeSortInPlace(MergeSort):
    """Merge Sort (In-place: Insertion Sort)"""
    def in_place(self, start, end):
        section_length = end - start

        if section_length > 1:
            midpoint = start + section_length // 2

            for _ in self.in_place(start, midpoint):
                yield
            for _ in self.in_place(midpoint, end):
                yield

            for merge_index in range(midpoint, end):

                for insert_index in range(merge_index, start, -1):
                    a, b = (0, insert_index - 1), (0, insert_index)

                    should_insert = self.playground.compare(a, ">", b)
                    yield

                    if should_insert:
                        self.playground.swap(a, b)
                        continue
                    break

    def run(self):
        for _ in self.in_place(0, len(self.playground.main_array)):
            yield


@dataclass
class RadixSort(Algorithm):
    """Radix Sort"""
    base: int = 10

    def run(self):
        raise NotImplementedError


class RadixLSDSort(RadixSort):
    """Radix LSD Sort"""
    def lsd_digit(self, num: int, place: int):
        digit = 0
        for _ in range(place):
            digit = num % self.base
            num = num // self.base

        return digit, num

    def run(self):
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


class RadixLSDSortInPlace(RadixLSDSort):
    """Radix LSD Sort In-Place"""
    def run(self):
        nums_len = len(self.playground.main_array)

        for digit_index in count(1, 1):

            digit_pointers = [nums_len for _ in range(self.base)]
            # where each bucket ends

            all_zeroes = True

            for checked_num in range(nums_len):
                # When 0 is at the start, we finished collecting all the numbers.
                num = self.playground.read((0, 0))
                yield

                digit, division = self.lsd_digit(num, digit_index)

                if digit or division:
                    all_zeroes = False

                for digit_pointer_index in range(digit):
                    digit_pointers[digit_pointer_index] -= 1

                destination = digit_pointers[digit]

                for num_index in range(destination - 1):
                    self.playground.swap((0, num_index), (0, num_index + 1))
                    yield
                # swap until destination

            if all_zeroes:
                break


class RadixMSDSort(RadixSort):
    """Radix MSD Sort"""
    def run(self):
        pass


class PigeonholeSort(Algorithm):
    """Pigeonhole Sort"""
    def run(self):
        min_num_index = (0, 0)
        for index in range(len(self.playground.main_array)):
            current_index = (0, index)

            new_min_number = self.playground.compare(current_index, "<", min_num_index)
            yield

            if new_min_number:
                min_num_index = current_index

        min_num = self.playground.read(min_num_index)
        yield

        self.playground.spawn_new_array(len(self.playground.main_array))
        yield

        for index in range(len(self.playground.main_array)):
            num = self.playground.read((0, index))
            yield

            copy_array_index = (1, num - min_num)

            self.playground.write(num, copy_array_index)
            yield

        for _ in self.playground.copy_array(1, 0):
            yield

        self.playground.delete_array(1)
        yield


class CountSort(Algorithm):
    """Count Sort"""
    def run(self):
        min_index = 0
        max_index = 0

        for index in range(len(self.playground.main_array)):
            new_min_found = self.playground.compare((0, index), "<", (0, min_index))
            yield

            if new_min_found:
                min_index = index

            new_max_found = self.playground.compare((0, max_index), "<", (0, index))
            yield

            if new_max_found:
                max_index = index

        min_num = self.playground.read((0, min_index))
        yield
        max_num = self.playground.read((0, max_index))
        yield

        self.playground.spawn_new_array(max_num - min_num + 2)

        for num in self.playground.array_iter(0):
            yield

            self.playground.increment(1, (1, num - min_num))
            yield

        index = 0
        for num, num_count in enumerate(self.playground.array_iter(1)):
            yield

            num += min_num
            # ?
            for _ in range(num_count):
                self.playground.write(num, (0, index))
                yield

                index += 1

        self.playground.delete_array(1)
        yield


class GravitySort(Algorithm):
    """Gravity Sort"""
    def run(self):
        array_length = len(self.playground.main_array)

        self.playground.spawn_new_array(array_length)
        for _ in self.playground.copy_array(0, 1):
            yield
        copy_array_index = 1

        max_num = 0
        for num in self.playground.array_iter(0):
            yield

            if num > max_num:
                max_num = num

        for height in range(max_num, 0, -1):
            beads_at_height = 0

            for index in range(array_length):
                num = self.playground.read((copy_array_index, index))
                yield

                if height <= num:
                    beads_at_height += 1

                    self.playground.increment(-1, (0, index))
                    # decrement
                yield

            for index in range(array_length - 1, array_length - 1 - beads_at_height, -1):
                self.playground.increment(1, (0, index))
                yield


class Concurrent(Algorithm):
    """Concurrent Sorts"""
    def run(self):
        raise NotImplementedError


class BatchersBitonicSort(Concurrent):
    """Batcher's Bitonic Sort"""
    def merge(self, start: int, section_len: int, direction: bool):
        # Direction is True if going up, False if going down.

        if section_len < 1:
            return

        comparison = ">" if direction else "<"

        half_len = section_len // 2

        mid_point = start + half_len

        for left_index, right_index in zip(range(start, mid_point), range(mid_point, start + section_len)):
            should_swap = self.playground.compare((0, left_index), comparison, (0, right_index))
            yield

            if should_swap:
                self.playground.swap((0, left_index), (0, right_index))
                yield

        for _ in chain(self.merge(start, half_len, direction), self.merge(start + half_len, half_len, direction)):
            yield

    def bitonic(self, start: int, section_len: int, direction: bool):
        if section_len < 1:
            return

        half_len = section_len // 2

        for _ in chain(self.bitonic(start, half_len, True), self.bitonic(start + half_len, half_len, False),
                       self.merge(start, section_len, direction)):
            yield

    def run(self):
        for _ in self.bitonic(0, len(self.playground.main_array), True):
            yield


class PairwiseSortingNetwork(Concurrent):
    """Pairwise Sorting Network"""

    def merge(self, start: int, amount: int, step: int):
        """Merges sub-lists of n amount every step items using binary search,
        Assumes 'step' parameter is a power of 2."""
        if amount < 2:
            return

        section_end = start + amount * step

        for index in range(start, section_end, step):

            binary_search_index = index
            power = step
            while binary_search_index < section_end:
                binary_search_index += power
                power *= 2
            power //= 2
            binary_search_index -= power
            # There's gotta be an easier way...

            while binary_search_index > index:

                if binary_search_index != index:
                    should_swap = self.playground.compare((0, binary_search_index), "<", (0, index))
                    yield

                    if should_swap:
                        self.playground.swap((0, index), (0, binary_search_index))
                        yield

                power //= 2
                binary_search_index -= power
            # Using binary search but starting at step;
            # swap value at current index with a smaller value,
            # if found at the binary search indexes.

    def sorting_network(self, start: int, amount: int, step: int):
        if amount < 2:
            return

        for _ in chain(self.sorting_network(start, amount // 2, step * 2),
                       self.sorting_network(start + step, amount // 2, step * 2),
                       self.merge(start, amount, step)):
            yield

    def run(self):
        """Assumes list's length is a power of 2."""
        for _ in self.sorting_network(0, len(self.playground.main_array), 1):
            yield


class BogoSort(Verify, Shuffle):
    """Bogo Sort"""
    def run(self):
        while True:
            for _ in Verify.run(self):
                yield

            print(self.sorted)

            if self.sorted:
                break

            for _ in Shuffle.run(self):
                yield


sorts = [BubbleSort, OptimizedBubbleSort, CocktailShakerSort, OptimizedCocktailShakerSort,
         InsertionSort,
         SelectionSort, MaxHeapSort, MinHeapSort,
         QuickSort,
         MergeSort, MergeSortInPlace,
         RadixLSDSort, RadixLSDSortInPlace, PigeonholeSort, CountSort, GravitySort,
         BatchersBitonicSort, PairwiseSortingNetwork,
         BogoSort]
