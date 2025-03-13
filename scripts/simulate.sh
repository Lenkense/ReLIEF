#!/bin/bash
cd ../Toolbox2/
mvn package

mvn install:install-file -DgroupId=edu.uncu.itic -DartifactId=Toolbox2 -Dversion=0.0.1-SNAPSHOT -Dpackaging=jar -Dfile=../Toolbox2/target/Toolbox2-0.0.1-SNAPSHOT.jar

cd ../WorkflowsFramework/
mvn package

mvn install:install-file -DgroupId=edu.uncu.itic -DartifactId=WorkflowsFramework -Dversion=0.0.1-SNAPSHOT -Dpackaging=jar -Dfile=../WorkflowsFramework/target/WorkflowsFramework-0.0.1-SNAPSHOT.jar

cd ../AutoscalingWfRL/
mvn package

classpath="./target/classes"

OTHER_LIBS="./target/lib"

for i in `find $OTHER_LIBS -name '*.jar' | grep -v OLD`
do
	classpath=$classpath":"$i
done

echo "------------------- LIBRARIES ------------------"
echo $classpath
echo "------------------------------------------------"
echo

#merging cases
#cat cases*.csv > cases.csv

casesFile=$1

echo "#cases since experiments starting on `date`" >> failed_cases
echo "#" >> failed_cases

IFS=$'\n'
for caseParameters in `cat $casesFile | grep -v "^#"` #avoid comments      | grep -v "Inspiral_1000.xml" | grep -v "Montage_1000.xml"
do
	caseID=`echo $caseParameters | sed "s/\-//g" | sed "s/ //g"`
	matches=`cat executedExperiments | grep "$caseID" | wc -l`
	if [ "$matches" != "0" ]
	then
		#echo "> already executed case, skipping..."
		:
	else
		echo ""
		echo "*****"
		echo "STARTING SIMULATION: $caseParameters"
		echo "*****"
		counter=0
		while true; do
			let counter=counter+1
			echo "$counter:     $caseParameters" > try_number
			java -Xmx1024m -cp "$classpath" com.cloudautoscaling.experiments.StartSingleExperimentCase $caseParameters
			if [ "$?" = "0" ]; then
				echo $caseID >> executedExperiments
				break #if simulation was ok then break
			fi
			#check for too many tries, skip and register the failed case
			if [ "$counter" = "30" ]; then
				cat try_number >> failed_cases
				break #continue with other cases
			fi
		done
		rm try_number
		#mv sim_trace $logsDirectory/sim_trace-$executionNumber
		#mv sim_report $logsDirectory/sim_report-$executionNumber
	fi
	rm sim_trace 2> /dev/null
	rm sim_report 2> /dev/null

	echo "---"
	./scripts/show-progress.sh
	echo "---"
done

#rm cases.csv

echo "DONE"
