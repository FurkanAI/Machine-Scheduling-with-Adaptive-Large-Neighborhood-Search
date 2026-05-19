import numpy as np
from itertools import permutations
import warnings

from src.decoders.base_decoder import Decoder


class V1Decoder(Decoder):

    def __init__(self, max_permutation_number=5):

        self.max_permutation_number = max_permutation_number

    def decode(
        self,
        solution,
        problem,
        rng
    ):

        try:
            # ----------------------------------------
            # Identify machine-job structure
            # ----------------------------------------
            machines, start_indices, job_counts = np.unique(
                solution.assignment_matrix[1, :],
                return_index=True,
                return_counts=True
            )

            machine_job_matrix = np.vstack((machines, start_indices, job_counts))


            if machines.size > self.max_permutation_number:
                machine_perm = rng.choice(machines, self.max_permutation_number, replace=False)
            else:
                machine_perm = machines.copy()

            machine_perm_list = list(permutations(machine_perm))
            machine_perm_array = np.array(machine_perm_list)

            # ----------------------------------------
            # Resource tracking arrays
            # ----------------------------------------
            T_k = np.zeros(solution.used_server_count)
            T_m = np.full(problem.total_machines, np.inf)

            # best solution.assignment_matrix tracking
            best_C = np.full(problem.total_jobs, np.inf)

            # ----------------------------------------
            # MAIN LOOP (permutation search)
            # ----------------------------------------
            for machine_order in machine_perm_array:

                # reset per permutation
                machine_job_matrix = np.vstack((machines, start_indices, job_counts))

                C_current = np.full(problem.total_jobs, np.inf)
                T_k.fill(0)
                T_m.fill(np.inf)

                T_m[machine_job_matrix[0] - 1] = 0

                # ----------------------------------------
                # Initial assignment phase
                # ----------------------------------------
                for machine_id in machine_order:

                    m_idx = machine_id - 1

                    mj_idx = np.where(machine_job_matrix[0, :] == machine_id)[0].item()
                    job_idx = solution.assignment_matrix[0, machine_job_matrix[1, mj_idx]] - 1

                    start_time = max(min(T_k), T_m[m_idx])

                    finish_time = (
                        start_time
                        + problem.setup_times[job_idx, m_idx]
                        + problem.processing_times[job_idx, m_idx]
                    )

                    C_current[job_idx] = finish_time

                    T_k[np.argmin(T_k)] = start_time + problem.setup_times[job_idx, m_idx]
                    T_m[m_idx] = finish_time

                    machine_job_matrix[2, mj_idx] -= 1
                    machine_job_matrix[1, mj_idx] += 1

                    zero_idx = np.where(machine_job_matrix[2, :] == 0)[0]

                    if zero_idx.size != 0:
                        machine_job_matrix[[1, 2], zero_idx] = -1
                        T_m[machine_job_matrix[0, zero_idx] - 1] = np.inf

                # ----------------------------------------
                # Remaining assignment phase
                # ----------------------------------------
                while np.count_nonzero(T_m == np.inf) != problem.total_machines:

                    m_idx = np.argmin(T_m)

                    mj_idx = np.where(machine_job_matrix[0, :] == m_idx + 1)[0].item()
                    job_idx = solution.assignment_matrix[0, machine_job_matrix[1, mj_idx]] - 1

                    start_time = max(min(T_k), T_m[m_idx])

                    finish_time = (
                        start_time
                        + problem.setup_times[job_idx, m_idx]
                        + problem.processing_times[job_idx, m_idx]
                    )

                    C_current[job_idx] = finish_time

                    T_k[np.argmin(T_k)] = start_time + problem.setup_times[job_idx, m_idx]
                    T_m[m_idx] = finish_time

                    machine_job_matrix[2, mj_idx] -= 1
                    machine_job_matrix[1, mj_idx] += 1

                    zero_idx = np.where(machine_job_matrix[2, :] == 0)[0]

                    if zero_idx.size != 0:
                        machine_job_matrix[[1, 2], zero_idx] = -1
                        T_m[machine_job_matrix[0, zero_idx] - 1] = np.inf

                # ----------------------------------------
                # Keep best permutation result
                # ----------------------------------------
                if C_current.sum() < best_C.sum():
                    best_C = C_current.copy()

            solution.completion_times = np.copy(best_C)
            
        except Exception as e:
            warnings.warn(f"An error occurred during decoding: {e}")
            return False

        return True
