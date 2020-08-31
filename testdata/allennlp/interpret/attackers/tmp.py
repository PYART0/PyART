from copy import deepcopy
from typing import Dict, List, Tuple

import numpy
import torch

from allennlp.common.util import JsonDict, sanitize
from allennlp.data import Instance, Token
from allennlp.data.fields import TextField
from allennlp.data.token_indexers import (
    ELMoTokenCharactersIndexer,
    TokenCharactersIndexer,
    SingleIdTokenIndexer,
)
from allennlp.interpret.attackers import utils
from allennlp.interpret.attackers.attacker import Attacker
from allennlp.modules.token_embedders import Embedding
from allennlp.nn import util
from allennlp.predictors.predictor import Predictor

DEFAULT_IGNORE_TOKENS = ["@@NULL@@", ".", ",", ";", "!", "?", "[MASK]", "[SEP]", "[CLS]"]


@Attacker.register("hotflip")
class Hotflip(Attacker):

    def __init__(
        self, predictor: Predictor, vocab_namespace: str = "tokens", max_tokens: int = 5000
    ) -> None:
        super().__init__(predictor)
        self.vocab = self.predictor._model.vocab
        self.namespace = vocab_namespace
        self.max_tokens = max_tokens
        self.invalid_replacement_indices: List[int] = []
        for i in self.vocab._index_to_token[self.namespace]:
            if not self.vocab._index_to_token[self.namespace][i].isalnum():
                self.invalid_replacement_indices.append(i)
        self.embedding_matrix: torch.Tensor = None
        self.embedding_layer: torch.nn.Module = None
        self.cuda_device = predictor.cuda_device

    def initialize(self):
        if self.embedding_matrix is None:
            self.embedding_matrix = self._construct_embedding_matrix()

    def _construct_embedding_matrix(self) -> Embedding:
        embedding_layer = util.find_embedding_layer(self.predictor._model)
        self.embedding_layer = embedding_layer
        if isinstance(embedding_layer, (Embedding, torch.nn.modules.sparse.Embedding)):
            return embedding_layer.weight

        all_tokens = list(self.vocab._token_to_index[self.namespace])[: self.max_tokens]
        max_index = self.vocab.get_token_index(all_tokens[-1], self.namespace)
        self.invalid_replacement_indices = [
            i for i in self.invalid_replacement_indices if i < max_index
        ]

        inputs = self._make_embedder_input(all_tokens)

        embedding_matrix = embedding_layer(inputs).squeeze()

        return embedding_matrix

    def _make_embedder_input(self, all_tokens: List[str]) -> Dict[str, torch.Tensor]:
        inputs = {}
        indexers = self.predictor._dataset_reader._token_indexers  # type: ignore
        for indexer_name, token_indexer in indexers.items():
            if isinstance(token_indexer, SingleIdTokenIndexer):
                all_indices = [
                    self.vocab._token_to_index[self.namespace][token] for token in all_tokens
                ]
                inputs[indexer_name] = {"tokens": torch.LongTensor(all_indices).unsqueeze(0)}
            elif isinstance(token_indexer, TokenCharactersIndexer):
                tokens = [Token(x) for x in all_tokens]
                max_token_length = max(len(x) for x in all_tokens)
                max_token_length = max(max_token_length, token_indexer._min_padding_length)
                indexed_tokens = token_indexer.tokens_to_indices(tokens, self.vocab)
                padding_lengths = token_indexer.get_padding_lengths(indexed_tokens)
                padded_tokens = token_indexer.as_padded_tensor_dict(indexed_tokens, padding_lengths)
                inputs[indexer_name] = {
                    "token_characters": torch.LongTensor(
                        padded_tokens["token_characters"]
                    ).unsqueeze(0)
                }
            elif isinstance(token_indexer, ELMoTokenCharactersIndexer):
                elmo_tokens = []
                for token in all_tokens:
                    elmo_indexed_token = token_indexer.tokens_to_indices(
                        [Token(text=token)], self.vocab
                    )["elmo_tokens"]
                    elmo_tokens.append(elmo_indexed_token[0])
                inputs[indexer_name] = {"elmo_tokens": torch.LongTensor(elmo_tokens).unsqueeze(0)}
            else:
                raise RuntimeError("Unsupported token indexer:", token_indexer)

        return util.move_to_device(inputs, self.cuda_device)

    def attack_from_json(
        self,
        inputs: JsonDict,
        input_field_to_attack: str = "tokens",
        grad_input_field: str = "grad_input_1",
        ignore_tokens: List[str] = None,
        target: JsonDict = None,
    ) -> JsonDict:
        instance = self.predictor._json_to_instance(inputs)
        if target is None:
            output_dict = self.predictor._model.forward_on_instance(instance)
        else:
            output_dict = target

        original_instances = self.predictor.predictions_to_labeled_instances(instance, output_dict)

        original_text_field: TextField = original_instances[0][  # type: ignore
            input_field_to_attack
        ]
        original_tokens = deepcopy(original_text_field.tokens)

        final_tokens = []
        final_outputs = []
        for instance in original_instances:
            tokens, outputs = self.attack_instance(
                instance=instance,
                inputs=inputs,
                input_field_to_attack=input_field_to_attack,
                grad_input_field=grad_input_field,
                ignore_tokens=ignore_tokens,
                target=target,
            )
            final_tokens.append(tokens)
            final_outputs.append(outputs)

        return sanitize(
            {"final": final_tokens, "original": original_tokens, "outputs": final_outputs}
        )

    def attack_instance(
        self,
        instance: Instance,
        inputs: JsonDict,
        input_field_to_attack: str = "tokens",
        grad_input_field: str = "grad_input_1",
        ignore_tokens: List[str] = None,
        target: JsonDict = None,
    ) -> Tuple[List[Token], JsonDict]:
        if self.embedding_matrix is None:
            self.initialize()

        ignore_tokens = DEFAULT_IGNORE_TOKENS if ignore_tokens is None else ignore_tokens

        sign = -1 if target is None else 1

        fields_to_compare = utils.get_fields_to_compare(inputs, instance, input_field_to_attack)

        text_field: TextField = instance[input_field_to_attack]  # type: ignore

        grads, outputs = self.predictor.get_gradients([instance])

        flipped: List[int] = []
        for index, token in enumerate(text_field.tokens):
            if token.text in ignore_tokens:
                flipped.append(index)
        if "clusters" in outputs:
            for cluster in outputs["clusters"]:
                for mention in cluster:
                    for index in range(mention[0], mention[1] + 1):
                        flipped.append(index)

        while True:
            grad = grads[grad_input_field][0]
            grads_magnitude = [g.dot(g) for g in grad]

            for index in flipped:
                grads_magnitude[index] = -1

            index_of_token_to_flip = numpy.argmax(grads_magnitude)
            if grads_magnitude[index_of_token_to_flip] == -1:
                break
            flipped.append(index_of_token_to_flip)

            text_field_tensors = text_field.as_tensor(text_field.get_padding_lengths())
            input_tokens = util.get_token_ids_from_text_field_tensors(text_field_tensors)
            original_id_of_token_to_flip = input_tokens[index_of_token_to_flip]

            new_id = self._first_order_taylor(
                grad[index_of_token_to_flip], original_id_of_token_to_flip, sign
            )

            new_token = Token(self.vocab._index_to_token[self.namespace][new_id])  # type: ignore
            text_field.tokens[index_of_token_to_flip] = new_token
            instance.indexed = False

            grads, outputs = self.predictor.get_gradients([instance])  # predictions
            for key, output in outputs.items():
                if isinstance(output, torch.Tensor):
                    outputs[key] = output.detach().cpu().numpy().squeeze()
                elif isinstance(output, list):
                    outputs[key] = output[0]

            labeled_instance = self.predictor.predictions_to_labeled_instances(instance, outputs)[0]

            has_changed = utils.instance_has_changed(labeled_instance, fields_to_compare)
            if target is None and has_changed:
                break
            if target is not None and not has_changed:
                break
        return text_field.tokens, outputs

    def _first_order_taylor(self, grad: numpy.ndarray, token_idx: torch.Tensor, sign: int) -> int:
        grad = util.move_to_device(torch.from_numpy(grad), self.cuda_device)
        if token_idx.size() != ():
            raise NotImplementedError(
                "You are using a character-level indexer with no other indexers. This case is not "
                "currently supported for hotflip. If you would really like to see us support "
                "this, please open an issue on github."
            )
        if token_idx >= self.embedding_matrix.size(0):
            inputs = self._make_embedder_input([self.vocab.get_token_from_index(token_idx)])
            word_embedding = self.embedding_layer(inputs)[0]
        else:
            word_embedding = torch.nn.functional.embedding(
                util.move_to_device(torch.LongTensor([token_idx]), self.cuda_device),
                self.embedding_matrix,
            )
        word_embedding = word_embedding.detach().unsqueeze(0)
        grad = grad.unsqueeze(0).unsqueeze(0)
        new_embed_dot_grad = torch.einsum("bij,kj->bik", (grad, self.embedding_matrix))
        prev_embed_dot_grad = torch.einsum("bij,bij->bi", (grad, word_embedding)).unsqueeze(-1)
        neg_dir_dot_grad = sign * (prev_embed_dot_grad - new_embed_dot_grad)
        neg_dir_dot_grad = neg_dir_dot_grad.detach().cpu().numpy()
        neg_dir_dot_grad[:, :, self.invalid_replacement_indices] = -numpy.inf
        reveal_type(neg_dir_dot_grad)