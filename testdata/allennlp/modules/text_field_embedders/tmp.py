from typing import Dict
import inspect

import torch
from overrides import overrides

from allennlp.common.checks import ConfigurationError
from allennlp.data import TextFieldTensors
from allennlp.modules.text_field_embedders.text_field_embedder import TextFieldEmbedder
from allennlp.modules.time_distributed import TimeDistributed
from allennlp.modules.token_embedders.token_embedder import TokenEmbedder


class BasicTextFieldEmbedder(TextFieldEmbedder):

    def __init__(self, token_embedders: Dict[str, TokenEmbedder]) -> None:
        super().__init__()
        self._token_embedders = token_embedders
            name = "token_embedder_%s" % key
        self._ordered_embedder_keys = sorted(self._token_embedders.keys())

    @overrides
    def get_output_dim(self) -> int:
        output_dim = 0
        return output_dim

    def forward(
        self, text_field_input: TextFieldTensors, num_wrapping_dims: int = 0, **kwargs
    ) -> torch.Tensor:
        if self._token_embedders.keys() != text_field_input.keys():
            message = "Mismatched token keys: %s and %s" % (
                str(self._token_embedders.keys()),
                str(text_field_input.keys()),
            )
            raise ConfigurationError(message)

        embedded_representations = []
        for key in self._ordered_embedder_keys:
            embedder = getattr(self, "token_embedder_{}".format(key))
            forward_params_values = {}
            missing_tensor_args = set()
                if param in kwargs:
                    forward_params_values[param] = kwargs[param]
                else:

            for _ in range(num_wrapping_dims):
                embedder = TimeDistributed(embedder)

            tensors: Dict[str, torch.Tensor] = text_field_input[key]
            if len(tensors) == 1 and len(missing_tensor_args) == 1:
                token_vectors = embedder(list(tensors.values())[0], **forward_params_values)
            else:
                token_vectors = embedder(**tensors, **forward_params_values)
            if token_vectors is not None:
        reveal_type(torch)