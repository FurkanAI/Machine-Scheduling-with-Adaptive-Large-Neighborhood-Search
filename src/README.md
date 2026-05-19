# Adaptive Large Neighborhood Search (ALNS)

## Overview

This study implements an Adaptive Large Neighborhood Search (ALNS) algorithm combined with a Simulated Annealing (SA) acceptance mechanism for solving scheduling and assignment optimization problems.

The algorithm iteratively improves a solution by partially destroying the current solution and reconstructing it using repair heuristics. During the optimization process, operator performances are evaluated adaptively, allowing the algorithm to learn which operators are more effective for the problem.

The framework is modular and supports:
- destroy heuristics,
- repair heuristics,
- decoding procedures,
- custom objective functions.

---

# Methodology

The optimization process begins with an initial feasible solution. At each iteration, the algorithm:
1. Selects destroy and repair operators,
2. Removes part of the current solution,
3. Repairs the incomplete solution,
4. Decodes the candidate solution,
5. Evaluates the objective value,
6. Decides whether to accept the candidate solution,
7. Updates adaptive parameters and operator weights.

The process continues until the maximum iteration limit is reached.

---

# Simulated Annealing Acceptance Criterion

Improving solutions are always accepted. Non-improving solutions may also be accepted probabilistically to avoid premature convergence.

The acceptance probability is defined as:

\[
P(accept)=
\exp\left(
-\frac{
f(s_{candidate}) - f(s_{current})
}{
T
}
\right)
\]

where:
- \(f(s)\) is the objective function,
- \(T\) is the current temperature.

The temperature decreases during the optimization process according to:

\[
T_{new}=T_{old}\times\alpha
\]

where:
- \(T\) is the temperature,
- \(\alpha\) is the cooling factor.

---

# Adaptive Operator Learning

Destroy and repair operators are selected using adaptive weights. Operators generating high-quality solutions receive higher rewards, increasing their future selection probability.

This mechanism allows the algorithm to dynamically adapt its search strategy during optimization.

---

# Adaptive Removal Probabilities

The framework dynamically adjusts:
- job removal probability,
- server removal probability.

Higher removal probabilities encourage exploration, while lower probabilities intensify the search around promising regions.

---

# Objective Function

The framework assumes a scalar objective function:

\[
f(s)
\]

The objective may include multiple criteria such as:
- completion time,
- machine utilization,
- server utilization,
- workload balancing.

---

# Main Parameters

| Parameter | Description |
|---|---|
| `initial_temperature` | Initial simulated annealing temperature |
| `temperature_factor` | Cooling coefficient |
| `max_iterations` | Maximum iteration count |
| `initial_job_removal_prob` | Initial job removal probability |
| `last_job_removal_prob` | Final job removal probability |
| `initial_server_removal_prob` | Initial server removal probability |
| `last_server_removal_prob` | Final server removal probability |
| `operator_update_period` | Frequency of operator weight updates |

---

# Pseudocode

```text
Initialize current solution
Evaluate current solution
Set best solution = current solution

FOR each iteration:

    Select destroy operator
    Select repair operator

    Destroy current solution
    Repair destroyed solution

    Decode candidate solution
    Evaluate candidate solution

    IF candidate solution is accepted:
        Update current solution

        IF candidate solution is better than best solution:
            Update best solution

    Update temperature
    Update adaptive probabilities

    Periodically update operator weights

RETURN best solution
```

---
