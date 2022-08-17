from time import sleep


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

    @property
    def array_count(self):
        return len(self.arrays)

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

        self.writes += 1
        sleep(self.delay)

    def increment(self, num: int, index: tuple[int, int]):
        self.pointers = {index}
        self.arrays[index[0]][index[1]] += num

        self.writes += 1
        sleep(self.delay)

    def array_iter(self, array_index: int):
        for index, num in enumerate(self.arrays[array_index]):
            self.pointers = {index}
            yield num

            sleep(self.delay)

    def compare(self, index_a: tuple[int, int], comparison: str, index_b: tuple[int, int]):
        """Compares nums at index_a and index_b and increases comparisons counter."""
        self.pointers = {index_a, index_b}
        self.reads += 2
        self.comparisons += 1

        sleep(self.delay)

        return eval(f"{self.arrays[index_a[0]][index_a[1]]}{comparison}{self.arrays[index_b[0]][index_b[1]]}")

    def swap(self, index_a: tuple[int, int], index_b: tuple[int, int]):
        """Swaps nums at index_a and index_b and increases swaps counter."""
        self.arrays[index_a[0]][index_a[1]], self.arrays[index_b[0]][index_b[1]] = \
            self.arrays[index_b[0]][index_b[1]], self.arrays[index_a[0]][index_a[1]]
        self.swaps += 1
        self.writes += 2

        sleep(self.delay)
