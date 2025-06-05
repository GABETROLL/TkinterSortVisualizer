from algorithms.algorithms import *
from algorithms.algorithm import Option
from typing import Iterable, Callable
from itertools import count, chain, cycle
from dataclasses import dataclass, field
from math import sqrt, floor

class BubbleSort(Algorithm):
    """Bubble Sort"""
    def run(self):
        nums_len = self.playground.main_array_len

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
        nums_len = self.playground.main_array_len

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
        nums_len = self.playground.main_array_len
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
        nums_len = self.playground.main_array_len

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


class OddEvenSort(Algorithm):
    """Odd Even Sort"""
    def network(self, start: int, amount: int):
        end = start + amount

        done = False
        while not done:
            done = True

            for index in chain(range(start, end - 1, 2),  # evens
                               range(start + 1, end - 1, 2)):  # odds
                should_swap = self.playground.compare((0, index), ">", (0, index + 1))
                yield

                if should_swap:
                    done = False

                    self.playground.swap((0, index), (0, index + 1))
                    yield

    def run(self):
        for _ in self.network(0, self.playground.main_array_len):
            yield


class InsertionSort(Algorithm):
    """Insertion Sort"""
    def _run(self, start: int, end: int):
        for unsorted_start_index in range(start + 1, end):
            # print(f"{unsorted_start_index = }")
            index: int = unsorted_start_index

            while start < index and self.playground.compare((0, index - 1), ">", (0, index)):
                yield

                # print(f"Needs to swap: {index - 1}, {index}")

                self.playground.swap((0, index - 1), (0, index))
                yield

                index -= 1

    def run(self):
        return self._run(0, self.playground.main_array_len)


class BinaryInsertionSort(InsertionSort):
    """Insertion Sort (Binary Search)"""
    def run(self):
        pass


class BaiaiSort(Algorithm):
    """Baiai Sort"""
    # Special thanks to Kuvina in YouTube,
    # where I received the knowledge to code this sort!
    def run(self):
        # The algorithm's time complexity is O(n^2).
        # Space complexity: O(1)
        end_indices: Iterable[int] = chain(
            range(2, self.playground.main_array_len + 1),
            range(self.playground.main_array_len - 1, 1, -1)
        )
        # O(1). Initializing these iterables doesn't compute anything.
        # Instead, they just store the start, stop, step and iterable parameters.

        for end_index in end_indices:
            # O(n)
            iteration_start_index: int = end_index & 1
            # O(1)
            for a_index in range(iteration_start_index, end_index, 2):
                # O(n)
                b_index: int = a_index + 1
                # O(1) 

                should_swap: bool = self.playground.compare((0, a_index), ">", (0, b_index))
                yield
                # O(1)

                if should_swap:
                    # O(1)
                    self.playground.swap((0, a_index), (0, b_index))
                    # O(1)
                    yield


class CircleSort(Algorithm):
    """Circle Sort"""
    def smallest_power_of_2_larger_or_equal_than(self, n: int) -> int:
        """
        Returns the smallest power of 2 that's greater or equal to `n`.

        If n < 1, this method throws a ValueError.

        n = 1 is valid, since it's 2^0, so it's a power of 2, and its an integer.
        However, no integer powers of 2 exist below 1. This method assumes `n`
        is the length of a sorting array in `self.playground`, and so it shouldn't be
        lower than 1.
        """
        if n < 1:
            raise ValueError(f"`n` is lower than 1! got: f{n}")

        power: int = 1

        while power < n:
            power <<= 1

        return power

    def recursive_iteration(self, start: int, circle_length: int):
        """
        Runs a recursive circle sort iteration on the section of the main array
        at `self.playground.main_array_len` in the indices [start, start + circle_length).

        This means this method first compares each next element
        from the start of the left side of the circle (from `start` to start + (circle_length >> 1) - 1)
        with each corresponding next element from the end of the circle.
        Then, this method calls itself in both the left and right sides
        of the circle: left -> [start, start + (circle_len >> 1)), right -> [start + (circle_len >> 1), end) 
        """
        if circle_length == 1:
            return

        circle_half_length: int = circle_length >> 1

        for left_index, right_index in zip(
            range(start, start + circle_half_length),
            range(start + circle_length - 1, start + circle_half_length - 1, -1),
        ):
            # The length of the circle (parameter `circle_len`)
            # could be larger than the list itself,
            # which means the conditional flip may need to be skipped.
            #
            # I believe you should be able to skip the flip
            # if the circle goes outise the length of the list,
            # and the algorithm should still work fine.
            if right_index >= self.playground.main_array_len:
                continue

            should_swap: bool = self.playground.compare((0, left_index), ">", (0, right_index))
            yield

            if should_swap:
                self.playground.swap((0, left_index), (0, right_index))
                yield

                if circle_length == 2:
                    self.never_swapped_with_circle_length_2 = False

        for _ in chain(
            self.recursive_iteration(start, circle_half_length),
            self.recursive_iteration(start + circle_half_length, circle_half_length),
        ):
            yield

    def run(self):
        """
        Repetedly runs iterations of Recursive Circle Sort,
        by calling `self.recursive_iteration` with start=0 and circle_length
        = to the smallest power of 2 larger or equal to the playground's
        main array's length.

        This method initializes `self.never_swapped_with_circle_length_2` to be true
        when called, and does so again before each iteration
        (where this method calls `self.recursive_iteration`).
        Then, after the call is over, this method checks
        `self.never_swapped_with_circle_length_2`, to see if the method
        never had to swap any elements in the array when the length of
        each circle was 2. if this variable is true, the algorithm should(?)
        be over.

        `recursive_iteration` is responsible for remotely turning this variable
        false whenever its `circle_length` parameter is 2 and it had to swap
        its two halves (which, at that length, should just be 2 pieces,
        one in each half of the circle). This means the algorithm may not be over yet,
        and so this method runs another iteration of `self.recursive_iteration`.
        """
        starting_circle_length: int = self.smallest_power_of_2_larger_or_equal_than(
            self.playground.main_array_len,
        )

        self.never_swapped_with_circle_length_2: bool = True

        while True:
            self.never_swapped_with_circle_length_2 = True

            for _ in self.recursive_iteration(0, starting_circle_length):
                yield

            if self.never_swapped_with_circle_length_2:
                break


