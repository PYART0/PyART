import torch
from overrides import overrides
from torch.nn.parameter import Parameter

from allennlp.common.checks import ConfigurationError
from allennlp.modules.span_extractors.span_extractor import SpanExtractor
from allennlp.modules.token_embedders.embedding import Embedding
from allennlp.nn import util


class BidirectionalEndpointSpanExtractor(SpanExtractor):

    def __init__(
        self,
        input_dim: int,
        forward_combination: str = "y-x",
        backward_combination: str = "x-y",
        num_width_embeddings: int = None,
        span_width_embedding_dim: int = None,
        bucket_widths: bool = False,
        use_sentinels: bool = True,
    ) -> None:
        super().__init__()
        self._input_dim = input_dim
        self._forward_combination = forward_combination
        self._backward_combination = backward_combination
        self._num_width_embeddings = num_width_embeddings
        self._bucket_widths = bucket_widths

        if self._input_dim % 2 != 0:
            raise ConfigurationError(
                "The input dimension is not divisible by 2, but the "
                "BidirectionalEndpointSpanExtractor assumes the embedded representation "
                "is bidirectional (and hence divisible by 2)."
            )
        if num_width_embeddings is not None and span_width_embedding_dim is not None:
            self._span_width_embedding = Embedding(
                num_embeddings=num_width_embeddings, embedding_dim=span_width_embedding_dim
            )
        elif num_width_embeddings is not None or span_width_embedding_dim is not None:
            raise ConfigurationError(
                "To use a span width embedding representation, you must"
                "specify both num_width_buckets and span_width_embedding_dim."
            )
        else:
            self._span_width_embedding = None

        self._use_sentinels = use_sentinels
        if use_sentinels:
            self._start_sentinel = Parameter(torch.randn([1, 1, int(input_dim / 2)]))
            self._end_sentinel = Parameter(torch.randn([1, 1, int(input_dim / 2)]))

    def get_input_dim(self) -> int:
        return self._input_dim

    def get_output_dim(self) -> int:
        unidirectional_dim = int(self._input_dim / 2)
        forward_combined_dim = util.get_combined_dim(
            self._forward_combination, [unidirectional_dim, unidirectional_dim]
        )
        backward_combined_dim = util.get_combined_dim(
            self._backward_combination, [unidirectional_dim, unidirectional_dim]
        )
        if self._span_width_embedding is not None:
            return (
                forward_combined_dim
                + backward_combined_dim
            )
        return forward_combined_dim + backward_combined_dim

    @overrides
    def forward(
        self,
        sequence_tensor: torch.FloatTensor,
        span_indices: torch.LongTensor,
        sequence_mask: torch.BoolTensor = None,
        span_indices_mask: torch.BoolTensor = None,
    ) -> torch.FloatTensor:

        forward_sequence, backward_sequence = sequence_tensor.split(
            int(self._input_dim / 2), dim=-1
        )

        span_starts, span_ends = [index.squeeze(-1) for index in span_indices.split(1, dim=-1)]

        if span_indices_mask is not None:
            span_starts = span_starts * span_indices_mask
            span_ends = span_ends * span_indices_mask
        exclusive_span_starts = span_starts - 1
        start_sentinel_mask = (exclusive_span_starts == -1).unsqueeze(-1)

        exclusive_span_ends = span_ends + 1

        if sequence_mask is not None:
        else:
            sequence_lengths = torch.ones_like(
                sequence_tensor[:, 0, 0], dtype=torch.long

        end_sentinel_mask = (exclusive_span_ends >= sequence_lengths.unsqueeze(-1)).unsqueeze(-1)

        exclusive_span_ends = exclusive_span_ends * ~end_sentinel_mask.squeeze(-1)
        exclusive_span_starts = exclusive_span_starts * ~start_sentinel_mask.squeeze(-1)

        if (exclusive_span_starts < 0).any() or (
            exclusive_span_ends > sequence_lengths.unsqueeze(-1)
        ).any():
            raise ValueError(
                f"Adjusted span indices must lie inside the length of the sequence tensor, "
                f"but found: exclusive_span_starts: {exclusive_span_starts}, "
                f"exclusive_span_ends: {exclusive_span_ends} for a sequence tensor with lengths "
                f"{sequence_lengths}."
            )

        forward_start_embeddings = util.batched_index_select(
            forward_sequence, exclusive_span_starts
        )

        backward_start_embeddings = util.batched_index_select(
            backward_sequence, exclusive_span_ends
        )
        backward_end_embeddings = util.batched_index_select(backward_sequence, span_starts)

        if self._use_sentinels:
            forward_start_embeddings = (
                forward_start_embeddings * ~start_sentinel_mask
                + start_sentinel_mask * self._start_sentinel
            )
            backward_start_embeddings = (
                backward_start_embeddings * ~end_sentinel_mask
                + end_sentinel_mask * self._end_sentinel
            )

        forward_spans = util.combine_tensors(
            self._forward_combination, [forward_start_embeddings, forward_end_embeddings]
        )
        backward_spans = util.combine_tensors(
            self._backward_combination, [backward_start_embeddings, backward_end_embeddings]
        )

        if self._span_width_embedding is not None:
            if self._bucket_widths:
                span_widths = util.bucket_values(
                    span_ends - span_starts, num_total_buckets=self._num_width_embeddings
                )
            else:
                span_widths = span_ends - span_starts

            span_width_embeddings = self._span_width_embedding(span_widths)
            return torch.cat([span_embeddings, span_width_embeddings], -1)

        if span_indices_mask is not None:)
            reveal_type(span_indices_mask)