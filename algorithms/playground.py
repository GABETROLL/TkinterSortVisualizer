class SortPlayground:
    """Playground for algorithms made of arrays.
    Counts swaps, comparisons, writes and reversals."""

    def __init__(self, main_array_len: int):
        self.arrays = [list(range(1, main_array_len + 1))]
        self.pointers = set()

        self.swaps = 0
        self.comparisons = 0
        self.reads = 0
        self.writes = 0
        self.reversals = 0

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
        self.pointers = set()

        self.swaps = 0
        self.comparisons = 0
        self.reads = 0
        self.writes = 0
        self.reversals = 0

    def change_main_array_len(self, new_len: int):
        self.arrays[0] = list(range(1, new_len + 1))
        self.reset()

    def spawn_new_array(self, size: int):
        self.arrays.append([0 for _ in range(size)])

    def copy_array(self, input_array_index: int, output_array_index: int):
        for index in range(len(self.arrays[input_array_index])):
            num = self.read((input_array_index, index))
            yield

            self.write(num, (output_array_index, index))
            yield

    def delete_array(self, index: int):
        self.arrays.pop(index)

    def read(self, index: tuple[int, int]):
        """Returns num at array_index[0], position index[1]."""
        self.pointers = {index}
        self.reads += 1

        return self.arrays[index[0]][index[1]]

    def write(self, num: int, index: tuple[int, int]):
        """Writes num at array_index[0], position index[1]."""
        self.pointers = {index}
        self.arrays[index[0]][index[1]] = num

        self.writes += 1

    def increment(self, num: int, index: tuple[int, int]):
        """Increments num at array_index[0], position index[1]."""
        self.pointers = {index}
        self.arrays[index[0]][index[1]] += num

        self.writes += 1

    def array_iter(self, array_index: int):
        """Yields nums at array_index."""
        for index, num in enumerate(self.arrays[array_index]):
            self.pointers = {(array_index, index)}
            yield num

    def compare(self, index_a: tuple[int, int], comparison: str, index_b: tuple[int, int]):
        """Compares nums at index_a and index_b and increases comparisons counter."""
        self.pointers = {index_a, index_b}
        self.reads += 2
        self.comparisons += 1

        return eval(f"{self.arrays[index_a[0]][index_a[1]]}{comparison}{self.arrays[index_b[0]][index_b[1]]}")

    def swap(self, index_a: tuple[int, int], index_b: tuple[int, int]):
        """Swaps nums at index_a and index_b and increases swaps counter."""
        self.pointers = {index_a, index_b}
        self.arrays[index_a[0]][index_a[1]], self.arrays[index_b[0]][index_b[1]] = \
            self.arrays[index_b[0]][index_b[1]], self.arrays[index_a[0]][index_a[1]]
        self.swaps += 1
        self.writes += 2
