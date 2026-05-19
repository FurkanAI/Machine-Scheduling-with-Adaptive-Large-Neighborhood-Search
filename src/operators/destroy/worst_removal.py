import numpy as np
from src.operators.destroy.destroy import Destroy


class WorstRemoval(Destroy):
    def __init__(self):
        super().__init__("worst_removal")
    
    def apply(self, solution, problem, state, rng=None):
            
        # Calculate the number of jobs to remove
        remove_count = int(np.ceil(problem.total_jobs * state.job_removal_prob))
        
        # Calculate combined setup and processing times for each job
        durations = problem.setup_times[solution.assignment_matrix[0,:] - 1, solution.assignment_matrix[1,:] - 1] + problem.processing_times[solution.assignment_matrix[0,:] - 1, solution.assignment_matrix[1,:] - 1]
        
        # Sort by the longest durations and select the jobs to remove
        removal_indices = np.argsort(durations)[-remove_count:][::-1]
        
        # Remove the jobs from the solution
        updated_matrix, removed_jobs = self.fast_column_removal(solution.assignment_matrix, removal_indices)
        
        return updated_matrix, removed_jobs

