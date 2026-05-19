import warnings
import numpy as np
import time
from gurobipy import Model, GRB, quicksum, Env, GurobiError
from src.solution import Solution
from src.objective import Objective


class GurobiRefiner:

    def __init__(self, config):
        self.config = config
        self.time_limit = config.gurobi_refinement.time_limit
        self.verbose = False
        self.model = None
        self.best_solution = None
        self.status = None
        self.solution_count = None
        self.runtime = None
        self.constraint_time = None
        self.variable_assignment_time = None
        self.optimization_time = None
        

    @staticmethod
    def has_valid_gurobi_license() -> bool:

        try:
            with Env(empty=True) as env:
                env.setParam("OutputFlag", 0)
                env.start()

                with Model(env=env) as model:
                    x = model.addVar(lb=0.0, name="x")

                    model.setObjective(x, GRB.MAXIMIZE)
                    model.addConstr(x <= 1)

                    model.optimize()

                    return model.Status == GRB.OPTIMAL

        except GurobiError:
            return False

        except Exception:
            return False

    def has_solution(self):
        if self.best_solution is None:
            return False

        return True

    def refine(
        self,
        solution,
        problem
    ):
        if not self.has_valid_gurobi_license():
            warnings.warn("Gurobi license is not available. Skipping Gurobi refinement.")
            return False

        try:
            start_time = time.time()

            N = np.arange(1, problem.total_jobs + 1)
            L = np.arange(1, problem.total_machines + 1)
            Q = np.arange(1, solution.used_server_count + 1)

            p_j = np.zeros(shape=problem.total_jobs, dtype=problem.processing_times.dtype)
            s_j = np.zeros(shape=problem.total_jobs, dtype=problem.setup_times.dtype)
            x = np.zeros(shape=(problem.total_jobs, problem.total_jobs, problem.total_machines), dtype=np.int16)

            dummy = np.zeros(shape=problem.total_machines, dtype=np.int16)

            for i in zip(solution.assignment_matrix[0], solution.assignment_matrix[1]):
                j_index = i[0] - 1
                m_index = i[1] - 1

                p_j[j_index] = problem.processing_times[j_index, m_index]
                s_j[j_index] = problem.setup_times[j_index, m_index]

                x[j_index, dummy[m_index], m_index] = 1
                dummy[m_index] += 1

            M = np.max(p_j + s_j) * problem.total_jobs

            model = Model("gurobi_refinement")
            model.setParam("OutputFlag", 1 if self.verbose else 0)
            model.setParam("TimeLimit", self.time_limit)

            C = model.addVars(N, vtype=GRB.INTEGER, lb=0, name="C")
            z = model.addVars(N, vtype=GRB.INTEGER, lb=0, name="z")
            e = model.addVars(N, N, vtype=GRB.BINARY, name="e")
            w = model.addVars(N, Q, vtype=GRB.BINARY, name="w")

            model.setObjective(quicksum(C[j] for j in N), GRB.MINIMIZE)

            model.addConstrs(
                (C[j] >= s_j[j-1] + p_j[j-1]
                for j in N for l in L if x[j-1, 0, l-1] == 1),
                name="c1"
            )

            model.addConstrs(
                (C[j] >= C[i] + s_j[j-1] + p_j[j-1]
                for i in N for j in N for l in L for h in N
                if (h > 1 and i != j and
                    x[j-1, h-1, l-1] == 1 and
                    x[i-1, h-2, l-1] == 1)),
                name="c2"
            )

            model.addConstrs(
                (z[j] == C[j] - p_j[j-1] for j in N),
                name="c3"
            )

            model.addConstrs(
                (quicksum(w[j, q] for q in Q) == 1 for j in N),
                name="c4"
            )

            model.addConstrs(
                (e[i, j] + e[j, i] == 1 for j in N for i in N if i != j),
                name="c5"
            )

            model.addConstrs(
                (z[j] >= z[i] + s_j[j-1]
                - M * (3 - w[j, q] - w[i, q] - e[i, j])
                for i in N for j in N for q in Q if i != j),
                name="c6"
            )

            self.constraint_time = time.time() - start_time

            model.optimize()

            self.optimization_time = time.time() - start_time - self.constraint_time

            C_np = np.zeros(problem.total_jobs)

            if model.SolCount > 0:
                for j in N:
                    C_np[j - 1] = C[j].X

            
            self.variable_assignment_time = time.time() - start_time - self.constraint_time - self.optimization_time

            runtime = time.time() - start_time

            self.model = model
            self.status = model.Status
            self.solution_count = model.SolCount
            self.runtime = runtime

            self.best_solution = Solution()
            self.best_solution.assignment_matrix = solution.assignment_matrix
            self.best_solution.used_server_count = solution.used_server_count
            self.best_solution.fixed_server_count = solution.fixed_server_count
            self.best_solution.completion_times = C_np
            self.best_solution.cost = Objective.compute(solution=self.best_solution, problem=problem, config=self.config)
            

        except GurobiError as e:
            warnings.warn(f"Gurobi optimization error: {e}")
            return False
        except Exception as e:
            warnings.warn(f"An error occurred during Gurobi refinement: {e}")
            return False

        return True