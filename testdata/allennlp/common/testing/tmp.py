import copy
import json
from os import PathLike
from typing import Any, Dict, Iterable, Set, Union

import torch
from numpy.testing import assert_allclose

from allennlp.commands.train import train_model_from_file
from allennlp.common import Params
from allennlp.common.testing.test_case import AllenNlpTestCase
from allennlp.data import DatasetReader, Vocabulary
from allennlp.data import DataLoader
from allennlp.data.batch import Batch
from allennlp.models import load_archive, Model
from allennlp.training import GradientDescentTrainer


class ModelTestCase(AllenNlpTestCase):

    def set_up_model(self, param_file, dataset_file):

        self.param_file = param_file

        if "vocabulary" in params:
            vocab_params = params["vocabulary"]
        else:
            vocab = Vocabulary.from_instances(instances)
        self.vocab = vocab
        self.instances = instances
        self.instances.index_with(vocab)

        self.dataset = Batch(list(self.instances))

    def ensure_model_can_train_save_and_load(
        self,
        param_file: Union[PathLike, str],
        tolerance: float = 1e-4,
        cuda_device: int = -1,
        gradients_to_ignore: Set[str] = None,
        overrides: str = "",
        metric_to_check: str = None,
        metric_terminal_value: float = None,
        metric_tolerance: float = 1e-4,
        disable_dropout: bool = True,
    ):
        save_dir = self.TEST_DIR / "save_and_load_test"
        archive_file = save_dir / "model.tar.gz"
        model = train_model_from_file(param_file, save_dir, overrides=overrides)
        metrics_file = save_dir / "metrics.json"
        if metric_to_check is not None:
            metric_value = metrics.get(f"best_validation_{metric_to_check}") or metrics.get(
                f"training_{metric_to_check}"
            )
            assert metric_value is not None, f"Cannot find {metric_to_check} in metrics.json file"
            assert metric_terminal_value is not None, "Please specify metric terminal value"
            assert abs(metric_value - metric_terminal_value) < metric_tolerance
        loaded_model = load_archive(archive_file, cuda_device=cuda_device).model
        assert state_keys == loaded_state_keys
        for key in state_keys:
            assert_allclose(
                model.state_dict()[key].cpu().numpy(),
                loaded_model.state_dict()[key].cpu().numpy(),
                err_msg=key,
            )
        params = Params.from_file(param_file, params_overrides=overrides)
        reader = DatasetReader.from_params(params["dataset_reader"])

        print("Reading with original model")
        model_dataset = reader.read(params["validation_data_path"])

        print("Reading with loaded model")
        loaded_dataset = reader.read(params["validation_data_path"])

        data_loader_params = params["data_loader"]
        data_loader_params["shuffle"] = False
        data_loader_params2 = Params(copy.deepcopy(data_loader_params.as_dict()))

        data_loader2 = DataLoader.from_params(dataset=loaded_dataset, params=data_loader_params2)

        model_batch = next(iter(data_loader))

        loaded_batch = next(iter(data_loader2))

        self.check_model_computes_gradients_correctly(
            model, model_batch, gradients_to_ignore, disable_dropout
        )

        for key in model_batch.keys():
            self.assert_fields_equal(model_batch[key], loaded_batch[key], key, 1e-6)

        for model_ in [model, loaded_model]:
            for module in model_.modules():
                if hasattr(module, "stateful") and module.stateful:
                    module.reset_states()
        print("Predicting with original model")
        model_predictions = model(**model_batch)
        print("Predicting with loaded model")
        loaded_model_predictions = loaded_model(**loaded_batch)

            self.assert_fields_equal(
                model_predictions[key], loaded_model_predictions[key], name=key, tolerance=tolerance
            )

        loaded_model_predictions = loaded_model(**loaded_batch)
        loaded_model_loss = loaded_model_predictions["loss"]
        assert loaded_model_loss is not None
        loaded_model_loss.backward()

        return model, loaded_model

    def ensure_model_can_train(
        self,
        trainer: GradientDescentTrainer,
        gradients_to_ignore: Set[str] = None,
        metric_to_check: str = None,
        metric_terminal_value: float = None,
        metric_tolerance: float = 1e-4,
        disable_dropout: bool = True,
    ):
        if metric_to_check is not None:
            metric_value = metrics.get(f"best_validation_{metric_to_check}") or metrics.get(
                f"training_{metric_to_check}"
            )
            assert metric_value is not None, f"Cannot find {metric_to_check} in metrics.json file"
            assert metric_terminal_value is not None, "Please specify metric terminal value"
            assert abs(metric_value - metric_terminal_value) < metric_tolerance

        model_batch = next(iter(trainer.data_loader))

        self.check_model_computes_gradients_correctly(
            trainer.model, model_batch, gradients_to_ignore, disable_dropout
        )

    def assert_fields_equal(self, field1, field2, name: str, tolerance: float = 1e-6) -> None:
        if isinstance(field1, torch.Tensor):
            assert_allclose(
                rtol=tolerance,
                err_msg=name,
            )
        elif isinstance(field1, dict):
            for key in field1:
                self.assert_fields_equal(
                    field1[key], field2[key], tolerance=tolerance, name=name + "." + str(key)
                )
        elif isinstance(field1, (list, tuple)):
            assert len(field1) == len(field2)
            for i, (subfield1, subfield2) in enumerate(zip(field1, field2)):
                self.assert_fields_equal(
                    subfield1, subfield2, tolerance=tolerance, name=name + f"[{i}]"
                )
        elif isinstance(field1, (float, int)):
            assert_allclose([field1], [field2], rtol=tolerance, err_msg=name)
        else:
            if field1 != field2:
                for key in field1.__dict__:
                    print(key, getattr(field1, key) == getattr(field2, key))
            assert field1 == field2, f"{name}, {type(field1)}, {type(field2)}"

    @staticmethod
    def check_model_computes_gradients_correctly(
        model: Model,
        model_batch: Dict[str, Union[Any, Dict[str, Any]]],
        params_to_ignore: Set[str] = None,
        disable_dropout: bool = True,
    ):
        print("Checking gradients")

        original_dropouts: Dict[str, float] = {}

        if disable_dropout:
            for name, module in model.named_modules():
                if isinstance(module, torch.nn.Dropout):
                    original_dropouts[name] = getattr(module, "p")
                    setattr(module, "p", 0)

        result = model(**model_batch)
        has_zero_or_none_grads = {}
        for name, parameter in model.named_parameters():
            if params_to_ignore and name in params_to_ignore:
                continue
            if parameter.requires_grad:

                if parameter.grad is None:
                    has_zero_or_none_grads[
                        name
                    ] = "No gradient computed (i.e parameter.grad is None)"

                elif parameter.grad.is_sparse or parameter.grad.data.is_sparse:
                    pass

                elif (parameter.grad.cpu() == zeros).all():
                    has_zero_or_none_grads[
                        name
                    ] = f"zeros with shape ({tuple(parameter.grad.size())})"
            else:
                assert parameter.grad is None

        if has_zero_or_none_grads:
                print(f"Parameter: {name} had incorrect gradient: {grad}")
            raise Exception("Incorrect gradients found. See stdout for more info.")

        if disable_dropout:
            for name, module in model.named_modules():
                if name in original_dropouts:
                    setattr(module, "p", original_dropouts[name])

    def ensure_batch_predictions_are_consistent(self, keys_to_ignore: Iterable[str] = ()):
        single_predictions = []
        for i, instance in enumerate(self.instances):
            dataset = Batch([instance])
            result = self.model(**tensors)
        full_dataset = Batch(self.instances)
        batch_predictions = self.model(**batch_tensors)
        for i, instance_predictions in enumerate(single_predictions):
                tolerance = 1e-6
                if "loss" in key:
                    continue
                if key in keys_to_ignore:
                    continue
                single_predicted = single_predicted[0]
                batch_predicted = batch_predictions[key][i]
                if isinstance(single_predicted, torch.Tensor):
                        slices = tuple(slice(0, size) for size in single_predicted.size())
                        batch_predicted = batch_predicted[slices]
                    assert_allclose(
                        single_predicted.data.numpy())
                    reveal_type(batch_predicted.data)