from sorting.sorts import *
from random import randint
from math import sin, pi


@dataclass
class Random(Algorithm):
    """Random"""
    def run(self):
        nums_len = len(self.playground.main_array)
        for index in range(nums_len):
            self.playground.write(randint(1, nums_len), (0, index))
            yield


@dataclass
class AlreadySorted(Algorithm):
    """Already Sorted"""
    def run(self):
        for index in range(len(self.playground.main_array)):
            self.playground.write(index + 1, (0, index))
            yield


@dataclass
class LinearShuffle(AlreadySorted):
    """Linear Shuffle"""
    def run(self):
        for _ in AlreadySorted.run(self):
            yield

        nums = self.playground.main_array

        for index in range(len(nums)):
            self.playground.swap((0, index), (0, randint(index, len(nums) - 1)))
            yield


@dataclass
class ManySimilar(LinearShuffle):
    """Many Similar"""
    div: int = 16

    def run(self):
        for index in range(len(self.playground.main_array)):
            num = index // self.div * self.div

            self.playground.write(num, (0, index))
            yield

        for _ in LinearShuffle.run(self):
            yield


@dataclass
class Reversed(AlreadySorted):
    """Reversed Linear"""
    def run(self):
        for _ in AlreadySorted.run(self):
            yield
        for _ in AlreadySorted.reversal(self, 0):
            yield


@dataclass
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


shuffles = [Random, LinearShuffle, ManySimilar, Reversed, AlreadySorted, SineWave]


class Verify(Algorithm):
    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums) - 1):
            check = self.playground.compare((0, index), ">", (0, index + 1))
            yield

            if check:
                break
