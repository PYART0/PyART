from typing import Dict, List

from overrides import overrides
import torch

from allennlp.common.checks import ConfigurationError
from allennlp.common.util import pad_sequence_to_length
from allennlp.data.tokenizers.token import Token
from allennlp.data.token_indexers.token_indexer import TokenIndexer, IndexedTokenList
from allennlp.data.vocabulary import Vocabulary


def _make_bos_eos(
    character: int,
    padding_character: int,
    beginning_of_word_character: int,
    end_of_word_character: int,
    max_word_length: int,
):
    char_ids = [padding_character] * max_word_length
    char_ids[0] = beginning_of_word_character
    char_ids[1] = character
    char_ids[2] = end_of_word_character
    return char_ids


class ELMoCharacterMapper:

    max_word_length = 50

    beginning_of_sentence_character = 256  # <begin sentence>
    end_of_sentence_character = 257  # <end sentence>
    beginning_of_word_character = 258  # <begin word>
    end_of_word_character = 259  # <end word>
    padding_character = 260  # <padding>

    beginning_of_sentence_characters = _make_bos_eos(
        beginning_of_sentence_character,
        padding_character,
        beginning_of_word_character,
        end_of_word_character,
        max_word_length,
    )
    end_of_sentence_characters = _make_bos_eos(
        end_of_sentence_character,
        padding_character,
        beginning_of_word_character,
        end_of_word_character,
        max_word_length,
    )

    bos_token = "<S>"
    eos_token = "</S>"

    def __init__(self, tokens_to_add: Dict[str, int] = None) -> None:
        self.tokens_to_add = tokens_to_add or {}

    def convert_word_to_char_ids(self, word: str) -> List[int]:
        if word in self.tokens_to_add:
            char_ids = [ELMoCharacterMapper.padding_character] * ELMoCharacterMapper.max_word_length
            char_ids[0] = ELMoCharacterMapper.beginning_of_word_character
            char_ids[1] = self.tokens_to_add[word]
            char_ids[2] = ELMoCharacterMapper.end_of_word_character
        elif word == ELMoCharacterMapper.bos_token:
            char_ids = ELMoCharacterMapper.beginning_of_sentence_characters
        elif word == ELMoCharacterMapper.eos_token:
            char_ids = ELMoCharacterMapper.end_of_sentence_characters
        else:
            word_encoded = word.encode("utf-8", "ignore")[
                : (ELMoCharacterMapper.max_word_length - 2)
            ]
            char_ids = [ELMoCharacterMapper.padding_character] * ELMoCharacterMapper.max_word_length
            char_ids[0] = ELMoCharacterMapper.beginning_of_word_character
            for k, chr_id in enumerate(word_encoded, start=1):
                char_ids[k] = chr_id
            char_ids[len(word_encoded) + 1] = ELMoCharacterMapper.end_of_word_character

        return [c + 1 for c in char_ids]

    def __eq__(self, other) -> bool:
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented


class ELMoTokenCharactersIndexer(TokenIndexer):

    def __init__(
        self,
        namespace: str = "elmo_characters",
        tokens_to_add: Dict[str, int] = None,
        token_min_padding_length: int = 0,
    ) -> None:
        super().__init__(token_min_padding_length)
        self._namespace = namespace
        self._mapper = ELMoCharacterMapper(tokens_to_add)

    @overrides
    def count_vocab_items(self, token: Token, counter: Dict[str, Dict[str, int]]):
        pass

    @overrides
    def get_empty_token_list(self) -> IndexedTokenList:
        return {"elmo_tokens": []}

    @overrides
    def tokens_to_indices(
        self, tokens: List[Token], vocabulary: Vocabulary
    ) -> Dict[str, List[List[int]]]:


        texts = [token.text for token in tokens]

        if any(text is None for text in texts):
            raise ConfigurationError(
                "ELMoTokenCharactersIndexer needs a tokenizer that retains text"
            )
        reveal_type(self._mapper)