import warnings
import numpy as np

from src.operators.repair.repair import Repair


class ShawInsertion(Repair):
    def __init__(self):
        super().__init__("shaw_insertion")

    def apply(self, candidate_solution, destroyed_solution, removed, problem, state, rng):

        try:
            # Find the unique machines used in the assigned jobs (removes duplicates)
            used_machines = np.unique(destroyed_solution[1,:])  # Get the unique machines used in the candidate solution
            # Create a mask for machines that are in use (True for used machines)
            mask = np.isin(np.arange(1, problem.total_machines+1), used_machines, assume_unique=True)
            
            # Identify machines that are not in use (free machines)
            free_machines = np.arange(1, problem.total_machines+1)[~mask]
            
            # If no free machines are available, assign jobs to the machine with the least completion time
            if free_machines.shape[0] == 0:
                # Initialize an array to store total completion times for each machine
                machine_completion_times = np.full(problem.total_machines, np.inf)

                total_time = 0
                previous_machine = destroyed_solution[1, 0]

                # Calculate the total completion time for each machine based on assigned jobs
                for job_id, machine_id in zip(destroyed_solution[0, :], destroyed_solution[1, :]):
                    if machine_id == previous_machine:
                        total_time += candidate_solution.completion_times[job_id - 1]
                    else:
                        machine_completion_times[previous_machine - 1] = total_time
                        total_time = candidate_solution.completion_times[job_id - 1]
                        previous_machine = machine_id
                
                # Set the last machine's total completion time
                machine_completion_times[previous_machine - 1] = total_time

                # Find the machine with the minimum total completion time
                assigned_machine_index = np.argmin(machine_completion_times[machine_completion_times > 0])
                
                # Append the jobs to the corresponding machine
                removed = np.hstack((removed[0,:], destroyed_solution[0,(destroyed_solution[1,:] == (assigned_machine_index+1))]))
                
                # Calculate total times (setup time + processing time) for the assigned job and machine
                total_times = problem.setup_times[removed-1,assigned_machine_index] + problem.processing_times[removed-1,assigned_machine_index]

                # Sort the assigned jobs based on total times (smallest time first)
                sorted_removed = removed[np.argsort(total_times)]      

                # Create a column with the sorted jobs and their corresponding machine ID
                assigned_job_machine_column = np.vstack((sorted_removed, (np.ones(sorted_removed.shape, dtype=sorted_removed.dtype.type)*(assigned_machine_index + 1))))
            
                # Find the first and last index of the machine in the candidate solution
                firs_index = np.where(destroyed_solution[1,:] == assigned_machine_index + 1)[0][0]
                last_index = np.where(destroyed_solution[1,:] == assigned_machine_index + 1)[0][-1]

                # Update candidate solution by inserting the sorted jobs into the appropriate position
                destroyed_solution = np.hstack((destroyed_solution[:,:firs_index], assigned_job_machine_column[:,:-1], destroyed_solution[:,last_index:]))   


            else:
                # If free machines are available, randomly select one to assign jobs
                assigned_machine_id = rng.choice(free_machines, size=1, replace=False)[0]  # Randomly select a free machine
                
                # Assign the jobs (jobs to be assigned are the ones from the candidate solution)
                removed = removed[0,:]
                
                # Calculate the total times for the selected jobs on the selected machine
                total_times = problem.setup_times[removed-1,assigned_machine_id-1] + problem.processing_times[removed-1,assigned_machine_id-1]

                # Sort the jobs based on total times (smallest time first)
                sorted_removed = removed[np.argsort(total_times)]      
                
                # Create a column with the sorted jobs and their corresponding machine ID
                assigned_job_machine_column = np.vstack((sorted_removed, (np.ones(sorted_removed.shape, dtype=np.int16)*(assigned_machine_id))))

                # Find the position in the solution array where the new machine should be inserted
                assigned_index = np.searchsorted(destroyed_solution[1,:], assigned_machine_id, side='left')
                
                # Insert the new jobs into the solution
                destroyed_solution = np.hstack((destroyed_solution[:,:assigned_index], assigned_job_machine_column, destroyed_solution[:, assigned_index:]))
        
            candidate_solution.assignment_matrix = np.copy(destroyed_solution)

        except Exception as e:
            warnings.warn(f"An error occurred during Shaw Insertion repair: {e}")
            return False

        return True

