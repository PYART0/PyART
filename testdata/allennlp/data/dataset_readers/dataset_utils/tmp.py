from typing import Callable, List, Set, Tuple, TypeVar, Optional
import warnings

from allennlp.common.checks import ConfigurationError
from allennlp.data.tokenizers.token import Token


TypedSpan = Tuple[int, Tuple[int, int]]
TypedStringSpan = Tuple[str, Tuple[int, int]]


class InvalidTagSequence(Exception):
    def __init__(self, tag_sequence=None):
        super().__init__()
        self.tag_sequence = tag_sequence

    def __str__(self):
        return " ".join(self.tag_sequence)


T = TypeVar("T", str, Token)


def enumerate_spans(
    sentence: List[T],
    offset: int = 0,
    max_span_width: int = None,
    min_span_width: int = 1,
    filter_function: Callable[[List[T]], bool] = None,
) -> List[Tuple[int, int]]:
    max_span_width = max_span_width or len(sentence)
    filter_function = filter_function or (lambda x: True)
    spans: List[Tuple[int, int]] = []

    for start_index in range(len(sentence)):
        last_end_index = min(start_index + max_span_width, len(sentence))
        first_end_index = min(start_index + min_span_width - 1, len(sentence))
        for end_index in range(first_end_index, last_end_index):
            start = offset + start_index
            end = offset + end_index
            if filter_function(sentence[slice(start_index, end_index + 1)]):
    return spans


def bio_tags_to_spans(
    tag_sequence: List[str], classes_to_ignore: List[str] = None
) -> List[TypedStringSpan]:
    classes_to_ignore = classes_to_ignore or []
    spans: Set[Tuple[str, Tuple[int, int]]] = set()
    span_start = 0
    span_end = 0
    active_conll_tag = None
    for index, string_tag in enumerate(tag_sequence):
        bio_tag = string_tag[0]
        if bio_tag not in ["B", "I", "O"]:
            raise InvalidTagSequence(tag_sequence)
        conll_tag = string_tag[2:]
        if bio_tag == "O" or conll_tag in classes_to_ignore:
            if active_conll_tag is not None:
            active_conll_tag = None
            continue
        elif bio_tag == "B":
            if active_conll_tag is not None:
                spans.add((active_conll_tag, (span_start, span_end)))
            active_conll_tag = conll_tag
            span_start = index
            span_end = index
        elif bio_tag == "I" and conll_tag == active_conll_tag:
            span_end += 1
        else:
            if active_conll_tag is not None:
                spans.add((active_conll_tag, (span_start, span_end)))
            active_conll_tag = conll_tag
            span_start = index
            span_end = index
    if active_conll_tag is not None:
        spans.add((active_conll_tag, (span_start, span_end)))
    return list(spans)


def iob1_tags_to_spans(
    tag_sequence: List[str], classes_to_ignore: List[str] = None
) -> List[TypedStringSpan]:
    classes_to_ignore = classes_to_ignore or []
    spans: Set[Tuple[str, Tuple[int, int]]] = set()
    span_start = 0
    span_end = 0
    active_conll_tag = None
    prev_bio_tag = None
    prev_conll_tag = None
    for index, string_tag in enumerate(tag_sequence):
        curr_bio_tag = string_tag[0]
        curr_conll_tag = string_tag[2:]

        if curr_bio_tag not in ["B", "I", "O"]:
            raise InvalidTagSequence(tag_sequence)
        if curr_bio_tag == "O" or curr_conll_tag in classes_to_ignore:
            if active_conll_tag is not None:
                spans.add((active_conll_tag, (span_start, span_end)))
            active_conll_tag = None
        elif _iob1_start_of_chunk(prev_bio_tag, prev_conll_tag, curr_bio_tag, curr_conll_tag):
            if active_conll_tag is not None:
                spans.add((active_conll_tag, (span_start, span_end)))
            active_conll_tag = curr_conll_tag
            span_start = index
            span_end = index
        else:
            span_end += 1

        prev_bio_tag = string_tag[0]
        prev_conll_tag = string_tag[2:]
    if active_conll_tag is not None:
        spans.add((active_conll_tag, (span_start, span_end)))
    return list(spans)


def _iob1_start_of_chunk(
    prev_bio_tag: Optional[str],
    prev_conll_tag: Optional[str],
    curr_bio_tag: str,
    curr_conll_tag: str,
) -> bool:
    if curr_bio_tag == "B":
        return True
    if curr_bio_tag == "I" and prev_bio_tag == "O":
        return True
    if curr_bio_tag != "O" and prev_conll_tag != curr_conll_tag:
        return True
    return False


def bioul_tags_to_spans(
    tag_sequence: List[str], classes_to_ignore: List[str] = None
) -> List[TypedStringSpan]:
    spans = []
    classes_to_ignore = classes_to_ignore or []
    index = 0
    while index < len(tag_sequence):
        label = tag_sequence[index]
        if label[0] == "U":
            spans.append((label.partition("-")[2], (index, index)))
        elif label[0] == "B":
            start = index
            while label[0] != "L":
                index += 1
                if index >= len(tag_sequence):
                    raise InvalidTagSequence(tag_sequence)
                label = tag_sequence[index]
                if not (label[0] == "I" or label[0] == "L"):
                    raise InvalidTagSequence(tag_sequence)
            spans.append((label.partition("-")[2], (start, index)))
        else:
            if label != "O":
                raise InvalidTagSequence(tag_sequence)
        index += 1
    return [span for span in spans if span[0] not in classes_to_ignore]


def iob1_to_bioul(tag_sequence: List[str]) -> List[str]:
    warnings.warn(
        "iob1_to_bioul has been replaced with 'to_bioul' to allow more encoding options.",
        FutureWarning,
    )
    return to_bioul(tag_sequence)


def to_bioul(tag_sequence: List[str], encoding: str = "IOB1") -> List[str]:
    if encoding not in {"IOB1", "BIO"}:
        raise ConfigurationError(f"Invalid encoding {encoding} passed to 'to_bioul'.")

    def replace_label(full_label, new_label):
        parts = list(full_label.partition("-"))
        parts[0] = new_label
        return "".join(parts)

    def pop_replace_append(in_stack, out_stack, new_label):
        new_tag = replace_label(tag, new_label)

    def process_stack(stack, out_stack):
        if len(stack) == 1:
            pop_replace_append(stack, out_stack, "U")
        else:
            recoded_stack = []
            pop_replace_append(stack, recoded_stack, "L")
            while len(stack) >= 2:
                pop_replace_append(stack, recoded_stack, "I")
            pop_replace_append(stack, recoded_stack, "B")

    bioul_sequence = []
    stack: List[str] = []

    for label in tag_sequence:

        if label == "O" and len(stack) == 0:
        elif label == "O" and len(stack) > 0:
            process_stack(stack, bioul_sequence)
            bioul_sequence.append(label)
        elif label[0] == "I":
            if len(stack) == 0:
                if encoding == "BIO":
                    raise InvalidTagSequence(tag_sequence)
            else:
                reveal_type(1])