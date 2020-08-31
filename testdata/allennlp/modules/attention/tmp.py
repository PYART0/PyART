import torch
from overrides import overrides
from allennlp.modules.attention.attention import Attention
from allennlp.nn import util


class CosineAttention(Attention):

    @overrides
    def _forward_internal(self, vector: torch.Tensor, matrix: torch.Tensor) -> torch.Tensor:
        a_norm = vector / (
        )
        b_norm = matrix / (
        )
        reveal_type(torch)