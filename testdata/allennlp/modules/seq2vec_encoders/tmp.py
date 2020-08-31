from typing import Optional, Tuple

from overrides import overrides
import torch
from torch.nn import Conv1d, Linear

from allennlp.modules.seq2vec_encoders.seq2vec_encoder import Seq2VecEncoder
from allennlp.nn import Activation


class CnnEncoder(Seq2VecEncoder):

    def __init__(
        self,
        embedding_dim: int,
        num_filters: int,
        ngram_filter_sizes: Tuple[int, ...] = (2, 3, 4, 5),
        conv_layer_activation: Activation = None,
        output_dim: Optional[int] = None,
    ) -> None:
        super().__init__()
        self._embedding_dim = embedding_dim
        self._num_filters = num_filters
        self._ngram_filter_sizes = ngram_filter_sizes
        self._output_dim = output_dim

        self._convolution_layers = [
            Conv1d(
                in_channels=self._embedding_dim,
                out_channels=self._num_filters,
                kernel_size=ngram_size,
            )
            for ngram_size in self._ngram_filter_sizes
        ]
        for i, conv_layer in enumerate(self._convolution_layers):

        maxpool_output_dim = self._num_filters * len(self._ngram_filter_sizes)
        if self._output_dim:
            self.projection_layer = Linear(maxpool_output_dim, self._output_dim)
        else:
            self.projection_layer = None
            self._output_dim = maxpool_output_dim

    @overrides
    def get_input_dim(self) -> int:
        return self._embedding_dim

    @overrides
    def get_output_dim(self) -> int:
        return self._output_dim

    def forward(self, tokens: torch.Tensor, mask: torch.BoolTensor):
        if mask is not None:


        filter_outputs = []
        for i in range(len(self._convolution_layers)):
            convolution_layer = getattr(self, "conv_layer_{}".format(i))

        maxpool_output = (
        )

        if self.projection_layer:
            reveal_type(self)