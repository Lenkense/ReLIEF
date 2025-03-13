#!/usr/bin/env bash

NCORES=$1
WORKFLOWS=( CyberShake_100.xml Inspiral_100.xml Montage_100.xml Sipht_100.xml )
ALGORITHMS=( NSGAIII DBEA )

# Parameter optimization
for WORKFLOW in ${WORKFLOWS[@]}; do
    bash ./scripts/tune-moea-case.sh EvolutiveScaling-${WORKFLOW}-1-10100-0 ${NCORES}
    # get params from the previous execution, tweek previous files for input output handling
done

JAVA_CMD=java
if [ ! -z $JAVA_HOME ]; then
	echo "Using JAVA_HOME = $JAVA_HOME"
	JAVA_CMD=$JAVA_HOME/bin/java
fi
classpath="./target/classes"
OTHER_LIBS="./target/lib"
for i in `find $OTHER_LIBS -name '*.jar' | grep -v OLD`; do   classpath=$classpath":"$i; done
JAVA_ARGS="-cp ${classpath} -Xmx512m "
set -e

# Evaluate all algorithms for all seeds
FILE_CASES="casesEvaluatorFinal.csv"
if [ -e ${FILE_CASES} ]; then
    rm -rf ${FILE_CASES}
fi
touch ${FILE_CASES}
for ALGORITHM in ${ALGORITHMS[@]}
do
	echo "Evaluating final seed"
    for WORKFLOW in ${WORKFLOWS[@]}; do
        SEED=31
		FINAL_PROBLEM="EvolutiveScaling-"${WORKFLOW}"-30-10100-0"
		echo "-p configurations/"${ALGORITHM}"_Params -i configurations/"${ALGORITHM}"_"${FINAL_PROBLEM}" -b "${FINAL_PROBLEM}" -a "${ALGORITHM}" -s "${SEED}" -o "${ALGORITHM}"_"${FINAL_PROBLEM}"_"${SEED}".set -x operator=ux+bf" >> ${FILE_CASES}
		echo "done."
	done
done
python3 scripts/simulate-saltelli.py ${NCORES} ${FILE_CASES}

# Generating cases for execution
$JAVA_CMD $JAVA_ARGS com.cloudautoscaling.experiments.generation.GenerateCases_RL

# run baseline
python3 scripts/simulate.py ${NCORES} casesEV+RL_train.csv

# parsing solutions to QTables
$JAVA_CMD $JAVA_ARGS com.cloudautoscaling.autoscaling.strategies.evolutive.scaling.Parser

# run evolutionary
python3 scripts/simulate.py ${NCORES} casesEV+RL_evotrain.csv

# running scripts for analysis
python3 scripts/learning_curves.py results/1.training_results_experiments.csv
python3 scripts/differences_curves.py results/1.training_results_experiments.csv
python3 scripts/generate_autoscaling_trajectories.py results/1.training_results_experiments.csv
