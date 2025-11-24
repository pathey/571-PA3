import time
import sys
import math

scheduleTime_RMEE = 1
scheduleList_RMEE = []
idleTime_RMEE = 0
joulesTotal_RMEE = 0
stopScheduling_RMEE = False

def schedule(taskName, runTime, CPU_Power = 625, CPU_Freq = 1188):
    #CPU_Power given in mW
    #CPU_Freq given in MHz
    global scheduleTime_RMEE
    global scheduleList_RMEE
    global idleTime_RMEE
    global joulesTotal_RMEE
    global stopScheduling_RMEE

    if taskName == "IDLE":
        joules = (taskInfo_RMEE[0][6] * 0.001) * runTime #taskInfo_RMEE[0][6] is IDLE CPU_Power at lowest freq
        idleTime_RMEE += runTime
    else:
        joules = (CPU_Power * 0.001) * runTime      #CPU_power given in mW

    

    if scheduleTime_RMEE + runTime >= 1000 and (not stopScheduling_RMEE): #1000 is given max execution time
        scheduleList_RMEE.append([scheduleTime_RMEE, taskName, CPU_Freq, 1000 - scheduleTime_RMEE, joules]) #1000 is given max execution time
        scheduleList_RMEE.append(["EXECUTION TIME ENDS, VALUES BELOW ARE TOTALS"])
        scheduleList_RMEE.append(["Execution Time: ", 1000]) #1000 is given max execution time
        scheduleList_RMEE.append(["Percentage Idle Time: ", round(((idleTime_RMEE / 1000) * 100), 3), "%"]) #1000 is given max execution time
        scheduleList_RMEE.append(["Total Energy Consumption: ", (round(joulesTotal_RMEE, 3)), "J"])
        stopScheduling_RMEE = True
    elif not stopScheduling_RMEE:
        scheduleList_RMEE.append([scheduleTime_RMEE, taskName, CPU_Freq, runTime, joules])

    scheduleTime_RMEE += runTime
    joulesTotal_RMEE += joules
    
indexW0 = 5
indexW1 = 5
indexW2 = 5
indexW3 = 5
indexW4 = 5

def RMEEScheduleCheck(numTasks_RMEE, taskList_RMEE):
    RMEE_Limit = numTasks_RMEE * (pow(2, (1 / numTasks_RMEE)) - 1)
    RMEE_TaskSum = RMEE_Limit + 1
    global indexW0
    global indexW1
    global indexW2
    global indexW3
    global indexW4
    execTimeIndex = 0   #index of slowest execution time that can be sped up
    

    # for i in range(len(taskList_RMEE)):
    #     for j in range(4):              #4 clock freq are given
    #         RMEE_TaskSum += (taskList_RMEE[i][2] / taskList_RMEE[i][1]) #Ci / Ti

    #     RMEE_TaskSum += (taskList_RMEE[i][2] / taskList_RMEE[i][1]) #Ci / Ti
    execTimes = [
    taskList_RMEE[0][indexW0],
    taskList_RMEE[1][indexW1],
    taskList_RMEE[2][indexW2],
    taskList_RMEE[3][indexW3],
    taskList_RMEE[4][indexW4],
    ]
    execTimes.sort(reverse=True)        #execTimes[0] will always be longest exec time

    while (not (RMEE_TaskSum <= RMEE_Limit)):   #while the RM equality is not met keep looking for how to meet it


        #if largest execution time is at task w reduce index by 1 to make execution faster by 1 step

        

        RMEE_TaskSum = 0  #reset calculation to check properly

        for index in range(len(taskList_RMEE)):
            if index == 0:
                if (execTimes[execTimeIndex] == taskList_RMEE[index][indexW0]) and indexW0 > 2: 
                    indexW0 -= 1
                RMEE_TaskSum += taskList_RMEE[index][indexW0] / taskList_RMEE[index][1]
            elif index == 1:
                if (execTimes[execTimeIndex] == taskList_RMEE[index][indexW1]) and indexW1 > 2:
                    indexW1 -= 1
                RMEE_TaskSum += taskList_RMEE[index][indexW1] / taskList_RMEE[index][1]
            elif index == 2:
                if (execTimes[execTimeIndex] == taskList_RMEE[index][indexW2]) and indexW2 > 2:
                    indexW2 -= 1
                RMEE_TaskSum += taskList_RMEE[index][indexW2] / taskList_RMEE[index][1]
            elif index == 3:
                if (execTimes[execTimeIndex] == taskList_RMEE[index][indexW3]) and indexW3 > 2:
                    indexW3 -= 1
                RMEE_TaskSum += taskList_RMEE[index][indexW3] / taskList_RMEE[index][1]
            elif index == 4:
                if (execTimes[execTimeIndex] == taskList_RMEE[index][indexW4]) and indexW4 > 2:
                    indexW4 -= 1
                RMEE_TaskSum += taskList_RMEE[index][indexW4] / taskList_RMEE[index][1]
        
        execTimes = [
        taskList_RMEE[0][indexW0],
        taskList_RMEE[1][indexW1],
        taskList_RMEE[2][indexW2],
        taskList_RMEE[3][indexW3],
        taskList_RMEE[4][indexW4],
        ]
        execTimes.sort(reverse=True)        #execTimes[0] will always be longest exec time

        for i in range(len(taskList_RMEE)):
            if i == 0 and execTimes[execTimeIndex] == taskList_RMEE[i][indexW0] and indexW0 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
            elif i == 1 and execTimes[execTimeIndex] == taskList_RMEE[i][indexW1] and indexW1 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
            elif i == 2 and execTimes[execTimeIndex] == taskList_RMEE[i][indexW2] and indexW2 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
            elif i == 3 and execTimes[execTimeIndex] == taskList_RMEE[i][indexW3] and indexW3 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
            elif i == 4 and execTimes[execTimeIndex] == taskList_RMEE[i][indexW4] and indexW4 == 2 and execTimeIndex < 4:
                execTimeIndex += 1
        
        
        
        if indexW0 == indexW1 == indexW2 == indexW3 == indexW4 == 2:
            break
        
    print(execTimes)
    print(execTimeIndex)
    print(indexW0, indexW1, indexW2, indexW3, indexW4)
    print("RMEE_TaskSum = ", round(RMEE_TaskSum, 3))
    print("RMEE_Limit = ", round(RMEE_Limit, 3))
    if RMEE_TaskSum <= RMEE_Limit:
        print("RM Schedule Is VALID")
        print("\n")
        return True
    else:
        print("RM Schedule Is INVALID")
        print("\n")
        return False


