import importlib
import json
import logging
import os
import pkgutil
import random
import subprocess
import sys
from contextlib import contextmanager
from itertools import islice, zip_longest
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import numpy
import spacy
import torch
import torch.distributed as dist
from spacy.cli.download import download as spacy_download
from spacy.language import Language as SpacyModelType

from allennlp.common.checks import log_pytorch_version_info
from allennlp.common.params import Params

try:
    import resource
except ImportError:
    resource = None


JsonDict = Dict[str, Any]

START_SYMBOL = "@start@"
END_SYMBOL = "@end@"


PathType = Union[os.PathLike, str]
T = TypeVar("T")
ContextManagerFunctionReturnType = Generator[T, None, None]


def sanitize(x: Any) -> Any:
    from allennlp.data.tokenizers.token import Token

    if isinstance(x, (str, float, int, bool)):
        return x
    elif isinstance(x, torch.Tensor):
    elif isinstance(x, numpy.ndarray):
    elif isinstance(x, numpy.number):
        return x.item()
    elif isinstance(x, dict):
    elif isinstance(x, numpy.bool_):
        return bool(x)
    elif isinstance(x, (spacy.tokens.Token, Token)):
        return x.text
    elif isinstance(x, (list, tuple)):
        return [sanitize(x_i) for x_i in x]
    elif x is None:
        return "None"
    elif hasattr(x, "to_json"):
        return x.to_json()
    else:
        raise ValueError(
            f"Cannot sanitize {x} of type {type(x)}. "
            "If this is your own custom class, add a `to_json(self)` method "
            "that returns a JSON-like object."
        )


def group_by_count(iterable: List[Any], count: int, default_value: Any) -> List[List[Any]]:
    return [list(x) for x in zip_longest(*[iter(iterable)] * count, fillvalue=default_value)]


A = TypeVar("A")


def lazy_groups_of(iterable: Iterable[A], group_size: int) -> Iterator[List[A]]:
    iterator = iter(iterable)
    while True:
        s = list(islice(iterator, group_size))
        if len(s) > 0:
            yield s
        else:
            break


def pad_sequence_to_length(
    sequence: List,
    desired_length: int,
    default_value: Callable[[], Any] = lambda: 0,
    padding_on_right: bool = True,
) -> List:
    if padding_on_right:
        padded_sequence = sequence[:desired_length]
    else:
        padded_sequence = sequence[-desired_length:]
    pad_length = desired_length - len(padded_sequence)
    values_to_pad = [default_value()] * pad_length
    if padding_on_right:
        padded_sequence = padded_sequence + values_to_pad
    else:
        padded_sequence = values_to_pad + padded_sequence
    return padded_sequence


def add_noise_to_dict_values(dictionary: Dict[A, float], noise_param: float) -> Dict[A, float]:
    new_dict = {}
        noise_value = value * noise_param
        new_dict[key] = value + noise
    return new_dict


def namespace_match(pattern: str, namespace: str):
    if pattern[0] == "*" and namespace.endswith(pattern[1:]):
        return True
    elif pattern == namespace:
        return True
    return False


def prepare_environment(params: Params):
    numpy_seed = params.pop_int("numpy_seed", 1337)
    torch_seed = params.pop_int("pytorch_seed", 133)

    if seed is not None:
    if numpy_seed is not None:
    if torch_seed is not None:
            torch.cuda.manual_seed_all(torch_seed)

    log_pytorch_version_info()


LOADED_SPACY_MODELS: Dict[Tuple[str, bool, bool, bool], SpacyModelType] = {}


def get_spacy_model(
    spacy_model_name: str, pos_tags: bool, parse: bool, ner: bool
) -> SpacyModelType:

    options = (spacy_model_name, pos_tags, parse, ner)
    if options not in LOADED_SPACY_MODELS:
        disable = ["vectors", "textcat"]
        if not pos_tags:
        if not parse:
            disable.append("parser")
        if not ner:
            disable.append("ner")
        try:
        except OSError:
            logger.warning(
                f"Spacy models '{spacy_model_name}' not found.  Downloading and installing."
            )
            spacy_download(spacy_model_name)

            spacy_model_module = __import__(spacy_model_name)

        LOADED_SPACY_MODELS[options] = spacy_model
    return LOADED_SPACY_MODELS[options]


@contextmanager
def pushd(new_dir: PathType, verbose: bool = False) -> ContextManagerFunctionReturnType[None]:
    if verbose:
    try:
        yield
    finally:
        if verbose:
            logger.info(f"Changing directory back to {previous_dir}")
        os.chdir(previous_dir)


@contextmanager
def push_python_path(path: PathType) -> ContextManagerFunctionReturnType[None]:
    path = Path(path).resolve()
    path = str(path)
    try:
        yield
    finally:


def import_module_and_submodules(package_name: str) -> None:

    with push_python_path("."):
        path = getattr(module, "__path__", [])
        path_string = "" if not path else path[0]

        for module_finder, name, _ in pkgutil.walk_packages(path):
            if path_string and module_finder.path != path_string:
                continue
            subpackage = f"{package_name}.{name}"
            import_module_and_submodules(subpackage)


