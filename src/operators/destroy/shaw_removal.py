
import numpy as np
from src.operators.destroy.destroy import Destroy


class ShawRemoval(Destroy):
    def __init__(self):
        super().__init__("shaw_removal")
 
    def apply(self, solution, problem, state=None, rng=None):

        # Initialize an array to store total completion times for each machine
        machine_completion_times = np.full(problem.total_machines, np.inf)
        
        total_time = 0
        previous_machine = solution.assignment_matrix[1, 0]

        # Calculate the total completion time for each machine
        for job_id, machine_id in zip(solution.assignment_matrix[0, :], solution.assignment_matrix[1, :]):
            if machine_id == previous_machine:
                total_time += solution.completion_times[job_id - 1]
            else:
                machine_completion_times[previous_machine - 1] = total_time
                total_time = solution.completion_times[job_id - 1]
                previous_machine = machine_id
        
        # Set the last machine's total completion time
        machine_completion_times[previous_machine - 1] = total_time
        
        # Find the machine with the minimum total completion time
        machine_to_remove_index = np.argmin(machine_completion_times[machine_completion_times > 0])
        
        # Find the indices of jobs assigned to the machine with the minimum completion time
        removal_indices = np.where(solution.assignment_matrix[1, :] == (machine_to_remove_index + 1))[0]
        
        # Remove the selected jobs from the solution
        updated_matrix, removed_jobs = self.fast_column_removal(solution.assignment_matrix, removal_indices)
        
        return updated_matrix, removed_jobs

