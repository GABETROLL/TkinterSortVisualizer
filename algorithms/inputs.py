from algorithms.algorithm import Algorithm
from dataclasses import dataclass
from random import randint
from math import sin, pi


class Input(Algorithm):
    """Input"""
    def run(self):
        raise NotImplementedError


class Random(Input):
    """Random Input"""
    def run(self):
        nums_len = len(self.playground.main_array)
        for index in range(nums_len):
            self.playground.write(randint(1, nums_len), (0, index))
            yield


class Linear(Input):
    """Linear Input"""
    def run(self):
        for index in range(len(self.playground.main_array)):
            self.playground.write(index + 1, (0, index))
            yield


class FinalRadixPass(Linear):
    """Final Radix Pass On Linear Input"""
    def run(self):
        half_nums_len = self.playground.array_len // 2

        for index in range(half_nums_len):
            even_num = index
            odd_num = index + half_nums_len

            self.playground.write(even_num + 1, (0, index * 2))
            yield
            self.playground.write(odd_num + 1, (0, index * 2 + 1))
            yield


class FinalMergePass(Linear):
    """Final Merge Pass On Linear Input"""
    def run(self):
        for index, odd in enumerate(range(1, self.playground.array_len + 1, 2)):
            self.playground.write(odd, (0, index))
            yield

        for index, even in enumerate(range(2, self.playground.array_len + 1, 2)):
            self.playground.write(even, (0, self.playground.array_len // 2 + index))
            yield


@dataclass
class ManySimilar(Linear):
    """Many Similar Linear Inputs"""
    div: int = 16

    def run(self):
        for index in range(len(self.playground.main_array)):
            num = index // self.div * self.div

            self.playground.write(num, (0, index))
            yield


class Quadratic(Input):
    """Quadratic Input"""
    def run(self):
        half_len = self.playground.array_len // 2
        shrink_factor = half_len ** 2 / self.playground.array_len
        for index in range(self.playground.array_len):
            input_index = index - half_len
            output = int((input_index + 1) ** 2 / shrink_factor)
            self.playground.write(output, (0, index))
            yield


class SineWave(Input):
    """Sine Wave Input"""
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


inputs = [Random, Linear, FinalRadixPass, FinalMergePass, ManySimilar, Quadratic, SineWave]
