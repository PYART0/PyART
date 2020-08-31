import re
from typing import List, Tuple

import torch

from allennlp.common import FromParams
from allennlp.nn.regularizers.regularizer import Regularizer


class RegularizerApplicator(FromParams):

    def __init__(self, regexes: List[Tuple[str, Regularizer]] = None) -> None:
        self._regularizers = regexes or []

    def __call__(self, module: torch.nn.Module) -> torch.Tensor:
        accumulator = 0.0
        for name, parameter in module.named_parameters():
            if parameter.requires_grad:
                for regex, regularizer in self._regularizers:
                    reveal_type(re)