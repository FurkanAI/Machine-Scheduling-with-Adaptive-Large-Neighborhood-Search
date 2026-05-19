# Adaptive Large Neighborhood Search for Machine Scheduling

This repository contains the core function implementations for an Adaptive Large Neighborhood Search (ALNS) approach to a machine scheduling problem with setup times, processing times, and server constraints.

The project uses an Adaptive Large Neighborhood Search (ALNS) framework as the primary optimization method.

Additionally, an optional Gurobi refinement stage can be applied after the ALNS phase.

The framework is configuration-driven and supports experiment management, result exporting, and schedule visualization.

In the considered problem:

- Each job can be assigned to any machine.
- Processing times are machine-dependent.
- Setup times are also machine-dependent.
- Setup operations require server resources.
- Servers are released after setup completion and are not needed during processing.


## The Objective

The optimization objective is to minimize a weighted combination of:

- Total job completion times
- Number of used machines
- Number of used servers

$$
\min \left(
w_c \sum C_j
+
w_m M
+
w_s S
\right)
$$

where:

- \( \sum C_j \) : total completion times
- \( M \) : number of used machines
- \( S \) : number of used servers
- \( w_c, w_m, w_s \) : objective weights

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Prepare a problem instance in the `instances/` directory.
    - There are 5 example problems.

2. Set the experiment configuration in `config.yaml`:
   - exexperiment name
   - instance path
   - ALNS parameters
   - objective weights
   - Gurobi refinement options
   - random seed

3. Run the project:

```bash
python main.py
```

4. After the optimization process is completed, result files and generated visualizations will be available in the results/ directory.

##  Repository Structure

```text
parallel-machine-scheduling-alns/
│
├── config.yaml                 # Experiment configuration
├── requirements.txt            # Project dependencies
├── .gitignore
├── README.md
│
├── instances/                  # Problem instances (.json)
│   └── README.md
│
├── src/
│   ├── decoders/               # Schedule decoders
│   ├── operators/              # ALNS operators
│   ├── __init__.py
│   ├── alns.py                 # ALNS framework
│   ├── config.py               # Config loading and validation
│   ├── gurobi_refinement.py    # Gurobi refinement phase
│   ├── instance_loader.py      # Instance loading
│   ├── objective.py            # Objective function
│   ├── problem.py              # Problem definition
│   ├── result_saver.py         # Result exporting
│   └── solution.py             # Solution representation
│
└── results/                    # Saved results and visualizations
    └── README.md
```