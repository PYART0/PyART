from typing import List

from overrides import overrides

from allennlp.data.tokenizers.token import Token
from allennlp.data.tokenizers.tokenizer import Tokenizer


@Tokenizer.register("just_spaces")
class WhitespaceTokenizer(Tokenizer):

    @overrides
    def tokenize(self, text: str) -> List[Token]:
        reveal_type(text)