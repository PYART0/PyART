import math

import torch
from torch.nn import Parameter
from overrides import overrides

from allennlp.nn import util
from allennlp.nn.activations import Activation
from allennlp.modules.matrix_attention.matrix_attention import MatrixAttention


class LinearMatrixAttention(MatrixAttention):

    def __init__(
        self,
        tensor_1_dim: int,
        tensor_2_dim: int,
        combination: str = "x,y",
        activation: Activation = None,
    ) -> None:
        super().__init__()
        self._combination = combination
        self._weight_vector = Parameter(torch.Tensor(combined_dim))
        self._bias = Parameter(torch.Tensor(1))

    def reset_parameters(self):

    @overrides
    def forward(self, matrix_1: torch.Tensor, matrix_2: torch.Tensor) -> torch.Tensor:
        combined_tensors = util.combine_tensors_and_multiply()
        reveal_type(matrix_1)