from sorting.sorts import *
from random import randint


@dataclass
class Shuffle(Algorithm):
    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums)):
            self.playground.swap((0, index), (0, randint(index, len(nums) - 1)))
            yield


@dataclass
class ManySimilar(Shuffle):
    div: int = 16

    def run(self):
        for index in range(len(self.playground.main_array)):
            num = index // self.div * self.div

            self.playground.write(num, (0, index))
            yield

        for _ in Shuffle.run(self):
            yield


@dataclass
class AlreadySorted(Algorithm):
    def run(self):
        for index in range(len(self.playground.main_array)):
            self.playground.write(index, (0, index))
            yield


@dataclass
class Reversed(AlreadySorted):
    def run(self):
        for _ in AlreadySorted.run(self):
            yield
        for _ in AlreadySorted.reversal(self, 0):
            yield


shuffles = [ManySimilar, Shuffle, Reversed, AlreadySorted]


class Verify(Algorithm):
    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums) - 1):
            check = self.playground.compare((0, index), ">", (0, index + 1))
            yield

            if check:
                break