taskInfo_RMEE = []
periodList_RMEE = []
taskList_RMEE = []
numTasks_RMEE = 0
currentTaskIndex_RMEE = 0
lockRM = False
lockRMTime = 0

input1 = open(sys.argv[1])  #the first argument should be the name of the txt file to open

lines = input1.readlines()

for line in lines:          #create taskInfo_RMEE array from txt file
    cleanLine = line.strip().split()

    for index, item in enumerate(cleanLine):
        if item.isdigit():
            cleanLine[index] = int(item)

    taskInfo_RMEE.append(cleanLine)

numTasks_RMEE = taskInfo_RMEE[0][0]
taskList_RMEE = taskInfo_RMEE[1:]
taskList_RMEE.sort(key = lambda task: task[1])   #sort by earliest deadline first

if RMEEScheduleCheck(numTasks_RMEE, taskList_RMEE):     #Is RM a valid scheduling method for our task list? if yes proceed
    for i in range(len(taskList_RMEE)):          #compute hyperPeriod_RMEE
        periodList_RMEE.append(taskList_RMEE[i][1])

    hyperPeriod_RMEE = math.lcm(*periodList_RMEE)

    for i in range(taskInfo_RMEE[0][1]):

        if (i % taskList_RMEE[0][1]) == 0 and not lockRM:
            schedule(taskList_RMEE[currentTaskIndex_RMEE][0], taskList_RMEE[currentTaskIndex_RMEE][2])
            lockRM = True
            lockRMTime = taskList_RMEE[currentTaskIndex_RMEE][2]   #lockRM the schedule for the duration of task
            currentTaskIndex_RMEE += 1

        elif (not lockRM) and (currentTaskIndex_RMEE <= 4):
            schedule(taskList_RMEE[currentTaskIndex_RMEE][0], taskList_RMEE[currentTaskIndex_RMEE][2])
            lockRM = True
            lockRMTime = taskList_RMEE[currentTaskIndex_RMEE][2]   #lockRM the schedule for the duration of task
            currentTaskIndex_RMEE += 1
        
        elif (not lockRM) and (currentTaskIndex_RMEE > 4):
            idleTime_RMEEScheduled = taskList_RMEE[0][1] - i % taskList_RMEE[0][1]
            schedule("IDLE", idleTime_RMEEScheduled)
            lockRM = True
            lockRMTime = idleTime_RMEEScheduled   #lockRM the schedule for the duration of task
            currentTaskIndex_RMEE = 0
        
        lockRMTime = lockRMTime - 1
        if lockRMTime == 0:
            lockRM = False

    for line in scheduleList_RMEE:
        for index, item in enumerate(line):
            line[index] = str(item)
        print(" ".join(line))
    
    print(taskList_RMEE)



else:
    pass

input1.close()