class IterativeCircleSort(CircleSort):
    """Iterative Circle Sort"""
    def run(self):
        starting_circle_length: int = self.smallest_power_of_2_larger_or_equal_than(
            self.playground.main_array_len,
        )

        finally_sorted: bool = False

        while not finally_sorted:
            circle_length: int = starting_circle_length

            while circle_length >= 2:
                circle_half_length: int = circle_length >> 1

                round_circle_count: int = starting_circle_length // circle_length

                never_swapped: bool = True

                # print(f"{circle_length = } {circle_half_length = } {round_circle_count = }")

                for circle in range(round_circle_count):

                    circle_start_index: int = circle * circle_length

                    # print(f"{circle = } {circle_start_index = }")

                    for a_index, b_index in zip(
                        range(circle_start_index, circle_start_index + circle_half_length),
                        range(circle_start_index + circle_length - 1, circle_start_index - 1, -1),
                    ):
                        # print(f"{a_index = } {b_index = }")

                        if b_index >= self.playground.main_array_len or a_index >= self.playground.main_array_len:
                            continue

                        should_swap: bool = self.playground.compare((0, a_index), ">", (0, b_index))
                        yield

                        if should_swap:
                            never_swapped = False

                            self.playground.swap((0, a_index), (0, b_index))
                            yield

                if circle_half_length == 1 and never_swapped:
                    finally_sorted = True

                circle_length >>= 1


class CombSort(Algorithm):
    """Comb Sort"""
    def run(self):
        interval: int = self.playground.main_array_len

        while True:
            interval = int(interval / 1.3)
            if interval < 1:
                interval = 1

            no_swaps_were_needed: bool = True

            for a_index in range(self.playground.main_array_len):
                b_index = a_index + interval

                if b_index not in range(self.playground.main_array_len):
                    break

                needs_swapping: bool = self.playground.compare((0, a_index), ">", (0, b_index))
                yield

                if needs_swapping:
                    no_swaps_were_needed = False
                    self.playground.swap((0, a_index), (0, b_index))
                    yield

            if no_swaps_were_needed and interval == 1:
                break


class ExchangeSort(Algorithm):
    """Exchange Sort"""
    def run(self):
        for start_index in range(self.playground.main_array_len - 1):
            for exchange_index in range(start_index + 1, self.playground.main_array_len):
                should_swap: bool = self.playground.compare((0, start_index), ">", (0, exchange_index))
                yield

                if should_swap:
                    self.playground.swap((0, start_index), (0, exchange_index))
                    yield


class SelectionSort(Algorithm):
    """Selection Sort"""
    def run(self):
        for unsorted_start_index in range(self.playground.main_array_len):
            smallest = None

            for i in range(unsorted_start_index, self.playground.main_array_len):

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
        for sorted_index in range(self.playground.main_array_len - 1, -1, -1):
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
            for _ in self.reverse_array(0, 0, self.playground.main_array_len):
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


class OptimizedMaxHeapSort(OptimizedHeapify, HeapSort):
    """Optimized Max Heap Sort"""
    def run(self):
        for _ in chain(self.optimized_heapify("max"), self.sort("max")):
            yield


class OptimizedMinHeapSort(OptimizedHeapify, HeapSort):
    """Optimized Min Heap Sort"""
    def run(self):
        for _ in chain(self.optimized_heapify("min"), self.sort("min")):
            yield


