
import numpy as np
from src.operators.destroy.destroy import Destroy

class BestBasedRemoval(Destroy):
    def __init__(self):
        super().__init__("best_based_removal")
    
    def apply(self, solution, problem, state, rng=None):

        # Calculate the number of jobs to remove
        remove_count = int(np.ceil(problem.total_jobs * state.job_removal_prob))
        
        # Calculate the difference in setup times between the current solution and the best solution
        # This will determine which jobs have the largest discrepancy in setup times
        diff_of_setup_times = problem.setup_times[solution.assignment_matrix[0,:] - 1, solution.assignment_matrix[1,:] - 1] - problem.setup_times[state.best_solution.assignment_matrix[0,:] - 1, state.best_solution.assignment_matrix[1,:] - 1]
        
        # Sort the jobs by the difference in setup times and select the jobs with the highest differences
        # The indices of the jobs to be removed are selected based on the largest differences
        removal_indices = np.argsort(diff_of_setup_times)[-remove_count:][::-1]
        
        # Remove the selected jobs from the solution
        updated_matrix, removed_jobs = self.fast_column_removal(solution.assignment_matrix, removal_indices)
        
        return updated_matrix, removed_jobs
