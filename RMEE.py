import time
import sys
import math

scheduleTime_RM = 1
scheduleList_RM = []
idleTime_RM = 0
joulesTotal_RM = 0
stopScheduling_RM = False

def schedule(taskName, runTime, CPU_Power = 625, CPU_Freq = 1188):
    #CPU_Power given in mW
    #CPU_Freq given in MHz
    global scheduleTime_RM
    global scheduleList_RM
    global idleTime_RM
    global joulesTotal_RM
    global stopScheduling_RM

    if taskName == "IDLE":
        joules = (taskInfo_RM[0][6] * 0.001) * runTime #taskInfo_RM[0][6] is IDLE CPU_Power at lowest freq
        idleTime_RM += runTime
    else:
        joules = (CPU_Power * 0.001) * runTime      #CPU_power given in mW

    

    if scheduleTime_RM + runTime >= 1000 and (not stopScheduling_RM): #1000 is given max execution time
        scheduleList_RM.append([scheduleTime_RM, taskName, CPU_Freq, 1000 - scheduleTime_RM, joules]) #1000 is given max execution time
        scheduleList_RM.append(["EXECUTION TIME ENDS, VALUES BELOW ARE TOTALS"])
        scheduleList_RM.append(["Execution Time: ", 1000]) #1000 is given max execution time
        scheduleList_RM.append(["Percentage Idle Time: ", round(((idleTime_RM / 1000) * 100), 3), "%"]) #1000 is given max execution time
        scheduleList_RM.append(["Total Energy Consumption: ", (round(joulesTotal_RM, 3)), "J"])
        stopScheduling_RM = True
    elif not stopScheduling_RM:
        scheduleList_RM.append([scheduleTime_RM, taskName, CPU_Freq, runTime, joules])

    scheduleTime_RM += runTime
    joulesTotal_RM += joules
    
    

def RMScheduleCheck(numTasks_RM, taskList_RM):
    RM_Limit = numTasks_RM * (pow(2, (1 / numTasks_RM)) - 1)
    RM_TaskSum = 0

    for i in range(len(taskList_RM)):
        RM_TaskSum += (taskList_RM[i][2] / taskList_RM[i][1]) #Ci / Ti
    
    print("RM_TaskSum = ", round(RM_TaskSum, 3))
    print("RM_Limit = ", round(RM_Limit, 3))
    if RM_TaskSum <= RM_Limit:
        print("RM Schedule Is VALID")
        return True
    else:
        print("RM Schedule Is INVALID")
        return False


taskInfo_RM = []
periodList_RM = []
taskList_RM = []
numTasks_RM = 0
currentTaskIndex_RM = 0
lockRM = False
lockRMTime = 0

input1 = open(sys.argv[1])  #the first argument should be the name of the txt file to open

lines = input1.readlines()

for line in lines:          #create taskInfo_RM array from txt file
    cleanLine = line.strip().split()

    for index, item in enumerate(cleanLine):
        if item.isdigit():
            cleanLine[index] = int(item)

    taskInfo_RM.append(cleanLine)

numTasks_RM = taskInfo_RM[0][0]
taskList_RM = taskInfo_RM[1:]
taskList_RM.sort(key = lambda task: task[1])   #sort by earliest deadline first

if RMScheduleCheck(numTasks_RM, taskList_RM):     #Is RM a valid scheduling method for our task list? if yes proceed
    for i in range(len(taskList_RM)):          #compute hyperPeriod_RM
        periodList_RM.append(taskList_RM[i][1])

    hyperPeriod_RM = math.lcm(*periodList_RM)

    for i in range(taskInfo_RM[0][1]):

        if (i % taskList_RM[0][1]) == 0 and not lockRM:
            schedule(taskList_RM[currentTaskIndex_RM][0], taskList_RM[currentTaskIndex_RM][2])
            lockRM = True
            lockRMTime = taskList_RM[currentTaskIndex_RM][2]   #lockRM the schedule for the duration of task
            currentTaskIndex_RM += 1

        elif (not lockRM) and (currentTaskIndex_RM <= 4):
            schedule(taskList_RM[currentTaskIndex_RM][0], taskList_RM[currentTaskIndex_RM][2])
            lockRM = True
            lockRMTime = taskList_RM[currentTaskIndex_RM][2]   #lockRM the schedule for the duration of task
            currentTaskIndex_RM += 1
        
        elif (not lockRM) and (currentTaskIndex_RM > 4):
            idleTime_RMScheduled = taskList_RM[0][1] - i % taskList_RM[0][1]
            schedule("IDLE", idleTime_RMScheduled)
            lockRM = True
            lockRMTime = idleTime_RMScheduled   #lockRM the schedule for the duration of task
            currentTaskIndex_RM = 0
        
        lockRMTime = lockRMTime - 1
        if lockRMTime == 0:
            lockRM = False

    for line in scheduleList_RM:
        for index, item in enumerate(line):
            line[index] = str(item)
        print(" ".join(line))



else:
    pass

input1.close()