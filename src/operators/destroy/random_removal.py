import numpy as np

from src.operators.destroy.destroy import Destroy


class RandomRemoval(Destroy):

    def __init__(self):
        super().__init__("random_removal")

    def apply(self, solution, problem, state, rng):

        total_jobs = problem.total_jobs

        remove_count = int(
            np.ceil(total_jobs * state.job_removal_prob)
        )

        removal_indices = rng.choice(
            np.arange(0, total_jobs),
            size=remove_count,
            replace=False
        )

        updated_matrix, removed_jobs = self.fast_column_removal(
            solution.assignment_matrix,
            removal_indices
        )

        return updated_matrix, removed_jobs