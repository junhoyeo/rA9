from collections import defaultdict


from copy import deepcopy
from itertools import chain
import jax.numpy as jnp

required = object()


class Optimizer(object):
    def __init__(self, params, defaults):
        self.state = defaultdict(dict)
        self.param_groups = list(params)
        if len(self.param_groups) == 0:
            raise ValueError('optimizer got an empty parameter list')
        if not isinstance(self.param_groups[0], dict):
            self.param_groups = [{'params': self.param_groups}]

        param_set = set()
        for group in self.param_groups:

            group['params'] = list(group['params'])
            group_set = set(group['params'])
            if not param_set.isdisjoint(group_set):
                raise ValueError('some parameters appear in more than one '
                                 'parameter group')
            param_set.update(group_set)

        for name, default in defaults.items():
            for i, group in enumerate(self.param_groups):
                if default is required and name not in group:
                    raise ValueError('parameter group ' + str(i) + ' didn't '
                                     'specify a value of required optimization parameter ' +
                                     name)
                else:
                    group.setdefault(name, default)

    def __getstate__(self):
        return {
            'state': self.state,
            'param_groups': self.param_groups,
        }

    def __setstate__(self, state):
        self.__dict__.update(state)

    def step(self, closure):
        raise NotImplementedError
