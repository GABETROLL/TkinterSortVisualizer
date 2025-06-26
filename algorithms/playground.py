from dataclasses import dataclass

Pointer = tuple[int, int]
PointerType = int

READ: PointerType = 0
WRITE: PointerType = 1


@dataclass
class Statistics:
    swaps: int = 0
    comparisons: int = 0
    reads: int = 0
    writes: int = 0
    array_spawns: int = 0
    array_deletions: int = 0
    reversals: int = 0


class SortPlayground:
    """
    Playground for algorithms made of arrays.

    Contains the arrays of data the sorting algorithms are using,
    and several builin methods for swapping, comparing, reading,
    writing, spawning and deleting arrays, copying slices of arrays,
    and regarding the pointers.

    Keeps track of how many times certain operations are done
    (reading/writing values, comparisons, swaps, etc),
    by incrementing counters in `self.statistics` each time
    the operation is performed by one of the methods.

    IF AN ALGORITHM DOES OPERATIONS MANUALLY,
    THE STATISTICS ARE NOT COUNTED, AND NEED TO BE COUNTED
    MANUALLY, AS WELL.
    """

    def __init__(self, main_array_len: int):
        self.arrays = [list(range(1, main_array_len + 1))]
        self.pointers: dict[Pointer, PointerType] = {}

        self.named_pointers: dict[str, Pointer] = {}
        """
        Pointers that show up as arrows with names that point to elements in arrays.
        Dictionary of the names of the pointers, and the pointers themselves.
        """

        self.statistics: Statistics = Statistics()

    @property
    def main_array(self):
        return self.arrays[0]

    @property
    def main_array_len(self):
        return len(self.arrays[0])

    @property
    def array_count(self):
        return len(self.arrays)

    def read_at_pointers(self):
        """Yields every num pointed to by self.pointers."""
        for pointer in self.pointers:
            yield self.arrays[pointer[0]][pointer[1]]
    # Meant to be used as a display method.

    def reset(self):
        """Resets counters, deletes extra arrays and all pointers."""
        self.arrays = self.arrays[:1]
        self.pointers = {}

        self.statistics = Statistics()

    def change_main_array_len(self, new_len: int):
        """
        Sets the main array to have `new_len` as its len,
        by making it contain all the numbers in `range(1, new_len + 1)`.

        Then, calls `self.reset()`.
        """
        self.arrays[0] = list(range(1, new_len + 1))
        self.reset()

    def spawn_new_array(self, size: int):
        """
        Appends a new array of length `size` to `self.arrays`.
        It only contains zeros.

        Increments the "array spawns" statistic by 1.
        """
        self.arrays.append([0 for _ in range(size)])
        self.statistics.array_spawns += 1

    def copy_array(self, input_array_index: int, output_array_index: int):
        for index in range(len(self.arrays[input_array_index])):
            num = self.read((input_array_index, index))
            yield

            self.write(num, (output_array_index, index))
            yield

    def copy_array_slice(
        self,
        input_array_index: int,
        input_start_index: int,
        output_array_index: int,
        output_start_index: int,
        len: int,
    ):
        for input_num_index, output_num_index in zip(
            range(input_start_index, input_start_index + len),
            range(output_start_index, output_start_index + len),
        ):
            num: int = self.read((input_array_index, input_num_index))
            yield

            self.write(num, (output_array_index, output_num_index))
            yield

    def delete_array(self, index: int):
        self.arrays.pop(index)
        self.statistics.array_deletions += 1

    def read(self, index: tuple[int, int]):
        """Returns num at array_index[0], position index[1]."""
        self.pointers = {index: READ}
        self.statistics.reads += 1

        return self.arrays[index[0]][index[1]]

    def write(self, num: int, index: tuple[int, int]):
        """Writes num at array_index[0], position index[1]."""
        self.pointers = {index: WRITE}
        self.arrays[index[0]][index[1]] = num

        self.statistics.writes += 1

    def increment(self, num: int, index: tuple[int, int]):
        """Increments num at array_index[0], position index[1]."""
        self.pointers = {index: WRITE}
        self.arrays[index[0]][index[1]] += num

        self.statistics.writes += 1

    def array_iter(self, array_index: int):
        """Yields nums at array_index."""
        for index, num in enumerate(self.arrays[array_index]):
            self.pointers = {(array_index, index): READ}
            yield num

    def compare(self, index_a: tuple[int, int], comparison: str, index_b: tuple[int, int]):
        """Compares nums at index_a and index_b and increases comparisons counter."""
        self.pointers = {index_a: READ, index_b: READ}
        self.statistics.reads += 2
        self.statistics.comparisons += 1

        return eval(f"{self.arrays[index_a[0]][index_a[1]]}{comparison}{self.arrays[index_b[0]][index_b[1]]}")

    def swap(self, index_a: tuple[int, int], index_b: tuple[int, int]):
        """Swaps nums at index_a and index_b and increases swaps counter."""
        self.pointers = {index_a: WRITE, index_b: WRITE}
        self.arrays[index_a[0]][index_a[1]], self.arrays[index_b[0]][index_b[1]] = \
            self.arrays[index_b[0]][index_b[1]], self.arrays[index_a[0]][index_a[1]]
        self.statistics.swaps += 1
        self.statistics.reads += 2
        self.statistics.writes += 2
