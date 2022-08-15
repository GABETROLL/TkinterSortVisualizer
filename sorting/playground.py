from time import sleep


class MinHeap:
    def __init__(self):
        self.items = []

    def read(self):
        return self.items[0]

    def insert(self, num: int):
        self.items.append(num)

        index = len(self.items) - 1

        while 0 < index:
            parent_index = (index - 1) >> 1

            if self.items[parent_index] > self.items[index]:
                self.items[index], self.items[parent_index] = self.items[parent_index], self.items[index]
            else:
                break

            index = parent_index

    def pop(self):
        self.items[0], self.items[-1] = self.items[-1], self.items[0]

        result = self.items.pop()

        index = 0
        while index < len(self.items):
            left_child_index = index * 2 + 1
            right_child_index = left_child_index + 1

            if self.items[index] > self.items[left_child_index]:
                self.items[index], self.items[left_child_index] = self.items[left_child_index], self.items[index]

                index = left_child_index
            elif self.items[index] > self.items[right_child_index]:
                self.items[index], self.items[right_child_index] = self.items[right_child_index], self.items[index]

                index = right_child_index
            else:
                break

        return result


class SortPlayground:
    """Playground for sorting made of sorting arrays.
    Counts swaps, comparisons, writes and reversals."""

    def __init__(self, capacity: int, delay: float):
        self.capacity = capacity

        self.arrays = [list(range(capacity))]
        self.pointers = set()

        self.swaps = 0
        self.comparisons = 0
        self.reads = 0
        self.writes = 0
        self.reversals = 0

        self.delay = delay

    @property
    def main_array(self):
        return self.arrays[0]

    def reset(self):
        """Resets counters, deletes extra arrays and all pointers."""
        self.arrays = [list(range(self.capacity))]
        self.pointers = set()

        self.swaps = 0
        self.comparisons = 0
        self.reads = 0
        self.writes = 0
        self.reversals = 0

    def spawn_new_array(self, size: int):
        self.arrays.append([0 for _ in range(size)])

        sleep(self.delay)

    def delete_array(self, index: int):
        self.arrays.pop(index)

        sleep(self.delay)

    def read(self, index: tuple[int, int]):
        self.pointers = {index}
        self.reads += 1

        sleep(self.delay)

        return self.arrays[index[0]][index[1]]

    def write(self, num: int, index: tuple[int, int]):
        self.pointers = {index}
        self.arrays[index[0]][index[1]] = num

        sleep(self.delay)

    def increment(self, num: int, index: tuple[int, int]):
        self.pointers = {index}
        self.arrays[index[0]][index[1]] += num

        sleep(self.delay)

    def array_iter(self, array_index: int):
        for index, num in enumerate(self.arrays[array_index]):
            self.pointers = {index}
            yield num

    def compare(self, index_a: tuple[int, int], comparison: str, index_b: tuple[int, int]):
        """Compares nums at index_a and index_b and increases comparisons counter."""
        self.pointers = {index_a, index_b}
        self.comparisons += 1

        sleep(self.delay)

        return eval(f"{self.arrays[index_a[0]][index_a[1]]}{comparison}{self.arrays[index_b[0]][index_b[1]]}")

    def swap(self, index_a: tuple[int, int], index_b: tuple[int, int]):
        """Swaps nums at index_a and index_b and increases swaps counter."""
        self.arrays[index_a[0]][index_a[1]], self.arrays[index_b[0]][index_b[1]] = \
            self.arrays[index_b[0]][index_b[1]], self.arrays[index_a[0]][index_a[1]]
        self.swaps += 1

        sleep(self.delay)
