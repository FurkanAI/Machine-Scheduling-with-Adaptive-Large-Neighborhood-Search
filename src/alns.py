import math
import copy
import time
import warnings

class ALNSState:

    def __init__(self, config):

        self.temperature = config.alns.initial_temperature
        self.job_removal_prob = config.alns.initial_job_removal_prob
        self.server_removal_prob = config.alns.initial_server_removal_prob
        self.best_solution=None



class ALNS:

    def __init__(self, problem, config, operator_manager, decoder, objective, rng):

        self.problem = problem
        self.config = config
        self.operators = operator_manager
        self.decoder = decoder
        self.objective = objective
        self.rng = rng

        self.state = ALNSState(config)

        self.job_removal_prob_period = self.compute_job_removal_prob_period()
        self.server_removal_prob_period = self.compute_server_removal_prob_period()
        self.job_removal_prob_factor = self.compute_job_removal_prob_factor()
        self.server_removal_prob_factor = self.compute_server_removal_prob_factor()

        self.best_solution = None
        self.cost_history = []

        self.runtime = None

    def evaluate(self, solution):
        return self.objective.compute(solution, self.problem, self.config)

    def accept(self, candidate_cost, current_cost):

        if candidate_cost < current_cost:
            return True

        prob = math.exp(
            -(candidate_cost - current_cost) / self.state.temperature
        )

        return self.rng.random() < prob

    def compute_job_removal_prob_period(self):
        return (self.config.alns.max_iterations // abs((self.config.alns.last_job_removal_prob - self.config.alns.initial_job_removal_prob) // 0.1)) if self.config.alns.initial_job_removal_prob != self.config.alns.last_job_removal_prob else self.config.alns.max_iterations

    def compute_server_removal_prob_period(self):
        return (self.config.alns.max_iterations // abs((self.config.alns.last_server_removal_prob - self.config.alns.initial_server_removal_prob) // 0.1)) if self.config.alns.initial_server_removal_prob != self.config.alns.last_server_removal_prob else self.config.alns.max_iterations
    
    def compute_job_removal_prob_factor(self):
        if self.config.alns.initial_job_removal_prob > self.config.alns.last_job_removal_prob:
            return -0.1
        else:
            return 0.1
    
    def compute_server_removal_prob_factor(self):
        if self.config.alns.initial_server_removal_prob > self.config.alns.last_server_removal_prob:
            return -0.1
        else:
            return 0.1

    def update_temperature(self):
        self.state.temperature *= self.config.alns.temperature_factor

    def update_job_removal_prob(self, iteration):
        if iteration % self.job_removal_prob_period == 0:
            self.state.job_removal_prob += self.job_removal_prob_factor

    def update_server_removal_prob(self, iteration):
        if iteration % self.server_removal_prob_period == 0:
            self.state.server_removal_prob += self.server_removal_prob_factor

    def update_used_server_count(self, candidate_solution):
        if self.rng.random() < self.state.server_removal_prob:
            candidate_solution.used_server_count = self.rng.choice(range(1, candidate_solution.used_machine_count+1))

    def reward(self, operator, current_cost, candidate_cost, best_cost):

        if candidate_cost < best_cost:
            operator.add_reward(0.2)

        elif candidate_cost < current_cost:
            operator.add_reward(0.1)

        else:
            operator.add_reward(-0.1)

    def run(self, initial_solution):

        start_time = time.time()
        
        try:
            current_solution = copy.deepcopy(initial_solution)
            current_solution.cost = self.evaluate(current_solution)

            candidate_solution = copy.deepcopy(current_solution)

            self.state.best_solution = copy.deepcopy(current_solution)
            self.cost_history = [current_solution.cost]

            for it in range(self.config.alns.max_iterations):

                # 1. select operators
                destroy_op = self.operators.select_destroy(rng=self.rng)
                repair_op = self.operators.select_repair(rng=self.rng)

                # 2. destroy
                destroyed_solution, removed = destroy_op.apply(
                    solution=current_solution,
                    problem=self.problem,
                    state=self.state,
                    rng=self.rng
                )

                # 3. repair → candidate solution
                if not repair_op.apply(
                    candidate_solution=candidate_solution,
                    destroyed_solution=destroyed_solution,
                    removed=removed,
                    problem=self.problem,
                    state=self.state,
                    rng=self.rng
                ):
                    warnings.warn("Repair operator failed to produce a candidate solution. Skipping iteration.")
                    continue
                    
                self.update_used_server_count(candidate_solution)

                self.decoder.decode(solution=candidate_solution, problem=self.problem, rng=self.rng)

                # 4. evaluate candidate
                candidate_solution.cost = self.evaluate(candidate_solution)

                # 5. acceptance decision
                if self.accept(candidate_solution.cost, current_solution.cost):

                    current_solution = copy.deepcopy(candidate_solution)
                    # reward operators
                    self.reward(destroy_op, current_solution.cost, candidate_solution.cost, self.state.best_solution.cost)
                    self.reward(repair_op, current_solution.cost, candidate_solution.cost, self.state.best_solution.cost)

                    # update best
                    if candidate_solution.cost < self.state.best_solution.cost:
                        self.state.best_solution = copy.deepcopy(candidate_solution)

                # 6. update parameters
                self.update_temperature()
                self.update_job_removal_prob(it)
                self.update_server_removal_prob(it)

                # 7. periodic operator update
                if it % self.config.alns.operator_update_period == 0:
                    self.operators.update_weights()

                self.cost_history.append(current_solution.cost)
        
            self.best_solution = copy.deepcopy(self.state.best_solution)
            self.runtime = time.time() - start_time

        except Exception as e:
            print(destroyed_solution)
            print(removed)
            print(candidate_solution.assignment_matrix)
            print(destroy_op.name, repair_op.name)
            warnings.warn(f"An error occurred during ALNS execution: {e}")
            return False

        return True