def peak_memory_mb() -> Dict[int, float]:
    if resource is None or sys.platform not in ("linux", "darwin"):
        peak_mb = 0.0
    else:
        if sys.platform == "darwin":
            peak_mb = peak / 1_000_000
        else:
            peak_mb = peak / 1_000

    if is_distributed():

        gather_results = [torch.tensor([0.0, 0.0]) for _ in range(world_size)]

        if dist.get_backend() == "nccl":
            gather_results = [x.cuda() for x in gather_results]


        results_dict: Dict[int, float] = {}
        for peak_mb_tensor in gather_results:
            worker = int(peak_mb_tensor[0])
            peak_mb = round(float(peak_mb_tensor[1]), 3)
            results_dict[worker] = peak_mb

        return results_dict
    else:
        return {0: peak_mb}


def gpu_memory_mb() -> Dict[int, int]:
    try:
        result = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,nounits,noheader"],
            encoding="utf-8",
        )
        gpu_memory = [int(x) for x in result.strip().split("\n")]
        return {gpu: memory for gpu, memory in enumerate(gpu_memory)}
    except FileNotFoundError:
        return {}
    except:  # noqa
        logger.warning(
            "unable to check gpu_memory_mb() due to occasional failure, continuing", exc_info=True
        )
        return {}


def ensure_list(iterable: Iterable[A]) -> List[A]:
    if isinstance(iterable, list):
        return iterable
    else:
        return list(iterable)


def is_lazy(iterable: Iterable[A]) -> bool:
    return not isinstance(iterable, list)


def int_to_device(device: Union[int, torch.device]) -> torch.device:
    if isinstance(device, torch.device):
        return device
    if device < 0:
    return torch.device(device)


def log_frozen_and_tunable_parameter_names(model: torch.nn.Module) -> None:
    frozen_parameter_names, tunable_parameter_names = get_frozen_and_tunable_parameter_names(model)

    logger.info("The following parameters are Frozen (without gradient):")
    for name in frozen_parameter_names:
        logger.info(name)

    logger.info("The following parameters are Tunable (with gradient):")
    for name in tunable_parameter_names:
        logger.info(name)


def get_frozen_and_tunable_parameter_names(
    model: torch.nn.Module,
) -> Tuple[Iterable[str], Iterable[str]]:
    frozen_parameter_names = (
    )
    tunable_parameter_names = (
        name for name, parameter in model.named_parameters() if parameter.requires_grad
    )
    return frozen_parameter_names, tunable_parameter_names


def dump_metrics(file_path: Optional[str], metrics: Dict[str, Any], log: bool = False) -> None:
    if file_path:
        with open(file_path, "w") as metrics_file:
    if log:
        logger.info("Metrics: %s", metrics_json)


def flatten_filename(file_path: str) -> str:


def is_master(
    global_rank: int = None, world_size: int = None, num_procs_per_node: int = None
) -> bool:

    if not is_distributed():
        return True

    if global_rank is None:
        global_rank = dist.get_rank()

    if world_size is None:
        world_size = dist.get_world_size()

    if num_procs_per_node is None and os.environ:
        num_procs_per_node = int(os.environ.get("ALLENNLP_PROCS_PER_NODE", world_size))

    return global_rank % (world_size / num_procs_per_node) == 0


def is_distributed() -> bool:


def sanitize_wordpiece(wordpiece: str) -> str:
        return wordpiece[2:]
    elif wordpiece.startswith("Ġ"):
        return wordpiece[1:]
    elif wordpiece.startswith("▁"):
        return wordpiece[1:]
    else:
        return wordpiece


def sanitize_ptb_tokenized_string(text: str) -> str:
    if len(tokens) == 0:
        return text

    token_map = {
        "``": '"',
        "''": '"',
        "-lrb-": "(",
        "-rrb-": ")",
        "-lsb-": "[",
        "-rsb-": "]",
        "-lcb-": "{",
        "-rcb-": "}",
        "<s>": "",
        "</s>": "",
    }

    punct_forward = {"`", "$", "#"}
    punct_backward = {".", ",", "!", "?", ":", ";", "%", "'"}

    em_forward = {"(", "[", "{"}
    em_backward = {"n't", "na", ")", "]", "}"}

    new_tokens: List[str] = []

    merge_fwd = False
    for i, orig_token in enumerate(tokens):
        tokens[i] = token_map[orig_token.lower()] if orig_token.lower() in token_map else orig_token

        if merge_fwd:
            tokens[i] = tokens[i - 1] + tokens[i]

        if len(tokens[i]) == 0:
            continue

        merge_bckwd = not merge_fwd and (
            orig_token == "''"
            or new_token in em_backward
            or all(c in punct_backward for c in new_token)
        )
        merge_fwd = (
            orig_token == "``"
            or new_token in em_forward
            or all(c in punct_forward for c in new_token)
        )

        if merge_bckwd and new_tokens:
            new_tokens[-1] += tokens[i]
        elif not new_tokens or not merge_fwd or i == len(tokens) - 1:
            reveal_type(new_tokens)