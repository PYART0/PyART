from typing import Dict, List, Union
import logging
import json
from overrides import overrides
from allennlp.common.file_utils import cached_path
from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.fields import LabelField, TextField, Field, ListField
from allennlp.data.instance import Instance
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer
from allennlp.data.tokenizers import Tokenizer, SpacyTokenizer
from allennlp.data.tokenizers.sentence_splitter import SpacySentenceSplitter



class TextClassificationJsonReader(DatasetReader):

    def __init__(
        self,
        token_indexers: Dict[str, TokenIndexer] = None,
        tokenizer: Tokenizer = None,
        segment_sentences: bool = False,
        max_sequence_length: int = None,
        skip_label_indexing: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._tokenizer = tokenizer or SpacyTokenizer()
        self._segment_sentences = segment_sentences
        self._max_sequence_length = max_sequence_length
        self._skip_label_indexing = skip_label_indexing
        self._token_indexers = token_indexers or {"tokens": SingleIdTokenIndexer()}
        if self._segment_sentences:
            self._sentence_segmenter = SpacySentenceSplitter()

    @overrides
    def _read(self, file_path):
        with open(cached_path(file_path), "r") as data_file:
            for line in data_file.readlines():
                if not line:
                    continue
                text = items["text"]
                if label is not None:
                    if self._skip_label_indexing:
                        try:
                            label = int(label)
                        except ValueError:
                            raise ValueError(
                                "Labels must be integers if skip_label_indexing is True."
                            )
                    else:
                        label = str(label)
                if instance is not None:
                    yield instance

    def _truncate(self, tokens):
        if len(tokens) > self._max_sequence_length:
            tokens = tokens[: self._max_sequence_length]
        return tokens

    @overrides
    def text_to_instance(
        self, text: str, label: Union[str, int] = None
    ) -> Instance:  # type: ignore

        fields: Dict[str, Field] = {}
        if self._segment_sentences:
            sentences: List[Field] = []
            for sentence in sentence_splits:
                if self._max_sequence_length is not None:
                    word_tokens = self._truncate(word_tokens)
                reveal_type(sentences)