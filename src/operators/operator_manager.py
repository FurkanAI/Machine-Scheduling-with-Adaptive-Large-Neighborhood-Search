import numpy as np

class OperatorManager:

    def __init__(self):

        self.destroy_operators = []
        self.repair_operators = []

    def add_destroy(self, op):
        self.destroy_operators.append(op)

    def add_repair(self, op):
        self.repair_operators.append(op)

    def _select(self, operators, rng):
        weights = [op.weight for op in operators]
        p = np.array(weights) / np.sum(weights)
        return rng.choice(operators, p=p)

    def select_destroy(self, rng):
        return self._select(self.destroy_operators, rng)

    def select_repair(self, rng):
        return self._select(self.repair_operators, rng)

    def update_weights(self):
        for op in self.destroy_operators + self.repair_operators:
            op.update_weight()