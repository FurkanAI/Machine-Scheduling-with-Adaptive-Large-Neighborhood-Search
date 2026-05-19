import numpy as np


class Solution:

    def __init__(
        self,
        assignment_matrix=None,
        used_server_count=None,
        completion_times=None,
        cost=None,
        fixed_server_count=None
    ):

        self.assignment_matrix = assignment_matrix

        self._used_server_count = used_server_count

        self.completion_times = completion_times

        self.cost = cost

        self.fixed_server_count = fixed_server_count


    @property
    def used_machine_count(self):
        return len(
            np.unique(self.assignment_matrix[1])
        )
    
    @property
    def used_server_count(self):

        if self.fixed_server_count is not None:
            return self.fixed_server_count

        return self._used_server_count
    
    @used_server_count.setter
    def used_server_count(self, value):
        if self.fixed_server_count is not None:
            self._used_server_count = self.fixed_server_count
        else:
            self._used_server_count = value
    

    @classmethod
    def generate_initial_solution(cls, problem, config, rng):
        
        assignment_matrix = np.arange(1, problem.total_jobs+1)
        rng.shuffle(assignment_matrix)
        assignment_matrix = np.insert(assignment_matrix, rng.integers(0, problem.total_jobs, problem.total_machines-1),-1)
        assignment_matrix = Solution.modify_solution(assignment_matrix)
        
        if config.alns.fixed_server_count is None:
            server_count = rng.choice(np.arange(1 , np.unique(assignment_matrix[1,:]).size + 1))
        else:
            server_count = config.alns.fixed_server_count

        
        initial_solution = cls(
            assignment_matrix=assignment_matrix, 
            used_server_count=server_count,
            fixed_server_count=config.alns.fixed_server_count
        )

        return initial_solution
    

    @classmethod
    def generate_initial_solution(cls, problem, decoder, config, rng):
        
        assignment_matrix = np.arange(1, problem.total_jobs+1)
        rng.shuffle(assignment_matrix)
        assignment_matrix = np.insert(assignment_matrix, rng.integers(0, problem.total_jobs, problem.total_machines-1),-1)
        assignment_matrix = Solution.modify_solution(assignment_matrix)
        
        if config.alns.fixed_server_count is None:
            server_count = rng.choice(np.arange(1 , np.unique(assignment_matrix[1,:]).size + 1))
        else:
            server_count = config.alns.fixed_server_count

        initial_solution = cls(
            assignment_matrix=assignment_matrix, 
            used_server_count=server_count,
            fixed_server_count=config.alns.fixed_server_count
        )

        decoder.decode(solution=initial_solution, problem=problem, rng=rng)

        return initial_solution


    @staticmethod
    def modify_solution(solution):
        """
        Modifies the solution by removing the -1 values (which represent machine transitions) and returns
        the updated solution along with the machine assignments for each job.
        """
        # Mask to exclude -1 values (machine transitions)
        mask = (solution != -1)
    
        # Filter out the jobs (excluding -1 values)
        valid_jobs = solution[mask]  

        # Track machine assignments based on transitions marked by -1
        machine_assignments = np.cumsum(solution == -1)  
        machine_assignments += 1  # Machine number starts from 1 instead of 0

        # Apply the mask to both jobs and machine assignments
        machines = machine_assignments[mask]
        jobs = valid_jobs

        # Combine jobs and machine assignments into a new solution matrix
        updated_solution = np.vstack((jobs, machines))
        
        return updated_solution