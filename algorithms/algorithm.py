from algorithms.playground import SortPlayground
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class Option:
    value: object
    allowed_values: Iterable


@dataclass
class Algorithm:
    playground: SortPlayground
    options: dict[str, Option] = field(default_factory=dict)

    def run(self):
        raise NotImplementedError("Algorithm is abstract.")
