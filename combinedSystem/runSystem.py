#!!--------Imports-----------!!
from functions.setup import getConfigInputs, argParse
from functions.fetch import fetchLists, fetchRepos, fetchHWInfo, fetchLimit, repo_has_tag
from functions.dataFrameHelper import updateDF, loadCSV, writeCSV
from functions.gradeProcess import cloneFromRepos, startGradingProcess, putGradesInRepos, putGradesInCSV, pushChangeToRepos
from functions.rmtree import rmtree

import argparse, os
from datetime import datetime
import sys
import pickle

#!!----------Static Variables------!!
tagName = "final_ver"
gradeFileName = "gradeReport.txt"
failedTestsDir = "/failed_testcases"
profDir = "/profFiles"
gradesDir = "/grades"
clonesDir = "/clones"
hwsDir = "/hws"

#!!----------Set Up File For Collecting Output------!!
outputFile = open('filteredOutput.txt', 'w')
outputFile.write("Ran on ")
outputFile.write(datetime.now().strftime("%m-%d %H:%M:%S") + "\n")

#!!----------Set Up Command Line Flag Input--------!!
parser = argparse.ArgumentParser("specify run options")
group = parser.add_mutually_exclusive_group()
group.add_argument("--hw_name", type = str, help= "specify the name of the homework to grade. example: python3 runSystem.py --hw_name hw02sort")
group.add_argument("--hw_range", type = str, nargs = 2, help = "specify a range of homeworks to grade. example: python3 runSystem.py --hw_range hw02sort hw04file")
group.add_argument("--grade_all", action="store_true", help = "specify this option to grade all homeworks. example: python3 runSystem.py --grade_all")
parser.add_argument("-d", "--delete", action ="store_true", help="specify this option if you would like to delete clones and grades folders after running. default is false")
parser.add_argument("-s", "--sanity", action="store_true", help = "specify this option to perform sanity check. example: python3 runSystem.py --hw_name hw02sort --sanity_check")
parser.add_argument("--config", type = str, nargs = 1, help = "specify the absolute path of a config.json file")
parser.add_argument("--grade_ceiling_list", type=str, nargs="+", help="specify a list of homeworks to grade. example: python3 runSystem.py --grade_ceiling_list hw_11 hw_12")

args = parser.parse_args()

if args.grade_ceiling_list and not args.grade_all:
    parser.error("--grade_ceiling_list requires --grade_all to be set to true")

[startIndex, endIndex, homeworkMasterList, configJSON, grade_ceiling_list] = argParse(args, profDir + hwsDir, profDir, outputFile)

#!!--------Set Up Variables From JSON File-----------!! 
#get variables from JSON config file
configInputs = getConfigInputs(configJSON)

#variables
organization =  configInputs["organization"]  #json file
authName = configInputs["authName"] #json file
authKey = configInputs["authKey"] #json file
repoFilter = configInputs.get("repoFilter", None) #json file

#!!----------Data Tracking for Development--------!!
[usedStart, remaining] = fetchLimit(authName, authKey) #Used for tracking requests, can be deleted
startTime = datetime.now()

#!!----------Run Actual System--------!!
if grade_ceiling_list:
    fetchRepo_file = "fetchRepo.pkl"
    filterRepo_file = "filterRepo.pkl"
    # Check if the fetchRepo.pkl file exists
    if os.path.exists(fetchRepo_file):
        # Load fetchRepo from the file
        with open(fetchRepo_file, "rb") as f:
            fetchRepo = pickle.load(f)
    else:
        # Fetch repos and store in the file
        fetchRepo = fetchRepos(organization, authName, authKey)
        with open(fetchRepo_file, "wb") as f:
            pickle.dump(fetchRepo, f)

    # Check if the filterRepo.pkl file exists
    if os.path.exists(filterRepo_file):
        # Load fetchRepo from the file
        with open(filterRepo_file, "rb") as f:
            filtered_repos = pickle.load(f)
    else:
        # Fetch repos and store in the file
        filtered_repos = [
            r for r in fetchRepo
            if any(hw in r["name"] for hw in grade_ceiling_list) and repo_has_tag(r, tagName, authName, authKey)
        ]
        with open(filterRepo_file, "wb") as f:
            pickle.dump(filtered_repos, f)

    [students, hws, repos] = fetchLists(filtered_repos, repoFilter)
else:
    [students, hws, repos] = fetchLists(fetchRepos(organization, authName, authKey), repoFilter)

num_graded = 0

