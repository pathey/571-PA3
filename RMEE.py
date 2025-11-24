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
    
indexW0 = 5
indexW1 = 5
indexW2 = 5
indexW3 = 5
indexW4 = 5

def RMEEScheduleCheck(numTasks_RM, taskList_RM):
    RM_Limit = numTasks_RM * (pow(2, (1 / numTasks_RM)) - 1)
    RM_TaskSum = RM_Limit + 1
    global indexW0
    global indexW1
    global indexW2
    global indexW3
    global indexW4
    execTimeIndex = 0   #index of slowest execution time that can be sped up
    

    # for i in range(len(taskList_RM)):
    #     for j in range(4):              #4 clock freq are given
    #         RM_TaskSum += (taskList_RM[i][2] / taskList_RM[i][1]) #Ci / Ti

    #     RM_TaskSum += (taskList_RM[i][2] / taskList_RM[i][1]) #Ci / Ti
    execTimes = [
    taskList_RM[0][indexW0],
    taskList_RM[1][indexW1],
    taskList_RM[2][indexW2],
    taskList_RM[3][indexW3],
    taskList_RM[4][indexW4],
    ]
    execTimes.sort(reverse=True)        #execTimes[0] will always be longest exec time

    while (not (RM_TaskSum <= RM_Limit)):   #while the RM equality is not met keep looking for how to meet it


        #if largest execution time is at task w reduce index by 1 to make execution faster by 1 step

        

        RM_TaskSum = 0  #reset calculation to check properly

        for index in range(len(taskList_RM)):
            if index == 0:
                if (execTimes[execTimeIndex] == taskList_RM[index][indexW0]) and indexW0 > 2: 
                    indexW0 -= 1
                RM_TaskSum += taskList_RM[index][indexW0] / taskList_RM[index][1]
            elif index == 1:
                if (execTimes[execTimeIndex] == taskList_RM[index][indexW1]) and indexW1 > 2:
                    indexW1 -= 1
                RM_TaskSum += taskList_RM[index][indexW1] / taskList_RM[index][1]
            elif index == 2:
                if (execTimes[execTimeIndex] == taskList_RM[index][indexW2]) and indexW2 > 2:
                    indexW2 -= 1
                RM_TaskSum += taskList_RM[index][indexW2] / taskList_RM[index][1]
            elif index == 3:
                if (execTimes[execTimeIndex] == taskList_RM[index][indexW3]) and indexW3 > 2:
                    indexW3 -= 1
                RM_TaskSum += taskList_RM[index][indexW3] / taskList_RM[index][1]
            elif index == 4:
                if (execTimes[execTimeIndex] == taskList_RM[index][indexW4]) and indexW4 > 2:
                    indexW4 -= 1
                RM_TaskSum += taskList_RM[index][indexW4] / taskList_RM[index][1]
        
        execTimes = [
        taskList_RM[0][indexW0],
        taskList_RM[1][indexW1],
        taskList_RM[2][indexW2],
        taskList_RM[3][indexW3],
        taskList_RM[4][indexW4],
        ]
        execTimes.sort(reverse=True)        #execTimes[0] will always be longest exec time

        for i in range(len(taskList_RM)):
            if i == 0 and execTimes[execTimeIndex] == taskList_RM[i][indexW0] and indexW0 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
            elif i == 1 and execTimes[execTimeIndex] == taskList_RM[i][indexW1] and indexW1 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
            elif i == 2 and execTimes[execTimeIndex] == taskList_RM[i][indexW2] and indexW2 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
            elif i == 3 and execTimes[execTimeIndex] == taskList_RM[i][indexW3] and indexW3 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
            elif i == 4 and execTimes[execTimeIndex] == taskList_RM[i][indexW4] and indexW4 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
        
        
        
        if indexW0 == indexW1 == indexW2 == indexW3 == indexW4 == 2:
            break
        
    print(execTimes)
    print(execTimeIndex)
    print(indexW0, indexW1, indexW2, indexW3, indexW4)
    print("RM_TaskSum = ", round(RM_TaskSum, 3))
    print("RM_Limit = ", round(RM_Limit, 3))
    if RM_TaskSum <= RM_Limit:
        print("RM Schedule Is VALID")
        print("\n")
        return True
    else:
        print("RM Schedule Is INVALID")
        print("\n")
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

if RMEEScheduleCheck(numTasks_RM, taskList_RM):     #Is RM a valid scheduling method for our task list? if yes proceed
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
    
    print(taskList_RM)



else:
    pass

input1.close()