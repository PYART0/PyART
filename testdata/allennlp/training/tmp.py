from typing import Dict, Any

import torch


class Scheduler:

    def __init__(
        self, optimizer: torch.optim.Optimizer, param_group_field: str, last_epoch: int = -1
    ) -> None:
        self.optimizer = optimizer
        self.param_group_field = param_group_field
        self._initial_param_group_field = f"initial_{param_group_field}"
        if last_epoch == -1:
            for i, group in enumerate(self.optimizer.param_groups):
                if param_group_field not in group:
                    raise KeyError(f"{param_group_field} missing from param_groups[{i}]")
                group.setdefault(self._initial_param_group_field, group[param_group_field])
        else:
            for i, group in enumerate(self.optimizer.param_groups):
                if self._initial_param_group_field not in group:
                    raise KeyError(
                        f"{self._initial_param_group_field} missing from param_groups[{i}]"
                    )
        self.base_values = [
            group[self._initial_param_group_field] for group in self.optimizer.param_groups
        ]
        self.last_epoch = last_epoch

    def state_dict(self) -> Dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if key != "optimizer"}

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        self.__dict__.update(state_dict)

    def get_values(self):
        raise NotImplementedError

    def step(self, metric: float = None) -> None:
        self.last_epoch += 1
        self.metric = metric
        reveal_type(self)