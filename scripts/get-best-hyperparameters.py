import sys
import glob

def getIndexOfMaxHypervolume(resultsFilename):
	with open(resultsFilename, "r") as resultsFile:
		results = resultsFile.readlines()
		bestIndex = 0
		maxHypervolume = results[bestIndex].strip().split(" ")[0]
		for index in range(len(results)):
			#result = results[index].strip()
			hypervolume = results[index].strip().split(" ")[0]
			if hypervolume > maxHypervolume:
				maxHypervolume = hypervolume
				bestIndex = index
	resultsFile.close()	
	return bestIndex 

#read parameters
algorithmPrefix = sys.argv[1]
problem = sys.argv[2]

samplesFile = open("configurations/" + algorithmPrefix + "_saltelli", "r")
samples = samplesFile.readlines()
samplesFile.close()

# properties
case = algorithmPrefix + "_" + problem
index = getIndexOfMaxHypervolume(case + ".average")
params = samples[index].strip()
print(str(case) + ".index=" + str(index))
print(str(case) + ".params=" + params)
nextRun = open("configurations/" + case.replace("-1-","-30-"),"w")
nextRun.write(params)
nextRun.close()

