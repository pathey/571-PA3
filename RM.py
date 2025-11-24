import time
import sys

scheduleTime = 1
scheduleList = []
idleTime = 0
joulesTotal = 0

def schedule(taskName, runTime, CPU_Power = 625, CPU_Freq = 1188):
    #CPU_Power given in mW
    #CPU_Freq given in MHz
    global scheduleTime
    global scheduleList
    global idleTime
    global joulesTotal

    if taskName == "IDLE":
        joules = (taskInfo[0][6] * 0.001) * runTime #taskInfo[0][6] is IDLE CPU_Power at lowest freq
        idleTime += runTime
    else:
        joules = (CPU_Power * 0.001) * runTime      #CPU_power given in mW

    if scheduleTime >= 1000:
        scheduleList.append("EXECUTION TIME ENDS, VALUES BELOW ARE TOTALS")
        scheduleList.append("Execution Time: ", scheduleTime)
        scheduleList.append("Percentage Idle Time: ", ((idleTime / scheduleTime) * 100), "%")
        scheduleList.append("Total Energy Consumption: ", joulesTotal, "J")
    else:
        scheduleList.append([scheduleTime, taskName, CPU_Freq, runTime, joules])
    
    scheduleTime += runTime
    joulesTotal += joules

taskInfo = []

input1 = open(sys.argv[1]) #the first argument should be the name of the txt file to open

lines = input1.readlines()

for line in lines:
    cleanLine = line.strip().split()

    for index, item in enumerate(cleanLine):
        if item.isdigit():
            cleanLine[index] = int(item)

    taskInfo.append(cleanLine)

tasks = taskInfo[1:]
tasks.sort(key = lambda task: task[1])

print(tasks)

numTasks = taskInfo[0][0]

for i in range(numTasks):
    i += 1
    taskInfo[i][0]

#below is schedule function and print test code
# schedule("w1", 30)
# schedule("w2", 50)

# for line in scheduleList:
#     for index, item in enumerate(line):
#         line[index] = str(item)
#     print(" ".join(line))



input1.close()