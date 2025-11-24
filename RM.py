import time
import sys
import math

scheduleTime = 1
scheduleList = []
idleTime = 0
joulesTotal = 0
stopScheduling = False

def schedule(taskName, runTime, CPU_Power = 625, CPU_Freq = 1188):
    #CPU_Power given in mW
    #CPU_Freq given in MHz
    global scheduleTime
    global scheduleList
    global idleTime
    global joulesTotal
    global stopScheduling

    if taskName == "IDLE":
        joules = (taskInfo[0][6] * 0.001) * runTime #taskInfo[0][6] is IDLE CPU_Power at lowest freq
        idleTime += runTime
    else:
        joules = (CPU_Power * 0.001) * runTime      #CPU_power given in mW

    

    if scheduleTime + runTime >= 1000 and (not stopScheduling): #replace 1000 is given max execution time
        scheduleList.append([scheduleTime, taskName, CPU_Freq, 1000 - scheduleTime, joules]) #replace 1000 is given max execution time
        scheduleList.append(["EXECUTION TIME ENDS, VALUES BELOW ARE TOTALS"])
        scheduleList.append(["Execution Time: ", 1000]) #replace 1000 is given max execution time
        scheduleList.append(["Percentage Idle Time: ", round(((idleTime / 1000) * 100), 3), "%"]) #replace 1000 is given max execution time
        scheduleList.append(["Total Energy Consumption: ", (round(joulesTotal, 3)), "J"])
        stopScheduling = True
    elif not stopScheduling:
        scheduleList.append([scheduleTime, taskName, CPU_Freq, runTime, joules])

    scheduleTime += runTime
    joulesTotal += joules
    
    

def RMScheduleCheck(numTasks, taskList):
    RM_Limit = numTasks * (pow(2, (1 / numTasks)) - 1)
    RM_TaskSum = 0

    for i in range(len(taskList)):
        RM_TaskSum += (taskList[i][2] / taskList[i][1]) #Ci / Ti
    
    print("RM_TaskSum = ", round(RM_TaskSum, 3))
    print("RM_Limit = ", round(RM_Limit, 3))
    if RM_TaskSum <= RM_Limit:
        print("RM Schedule Is VALID")
        return True
    else:
        print("RM Schedule Is INVALID")
        return False


taskInfo = []
periodList = []
taskList = []
numTasks = 0
currentTaskIndex = 0
lock = False
lockTime = 0

input1 = open(sys.argv[1])  #the first argument should be the name of the txt file to open

lines = input1.readlines()

for line in lines:          #create taskInfo array from txt file
    cleanLine = line.strip().split()

    for index, item in enumerate(cleanLine):
        if item.isdigit():
            cleanLine[index] = int(item)

    taskInfo.append(cleanLine)

numTasks = taskInfo[0][0]
taskList = taskInfo[1:]
taskList.sort(key = lambda task: task[1])   #sort by earliest deadline first

if RMScheduleCheck(numTasks, taskList):     #Is RM a valid scheduling method for our task list? if yes proceed
    for i in range(len(taskList)):          #compute hyperPeriod
        periodList.append(taskList[i][1])

    hyperPeriod = math.lcm(*periodList)

    for i in range(taskInfo[0][1]):

        if (i % taskList[0][1]) == 0 and not lock:
            schedule(taskList[currentTaskIndex][0], taskList[currentTaskIndex][2])
            lock = True
            lockTime = taskList[currentTaskIndex][2]   #lock the schedule for the duration of task
            currentTaskIndex += 1

        elif (not lock) and (currentTaskIndex <= 4):
            schedule(taskList[currentTaskIndex][0], taskList[currentTaskIndex][2])
            lock = True
            lockTime = taskList[currentTaskIndex][2]   #lock the schedule for the duration of task
            currentTaskIndex += 1
        
        elif (not lock) and (currentTaskIndex > 4):
            idleTimeScheduled = taskList[0][1] - i % taskList[0][1]
            schedule("IDLE", idleTimeScheduled)
            lock = True
            lockTime = idleTimeScheduled   #lock the schedule for the duration of task
            currentTaskIndex = 0
        
        lockTime = lockTime - 1
        if lockTime == 0:
            lock = False

    for line in scheduleList:
        for index, item in enumerate(line):
            line[index] = str(item)
        print(" ".join(line))



else:
    pass

input1.close()