
import numpy as np
from src.operators.destroy.destroy import Destroy


class ShawRemoval2(Destroy):
    def __init__(self):
        super().__init__("shaw_removal_2")

    def apply(self, solution, rng, problem=None, state=None):

        # Find the machines that are used
        used_machines = np.unique(solution.assignment_matrix[1,:])
        
        machine_to_remove_index = rng.choice(used_machines, size=1, replace=False)
        
        # Find the indices of jobs assigned to the machine with the minimum completion time
        removal_indices = np.where(solution.assignment_matrix[1, :] == (machine_to_remove_index))[0]
        
        # Remove the selected jobs from the solution
        updated_matrix, removed_jobs = self.fast_column_removal(solution.assignment_matrix, removal_indices)     
        
        return updated_matrix, removed_jobs


