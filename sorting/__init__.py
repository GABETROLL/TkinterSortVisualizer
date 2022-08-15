from sorting.sorts import *
from random import randint


@dataclass
class Shuffle(Algorithm):
    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums)):
            self.playground.swap((0, index), (0, randint(index, len(nums) - 1)))
            yield


class Verify(Algorithm):
    def run(self):
        nums = self.playground.main_array

        for index in range(len(nums) - 1):
            check = self.playground.compare((0, index), ">", (0, index + 1))
            yield

            if check:
                break
