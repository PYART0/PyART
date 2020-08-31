import logging
from typing import List, Optional

from overrides import overrides
import torch

from allennlp.training.learning_rate_schedulers.learning_rate_scheduler import LearningRateScheduler


logger = logging.getLogger(__name__)


@LearningRateScheduler.register("slanted_triangular")
class SlantedTriangular(LearningRateScheduler):

    def __init__(
        self,
        optimizer: torch.optim.Optimizer,
        num_epochs: int,
        num_steps_per_epoch: Optional[int] = None,
        cut_frac: float = 0.1,
        ratio: int = 32,
        last_epoch: int = -1,
        gradual_unfreezing: bool = False,
        discriminative_fine_tuning: bool = False,
        decay_factor: float = 0.38,
    ) -> None:
        self.num_epochs = num_epochs
        self.num_steps_per_epoch = num_steps_per_epoch
        self.cut_frac = cut_frac
        self.ratio = ratio
        self.gradual_unfreezing = gradual_unfreezing
        self.freezing_current = self.gradual_unfreezing
        self.is_first_epoch = True
        self.batch_num_total_epoch_end: List[int] = []
        if self.gradual_unfreezing:
            assert not optimizer.param_groups[-1]["params"], "The default group should be empty."
        if self.gradual_unfreezing or discriminative_fine_tuning:
            assert len(optimizer.param_groups) > 2, (
                "There should be at least 3 param_groups (2 + empty default group)"
                " for gradual unfreezing / discriminative fine-tuning to make sense."
            )
        super().__init__(optimizer, last_epoch)
        self.step()
        if discriminative_fine_tuning:
            exponent = 0
            for i in range(len(self.base_values) - 1, -1, -1):
                param_group = optimizer.param_groups[i]
                if param_group["params"]:
                    param_group["lr"] = self.base_values[i] * decay_factor ** exponent
                    self.base_values[i] = param_group["lr"]
                    exponent += 1
        self.last_batch_num_total = -1
        self.step_batch(0)

    @overrides
    def step(self, metric: float = None) -> None:
        self.last_epoch += 1
        if len(self.batch_num_total_epoch_end) == 0:
            self.batch_num_total_epoch_end.append(0)
        else:
            self.batch_num_total_epoch_end.append(self.last_batch_num_total)

        if self.gradual_unfreezing:
            if self.is_first_epoch:
                num_layers_to_unfreeze = 1
                self.is_first_epoch = False
            else:
                num_layers_to_unfreeze = self.last_epoch + 1
            if num_layers_to_unfreeze >= len(self.optimizer.param_groups) - 1:
                logger.info("Gradual unfreezing finished. Training all layers.")
                self.freezing_current = False
            else:
                logger.info(
                    f"Gradual unfreezing. Training only the top {num_layers_to_unfreeze} layers."
                )
            for i, param_group in enumerate(reversed(self.optimizer.param_groups)):
                for param in param_group["params"]:
                    param.requires_grad = bool(i <= num_layers_to_unfreeze)

    def step_batch(self, batch_num_total: int = None):
        if batch_num_total is None:
            batch_num_total = self.last_batch_num_total + 1
        self.last_batch_num_total = batch_num_total
        reveal_type(self)