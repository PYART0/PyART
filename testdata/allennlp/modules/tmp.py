from typing import List, Union

import torch

from allennlp.common import FromParams
from allennlp.common.checks import ConfigurationError
from allennlp.nn import Activation


class FeedForward(torch.nn.Module, FromParams):

    def __init__(
        self,
        input_dim: int,
        num_layers: int,
        hidden_dims: Union[int, List[int]],
        activations: Union[Activation, List[Activation]],
        dropout: Union[float, List[float]] = 0.0,
    ) -> None:

        super().__init__()
        if not isinstance(hidden_dims, list):
            hidden_dims = [hidden_dims] * num_layers  # type: ignore
        if not isinstance(activations, list):
            activations = [activations] * num_layers  # type: ignore
        if not isinstance(dropout, list):
            dropout = [dropout] * num_layers  # type: ignore
        if len(hidden_dims) != num_layers:
            raise ConfigurationError(
                "len(hidden_dims) (%d) != num_layers (%d)" % (len(hidden_dims), num_layers)
            )
        if len(activations) != num_layers:
            raise ConfigurationError(
                "len(activations) (%d) != num_layers (%d)" % (len(activations), num_layers)
            )
        if len(dropout) != num_layers:
            raise ConfigurationError(
                "len(dropout) (%d) != num_layers (%d)" % (len(dropout), num_layers)
            )
        self._activations = torch.nn.ModuleList(activations)
        input_dims = [input_dim] + hidden_dims[:-1]
        linear_layers = []
        for layer_input_dim, layer_output_dim in zip(input_dims, hidden_dims):
        self._linear_layers = torch.nn.ModuleList(linear_layers)
        reveal_type(torch.nn)