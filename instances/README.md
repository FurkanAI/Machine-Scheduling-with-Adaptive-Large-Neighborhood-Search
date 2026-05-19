# Problem Instance Specification

This directory contains the problem instances for the Multi-Objective Machine Scheduling solver. The instances must be formatted as `.json` files and structured exactly as described below to be successfully parsed by the framework.

---

## JSON Schema Specification

Every instance file must contain the following keys:

| Key | Type | Description |
| :--- | :--- | :--- |
| `total_jobs` | `int` | Total number of tasks/jobs ($N$) to be scheduled. |
| `total_machines` | `int` | Total number of available machines ($M$). |
| `processing_times` | `List[List[int/float]]` | An $N \times M$ matrix where row $i$ defines the processing time of Job $i$ across all machines. |
| `setup_times` | `List[List[int/float]]` | An $N \times M$ matrix where row $i$ defines the setup time of Job $i$ across all machines. |

---

## Template Example

Below is the standard data layout for an instance with **3 jobs** and **3 machines**:

```json
{
  "total_jobs": 3,
  "total_machines": 3,
  "processing_times": [
    [10, 13, 15],
    [21, 6, 10],
    [35, 2, 23]
  ],
  "setup_times": [
    [4, 4, 5],
    [9, 1, 13],
    [15, 6, 17]
  ]
}
```