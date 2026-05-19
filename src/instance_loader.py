import json
from pathlib import Path


def load_instance(instance_path: str):

    instance_path = Path(instance_path)

    if not instance_path.exists():
        raise FileNotFoundError(f"❌ Instance file not found: {instance_path}")

    with open(instance_path, "r") as f:
        data = json.load(f)

    # -------------------------
    # REQUIRED FIELDS
    # -------------------------
    
    required_keys = ["total_jobs", "total_machines", "processing_times", "setup_times"]

    for key in required_keys:
        if key not in data:
            raise ValueError(f"❌ Missing required field in instance: {key}")

    total_jobs = data["total_jobs"]
    total_machines = data["total_machines"]
    processing = data["processing_times"]
    setup = data["setup_times"]

    # -------------------------
    # VALIDATION 
    # -------------------------

    if len(processing) != total_jobs:
        raise ValueError("❌ processing_times row count != total_jobs")

    if len(setup) != total_jobs:
        raise ValueError("❌ setup_times row count != total_jobs")

    for j in range(total_jobs):
        if len(processing[j]) != total_machines:
            raise ValueError(f"❌ processing_times[{j}] size mismatch")

        if len(setup[j]) != total_machines:
            raise ValueError(f"❌ setup_times[{j}] size mismatch")


    return {
        "total_jobs": total_jobs,
        "total_machines": total_machines,
        "processing_times": processing,
        "setup_times": setup
    }