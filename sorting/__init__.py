from sorting.sorts import *
from random import randint
from math import sin, pi


class Random(Algorithm):
    """Random"""
    def run(self):
        nums_len = len(self.playground.main_array)
        for index in range(nums_len):
            self.playground.write(randint(1, nums_len), (0, index))
            yield


class Linear(Algorithm):
    """Linear"""
    def run(self):
        for index in range(len(self.playground.main_array)):
            self.playground.write(index + 1, (0, index))
            yield


class Shuffle(Algorithm):
    """Shuffle"""
    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums)):
            self.playground.swap((0, index), (0, randint(index, len(nums) - 1)))
            yield


class LinearShuffle(Linear, Shuffle):
    """Shuffled Linear"""
    def run(self):
        for _ in chain(Linear.run(self), Shuffle.run(self)):
            yield


@dataclass
class ManySimilar(Shuffle):
    """Many Similar"""
    div: int = 16

    def run(self):
        for index in range(len(self.playground.main_array)):
            num = index // self.div * self.div

            self.playground.write(num, (0, index))
            yield

        for _ in Shuffle.run(self):
            yield


class Reversed(Linear):
    """Reversed Linear"""
    def run(self):
        for _ in Linear.run(self):
            yield
        for _ in Linear.reversal(self, 0):
            yield


class FinalRadixPass(Linear):
    """Final Radix Pass"""
    def run(self):
        half_nums_len = self.playground.capacity // 2

        for index in range(half_nums_len):
            even_num = index
            odd_num = index + half_nums_len

            self.playground.write(even_num + 1, (0, index * 2))
            yield
            self.playground.write(odd_num + 1, (0, index * 2 + 1))
            yield


class Quadratic(Algorithm):
    """Quadratic"""
    def run(self):
        half_len = self.playground.capacity // 2
        shrink_factor = half_len ** 2 / self.playground.capacity
        for index in range(self.playground.capacity):
            input_index = index - half_len
            output = int((input_index + 1) ** 2 / shrink_factor)
            self.playground.write(output, (0, index))
            yield


class ShuffledQuadratic(Quadratic, Shuffle):
    """Shuffled Quadratic"""
    def run(self):
        for _ in chain(Quadratic.run(self), Shuffle.run(self)):
            yield


class SineWave(Algorithm):
    """Sine Wave"""
    def run(self):
        nums_len = len(self.playground.main_array)
        shrink_factor = 2 * pi / nums_len
        # input goes from [0, num_len) to [0, 2 * pi)

        for index in range(nums_len):
            num = sin(shrink_factor * index)
            num += 1
            # push sine wave up from (-1, 1) to (0, 2)
            num *= nums_len / 2
            # scale up to (0, nums_len)
            num = int(num)
            # round

            self.playground.write(num, (0, index))
            yield


shuffles = [Random, LinearShuffle, ManySimilar, Reversed, Linear, FinalRadixPass,
            Quadratic, ShuffledQuadratic, SineWave]


class Verify(Algorithm):
    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums) - 1):
            check = self.playground.compare((0, index), ">", (0, index + 1))
            yield

            if check:
                break
