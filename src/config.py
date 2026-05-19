from dataclasses import dataclass, field, fields
import yaml
from pathlib import Path
import warnings
import numpy as np



def get_int(v, default, name):
    try:
        if isinstance(v, bool):
            raise ValueError
        return int(v)
    except:
        warnings.warn(f"[CONFIG] {name} invalid int: {v}. Using default {default}")
        return default
    

def get_float(v, default, name):
    try:
        if isinstance(v, bool):
            raise ValueError
        return float(v)
    except:
        warnings.warn(f"[CONFIG] {name} invalid float: {v}. Using default {default}")
        return default
    

def get_bool(v, default, name):
    if isinstance(v, bool):
        return v

    if isinstance(v, str):
        if v.lower() in ["true", "1", "yes"]:
            return True
        if v.lower() in ["false", "0", "no"]:
            return False

    if isinstance(v, int):
        if v in [0, 1]:
            return bool(v)

    warnings.warn(f"[CONFIG] {name} invalid bool: {v}. Using default {default}")
    return default

def get_prob(v, default, name):
    try:
        if isinstance(v, bool):
            raise ValueError

        v = float(v)

        if 0.0 <= v <= 1.0:
            return v

        raise ValueError

    except (TypeError, ValueError):
        warnings.warn(
            f"[CONFIG] {name} must be float in [0,1]. "
            f"Got {v}. Using default {default}"
        )
        return default



@dataclass
class ExperimentConfig:
    name: str = "default_experiment"


@dataclass
class InstanceConfig:
    path: str = "./instance.txt"


@dataclass
class ALNSConfig:
    max_iterations: int = 1000
    initial_temperature: float = 1000
    temperature_factor: float = 0.99
    operator_update_period: int = 50
    initial_job_removal_prob: float = 0.6
    last_job_removal_prob: float = 0.2
    initial_server_removal_prob: float = 0.2
    last_server_removal_prob: float = 0.2
    fixed_server_count: int | None = None


@dataclass
class GurobiConfig:
    use_gurobi_refinement: bool = False
    time_limit: int = 300


@dataclass
class WeightConfig:
    completion_times: float = 1.0
    server: float = 1.0
    machine: float = 1.0


@dataclass
class Objective:
    weights: WeightConfig = field(default_factory=WeightConfig)


@dataclass
class RandomConfig:
    seed: int = 42


@dataclass
class Config:

    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    instance: InstanceConfig = field(default_factory=InstanceConfig)
    alns: ALNSConfig = field(default_factory=ALNSConfig)
    gurobi_refinement: GurobiConfig = field(default_factory=GurobiConfig)
    objective: Objective = field(default_factory=Objective)
    random: RandomConfig = field(default_factory=RandomConfig)

    @classmethod
    def from_yaml(cls, path: str):

        # -----------------------
        # HARD FAIL: file missing
        # -----------------------
        if not Path(path).exists():
            raise FileNotFoundError(f"[CONFIG ERROR] Config file not found: {path}")

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}

            instance_data = data.get("instance")

            if instance_data is None or "path" not in instance_data:
                raise ValueError("[CONFIG ERROR] instance.path is required but missing")

            if not isinstance(instance_data["path"], str):
                raise ValueError("[CONFIG ERROR] instance.path must be a string")

            instance = InstanceConfig(path=instance_data["path"])


            alns = data.get("alns", {})
            gurobi = data.get("gurobi_refinement", {})
            decoder = data.get("schedule_decoder", {})
            objective = data.get("objective", {}).get("weights", {})
            random = data.get("random", {})

            return cls(

                experiment=ExperimentConfig(
                    name=data.get("experiment", {}).get("name", "default")
                ),

                instance=instance,

                alns=ALNSConfig(
                    max_iterations=get_int(alns.get("max_iterations"), 1000, "max_iterations"),
                    initial_temperature=get_float(alns.get("initial_temperature"), 1000.0, "initial_temperature"),
                    temperature_factor=get_float(alns.get("temperature_factor"), 0.99, "temperature_factor"),
                    operator_update_period=get_int(alns.get("operator_update_period"), 50, "operator_update_period"),

                    initial_job_removal_prob=get_prob(alns.get("initial_job_removal_prob"), 0.6, "initial_job_removal_prob"),
                    last_job_removal_prob=get_prob(alns.get("last_job_removal_prob"), 0.2, "last_job_removal_prob"),
                    initial_server_removal_prob=get_prob(alns.get("initial_server_removal_prob"), 0.2, "initial_server_removal_prob"),
                    last_server_removal_prob=get_prob(alns.get("last_server_removal_prob"), 0.2, "last_server_removal_prob"),

                    fixed_server_count=get_int(alns.get("fixed_server_count"), None, "fixed_server_count"),
                ),

                gurobi_refinement=GurobiConfig(
                    use_gurobi_refinement=get_bool(
                        gurobi.get("use_gurobi_refinement"),
                        False,
                        "use_gurobi_refinement"
                    ),
                    time_limit=get_int(gurobi.get("time_limit"), 600, "time_limit")
                ),

                objective=Objective(
                    weights=WeightConfig(
                        completion_times=get_float(objective.get("completion_times"), 1.0, "completion_times"),
                        server=get_float(objective.get("server"), 1.0, "server"),
                        machine=get_float(objective.get("machine"), 1.0, "machine"),
                    )
                ),

                random=RandomConfig(
                    seed=get_int(random.get("seed"), np.random.SeedSequence().entropy, "seed")
                )
            )

        except yaml.YAMLError as e:
            raise ValueError(f"[CONFIG ERROR] YAML parsing failed: {e}")

        except Exception as e:
            # safety net: unexpected crash
            raise RuntimeError(f"[CONFIG ERROR] Unexpected error while loading config: {e}")