class QuickSort(Algorithm):
    """Quick Sort"""
    def median_of_three(self, index_a: int, index_b: int, index_c: int):
        """Returns index of the median of three numbers
        located in the main array's 'a', 'b' and 'c' indexes."""
        indexes = {index_a, index_b, index_c}
        indexes.remove(min(indexes, key=lambda i: self.playground.read((0, i))))
        return min(indexes, key=lambda i: self.playground.read((0, i)))

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
            end = self.playground.main_array_len

        pivot_index = self.median_of_three(start, (start + end) // 2, end - 1)
        self.playground.swap((0, start), (0, pivot_index))
        yield

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

        # print(start, pivot_index, pivot_index + 1, amount)

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
    def merge_halves_out_of_place(self, start: int, midpoint: int, end: int):
        assert start <= midpoint <= end, f"{start = }, {midpoint = }, {end = }"

        # Merge the two halves in the auxiliary array,
        # starting at the same position as `start`:

        left_index: int = start
        right_index: int = midpoint

        merge_index: int = start

        while left_index < midpoint and right_index < end:
            left_goes_first: bool = self.playground.compare((0, left_index), "<=", (0, right_index))
            yield

            if left_goes_first:
                num: int = self.playground.read((0, left_index))
                yield
                self.playground.write(num, (1, merge_index))
                yield

                left_index += 1
            else:
                num: int = self.playground.read((0, right_index))
                yield
                self.playground.write(num, (1, merge_index))
                yield

                right_index += 1
            merge_index += 1

        # If the left_index < midpoint and right_index == end
        while left_index < midpoint:
            num: int = self.playground.read((0, left_index))
            yield
            self.playground.write(num, (1, merge_index))
            yield

            left_index += 1
            merge_index += 1
        # If the left_index == midpoint and right_index < end
        while right_index < end:
            num: int = self.playground.read((0, right_index))
            yield
            self.playground.write(num, (1, merge_index))
            yield

            right_index += 1
            merge_index += 1

        # Copy the merged halves from the auxiliary array into the main array:

        # (merge_index SHOULD BE EQUAL TO end NOW)
        for copy_index in range(start, merge_index):
            num: int = self.playground.read((1, copy_index))
            yield
            self.playground.write(num, (0, copy_index))
            yield

    def merge_sort(self, start: int, end: int):
        section_length: int = end - start

        if section_length <= 1:
            return

        midpoint: int = start + (section_length >> 1)

        for _ in self.merge_sort(start, midpoint):
            yield
        for _ in self.merge_sort(midpoint, end):
            yield

        for _ in self.merge_halves_out_of_place(start, midpoint, end):
            yield

    def run(self):
        self.playground.spawn_new_array(self.playground.main_array_len)
        yield

        for _ in self.merge_sort(0, self.playground.main_array_len):
            yield

        self.playground.delete_array(1)
        yield


@dataclass
class MergeSortInPlace(InsertionSort, MergeSort):
    """Merge Sort (In-place: Insertion Sort)"""
    options: dict[str, Option] = field(default_factory={
        'algorithm': Option(
            'Insertion Sort',
            ('Insertion Sort', 'Weave'),
        ),
    }.copy)

    def combine_halves_insertion(self, start: int, midpoint: int, end: int):
        return InsertionSort._run(self, start, end)

    def slide_to_destination(self, start_index: int, destination_index: int):
        """
        Slides the element at index `start_index` in `self.playground.main_array`
        to `destination_index`, shifting everyting in (start_index, destination_index]
        by 1 toward the start_index.

        Swaps the element in `start_index` with the next-closest element to `destination_index`
        in `self.playground.main_array`, until it swaps it with the element AT `destination_index`,
        then breaks.

        Yields after every swap, including the last one, then stops iteration.
        """
        if start_index == destination_index:
            return

        step: int = -1 if destination_index < start_index else 1

        # print(f"SLIDING TO DESTINATION: {start_index = }, {destination_index = }, {step = }")

        for index in range(start_index, destination_index, step):
            next_index: int = index + step
            # In the last iteration, `index` will be destination_index - step,
            # and `next_index` will be destination_index.
            # This is because `range` end before `destination_index`, making the last `index`
            # ***IN THIS CASE*** equal to `destination_index - step`.
            #
            # This works nicely, anyways, because the last swap we'll need to slide
            # an element to its destination is to swap it from the second-to-last
            # position to `destination_index`.

            # print(f"{index = }, {next_index = }")

            self.playground.swap((0, index), (0, next_index))
            yield

    def _weave_halves(self, start: int, midpoint: int, end: int):
        """
        ASSUMING start < midpoint < end, and `midpoint` IS the midpoint between `start` and `end`,
        meaning midpoint - start is at most one bigger or smaller than end - midpoint,
        
        this method "weaves" all elements in indices [start, midpoint) with elements in
        [midpoint, end). Slides each element from [midpoint, end) into its corresponding
        spot, such that every ith element from [midpoint, end) ends up
        after every ith element in [start, midpoint).

        If there are n elements in [start, midpoint) and m elements in [midpoint, end),
        and n and m are one apart in the numberline, then these are all the possible
        cases for weaving, for example:

        n < m, n is odd and m is even:
        n = 3, m = 4:
        0 1 2|3 4 5 6
        n n n m m m m
        3 -> 1, 4 -> 3, 5 -> 5

        0 3 1 2 4 5 6
        n m n n m m m
        0 3 1 4 2 5 6
        n m n m n m m
        0 3 1 4 2 5 6
        n m n m n m m

        n < m, n is even and m is odd:
        n = 4, m = 5:
        0 1 2 3|4 5 6 7 8
        n n n n m m m m m
        4 -> 1, 5 -> 3, 6 -> 5, 7 -> 7

        0 4 1 2 3 5 6 7 8
        n m n n n m m m m
        0 4 1 5 2 3 6 7 8
        n m n m n n m m m
        0 4 1 5 2 6 3 7 8
        n m n m n m n m m
        0 4 1 5 2 6 3 7 8
        n m n m n m n m m

        n > m, n is even and m is odd:
        n = 4, m = 3:
        0 1 2 3|4 5 6
        n n n n m m m
        4 -> 1, 5 -> 3, 6 -> 5

        0 4 1 2 3 5 6
        n m n n n m m
        0 4 1 5 2 3 6
        n m n m n n m
        0 4 1 5 2 6 3
        n m n m n m n

        n > m, n is odd and m is even:
        n = 5, m = 4:
        0 1 2 3 4|5 6 7 8
        n n n n n m m m m
        5 -> 1, 6 -> 3, 7 -> 5, 8 -> 7

        0 5 1 2 3 4 6 7 8
        n m n n n n m m m
        0 5 1 6 2 3 4 7 8
        n m n m n n n m m
        0 5 1 6 2 7 3 4 8
        n m n m n m n n m
        0 5 1 6 2 7 3 8 4
        n m n m n m n m n

        And if both [start, midpoint) and [midpoint, end) have the same amount of elements,
        these are all the possible weave cases:

        n == m, n and m are both odd:
        n = 5, m = 5:
        0 1 2 3 4|5 6 7 8 9
        n n n n n m m m m m
        5 -> 1, 6 -> 3, 7 -> 5, 8 -> 7, 9 -> 9

        0 5 1 2 3 4 6 7 8 9
        n m n n n n m m m m
        0 5 1 6 2 3 4 7 8 9
        n m n m n n n m m m
        0 5 1 6 2 7 3 4 8 9
        n m n m n m n n m m
        0 5 1 6 2 7 3 8 4 9
        n m n m n m n m n m
        0 5 1 6 2 7 3 8 4 9
        n m n m n m n m n m

        n == m, n and m are both even:
        n = 4, m = 4:
        0 1 2 3|4 5 6 7
        n n n n m m m m
        4 -> 1, 5 -> 3, 6 -> 5, 7 -> 7

        0 4 1 2 3 5 6 7
        n m n n n m m m
        0 4 1 5 2 3 6 7
        n m n m n n m m
        0 4 1 5 2 6 3 7
        n m n m n m n m
        0 4 1 5 2 6 3 7
        n m n m n m n m

        IMPORTANT: This should work for ALL section lengths. If you spot any bugs in this algorithm,
        or any algorithm in here, please let me know! I'd be glad to fix it!
        Although, since this step is followed by insertion sort, it may not even matter much
        if this method has a few inaccuracies, since the insertion sort step takes care of them.
        """
        # print(f"WEAVING HALVES: {start = }, {midpoint = }, {end = }")
        for start_index, destination_index in zip(
            range(midpoint, end),
            range(start + 1, end, 2),
        ):
            # print(f"{start_index} -> {destination_index}")
            for _ in self.slide_to_destination(start_index, destination_index):
                yield

    def combine_halves_weave(self, start: int, midpoint: int, end: int):
        """
        Weaves the elements in indices [start, midpoint)
        with the elements in indices [midpoint, end),
        inside of `self.playground.main_array`, by using `self._weave_halves`;
        then runs insertion sort in [start, end)
        to finish combining (mergin) the two halves,
        by using `InsertionSort._run(self, start, end)`.
        """
        # print(f"COMBINING HALVES: {start = }, {midpoint = }, {end = } (WEAVE)")

        for _ in self._weave_halves(start, midpoint, end):
            yield

        # print(f"INSERTIONING HALVES")

        for _ in InsertionSort._run(self, start, end):
            yield

    @property
    def combine_halves_method(self) -> Callable[[int, int, int], object]:
        methods = {
            "Insertion Sort": self.combine_halves_insertion,
            "Weave": self.combine_halves_weave,
        }

        return methods[self.options["algorithm"].value]

    def in_place(self, start: int, end: int):
        """
        Runs itself in [start, midpoint) and [midpoint, end),
        then combines the two halves using `self.combine_halves_method`.

        If the length of the section [start, end) (end - start)
        is smaller or equal to 1, this method doesn't do anything.
        This means that if start - end == 2, the recursive `self.in_place` calls
        for the two smaller halves should have length 1, won't do anything,
        and this method call will then combine the two halves of length one
        by calling `self.combine_halves_method(start, midpoint, end)`.
        """
        # print(f"{start = }, {end = }")
        section_length: int = end - start

        if section_length > 1:
            midpoint: int = start + (section_length >> 1)

            # print(f"{section_length = }, {section_length >> 1}, {midpoint = }")

            for _ in self.in_place(start, midpoint):
                yield
            for _ in self.in_place(midpoint, end):
                yield

            for _ in self.combine_halves_method(start, midpoint, end):
                yield

    def run(self):
        for _ in self.in_place(0, self.playground.main_array_len):
            yield


@dataclass
class RadixSort(Algorithm):
    """Radix Sort"""
    options: dict[str, Option] = field(default_factory={"base": Option(10, range(2, 1025))}.copy)

    def run(self):
        raise NotImplementedError


class RadixLSDSort(RadixSort):
    """Radix LSD Sort"""
    def lsd_digit(self, num: int, place: int) -> tuple[int, int]:
        """
        TODO: DOCUMENT
        """
        digit = 0
        for _ in range(place):
            digit = num % self.options["base"].value
            num = num // self.options["base"].value

        return digit, num

    def run(self):
        self.playground.spawn_new_array(self.playground.main_array_len)
        copy_array_index = 1
        yield
        # nums copy

        for digit_index in count(1, 1):

            self.playground.spawn_new_array(self.options["base"].value)
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
            for count_index in range(self.options["base"].value):
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
        nums_len = self.playground.main_array_len

        for digit_index in count(1, 1):

            digit_pointers = [nums_len for _ in range(self.options["base"].value)]
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
        for index in range(self.playground.main_array_len):
            current_index = (0, index)

            new_min_number = self.playground.compare(current_index, "<", min_num_index)
            yield

            if new_min_number:
                min_num_index = current_index

        min_num = self.playground.read(min_num_index)
        yield

        self.playground.spawn_new_array(self.playground.main_array_len)
        yield

        for index in range(self.playground.main_array_len):
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

        for index in range(self.playground.main_array_len):
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
        main_array_length = self.playground.main_array_len

        self.playground.spawn_new_array(main_array_length)
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

            for index in range(main_array_length):
                num = self.playground.read((copy_array_index, index))
                yield

                if height <= num:
                    beads_at_height += 1

                    self.playground.increment(-1, (0, index))
                    # decrement
                yield

            for index in range(main_array_length - 1, main_array_length - 1 - beads_at_height, -1):
                self.playground.increment(1, (0, index))
                yield


class SquareRootSort(Algorithm):
    """Square Root Sort"""

    # Iterative mergesort with roll-and-drop example:
    # 0 1 2 3 4 5 6 7 8 9 A B C D E F
    # 5 A 9 2 D E C 8 1 B 0 3 6 4 F 7
    #|5|A|9|2|D|E|C|8|1|B|0|3|6|4|F|7|
    # ...|
    #|5 A 2 9|D E 8 C 1 B 0 3 4 6 7 F  1 2
    #|2 A 5 9|D E 8 C 1 B 0 3 4 6 7 F  2 1
    #|2 5 A 9|D E 8 C 1 B 0 3 4 6 7 F    2  
    #|2 5 9 A|D E 8 C 1 B 0 3 4 6 7 F
    # 2 5 9 A|D E 8 C|1 B 0 3 4 6 7 F  1 2
    # 2 5 9 A|8 E D C|1 B 0 3 4 6 7 F  2 1
    # 2 5 9 A|8 C D E|1 B 0 3 4 6 7 F  1 2
    # 2 5 9 A|8 C D E|1 B 0 3 4 6 7 F    2
    # 2 5 9 A|8 C D E|1 B 0 3 4 6 7 F
    # 2 5 9 A 8 C D E|1 B 0 3|4 6 7 F  1 2
    # 2 5 9 A 8 C D E|0 B 1 3|4 6 7 F  2 1
    # 2 5 9 A 8 C D E|0 1 B 3|4 6 7 F  1 2
    # 2 5 9 A 8 C D E|0 1 B 3|4 6 7 F    2
    # 2 5 9 A 8 C D E|0 1 3 B|4 6 7 F    2
    # 2 5 9 A 8 C D E|0 1 3 B|4 6 7 F
    # 2 5 9 A 8 C D E 0 1 3 B|4 6 7 F| 1 2
    # 2 5 9 A 8 C D E 0 1 3 B|4 6 7 F|   2
    # 2 5 9 A 8 C D E 0 1 3 B|4 6 7 F|
    #
    #|2 5 9 A 8 C D E|0 1 3 B 4 6 7 F  1 2 3 4
    #|2 5 9 A 8 C D E|0 1 3 B 4 6 7 F    2 3 4
    #|2 5 9 A 8 C D E|0 1 3 B 4 6 7 F      3 4
    #|2 5 8 A 9 C D E|0 1 3 B 4 6 7 F      4 3
    #|2 5 8 9 A C D E|0 1 3 B 4 6 7 F      3 4
    #|2 5 8 9 A C D E|0 1 3 B 4 6 7 F        4
    #|2 5 8 9 A C D E|0 1 3 B 4 6 7 F
    # 2 5 8 9 A C D E|0 1 3 B 4 6 7 F| 1 2 3 4
    # 2 5 8 9 A C D E|0 1 3 B 4 6 7 F|   2 3 4
    # 2 5 8 9 A C D E|0 1 3 B 4 6 7 F|     3 4
    # 2 5 8 9 A C D E|0 1 3 B 4 6 7 F|       4
    # 2 5 8 9 A C D E|0 1 3 4 B 6 7 F|       4
    # 2 5 8 9 A C D E|0 1 3 4 6 B 7 F|       4
    # 2 5 8 9 A C D E|0 1 3 4 6 7 B F|       4
    # 2 5 8 9 A C D E|0 1 3 4 6 7 B F|
    #
    #|2 5 8 9 A C D E|0 1 3 4 6 7 B F  1 2 3 4 5 6 7 8
    # 0|5 8 9 A C D E 2|1 3 4 6 7 B F  2 3 4 5 6 7 8 1
    # 0 1|8 9 A C D E 2 5|3 4 6 7 B F  3 4 5 6 7 8 1 2
    # 0 1|2 9 A C D E 8 5|3 4 6 7 B F  1 4 5 6 7 8 3 2
    # 0 1 2|9 A C D E 8 5|3 4 6 7 B F    4 5 6 7 8 3 2
    # 0 1 2 3|A C D E 8 5 9|4 6 7 B F    5 6 7 8 3 2 4
    # 0 1 2 3 4|C D E 8 5 9 A|6 7 B F    6 7 8 3 2 4 5
    # 0 1 2 3 4|5 D E 8 C 9 A|6 7 B F    2 7 8 3 6 4 5
    # 0 1 2 3 4 5|D E 8 C 9 A|6 7 B F      7 8 3 6 4 5
    # 0 1 2 3 4 5 6|E 8 C 9 A D|7 B F      8 3 6 4 5 7
    # 0 1 2 3 4 5 6 7|8 C 9 A D E|B F      3 6 4 5 7 8
    # 0 1 2 3 4 5 6 7|8 C 9 A D E|B F      3 6 4 5 7 8
    # 0 1 2 3 4 5 6 7 8|C 9 A D E|B F        6 4 5 7 8
    # 0 1 2 3 4 5 6 7 8|9 C A D E|B F        4 6 5 7 8
    # 0 1 2 3 4 5 6 7 8 9|C A D E|B F          6 5 7 8
    # 0 1 2 3 4 5 6 7 8 9|A C D E|B F          5 6 7 8
    # 0 1 2 3 4 5 6 7 8 9 A|C D E|B F            6 7 8
    # 0 1 2 3 4 5 6 7 8 9 A B|D E C|F            7 8 6
    # 0 1 2 3 4 5 6 7 8 9 A B|C E D|F            6 8 7
    # 0 1 2 3 4 5 6 7 8 9 A B C|E D|F              8 7
    # 0 1 2 3 4 5 6 7 8 9 A B C|D E|F              7 8
    # 0 1 2 3 4 5 6 7 8 9 A B C D|E|F                8
    # 0 1 2 3 4 5 6 7 8 9 A B C D|E|F                8
    # 0 1 2 3 4 5 6 7 8 9 A B C D E F

    # Square Root Sort iteration example:
    # ...
    #  2 5 8 9 A C D E|0 1 3 4 6 7 B F
    # sort blocks:
    # |2 5|8 9|A C|D E|0 1|3 4|6 7|B F|  A A A A B B B B  |2 8 A D|1 4 7 F  0 1 2 3
    # |0 1|8 9|A C|D E|2 5|3 4|6 7|B F|  B A A A A B B B   1|8 A D 2|4 7 F  1 2 3 0
    # |0 1|2 5|A C|D E|8 9|3 4|6 7|B F|  B A A A A B B B   1|2 A D 8|4 7 F  0 2 3 1
    # |0 1|2 5|A C|D E|8 9|3 4|6 7|B F|  B A A A A B B B   1 2|A D 8|4 7 F    2 3 1
    # |0 1|2 5|3 4|D E|8 9|A C|6 7|B F|  B A B A A A B B   1 2 4|D 8 A|7 F    3 1 2
    # |0 1|2 5|3 4|6 7|8 9|A C|D E|B F|  B A B B A A A B   1 2 4 7|8 A D|F    1 2 3
    # |0 1|2 5|3 4|6 7|8 9|A C|D E|B F|  B A B B A A A B   1 2 4 7|8 A D|F    1 2 3
    # |0 1|2 5|3 4|6 7|8 9|A C|D E|B F|  B A B B A A A B   1 2 4 7 8|A D|F      2 3
    # |0 1|2 5|3 4|6 7|8 9|A C|D E|B F|  B A B B A A A B   1 2 4 7 8|A D|F      2 3
    # |0 1|2 5|3 4|6 7|8 9|A C|D E|B F|  B A B B A A A B   1 2 4 7 8 A|D|F        3
    # |0 1|2 5|3 4|6 7|8 9|A C|D E|B F|  B A B B A A A B   1 2 4 7 8 A|D|F        3
    # |0 1|2 5|3 4|6 7|8 9|A C|D E|B F|  B A B B A A A B   1 2 4 7 8 A D F
    # merge blocks:
    #     * When mergin a B-block to the merged section,
    #       IF THE PREVIOUSLY MERGED BLOCK WAS AN A-BLOCK,
    #       OR IT'S THE FIRST BLOCK TO BE MERGED,
    #       just attach it to the merged section.
    #       This is because the first element in the A-block
    #       after the B-block must be STRICTLY GREATER (>, not >=)
    #       than the last element of the B-block, and because
    #       the first element of the A-block is the current
    #       first element in the merged section.
    #       And so, EVERY element in the B-block belongs before
    #       that element, and before EVERY element in the A-block,
    #       no matter where they are in the merged block,
    #       and also, EVERY element in the merged section.
    #       Since both the merged section and the B-block
    #       are now sorted, just attach the B-block!
    #  0 1 2 5 3 4 6 7 8 9 A C D E|B F|* B A B B A A A B
    #  0 1 2 5 3 4 6 7 8 9 A C D E B F   B A B B A A A M
    #  0 1 2 5 3 4 6 7 8 9 A C|D E|B F   B A B B A A A M   0 1
    #  0 1 2 5 3 4 6 7 8 9 A C B|E D|F                     1 0
    #  0 1 2 5 3 4 6 7 8 9 A C B|D E|F                     0 1
    #  0 1 2 5 3 4 6 7 8 9 A C B D|E|F                       1
    #  0 1 2 5 3 4 6 7 8 9 A C B D|E|F                       1
    #  0 1 2 5 3 4 6 7 8 9 A C B D E F   B A B B A A M M
    #  0 1 2 5 3 4 6 7 8 9|A C|B D E F   B A B B A A M M   0 1
    #  0 1 2 5 3 4 6 7 8 9|A C|B D E F                     0 1
    #  0 1 2 5 3 4 6 7 8 9 A|C|B D E F                       1
    #  0 1 2 5 3 4 6 7 8 9 A B|C|D E F                       1
    #  0 1 2 5 3 4 6 7 8 9 A B|C|D E F                       1
    #  0 1 2 5 3 4 6 7 8 9 A B C D E F   B A B B A M M M
    #  0 1 2 5 3 4 6 7|8 9|A B C D E F   B A B B A M M M   0 1
    #  0 1 2 5 3 4 6 7|8 9|A B C D E F                     0 1
    #  0 1 2 5 3 4 6 7 8|9|A B C D E F                       1
    #  0 1 2 5 3 4 6 7 8|9|A B C D E F                       1
    #  0 1 2 5 3 4 6 7 8 9 A B C D E F   B A B B M M M M
    #  0 1 2 5 3 4|6 7|8 9 A B C D E F * B A B B M M M M   0 1
    #  0 1 2 5 3 4|6 7|8 9 A B C D E F                     0 1
    #  0 1 2 5 3 4 6|7|8 9 A B C D E F                       1
    #  0 1 2 5 3 4 6|7|8 9 A B C D E F                       1
    #  0 1 2 5 3 4 6 7 8 9 A B C D E F   B A B M M M M M
    #  0 1 2 5|3 4|6 7 8 9 A B C D E F   B A B M M M M M   0 1
    #  0 1 2 5|3 4|6 7 8 9 A B C D E F                     0 1
    #  0 1 2 5 3|4|6 7 8 9 A B C D E F                       1
    #  0 1 2 5 3|4|6 7 8 9 A B C D E F                       1
    #  0 1 2 5 3 4 6 7 8 9 A B C D E F   B A M M M M M M
    #  0 1|2 5|3 4 6 7 8 9 A B C D E F   B A M M M M M M   0 1
    #  0 1|2 5|3 4 6 7 8 9 A B C D E F                     0 1
    #  0 1 2|5|3 4 6 7 8 9 A B C D E F                       1
    #  0 1 2 3|5|4 6 7 8 9 A B C D E F                       1
    #  0 1 2 3 4|5|6 7 8 9 A B C D E F                       1
    #  0 1 2 3 4|5|6 7 8 9 A B C D E F                       1
    #  0 1 2 3 4 5 6 7 8 9 A B C D E F   B M M M M M M M
    # |0 1|2 3 4 5 6 7 8 9 A B C D E F * B M M M M M M M   0 1
    # |0 1|2 3 4 5 6 7 8 9 A B C D E F                     0 1
    #  0|1|2 3 4 5 6 7 8 9 A B C D E F                       1
    #  0|1|2 3 4 5 6 7 8 9 A B C D E F                       1
    #  0 1 2 3 4 5 6 7 8 9 A B C D E F   M M M M M M M M

    # Alternate way of sorting the blocks:
    #  0 1 2 5 3 4 6 7 8 9 A C D E|B F|  B A B B A A A B
    #  0 1 2 5 3 4 6 7 8 9 A C|D E|B F|  B A B B A A A M   D E
    #                          w   ^                       ^
    #  0 1 2 5 3 4 6 7 8 9 A C|B E B F|                    D E
    #                            w   ^                     ^
    #  0 1 2 5 3 4 6 7 8 9 A C|B D B F|                    D E
    #                              w ^                       ^
    #  0 1 2 5 3 4 6 7 8 9 A C|B D E F|                    D E
    #                                ^
    #  0 1 2 5 3 4 6 7 8 9 A C|B D E F|                    D E
    #  0 1 2 5 3 4 6 7 8 9|A C|B D E F|  B A B B A A M M   A C
    #                      w   ^                           ^
    #  0 1 2 5 3 4 6 7 8 9|A C B D E F|                    A C
    #                        w ^                             ^
    #  0 1 2 5 3 4 6 7 8 9|A B B D E F|                    A C
    #                          w ^                           ^
    #  0 1 2 5 3 4 6 7 8 9|A B C D E F|                    A C
    #                            ^
    #  0 1 2 5 3 4 6 7 8 9|A B C D E F|                    A C
    #  0 1 2 5 3 4 6 7|8 9|A B C D E F|  B A B B A M M M   8 9
    #                  w   ^                               ^
    #  0 1 2 5 3 4 6 7|8 9 A B C D E F|                    8 9
    #                    w ^                                 ^
    #  0 1 2 5 3 4 6 7|8 9 A B C D E F|                    8 9
    #                      ^
    #  0 1 2 5 3 4 6 7|8 9 A B C D E F|                    8 9
    #  0 1 2 5 3 4|6 7|8 9 A B C D E F|  B A B B M M M M   8 9
    #  0 1 2 5|3 4|6 7 8 9 A B C D E F|  B A B M M M M M   3 4
    #          w   ^                                       ^
    #  0 1 2 5|3 4 6 7 8 9 A B C D E F|                    3 4
    #            w ^                                         ^
    #  0 1 2 5|3 4 6 7 8 9 A B C D E F|                    3 4
    #              ^
    #  0 1 2 5|3 4 6 7 8 9 A B C D E F|                    3 4
    #  0 1|2 5|3 4 6 7 8 9 A B C D E F|  B A M M M M M M   2 5
    #      w   ^                                           ^
    #  0 1|2 5 3 4 6 7 8 9 A B C D E F|                    2 5
    #        w ^                                             ^
    #  0 1|2 3 3 4 6 7 8 9 A B C D E F|                    2 5
    #          w ^                                           ^
    #  0 1|2 3 4 4 6 7 8 9 A B C D E F|                    2 5
    #            w ^                                         ^
    #  0 1|2 3 4 5 6 7 8 9 A B C D E F|                    2 5
    #              ^
    #  0 1|2 3 4 5 6 7 8 9 A B C D E F|                    2 5
    # |0 1|2 3 4 5 6 7 8 9 A B C D E F|  B M M M M M M M   2 5
    # |0 1 2 3 4 5 6 7 8 9 A B C D E F|  M M M M M M M M
    AUX_ARRAY_INDEX = 1

    def swap_sections(self, a_start: int, b_start: int, len: int):
        """
        Swaps the two sections of the array: [a_start, a_start + len)
        and [b_start, b_start + len).
        
        Swaps every ith element in the "a section" with every ith element
        in the "b section".

        **ASSUMING THE TWO SECTIONS DON'T OVERLAP. IF THEY OVERLAP,
        WEIRD BEHAVIOR COULD OCCUR.
        """
        for relative_index in range(len):
            a_index: int = a_start + relative_index
            b_index: int = b_start + relative_index

            self.playground.swap((0, a_index), (0, b_index))
            yield
    
    def roll(self, section: range, lowest_in_section: int, destination: int):
        """
        Rolls the section in `self.playground.main_array` represented by `section`
        from where it currently is to `destination`.

        `section` is the range of indices of all the elements in the section in
        `self.playground.main_array` to roll.
        This method asserts that `section` doesn't contain any indices outside
        of the range of `self.playground.main_array`'s range of indices.

        `lowest_in_section` should be the index of the element
        in the section with lowest value (or the one that goes first amongst
        the rest of the elements in the section).
        This method asserts that the index `lowest_in_section` is in the `section` range.
        ***THIS METHOD DOES NOT CHECK IF THE ELEMENT IN `lowest_in_section`
        IS ACTUALLY THE LOWEST IN THE SECTION.

        Example:
        ********01234****************
                           ^
        *********12340***************
                           ^
        **********23401**************
                           ^
        ***********34012*************
                           ^
        ************40123************
                           ^
        *************01234***********
                           ^
        **************12340**********
                           ^
        ***************23401*********
                           ^
        ****************34012********
                           ^
        *****************40123*******
                           ^
        ******************01234******
                           ^
        *******************12340*****
                           ^
        """
        for current_section_start_index in range(section.start, destination):
            self.playground.swap(
                (0, current_section_start_index),
                (0, current_section_start_index + len(section))
            )
            yield

    def merge_by_roll_and_drop(self, start: int, a_len: int, b_len: int):
        """
        Since all a_len items in the a-section, in the worst case scenario,
        need to roll from before the b-section to after the b-section,
        and each "roll swap" moves one element from the b-section
        from in front of the a-section to behind it,
        thie method's time complexity would be in O(b_len).

        However, copying the sorted a-section from the aux array
        each time an element is dropped is, in the worst case scenario,
        O(a_len). Dropping an element is just moving the a-section
        range's start index by one, so it's in O(1). Since there are
        a_len elements in the a-section to drop in total, in the worst-case
        scenario, the number of drops to make is also in O(a_len).

        Since for each of the O(b_len) rolls, an O(a_len) aux array copy
        needs to be made, the total time complexity for this method would be
        O(b_len + a_len * a_len)

        a_len = 6
        b_len = 8
        
        A < 0 <= B

         012345**AB**** 012345
        |      |        ^
        roll (1):
         *123450*AB**** 012345
         |      |       ^
        roll (2):
         **234501AB**** 012345
          |      |      ^
        roll (3):
         **A345012B**** 012345
           |      |     ^
        copy (1):
         **A045012B**** 012345
           |      |     ^
        copy (2):
         **A015012B**** 012345
           |      |     ^
        copy (3):
         **A012012B**** 012345
           |      |     ^
        copy (4):
         **A012312B**** 012345
           |      |     ^
        copy (5):
         **A012342B**** 012345
           |      |     ^
        copy (6):
         **A012345B**** 012345
           |      |     ^
        drop (1):
         **A012345B**** 012345
            |     |      ^
        next position (this isn't binary search, it's just an illustration):
         ***012345**AB* 012345
            |     |      ^
        roll (4):
         ***0*23451*AB* 012345
             |     |     ^
        roll (5):
         ***0**34512AB* 012345
              |     |    ^
        roll (6):
         ***0**A45123B* 012345
               |     |   ^
        copy (7):
         ***0**A15123B* 012345
               |     |   ^
        copy (8):
         ***0**A12123B* 012345
               |     |   ^
        copy (9):
         ***0**A12323B* 012345
               |     |   ^
        copy (10):
         ***0**A12343B* 012345
               |     |   ^
        copy (11):
         ***0**A12345B* 012345
               |     |   ^
        drop (2):
         ***0**A12345B* 012345
                |    |    ^
        next position:
         ***0***12345*A 012345
                |    |    ^
        roll (7):
         ***0***1*3452A 012345
                 |    |   ^
        roll (8 == b_len):
         ***0***1*A4523 012345
                  |    |  ^
        copy (12):
         ***0***1*A2523 012345
                  |    |  ^
        copy (13):
         ***0***1*A2323 012345
                  |    |  ^
        copy (14):
         ***0***1*A2343 012345
                  |    |  ^
        copy (15):
         ***0***1*A2345 012345
                  |    |  ^
        drop (3):
         ***0***1*A2345 012345
                   |   |   ^
        copy (16):
         ***0***1*A2345 012345
                   |   |   ^
        copy (17):
         ***0***1*A2345 012345
                   |   |   ^
        copy (18):
         ***0***1*A2345 012345
                   |   |   ^
        drop (4):
         ***0***1*A2345 012345
                    |  |    ^
        copy (19):
         ***0***1*A2345 012345
                    |  |    ^
        copy (20):
         ***0***1*A2345 012345
                    |  |    ^
        drop (5):
         ***0***1*A2345 012345
                     | |     ^
        copy (21):
         ***0***1*A2345 012345
                     | |     ^
        drop (6 == a_len):
         ***0***1*A2345 012345
                      ||      ^ 
        """
        end_index: int = start + a_len + b_len

        print(f"{end_index = }")

        if end_index > self.playground.main_array_len:
            raise ValueError(f"""the range of the two halves to merge \
exceeds the length of the main array:
({start = }) + ({a_len = }) + ({b_len = }) = {end_index} > {self.playground.main_array_len}""")

        # Copy the nums from the a section to an auxiliary array.
        #
        # Since I'm assuming that `a_len` will be in O(sqrt(main_array_len)),
        # then this algorithm will have space complexity O(sqrt(n)),
        # where n is the number of elements to sort.
        for _ in self.playground.copy_array_slice(
            input_array_index=0, input_start_index=start,
            output_array_index=self.AUX_ARRAY_INDEX, output_start_index=0,
            len=a_len,
        ):
            yield

        current_section_range: range = range(start, start + a_len)
        aux_start_index: int = 0

        while len(current_section_range) > 0:
            index_to_compare: int = current_section_range.stop

            print(f"{current_section_range = }, {aux_start_index = } {index_to_compare = }")

            if index_to_compare > self.playground.main_array_len:
                raise ValueError(f"""The index to compare is somehow \
larger than the length of the main array: {index_to_compare}.
How did this happen?""")
            
            if index_to_compare > end_index:
                raise ValueError(f"""The index to compare is somehow \
larger than the end index of the two halves to merge: {index_to_compare}.
How did this happen?""")

            if index_to_compare == end_index:
                # There are no more elements to compare with the lowest element
                # in the a-section slice. This means that every element in the array
                # was strictly lesser than the lowest number of the a section,
                # and means that all the numbers in the slice belong at the end of the array,
                # where they currently are! So, this algorithm is over,
                # even though we didn't drop all the numbers in the section yet.
                # We can just drop them all right here, right now.
                #
                # BUT FIRST, they may not be in order yet, so we need to copy them
                # from the aux array.

                for _ in self.playground.copy_array_slice(
                    self.AUX_ARRAY_INDEX, aux_start_index,
                    0, current_section_range.start,
                    len(current_section_range),
                ):
                    yield

                break

            should_drop: bool = self.playground.compare(
                (self.AUX_ARRAY_INDEX, aux_start_index),
                "<=",
                (0, index_to_compare),
            )
            yield

            if should_drop:
                # copy
                for _ in self.playground.copy_array_slice(
                    self.AUX_ARRAY_INDEX, aux_start_index,
                    0, current_section_range.start,
                    len(current_section_range),
                ):
                    yield

                # move the indices
                new_start: int = current_section_range.start + 1

                # Drop the CURRENT lowest number:
                current_section_range = range(
                    new_start,
                    current_section_range.stop,
                )
                # move the index of the lowest 
                aux_start_index += 1
            else:
                # roll
                self.playground.swap((0, current_section_range.start), (0, current_section_range.stop))
                yield

                current_section_range = range(
                    current_section_range.start + 1,
                    current_section_range.stop + 1,
                )

    def merge_halves(self, start: int, a_len: int, b_len: int):
        return self.merge_by_roll_and_drop(start, a_len, b_len)

    def merge_mostly_equal_halves(self, start: int, a_len: int, b_len: int):
        total_len: int = a_len + b_len

        block_size: int = int(sqrt(total_len))
        total_elements_in_perfect_blocks: int = block_size ** 2

        # If we split the slice in the array with the two halves to merge
        # (it's [start, start + total_len) into `block_size` blocks,
        # each containing `block_size` elements, it's possible that
        # `block_size` doesn't evenly divide `total_len`, and we have a remainder
        # of elements, in [0, block_size).
        #
        # For example:
        # # # # #|# # # #|# # # #|# # # #|# # <-- remainder
        #                  ^ middle
        # (each half here contains 9 elements)
        #
        # We also want each half to have both its blocks
        # start and end from the center of the slice.
        # We can do this, by dividing the remainder of elements
        # by 2 (by right shifting by 1), and placing the start
        # index for the blocks at that result:
        #
        # #|# # # #|# # # #|# # # #|# # # #|#
        #                  ^ middle
        #
        # For an odd number of total elements to merge:
        # # # # #|# # # #|# # # #|# # # #|# # # <-- remainder
        #                    ^ middle
        # (a_len = 10, b_len = 9)
        # # #|# # # #|# # # #|# # # #|# # # #|#
        # and
        # # # # #|# # # #|# # # #|# # # #|# # # <-- remainder
        #                  ^ middle
        # (a_len = 9, b_len = 10)
        # #|# # # #|# # # #|# # # #|# # # #|# #
        remaining_elements: int = total_len - total_elements_in_perfect_blocks
        blocks_start_index: int = remaining_elements >> 1

        for block_start_index in range(blocks_start_index, total_len, block_size):
            # Each of these [block_start_index, block_start_index + block_size)
            # equals to one block.
            pass

        return self.merge_by_roll_and_drop(start, a_len, b_len)

    def run(self):
        """
        TODO: THE LAST BLOCKS TO MERGE MAY HAVE
        AN IRREGULAR SIZE. THIS MAY CAUSE BUGS.
        """
        merge_len: int = 2

        while merge_len <= self.playground.main_array_len:
            halves_len: int = merge_len >> 1

            self.playground.spawn_new_array(halves_len)

            for merge_start_index in range(0, self.playground.main_array_len, merge_len):

                print(f"{merge_start_index = } {merge_len = } {halves_len = }")

                for _ in self.merge_halves(merge_start_index, halves_len, halves_len):
                    yield

            self.playground.delete_array(1)
            merge_len <<= 1


class Concurrent(Algorithm):
    """Concurrent Sorts"""
    options: dict[str, Option] = field(default_factory={"run in parallel": False}.copy)

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
        for _ in self.bitonic(0, self.playground.main_array_len, True):
            yield


class IRBitonicSort(BatchersBitonicSort):
    """Bitonic Sort (Iterative Network, Recursive Merge)"""
    def run(self):
        """Assumes main array has a power of 2 as its length."""
        section_len = 2
        while section_len <= self.playground.main_array_len:
            for start, direction in zip(range(0, self.playground.main_array_len, section_len), cycle((True, False))):
                for _ in self.merge(start, section_len, direction):
                    yield

            section_len *= 2


class IterativeBitonicSort(BatchersBitonicSort):
    """Iterative Bitonic Sort"""
    def run(self):
        """Assumes main array has a power of 2 as its length."""
        section_len = 2
        while section_len <= self.playground.main_array_len:
            half_section_len = section_len // 2
            merge_len = half_section_len
            while merge_len:

                directions = cycle(direction for direction in ">" * half_section_len + "<" * half_section_len)

                double_merge_len = merge_len * 2
                for start in range(0, self.playground.main_array_len - merge_len, double_merge_len):

                    for left in range(start, start + merge_len):
                        right = left + merge_len

                        should_swap = self.playground.compare((0, left), next(directions), (0, right))
                        yield

                        if should_swap:
                            self.playground.swap((0, left), (0, right))
                            yield

                merge_len //= 2
            section_len *= 2


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
        for _ in self.sorting_network(0, self.playground.main_array_len, 1):
            yield


class OddEvenMergesort(Concurrent):
    """Odd-Even Merge Sort"""
    def merge(self, start: int, amount: int, step=1):
        if amount < 2:
            return

        new_amount = amount // 2
        double_step = step * 2
        for _ in chain(self.merge(start, new_amount, double_step), self.merge(start + step, new_amount, double_step)):
            yield

        for index in range(start + step, start + amount * step, step):
            previous, current = (0, index - step), (0, index)
            should_swap = self.playground.compare(previous, ">", current)
            yield

            if should_swap:
                self.playground.swap(previous, current)
                yield

    def network(self, start: int, amount: int):
        if amount < 2:
            return

        new_amount = amount // 2

        for _ in chain(self.network(start, new_amount),
                       self.network(start + new_amount, new_amount),
                       self.merge(start, amount)):
            yield

    def run(self):
        for _ in self.network(0, self.playground.main_array_len):
            yield


class IROddEvenMergesort(OddEvenMergesort):
    """Odd-Even Mergesort (Iterative Network, Recursive Merge)"""
    def run(self):
        amount = 2
        while amount <= self.playground.main_array_len:
            for start in range(0, self.playground.main_array_len, amount):
                for _ in self.merge(start, amount):
                    yield
            amount *= 2


class IterativeOddEvenMergesort(OddEvenMergesort):
    """Iterative Odd-Even Mergesort"""
    def run(self):
        amount = 2
        while amount <= self.playground.main_array_len:

            comb_distance = amount
            while comb_distance:
                for start in range(0, self.playground.main_array_len, amount):
                    for left in range(start, start + amount - comb_distance):
                        right = left + comb_distance

                        should_swap = self.playground.compare((0, left), ">", (0, right))
                        yield

                        if should_swap:
                            self.playground.swap((0, left), (0, right))
                            yield

                comb_distance //= 2
            amount *= 2


class ParallelOddEvenMergeSort(Concurrent):
    """Parallel Odd Even Merge Sort"""
    def run(self):
        merge_len: int = 1

        while merge_len <= self.playground.main_array_len:
            section_len: int = merge_len << 1

            parallel_len: int = section_len

            comb_len: int = merge_len
            while comb_len >= 2:
                for section_start_index in range(0, self.playground.main_array_len, section_len):
                    pass
                comb_len >>= 1
                parallel_len >>= 1
            merge_len <<= 1                


class SlowSort(Algorithm):
    """Slow Sort"""
    def slow(self, start: int, amount: int):
        if amount < 2:
            return

        left_amount = amount // 2
        right_amount = (amount + 1) // 2
        for _ in chain(self.slow(start, left_amount), self.slow(start + left_amount, right_amount)):
            yield

        for current_amount in range(amount, 1, -1):
            left_end = start + current_amount // 2 - 1
            right_end = start + current_amount - 1

            should_swap = self.playground.compare((0, left_end),
                                                  ">",
                                                  (0, right_end))
            yield

            if should_swap:
                self.playground.swap((0, left_end), (0, right_end))
                yield

            right_half_amount = current_amount // 2
            current_amount -= 1
            left_half_amount = current_amount // 2
            # Right side may have one more element when amount is odd.

            for _ in chain(self.slow(start, left_half_amount),
                           self.slow(start + left_half_amount, right_half_amount)):
                yield

    def run(self):
        for _ in self.slow(0, self.playground.main_array_len):
            yield


class BogoSort(Verify, Shuffle):
    """Bogo Sort"""
    def run(self):
        while True:
            self.sorted = True

            for _ in Verify.run(self):
                yield

            if self.sorted:
                break

            for _ in Shuffle.run(self):
                yield


sorts = [BubbleSort, OptimizedBubbleSort, CocktailShakerSort, OptimizedCocktailShakerSort, OddEvenSort,
         InsertionSort, BaiaiSort, CircleSort, IterativeCircleSort, CombSort, ExchangeSort,
         SelectionSort, MaxHeapSort, MinHeapSort, OptimizedMaxHeapSort, OptimizedMinHeapSort,
         QuickSort,
         MergeSort, MergeSortInPlace,
         RadixLSDSort, RadixLSDSortInPlace, PigeonholeSort, CountSort, GravitySort,
         SquareRootSort,
         BatchersBitonicSort, IRBitonicSort, IterativeBitonicSort, PairwiseSortingNetwork,
         OddEvenMergesort, IROddEvenMergesort, IterativeOddEvenMergesort,
         SlowSort, BogoSort]
