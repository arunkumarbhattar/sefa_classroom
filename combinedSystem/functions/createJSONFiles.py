import os
import re
import json

def findDirsWithoutJSON(HWDirectory): #Returns directories without JSON Files (returns theoretical path that includes JSON file for these directories)
	dirNames = []
	for roots, dirs, files in os.walk(HWDirectory, topdown = False): #Find all directories
		for dir in dirs:
			dirNames.append(dir)
	directoryFileFormat = re.compile(r"HW.*")
	HWDirNames = []
	for dir in dirNames: #Narrow directories down just to HW Names
		doesMatch = directoryFileFormat.match(dir)
		if(doesMatch != None):
			HWDirNames.append(doesMatch.group())
	pathOfJSONS = [dir + "/weights.json" for dir in HWDirNames]
	dirsWithoutJSON = []
	for dir in pathOfJSONS: #Get the final paths for directories that do not have JSON
		if(os.path.exists(HWDirectory + "/" + dir) == False):
			dirsWithoutJSON.append(HWDirectory + "/" + dir)
	return dirsWithoutJSON

def createJSONFiles(HWDirectory): # Uses findDirsWithoutJSON
	dirsWithoutJSON = findDirsWithoutJSON(HWDirectory)
	weightsDict = {}
	weightsDict["weights"] = []
	for num in range(1, 11):
		testDict = {}
		testElement = "test" + str(num)
		testDict[testElement] = [0.1]
		weightsDict["weights"].append(testDict)
	memDict = {}
	memElement = "mem_coeff"
	memDict[memElement] = [1]
	weightsDict["weights"].append(memDict)
	lateDict = {}
	lateElement = "late_coeff"
	lateDict[lateElement] = [5]
	weightsDict["weights"].append(lateDict)
	gradedDict = {}
	gradedElement = "graded_late_work"
	gradedDict[gradedElement] = [False]
	weightsDict["weights"].append(gradedDict)
	for dir in dirsWithoutJSON:
		with open(dir, "w") as f:
			json.dump(weightsDict, f)

def deleteSpecificJSONFiles(HWDirectory):
	dirNames = []
	for roots, dirs, files in os.walk(HWDirectory, topdown = False): #Find all directories
		for dir in dirs:
			dirNames.append(dir)
	directoryFileFormat = re.compile(r"HW.*")
	HWDirNames = []
	for dir in dirNames: #Narrow directories down just to HW Names
		doesMatch = directoryFileFormat.match(dir)
		if(doesMatch != None):
			HWDirNames.append(doesMatch.group())
	pathOfJSONS = [dir + "/weights.json" for dir in HWDirNames]
	for dir in pathOfJSONS:
		os.remove(HWDirectory + "/" + dir)
	print("Files Deleted")


def checkForJSONFile(HWDirectory):#Simple function to figure out which directories DO NOT have JSON Files
	dirsWithoutJSON = findDirsWithoutJSON(HWDirectory)
	if(dirsWithoutJSON != []):
		print("Warning! The following directories do not have a weights JSON File!")
		for dir in dirsWithoutJSON:
			print(str(dir))
	else:
		print("All files have their respective weights.json.")

#If you want to run this file by itself, this file automatically adds the pertinent information
HWDirectory = "../backend/TestCases/2020homeworks"
print(str(deleteSpecificJSONFiles(HWDirectory)))
