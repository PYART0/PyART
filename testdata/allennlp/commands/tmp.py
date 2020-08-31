import argparse
import logging
import math
import os
import re
from typing import List, Tuple
import itertools

from overrides import overrides

from allennlp.commands.subcommand import Subcommand
from allennlp.common import Params, Tqdm
from allennlp.common import logging as common_logging
from allennlp.common.checks import check_for_gpu, ConfigurationError
from allennlp.common.util import prepare_environment
from allennlp.data import Vocabulary
from allennlp.data import DataLoader
from allennlp.models import Model
from allennlp.training import GradientDescentTrainer, Trainer
from allennlp.training.util import create_serialization_dir, datasets_from_params
reveal_type(Subcommand)