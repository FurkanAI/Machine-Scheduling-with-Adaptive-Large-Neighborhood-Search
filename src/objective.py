import numpy as np


class Objective:

    @staticmethod
    def compute(solution, problem, config):

        completion_times_cost = config.objective.weights.completion_times * np.sum(solution.completion_times) / problem.completion_time_normalization_factor 

        used_machines_cost = config.objective.weights.machine * solution.used_machine_count / problem.used_machines_count_normalization_factor

        used_servers_cost = config.objective.weights.server * solution.used_server_count / problem.used_servers_count_normalization_factor

        return (completion_times_cost + used_machines_cost + used_servers_cost)
    
    @staticmethod
    def compute_seperate(solution, problem, config):

        completion_times_cost = config.objective.weights.completion_times * np.sum(solution.completion_times) / problem.completion_time_normalization_factor 

        used_machines_cost = config.objective.weights.machine * solution.used_machine_count / problem.used_machines_count_normalization_factor

        used_servers_cost = config.objective.weights.server * solution.used_server_count / problem.used_servers_count_normalization_factor

        return (completion_times_cost, used_machines_cost, used_servers_cost)
