from sorting.sorts import *
from random import randint


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
class Shuffle(AlreadySorted):
    """Linear Shuffle"""
    def run(self):
        AlreadySorted.run(self)

        nums = self.playground.main_array

        for index in range(len(nums)):
            self.playground.swap((0, index), (0, randint(index, len(nums) - 1)))
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


@dataclass
class Reversed(AlreadySorted):
    """Reversed Linear"""
    def run(self):
        for _ in AlreadySorted.run(self):
            yield
        for _ in AlreadySorted.reversal(self, 0):
            yield


shuffles = [Random, Shuffle, ManySimilar, Reversed, AlreadySorted]


class Verify(Algorithm):
    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums) - 1):
            check = self.playground.compare((0, index), ">", (0, index + 1))
            yield

            if check:
                break
