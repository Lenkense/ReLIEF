#!/usr/bin/env bash

# Configuration

export $(cat configurations/config_tune.sh)
ALGORITHMS=( NSGAIII DBEA )
PROBLEM=$1
NCORES=$2

SEEDS=$(seq 1 ${NSEEDS})
JAVA_CMD=java
if [ ! -z $JAVA_HOME ]; then
	echo "Using JAVA_HOME = $JAVA_HOME"
	JAVA_CMD=$JAVA_HOME/bin/java
fi
classpath="./target/classes"
OTHER_LIBS="./target/lib"
for i in `find $OTHER_LIBS -name '*.jar' | grep -v OLD`; do   classpath=$classpath":"$i; done
JAVA_ARGS="-cp ${classpath} -Xmx512m -Dorg.moeaframework.core.suppress_truncation_warning=true"
set -e

# Deploy maven project
if [[ $* == *--skip-mvn-deploy* ]]
then
	echo -n "0) Skipping deployment of Maven project."
else
	echo -n "0) Deploying Maven project..."
	#scripts/mvn-deploy.sh
	echo "done."
fi


# Clear old data
echo -n "1) Clearing old data (if any)..."
#rm -f *_${PROBLEM}_*.set
rm -f *_${PROBLEM}_*.metrics
echo "done."


# Generate the parameter samples
echo -n "2) Generating parameter samples..."
for ALGORITHM in ${ALGORITHMS[@]}
do
	$JAVA_CMD ${JAVA_ARGS} org.moeaframework.analysis.tools.SampleGenerator -n $NSAMPLES -p configurations/${ALGORITHM}_Params -m ${METHOD} -s 1234 -o configurations/${ALGORITHM}_${METHOD}
done
echo "done."

PREFIX=""


# Evaluate all algorithms for all seeds
FILE_CASES="casesEvaluator.csv"
if [ -e ${FILE_CASES} ]; then
	rm -rf ${FILE_CASES}
fi
touch ${FILE_CASES}
for ALGORITHM in ${ALGORITHMS[@]}
do
	echo "3) Evaluating ${ALGORITHM}:"
	for SEED in ${SEEDS}
	do
		echo "-p configurations/"${ALGORITHM}"_Params -i configurations/"${ALGORITHM}"_"${METHOD}" -b "${PROBLEM}" -a "${ALGORITHM}" -s "${SEED}" -o "${ALGORITHM}"_"${PROBLEM}"_"${SEED}".set -x operator=ux+bf" >> ${FILE_CASES}
	done
done
python3 scripts/simulate-saltelli.py ${NCORES} ${FILE_CASES}


# Generate the combined approximation sets for each algorithm
for ALGORITHM in ${ALGORITHMS[@]}
do
	echo -n "4) Generating combined approximation set for ${ALGORITHM}..."
	$JAVA_CMD ${JAVA_ARGS} org.moeaframework.analysis.tools.ResultFileMerger -b ${PROBLEM} -o ${ALGORITHM}_${PROBLEM}.combined ${ALGORITHM}_${PROBLEM}_*.set
	echo "done."
done


# Generate the reference set from all combined approximation sets
echo -n "5) Generating reference set..."
$JAVA_CMD ${JAVA_ARGS} org.moeaframework.analysis.tools.ReferenceSetMerger -o ${PROBLEM}.reference *_${PROBLEM}.combined > /dev/null
echo "done."


# Evaluate the performance metrics
for ALGORITHM in ${ALGORITHMS[@]}
do
	echo "6) Calculating performance metrics for ${ALGORITHM}:"
	for SEED in ${SEEDS}
	do
		echo -n " Processing seed ${SEED}..."
		$JAVA_CMD ${JAVA_ARGS} org.moeaframework.analysis.tools.ResultFileEvaluator -b ${PROBLEM} -i ${ALGORITHM}_${PROBLEM}_${SEED}.set -r ${PROBLEM}.reference -o ${ALGORITHM}_${PROBLEM}_${SEED}.metrics
		echo "done."
	done
done


# Average the performance metrics across all seeds
for ALGORITHM in ${ALGORITHMS[@]}
do
	echo -n "7) Averaging performance metrics for ${ALGORITHM}..."
	$JAVA_CMD ${JAVA_ARGS} org.moeaframework.analysis.tools.SimpleStatistics -m average -o ${ALGORITHM}_${PROBLEM}.average ${ALGORITHM}_${PROBLEM}_*.metrics
	echo "done."
done


# Perform the analysis
echo ""
echo "8) Analysis:"
for ALGORITHM in ${ALGORITHMS[@]}
do
	$JAVA_CMD ${JAVA_ARGS} org.moeaframework.analysis.tools.Analysis -p configurations/${ALGORITHM}_Params -i configurations/${ALGORITHM}_${METHOD} -o ${ALGORITHM}_${PROBLEM}.analysis -m 1 ${ALGORITHM}_${PROBLEM}.average
done


# Calculate set contribution
echo ""
echo "9) Set contribution:"
$JAVA_CMD ${JAVA_ARGS} org.moeaframework.analysis.tools.SetContribution -r ${PROBLEM}.reference *_${PROBLEM}.combined 


# Calculate Sobol sensitivities
if [ ${METHOD} == "saltelli" ]
then
	for ALGORITHM in ${ALGORITHMS[@]}
	do
		echo ""
		echo "Sobol sensitivities for ${ALGORITHM}"
		$JAVA_CMD ${JAVA_ARGS} org.moeaframework.analysis.tools.SobolAnalysis -p configurations/${ALGORITHM}_Params -i ${ALGORITHM}_${PROBLEM}.average -o ${ALGORITHM}_${PROBLEM}.sobol -m 1
	done
fi

echo ""
echo "10) Generating files for final run"
for ALGORITHM in ${ALGORITHMS[@]}
do
    python3 ./scripts/get-best-hyperparameters.py ${ALGORITHM} ${PROBLEM}
done
