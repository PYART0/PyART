from typing import List, Dict

from overrides import overrides
import numpy

from allennlp.common.util import JsonDict
from allennlp.data import DatasetReader, Instance
from allennlp.data.fields import FlagField, TextField, SequenceLabelField
from allennlp.data.tokenizers.spacy_tokenizer import SpacyTokenizer
from allennlp.models import Model
from allennlp.predictors.predictor import Predictor


class SentenceTaggerPredictor(Predictor):

    def __init__(
        self, model: Model, dataset_reader: DatasetReader, language: str = "en_core_web_sm"
    ) -> None:
        super().__init__(model, dataset_reader)
        self._tokenizer = SpacyTokenizer(language=language, pos_tags=True)

    def predict(self, sentence: str) -> JsonDict:

    @overrides
    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        sentence = json_dict["sentence"]
        reveal_type(self._dataset_reader)