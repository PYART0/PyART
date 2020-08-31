import logging
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Union

import numpy
import torch

from allennlp.common.checks import ConfigurationError
from allennlp.common.util import ensure_list
from allennlp.data.instance import Instance
from allennlp.data.vocabulary import Vocabulary



class Batch(Iterable):

    __slots__ = ["instances"]

    def __init__(self, instances: Iterable[Instance]) -> None:
        super().__init__()

        self.instances = ensure_list(instances)
        self._check_types()

    def _check_types(self) -> None:
        all_instance_fields_and_types: List[Dict[str, str]] = [
            {k: v.__class__.__name__ for k, v in x.fields.items()} for x in self.instances
        ]
        if not all(all_instance_fields_and_types[0] == x for x in all_instance_fields_and_types):
            raise ConfigurationError("You cannot construct a Batch with non-homogeneous Instances.")

    def get_padding_lengths(self) -> Dict[str, Dict[str, int]]:
        padding_lengths: Dict[str, Dict[str, int]] = defaultdict(dict)
        all_instance_lengths: List[Dict[str, Dict[str, int]]] = [
            instance.get_padding_lengths() for instance in self.instances
        ]
        all_field_lengths: Dict[str, List[Dict[str, int]]] = defaultdict(list)
        for instance_lengths in all_instance_lengths:
                max_value = max(x.get(padding_key, 0) for x in field_lengths)
                padding_lengths[field_name][padding_key] = max_value
        return {**padding_lengths}

    def as_tensor_dict(
        self, padding_lengths: Dict[str, Dict[str, int]] = None, verbose: bool = False
    ) -> Dict[str, Union[torch.Tensor, Dict[str, torch.Tensor]]]:
        padding_lengths = padding_lengths or defaultdict(dict)
        if verbose:
            logger.info("Getting max lengths from instances")
        if verbose:
            logger.info(f"Instance max lengths: {instance_padding_lengths}")
        lengths_to_use: Dict[str, Dict[str, int]] = defaultdict(dict)
                if padding_key in padding_lengths[field_name]:
                    lengths_to_use[field_name][padding_key] = padding_lengths[field_name][
                        padding_key
                    ]
                else:
                    lengths_to_use[field_name][padding_key] = instance_field_lengths[padding_key]

        field_tensors: Dict[str, list] = defaultdict(list)
        if verbose:
            logger.info(f"Now actually padding instances to length: {lengths_to_use}")
        for instance in self.instances:
            for field, tensors in instance.as_tensor_dict(lengths_to_use).items():

        field_classes = self.instances[0].fields
        return {
            field_name: field_classes[field_name].batch_tensors(field_tensor_list)
        }

    def __iter__(self) -> Iterator[Instance]:
        return iter(self.instances)

    def index_instances(self, vocab: Vocabulary) -> None:
        for instance in self.instances:

    def print_statistics(self) -> None:
        sequence_field_lengths: Dict[str, List] = defaultdict(list)
        for instance in self.instances:
            if not instance.indexed:
                raise ConfigurationError(
                    "Instances must be indexed with vocabulary "
                    "before asking to print dataset statistics."
                )
            for field, field_padding_lengths in instance.get_padding_lengths().items():

        print("\n\n----Dataset Statistics----\n")
            print(f"Statistics for {name}:")
            print(
                f"\tLengths: Mean: {numpy.mean(lengths)}, Standard Dev: {numpy.std(lengths)}, "
                f"Max: {numpy.max(lengths)}, Min: {numpy.min(lengths)}"
            )

        print("\n10 Random instances:")
        reveal_type(numpy.random)