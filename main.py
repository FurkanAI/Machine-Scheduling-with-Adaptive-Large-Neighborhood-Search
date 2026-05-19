import numpy as np
from pathlib import Path

from src.operators.repair.repair import Repair
from src.config import Config
from src.problem import Problem
from src.solution import Solution
from src.alns import ALNS
from src.decoders.v1_decoder import V1Decoder
from src.objective import Objective
from src.operators.operator_manager import OperatorManager
from src.result_saver import ResultSaver
from src.gurobi_refinement import GurobiRefiner


from src.operators.destroy.best_based_removal import BestBasedRemoval
from src.operators.destroy.shaw_removal import ShawRemoval
from src.operators.destroy.shaw_removal_2 import ShawRemoval2
from src.operators.destroy.worst_removal import WorstRemoval
from src.operators.destroy.random_removal import RandomRemoval

from src.operators.repair.greedy_insertion import GreedyInsertion
from src.operators.repair.greedy_insertion_2 import GreedyInsertion2
from src.operators.repair.random_insertion import RandomInsertion
from src.operators.repair.shaw_insertion import ShawInsertion
from src.operators.repair.simple_insertion import SimpleInsertion


def main():

    # -------------------------
    # 1. PATHS
    # -------------------------
    BASE_DIR = Path(__file__).resolve().parent

    config_path = BASE_DIR / "config.yaml"

    # -------------------------
    # 2. CONFIG
    # -------------------------
    config = Config.from_yaml(config_path)

    # -------------------------
    # 3. PROBLEM
    # -------------------------
    problem = Problem.from_json(config.instance.path)

    # -------------------------
    # 4. RNG
    # -------------------------
    rng = np.random.default_rng(config.random.seed)

    # -------------------------
    # 5. DECODER
    # -------------------------
    decoder = V1Decoder()

    # -------------------------
    # 6. OBJECTIVE
    # -------------------------
    objective = Objective()

    # -------------------------
    # 7. INITIAL SOLUTION
    # -------------------------
    initial_solution = Solution.generate_initial_solution(problem, decoder, config, rng)
    initial_solution.cost = objective.compute(initial_solution, problem, config)

    # -------------------------
    # 8. OPERATORS
    # -------------------------
    operator_manager = OperatorManager()

    # Adding destroy operators
    operator_manager.add_destroy(RandomRemoval())
    operator_manager.add_destroy(WorstRemoval())
    operator_manager.add_destroy(ShawRemoval())
    operator_manager.add_destroy(ShawRemoval2())
    operator_manager.add_destroy(BestBasedRemoval())

    # Adding repair operators
    operator_manager.add_repair(RandomInsertion())
    operator_manager.add_repair(ShawInsertion())
    operator_manager.add_repair(GreedyInsertion())
    operator_manager.add_repair(GreedyInsertion2())
    operator_manager.add_repair(SimpleInsertion())
     

    # -------------------------
    # 9. ALNS
    # -------------------------
    alns = ALNS(
        problem=problem,
        config=config,
        operator_manager=operator_manager,
        decoder=decoder,
        objective=objective,
        rng=rng
    )


    # -------------------------
    # 10. RUN
    # -------------------------

    alns.run(initial_solution)

    # -------------------------
    # 11 Gurobi refinement
    # -------------------------
    gurobi_refinement = GurobiRefiner(config=config)
    if config.gurobi_refinement.use_gurobi_refinement:
        gurobi_refinement.refine(solution=alns.best_solution, problem=problem)

    # -------------------------
    # 12. Save Results
    # -------------------------
    result_saver = ResultSaver(file_name=config.experiment.name)
    result_saver.save(alns=alns, gurobi_refinement=gurobi_refinement, config=config, problem=problem)
    if gurobi_refinement.has_solution():
        result_saver.generate_gantt(solution=gurobi_refinement.best_solution, problem=problem)
    else:
        result_saver.generate_gantt(solution=alns.best_solution, problem=problem)
    
    print("Completed Successfuly.")

if __name__ == "__main__":
    main()