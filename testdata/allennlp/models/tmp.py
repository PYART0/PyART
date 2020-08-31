import logging
import os
from os import PathLike
from typing import Dict, List, Set, Type, Optional, Union

import numpy
import torch

from allennlp.common.checks import ConfigurationError
from allennlp.common.params import Params
from allennlp.common.registrable import Registrable
from allennlp.data import Instance, Vocabulary
from allennlp.data.batch import Batch
from allennlp.nn import util
from allennlp.nn.regularizers import RegularizerApplicator


_DEFAULT_WEIGHTS = "best.th"


class Model(torch.nn.Module, Registrable):

    _warn_for_unseparable_batches: Set[str] = set()
    default_predictor: Optional[str] = None

    def __init__(self, vocab: Vocabulary, regularizer: RegularizerApplicator = None) -> None:
        super().__init__()
        self.vocab = vocab
        self._regularizer = regularizer

    def get_regularization_penalty(self) -> Optional[torch.Tensor]:
        if self._regularizer is None:
            regularization_penalty = None
        else:
            try:
                regularization_penalty = self._regularizer(self)
                if isinstance(regularization_penalty, float):
                    assert regularization_penalty == 0.0
            except AssertionError:
                raise RuntimeError("The regularizer cannot be a non-zero float.")
        return regularization_penalty

    def get_parameters_for_histogram_tensorboard_logging(self) -> List[str]:
        return [name for name, _ in self.named_parameters()]

    def forward(self, *inputs) -> Dict[str, torch.Tensor]:
        raise NotImplementedError

    def forward_on_instance(self, instance: Instance) -> Dict[str, numpy.ndarray]:
        return self.forward_on_instances([instance])[0]

    def forward_on_instances(self, instances: List[Instance]) -> List[Dict[str, numpy.ndarray]]:
        batch_size = len(instances)
            cuda_device = self._get_prediction_device()
            dataset = Batch(instances)
            outputs = self.make_output_human_readable(self(**model_input))

            instance_separated_output: List[Dict[str, numpy.ndarray]] = [
                {} for _ in dataset.instances
            ]
            for name, output in list(outputs.items()):
                if isinstance(output, torch.Tensor):
                    if output.dim() == 0:

                    if output.size(0) != batch_size:
                        self._maybe_warn_for_unseparable_batches(name)
                        continue
                elif len(output) != batch_size:
                    self._maybe_warn_for_unseparable_batches(name)
                    continue
                for instance_output, batch_element in zip(instance_separated_output, output):
                    instance_output[name] = batch_element
            return instance_separated_output

    def make_output_human_readable(
        self, output_dict: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:

        return output_dict

    def get_metrics(self, reset: bool = False) -> Dict[str, float]:

        return {}

    def _get_prediction_device(self) -> int:
        devices = {util.get_device_of(param) for param in self.parameters()}

        if len(devices) > 1:
            devices_string = ", ".join(str(x) for x in devices)
            raise ConfigurationError(f"Parameters have mismatching cuda_devices: {devices_string}")
        elif len(devices) == 1:
        else:
            return -1

    def _maybe_warn_for_unseparable_batches(self, output_key: str):
        if output_key not in self._warn_for_unseparable_batches:
            logger.warning(
                f"Encountered the {output_key} key in the model's return dictionary which "
                "couldn't be split by the batch size. Key will be ignored."
            )

    @classmethod
    def _load(
        cls,
        config: Params,
        serialization_dir: Union[str, PathLike],
        weights_file: Optional[Union[str, PathLike]] = None,
        cuda_device: int = -1,
    ) -> "Model":

        vocab_dir = os.path.join(serialization_dir, "vocabulary")
        vocab = vocab_class.from_files(
        )

        model_params = config.get("model")

        remove_pretrained_embedding_params(model_params)

        if cuda_device >= 0:
        else:
            model.cpu()

        model.extend_embedder_vocab()

        model.load_state_dict(model_state)

        return model

    @classmethod
    def load(
        cls,
        config: Params,
        serialization_dir: Union[str, PathLike],
        weights_file: Optional[Union[str, PathLike]] = None,
        cuda_device: int = -1,
    ) -> "Model":

        model_type = (
            config["model"] if isinstance(config["model"], str) else config["model"]["type"]
        )


        if not isinstance(model_class, type):
            model_class = Model
        return model_class._load(config, serialization_dir, weights_file, cuda_device)

    def extend_embedder_vocab(self, embedding_sources_mapping: Dict[str, str] = None) -> None:
        embedding_sources_mapping = embedding_sources_mapping or {}
        for model_path, module in self.named_modules():
            if hasattr(module, "extend_vocab"):
                module.extend_vocab(
                    self.vocab, extension_pretrained_file=pretrained_file, model_path=model_path,
                )

    @classmethod
    def from_archive(cls, archive_file: str, vocab: Vocabulary = None) -> "Model":
        from allennlp.models.archival import load_archive  # here to avoid circular imports

        model = load_archive(archive_file).model
        if vocab:
            model.extend_embedder_vocab()
        return model




def remove_pretrained_embedding_params(params: Params):
    if isinstance(params, Params):  # The model could possibly be a string, for example.
        if "pretrained_file" in keys:
            del params["pretrained_file"]
        reveal_type(params)