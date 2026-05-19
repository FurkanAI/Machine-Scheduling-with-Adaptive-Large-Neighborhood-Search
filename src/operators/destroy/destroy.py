from src.operators.base_operator import Operator
import numpy as np


class Destroy(Operator):

    def apply(self, solution, problem, state, rng):
        raise NotImplementedError
    
    @staticmethod
    def fast_column_removal(arr: np.ndarray, indices_to_remove):

        if isinstance(indices_to_remove, int):
            indices_to_remove = [indices_to_remove]

        mask = np.ones(arr.shape[1], dtype=bool)
        mask[indices_to_remove] = False

        new_arr = arr[:, mask]
        removed_arr = arr[:, ~mask]

        return new_arr, removed_arr