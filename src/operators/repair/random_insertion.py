import numpy as np
import warnings
from src.operators.repair.repair import Repair

class RandomInsertion(Repair):
    def __init__(self):
        super().__init__("random_insertion")

    def apply(self, candidate_solution, destroyed_solution, removed, problem, state, rng):
        
        try:
                # Get the number of assigned jobs
            removed_count = removed.shape[1]
            
            if removed_count != problem.total_jobs:
                
                # Randomly select indices to add (with replacement)
                removed_index = rng.choice(np.arange(0, problem.total_jobs - removed_count), size=removed_count, replace=True)

                # Iterate through each selected index and job
                for i, j in zip(removed_index, removed[0, :]):

                    # If the job is the first in the list, add it to the beginning of the solution
                    if i == 0:
                        # Randomly select a machine ID for the job
                        assigned_job_machine_id = rng.choice(np.arange(1, destroyed_solution[1, 0] + 1), size=1, replace=False)

                        # Create a column for the job assignment and add it to the beginning of the solution
                        assigned_job_machine_column = np.array([[j], assigned_job_machine_id]) 
                        destroyed_solution = np.hstack((assigned_job_machine_column, destroyed_solution))

                    # If the job is the last in the list, add it to the end of the solution
                    elif i == (problem.total_jobs - removed_count - 1):
                        # Randomly select a machine ID for the job
                        assigned_job_machine_id = rng.choice(np.arange(destroyed_solution[1, -1], problem.total_machines + 1), size=1, replace=False)

                        # Create a column for the job assignment and add it to the end of the solution
                        assigned_job_machine_column = np.array([[j], assigned_job_machine_id])
                        destroyed_solution = np.hstack((destroyed_solution, assigned_job_machine_column))

                    # For other jobs, add them between two existing machine assignments in the solution
                    else:
                        # Randomly select a machine ID for the job between the existing machine IDs

                        assigned_job_machine_id = rng.choice(np.arange(destroyed_solution[1, i - 1], destroyed_solution[1, i] + 1), size=1, replace=False)

                        # Create a column for the job assignment and add it to the solution
                        assigned_job_machine_column = np.array([[j], assigned_job_machine_id]) 
                        destroyed_solution = np.hstack((destroyed_solution[:, :i], assigned_job_machine_column, destroyed_solution[:, i:]))
            
            # if all candidate solution deleted =>
            else: 
                
                destroyed_solution = rng.choice(np.arange(1, problem.total_jobs+1), size=problem.total_jobs, replace=False)
                machines_ids = rng.choice(np.arange(1, problem.total_machines+1), size=problem.total_jobs, replace=True)
                destroyed_solution = np.vstack((destroyed_solution, machines_ids))
                sort_indices = np.argsort(destroyed_solution[1, :])
                destroyed_solution = destroyed_solution[:, sort_indices]

                candidate_solution.assignment_matrix = np.copy(destroyed_solution)
        
        except Exception as e:
            warnings.warn(f"An error occurred during Random Insertion repair: {e}")
            return False
        
        return True
