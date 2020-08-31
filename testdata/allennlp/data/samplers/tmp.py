from typing import List, Iterable
from torch.utils import data

from allennlp.common.registrable import Registrable



class Sampler(Registrable):

    def __iter__(self) -> Iterable[int]:

        raise NotImplementedError


class BatchSampler(Registrable):

    def __iter__(self) -> Iterable[List[int]]:

        raise NotImplementedError


class SequentialSampler(data.SequentialSampler, Sampler):

    def __init__(self, data_source: data.Dataset):
        super().__init__(data_source)


@Sampler.register("random")
class RandomSampler(data.RandomSampler, Sampler):

    def __init__(
        self, data_source: data.Dataset, replacement: bool = False, num_samples: int = None
    ):
        super().__init__(data_source, replacement, num_samples)


@Sampler.register("subset_random")
class SubsetRandomSampler(data.SubsetRandomSampler, Sampler):

    def __init__(self, indices: List[int]):
        super().__init__(indices)


@Sampler.register("weighted_random")
class WeightedRandomSampler(data.WeightedRandomSampler, Sampler):

    def __init__(self, weights: List[float], num_samples: int, replacement: bool = True):
        super().__init__(weights, num_samples, replacement)
reveal_type(BatchSampler)