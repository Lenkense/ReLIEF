# ReLIEF
ReLIEF: Reinforcement Learning Initialization by Evolutionary Formulation. 

This project contains the runnable code for the experiments of the work "ReLIEF: Reinforcement Learning Initialization by Evolutionary Formulation: Application for workflow autoscaling in the Cloud".

## Abstract

Workflow technologies are useful tools for handling scientific applications. Usually, workflows use Cloud Computing to satisfy resource requirements. However, Cloud performance variability requires proper scheduling schemes for efficient and cheap execution. In this sense, Reinforcement Learning, (RL) has been used to generate autoscaling agents for scientific workflow execution. RL is a versatile technique for the problem, but can present low-quality performance due to unfit initialization. Here, we present ReLIEF: Reinforcement Learning Initialization by Evolutionary Formulation, a novel initialization for RL-based autoscaling agents that uses evolutionary algorithms, (EAs). First, an initial RL policy is generated via EAs. Later, the initial policy is fed into an RL environment for further refining. Four benchmark workflows were used for assessing performance during training of the new agents producing savings in monetary cost and execution time (i.e. makespanH). In most cases (3/4 workflows) EA-based strategies outperform the non initialized RL-based strategy used as baseline with gains between 3.82 - 38.12% considering makespan and cost aggregated. Only one workflow presents a loss of 0.81\%, along with a significant gain of 14.09% in terms of makespan. Interestingly, this proposal provides a novel initialization for RL algorithms that can also be used in areas outside of workflow execution.

## Contact Information

* Luciano Robino ([lrobino@conicet.gov.ar](mailto:lrobino@conicet.gov.ar))
* Yisel Garí ([ygari@uncu.edu.ar](mailto:ygari@uncu.edu.ar))
* Elina Pacini ([epacini@uncu.edu.ar](mailto:epacini@uncu.edu.ar))
* Cristian Mateos ([cristian.mateos@isistan.unicen.edu.ar](mailto:cristian.mateos@isistan.unicen.edu.ar))
* Virginia Yannibelli ([virginia.yannibelli@isistan.unicen.edu.ar](mailto:virginia.yannibelli@isistan.unicen.edu.ar))
* David A. Monge ([dmonge@uncu.edu.ar](mailto:dmonge@uncu.edu.ar))

## How to run the code

To reproduce the experiments, please use the following entry-point script and command:

```
bash scripts/run.sh
```

The output of the experiments will be placed in the following folder:

```
results/
```

### Output

```
1.training_results_experiments.csv
summary.csv
Table3.csv
Table4.csv
trainingInfo.csv
<metric>_<workflow>_<epsilon>_<algorithm>.pdf
<metric>_<workflow>_<epsilon>_relative_<algorithm>.pdf
<metric>_<workflow>_<epsilon>_learning_curve.pdf
trajectories_<workflow>_exponential_<epsilon>_linear_avg.pdf
```

Where the possible values are:
```
<metric> ::== aggMC | makespan | totalCost | totalReward
<workflow> ::== CyberShake-100 | LIGO-100 | Montage-100 | SIPHT-97
<epsilon> ::== 0.0 | 0.1
<algorithm> ::== QLNSGAIII | QLDBEA
```

## Project Structure

```
configurations               # Configuration files for MOEA CLI tools and RL environment
data/instances               # VM info
libs                         # Library dependencies (JAR format)
logs                         # Empty path where logs will be saved (required)
scripts                      # Python and bash script for automation
target                       # compiled files from code
tmp                          # Empty path for temporary files (required for restart from incomplete execution)
workflows                    # Workflow information
README.md                    # This file
moeaframework.properties     # Additional properties for MOEA (LIGO does not present trade-off between objectives)
```

## Execution details and used libraries


The experiments reported in the paper were run on 2 virtual nodes of TOKO with AMD Epyc 7281 con 16 cores, 32 logical processors, 128GB of RAM running Slackware Linux 14.0 and Java version 17. The description of the four workflows studied are available on-line through the Pegasus WorkflowGenerator: [https://confluence.pegasus.isi.edu/display/pegasus/WorkflowHub](https://confluence.pegasus.isi.edu/display/pegasus/WorkflowHub). The implementation of the evolutionary
algorithms was provided by MOEA Framework version 4.5 \footnote{MOEA: \url{https://moeaframework.org/}}. The implementation of the Q-learning and SARSA algorithms was provided by the Brown-UMBC Reinforcement Learning and Planning (BURLAP) [http://burlap.cs.brown.edu/](http://burlap.cs.brown.edu/) Java code library version 3.0. Simulations were performed using the CloudSimPlus [https://cloudsimplus.org/](https://cloudsimplus.org/) simulator version 7.2.0. For the python3 libraries used the following dependencies are mandatory
```
matplotlib   3.2.2
pandas       1.5.3
scipy        1.10.1
seaborn      0.12.2
```
* ScyPy: [https://scipy.org/](https://scipy.org/)
* Matplotlib: [https://matplotlib.org/](https://matplotlib.org/)
* Seaborn: [https://seaborn.pydata.org/](https://seaborn.pydata.org/)
* Pandas: [https://pandas.pydata.org/](https://pandas.pydata.org/)
