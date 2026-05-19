import numpy as np
from src.operators.base_operator import Operator


class Repair(Operator):

    def apply(
        self,
        candidate_solution,
        destroyed_solution,
        removed_jobs,
        problem,
        config
    ):
        raise NotImplementedError
    
    @staticmethod
    def get_max_value_for_dtype(dtype):
        if np.issubdtype(dtype, np.integer):
            return np.iinfo(dtype).max
        elif np.issubdtype(dtype, np.floating):
            return np.inf
        else:
            raise TypeError("Undefined dtype.")