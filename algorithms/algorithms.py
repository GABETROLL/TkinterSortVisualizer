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


class OptimizedHeapify(Algorithm):
    def optimized_heap_insert(self, new_index: int, mode: str = "min"):
        """
        TODO: FIX

        (UNUSED)

        By assuming that all [0, new_index) of `self.playground.main_array`
        are PART OF AN ALREADY VALID HEAP (max/min, depending on the `mode` parameter),
        this method insert an (ASSUMED) NEW number to this heap, which should be located
        in `new_index`, in `self.playground.main_array`.

        This method uses the optimized version of heap insertion,
        where instead of repeatedly checking if the current new element should be
        swapped with its parent, it starts by swapping the new element and
        the current root of the heap, and checking if it needs to be swapped
        with either of its children. If it does, it swaps it with the more optimal child.
        """
        self.playground.swap((0, 0), (0, new_index))

        compare_index: int = 0
        sign: str = ">" if mode == "min" else "<"

        while True:
            left_child_index: int = (compare_index << 1) + 1
            right_child_index: int = (compare_index << 1) + 2

            should_swap_with_left_child: bool = self.playground.compare(
                (0, compare_index),
                sign,
                (0, left_child_index),
            )
            should_swap_with_right_child: bool = self.playground.compare(
                (0, compare_index),
                sign,
                (0, right_child_index)
            )

            if should_swap_with_left_child or should_swap_with_right_child:
                if self.playground.compare((0, left_child_index), sign, (0, right_child_index)):
                    self.playground.swap((0, compare_index), (0, left_child_index))
                    compare_index = left_child_index
                else:
                    self.playground.swap((0, compare_index), (0, right_child_index))
                    compare_index = right_child_index

    def ultra_optimized_heap_insert(self, new_index: int, mode: str = "min"):
        """
        By assuming that all [0, new_index) of `self.playground.main_array`
        are PART OF AN ALREADY VALID HEAP (max/min, depending on the `mode` parameter),
        this method insert an (ASSUMED) NEW number to this heap, which should be located
        in `new_index`, in `self.playground.main_array`.

        This method uses the optimized version of heap insertion,
        where instead of repeatedly checking if the current new element should be
        swapped with its parent, it starts by swapping the new element and
        the current root of the heap, and checking if it needs to be swapped
        with either of its children. If it does, it swaps it with the more optimal child.
        """
        compare_index: int = 0
        sign: str = ">" if mode == "min" else "<"

        while True:
            # print(compare_index, new_index)
            # Compare element at current `compare_index` with element currently in `new_index`,
            # and swap if necessary.
            should_swap: bool = self.playground.compare(
                (0, compare_index),
                sign,
                (0, new_index),
            )
            yield

            if should_swap:
                self.playground.swap((0, compare_index), (0, new_index))
                yield

            # Calculate positions of the left and right children
            # of the element at `compare_index`
            left_child_index: int = (compare_index << 1) + 1
            right_child_index: int = (compare_index << 1) + 2

            # Decide what child is the most optimal to compare against, next iteration.
            #
            # If the indices of the children of the element that's being compared
            # are outside the range of the heap, meaning,
            # both `left_child_index` and `right_child_index` > `new_index`,
            # there is nowhere else for the element at `compare_index`
            # to go, and that means this algorithm has finished successfully
            # (because the element in `compare_index` has been swapped into a leaf position,
            # it must be farther from the root than its now parent (that used to be its child),
            # so it's in order)
            #
            # If left_child_index == new_index, and new_index < right_child_index,
            # right_child_index is outside of the range of the heap. This means only
            # the left child can be compared with the element at `compare_index`,
            # and swapped if necessary. Then, the algorithm would have finished successfully.
            #
            # If left_child_index < new_index, and new_index == right_child_index,
            # two things could happen:
            # 1) the element at `left_child_index` is farther from the root, so then,
            # that element and the element at `new_index` are compared, swapped if necessary,
            # then the algorithm would have finished successfully.
            # 2) the element at `right_child_index`, a.k.a. `new_index` is farther from the root,
            # then the element at `new_index` is compared against itself, doesn't need swapping
            # (the sign doesn't include euqals), and the algorithm finishes successfully.
            #
            # Finally, if both `left_child_index` and `right_child_index` < `new_index`,
            # The child farthest from the root is chosen as the new `compare_index`,
            # and the algorithm continues like normal.
            if new_index < left_child_index and new_index < right_child_index:
                break
            elif new_index < right_child_index:
                # new_index == left_child_index < right_child_index
                compare_index = left_child_index
            else:
                # left_child_index < new_index == right_child_index
                # - or -
                # left_child_index and right_child_index < new_index
                left_child_farther_from_root: bool = self.playground.compare((0, left_child_index), sign, (0, right_child_index))

                if left_child_farther_from_root:
                    compare_index = left_child_index
                else:
                    compare_index = right_child_index

    def optimized_heapify(self, mode: str = "min"):
        """
        Turns the main array in `self.playground` into a heap,
        using the optimized heap insert algorithm above.
        """
        for index in range(1, self.playground.main_array_len):
            for _ in self.ultra_optimized_heap_insert(index, mode):
                yield


class MaxHeapShuffle(OptimizedHeapify):
    """Max Heap"""
    def run(self):
        for _ in self.optimized_heapify("max"):
            yield


class MinHeapShuffle(OptimizedHeapify):
    """Min Heap"""
    def run(self):
        for _ in self.optimized_heapify("min"):
            yield


shuffles = [Nothing, Shuffle, Reversal, RecursiveReversal, HalfRotation, MaxHeapShuffle, MinHeapShuffle]
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
