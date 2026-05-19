import warnings
import numpy as np
from src.operators.repair.repair import Repair

class SimpleInsertion(Repair):
    
    def __init__(self):
        super().__init__("simple_insertion")

    def apply(self, candidate_solution, destroyed_solution, removed, problem, state, rng):

        try:
            # Find the unique machines used in the assigned jobs (removes duplicates)
            used_machines = np.unique(destroyed_solution[1,:])  # Get unique machine IDs used in the candidate solution
            
            # Create a mask for machines that are in use (True for used machines)
            mask = np.isin(np.arange(1, problem.total_machines+1), used_machines, assume_unique=True)  # True for machines in use
            
            # Calculate setup times for the assigned jobs on each machine
            removed_setup_time = problem.setup_times[removed[0,:]-1,:]  # Setup times for the jobs

            # Mask the setup times for unused machines as np.inf (so they won't be selected)
            removed_setup_time[:,~mask] = self.get_max_value_for_dtype(removed_setup_time.dtype)  # Set unused machines' setup times to a large value
            # Assign jobs to machines based on the minimum setup time
            assigned_machine_indices = np.argmin(removed_setup_time, axis=1)  # Find the machine with the minimum setup time
            assigned_machine_ids = assigned_machine_indices + 1  # Adjust machine index to be 1-based
            
            if used_machines.size != 0:
                # Loop through each job and assign it to the corresponding machine
                for i in zip(removed[0,:], assigned_machine_ids):

                    # Find the first and last index of the machine in the candidate solution
                    firs_index = np.where(destroyed_solution[1,:] == i[1])[0][0]  # Find the first occurrence of the machine
                    last_index = np.where(destroyed_solution[1,:] == i[1])[0][-1]  # Find the last occurrence of the machine

                    # Randomly select a position between the first and last index of the machine to insert the job
                    assigned_index = rng.choice(np.arange(firs_index, last_index + 1), size=1, replace=False)[0]  # Randomly choose a position

                    # Create a column array for the job and its assigned machine
                    assigned_job_machine_column = np.vstack((i[0], i[1]))  # Stack job and machine into a column

                    # Update candidate solution by inserting the new job into the appropriate position
                    destroyed_solution = np.hstack((destroyed_solution[:,:assigned_index], assigned_job_machine_column, destroyed_solution[:,assigned_index:]))  # Insert the job at the selected position
            else:
                
                destroyed_solution = np.vstack((removed[0,:], assigned_machine_ids))
                
                # Sort the solution based on the machine assignments (to maintain a consistent order)
                sorted_indices = np.argsort(destroyed_solution[1, :])
                destroyed_solution = destroyed_solution[:, sorted_indices]  # Reorder columns
            
            candidate_solution.assignment_matrix = np.copy(destroyed_solution)

        except Exception as e:
            warnings.warn(f"An error occurred during Simple Insertion repair: {e}")
            return False
        
        return True

