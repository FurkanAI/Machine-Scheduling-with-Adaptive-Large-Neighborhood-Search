import numpy as np
import json

def check_matrix(mat, row_count, colum_count, name):
    if not isinstance(mat, list):
        raise ValueError(f"[PROBLEM ERROR] {name} must be 2D list")

    if len(mat) != row_count:
        raise ValueError(
            f"[PROBLEM ERROR] {name} row mismatch: expected {row_count}, got {len(mat)}"
        )

    for i, row in enumerate(mat):
        if not isinstance(row, list):
            raise ValueError(f"[PROBLEM ERROR] {name}[{i}] must be list")

        if len(row) != colum_count:
            raise ValueError(
                f"[PROBLEM ERROR] {name}[{i}] col mismatch: expected {colum_count}, got {len(row)}"
            )


class Problem:

    def __init__(
        self,
        total_jobs: int,
        total_machines: int,
        processing_times: np.ndarray,
        setup_times: np.ndarray,
        instance_path: str | None = None
    ):

        self._total_jobs = total_jobs
        self._total_machines = total_machines

        self._processing_times = np.array(processing_times)
        self._processing_times.setflags(write=False)

        self._setup_times = np.array(setup_times)
        self._setup_times.setflags(write=False)

        self._instance_path = instance_path

        self._completion_time_normalization_factor = self.compute_completion_time_normalization_factor()
        self._used_machines_count_normalization_factor = self.compute_used_machines_count_normalization_factor()
        self._used_servers_count_normalization_factor = self.compute_used_servers_count_normalization_factor()

    @classmethod
    def from_json(cls, instance_path: str):

        with open(instance_path, "r") as file:
            data = json.load(file)

        return cls(
            total_jobs=data["total_jobs"],
            total_machines=data["total_machines"],
            processing_times=np.array(data["processing_times"]),
            setup_times=np.array(data["setup_times"]),
            instance_path=instance_path
        )
    
    @classmethod
    def from_json(cls, instance_path: str):


        with open(instance_path, "r") as file:
            data = json.load(file)

        # -----------------------
        # REQUIRED FIELDS CHECK
        # -----------------------
        if "total_jobs" not in data or "total_machines" not in data:
            raise ValueError("[PROBLEM ERROR] total_jobs or total_machines missing")

        if "processing_times" not in data or "setup_times" not in data:
            raise ValueError("[PROBLEM ERROR] processing_times or setup_times missing")

        total_jobs = data["total_jobs"]
        total_machines = data["total_machines"]

        processing_times = data["processing_times"]
        setup_times = data["setup_times"]


        if not isinstance(total_jobs, int) or total_jobs <= 0:
            raise ValueError("[PROBLEM ERROR] total_jobs must be positive int")

        if not isinstance(total_machines, int) or total_machines <= 0:
            raise ValueError("[PROBLEM ERROR] total_machines must be positive int")

        check_matrix(processing_times, total_jobs, total_machines, "processing_times")
        check_matrix(setup_times, total_jobs, total_machines, "setup_times")


        return cls(
            total_jobs=total_jobs,
            total_machines=total_machines,
            processing_times=np.array(processing_times),
            setup_times=np.array(setup_times),
            instance_path=instance_path
        )


    def compute_completion_time_normalization_factor(self):

        avg_processing_time = np.mean(self.processing_times + self.setup_times)

        beta = int(2 * self.total_jobs / self.total_machines + 1)

        return (self.total_jobs / beta) * sum(
            (i * avg_processing_time for i in range(1, beta + 1))
        )

    def compute_used_machines_count_normalization_factor(self):

        return self.total_machines

    def compute_used_servers_count_normalization_factor(self):

        return self.total_machines

    @property
    def total_jobs(self):
        return self._total_jobs

    @property
    def total_machines(self):
        return self._total_machines

    @property
    def processing_times(self):
        return self._processing_times

    @property
    def setup_times(self):
        return self._setup_times

    @property
    def instance_path(self):
        return self._instance_path

    @property
    def completion_time_normalization_factor(self):
        return self._completion_time_normalization_factor

    @property
    def used_machines_count_normalization_factor(self):
        return self._used_machines_count_normalization_factor

    @property
    def used_servers_count_normalization_factor(self):
        return self._used_servers_count_normalization_factor