if grade_ceiling_list:  # Check if grade_ceiling_list is provided
    df = loadCSV(os.getcwd() + profDir + "/masterGrades.csv") # Load the masterGrades.csv file as a DataFrame
    df_ceiling = df.copy()  # Create a copy of the df DataFrame
    df_ceiling['maxGrade'] = 0  # Add an extra column named "maxGrade" with default value 0

    # Update the "maxGrade" column with the ceiling grade information from grade_ceiling_list
    # Create a dictionary to store the submitted assignments count for each student
    submitted_assignments_count = {}

    # Iterate through filtered_repos list
    for repo in filtered_repos:
        Username = str(repo['name']).split('-')[-1]

        # Check if the assignment is HW13 or later and has "final_ver" tag
        if int(str(repo['name']).split('purdueece264-spring2023-')[1].split('-')[0][2:]) >= 13:
            if Username not in submitted_assignments_count:
                submitted_assignments_count[Username] = 0
            submitted_assignments_count[Username] += 1

    # Update the "maxGrade" based on the number of submitted assignments for each student
    for index, row in df_ceiling.iterrows():
        Username = row['GitHub Username']

        if Username in submitted_assignments_count:
            submitted_assignments = submitted_assignments_count[Username]

            if submitted_assignments >= 4:
                df_ceiling.at[index, 'maxGrade'] = 100
            elif submitted_assignments == 3:
                df_ceiling.at[index, 'maxGrade'] = 87
            elif submitted_assignments == 2:
                df_ceiling.at[index, 'maxGrade'] = 83
            elif submitted_assignments == 1:
                df_ceiling.at[index, 'maxGrade'] = 80
            else:
                df_ceiling.at[index, 'maxGrade'] = 55

    # Save the df_ceiling DataFrame as CeilingGrade.csv
    writeCSV(os.getcwd() + profDir + "/CeilingGrade.csv", df_ceiling)
    sys.exit(0)

for x in range(startIndex, endIndex + 1): #for each homework
    hwName = homeworkMasterList[x]
    hwNum = fetchHWInfo(None, hwName)[1]
    outputFile.write('\n--[[Currently grading : '+ hwName + ']]--\n')

    #!!----------Collect List of Students, Homeworks, and Repositories--------!!
    df = loadCSV(os.getcwd() + profDir + "/masterGrades.csv")
    df = updateDF(hws, students, df) # adding rows and columns based on new students and hws in the class
    writeCSV(os.getcwd() + profDir + "/masterGrades.csv", df)

    #!!----------Clone Appropriate Repositories--------!!
    for repo in repos: #for each repo

        [needsToBeGraded, hoursLate] = cloneFromRepos(organization, repo, hwNum, tagName, authName, authKey, profDir + hwsDir, clonesDir, outputFile)
        #[repos cloned to the server at this step, each repo and its hours late]
        #clones all repositories of students with the specified homework name and tag

        if (needsToBeGraded == True):
            #!!---------Run Grading Script--------!!
            startGradingProcess(repo, hoursLate, homeworkMasterList[x], outputFile, gradesDir, clonesDir, profDir + hwsDir, gradeFileName, failedTestsDir)
            outputFile.write('\n  --Successfully ran startGradingProcess\n')

            #!!---------Put Grade Text File Into Cloned Repos--------!!
            putGradesInRepos(gradesDir, clonesDir, gradeFileName, repo)
            outputFile.write('  --Successfully ran putGradesInRepos\n')

            #!!---------Add Grades to CSV For Prof Access--------!!
            putGradesInCSV(profDir, gradesDir, gradeFileName, repo)
                #adds new hws and students to a csv
                #uses the grade directory to modify data points
            outputFile.write('  --Successfully ran putGradesInCSV\n')

            #!!---------Push Grade File to Student Repos--------!!
            pushChangeToRepos(clonesDir, gradeFileName, failedTestsDir, repo)
                #also adds graded_ver tag
            outputFile.write('  --Successfully ran pushChangeToRepos\n')
            outputFile.write('[Finished grading ' + repo + ']\n')            

            #!!---------Remove Local Repository--------!!
            if args.delete != False:
                repoPath = os.getcwd() + clonesDir + '/' + repo
                if os.path.exists(repoPath):
                    rmtree(repoPath)

            num_graded += 1

            if args.sanity:
                # This is sanity check
                if num_graded >= 2:
                    break

    if args.sanity:
        # This is sanity test and we only grade 2 home works.
        if num_graded >= 2:
            print("Graded 2 homeworks. Exiting as this is a sanity check.")
            break

#!!----------Delete Clones and Grades Folders--------!!
if args.delete != False: #it defaults to true
    if os.path.exists(os.getcwd() + clonesDir):
        rmtree('clones') 
        outputFile.write('\n\nRemoved clones')
            #removes all cloned folders
    if os.path.exists(os.getcwd() + gradesDir):
        rmtree('grades')
        outputFile.write('\nRemoved grades')
            #removes folder of grades

outputFile.write('\n***Finished grading process***')

#!!----------Data Tracking for Development--------!!
[usedFinal, remaining] = fetchLimit(authName, authKey)
outputFile.write('\n\nRequests Used this Runtime: ' + str(usedFinal - usedStart) + '\nHourly Requests Left: ' + str(remaining) + '\n')
endTime = datetime.now()
diffTime = endTime - startTime
totalSeconds = int(diffTime.total_seconds())
totalMinutes = int(divmod(totalSeconds, 60)[0])
totalSeconds = totalSeconds - (totalMinutes * 60)
outputFile.write('Total Runtime is: ' + str(totalMinutes) + ' Minutes and ' + str(totalSeconds) + ' Seconds' '\n')

#!!----------Close Output File--------!!
outputFile.close()
fetchRepo = "fetchRepo.pkl"
if os.path.exists(fetchRepo):
    os.remove(fetchRepo)
filterRepo = "filterRepo.pkl"
if os.path.exists(filterRepo):
    os.remove(filterRepo)