import warnings
import numpy as np
from src.operators.repair.repair import Repair


class GreedyInsertion2(Repair):
    def __init__(self):
        super().__init__("greedy_insertion_2")

    def apply(self, candidate_solution, destroyed_solution, removed, problem, state, rng):

        try:
            # Shuffle the jobs randomly
            shuffled_matrix = removed.T  # Transpose the matrix to shuffle columns
            rng.shuffle(shuffled_matrix)  # Shuffle the rows (jobs)
            removed = shuffled_matrix.T  # Transpose back to original shape
            
            # Find the unique machines used in the assigned jobs (removes duplicates)
            used_machines = np.unique(destroyed_solution[1,:])
            # Create a mask for machines that are in use (True for used machines)
            mask = np.isin(np.arange(1, problem.total_machines+1), used_machines, assume_unique=True)

            # Calculate total times (setup time + processing time) for each job on each machine
            total_times = problem.setup_times[removed[0,:]-1,:] + problem.processing_times[removed[0,:]-1,:]

            # Mask the total times of unused machines as np.inf (so they won't be selected)
            total_times[:,~mask] = self.get_max_value_for_dtype(total_times.dtype)  # Set unused machines' times to a large value

            # Assign jobs to machines based on the minimum total time
            assigned_job_machine_id = np.argmin(total_times, axis=1)  # Find the machine with the minimum time
            assigned_job_machine_id += 1  # Adjust the machine index (1-based)

            # Assign each job to a machine
            for i, j in zip(removed[0,:], assigned_job_machine_id):
                assigned_job_machine_column = np.array([[i], [j]])  # Create column for the assigned job and machine
                indices = np.where(destroyed_solution[1,:] == j)[0]  # Find indices of rows with the same machine

                if indices.shape[0] == 0:  # If no existing job assigned to this machine
                    # Add the job to the end of the solution
                    destroyed_solution = np.hstack((destroyed_solution, assigned_job_machine_column))
                else:
                    # If there is space, insert the job at the selected position
                    assigned_job_index = rng.choice(indices, size=1, replace=False)[0]  # Randomly select an index
                    destroyed_solution = np.hstack((destroyed_solution[:, :assigned_job_index], assigned_job_machine_column, destroyed_solution[:, assigned_job_index:]))        
            
            # Sort the solution based on the machine assignments (to maintain a consistent order)
            sorted_indices = np.argsort(destroyed_solution[1, :])
            destroyed_solution = destroyed_solution[:, sorted_indices]  # Reorder columns

            candidate_solution.assignment_matrix = np.copy(destroyed_solution)

        except Exception as e:
            warnings.warn(f"An error occurred in GreedyInsertion2 repair operator: {e}")
            return False

        return True