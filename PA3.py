#import numpy as np
import time
from dataclasses import dataclass
from typing import Dict, List
import sys
import math
import itertools

@dataclass
class SystemConfig:
	task_quantity: int		#of tasks in the system
	time_limit: int			#how long the system should run for in seconds
	active_power: Dict[int, int]	#active CPU power in mW at a given frequency

@dataclass
class Task:
	name: str			#task name (duh)
	period: int			#period in seconds
	next_deadline: int		#next deadline (changes throughout the run)
	time_remaining: int		#remaining time of execution
	status: str			#track whether the task is in the system or waiting to "arrive" again
	wcet: Dict[int, int]		#worst-case execution time at a given frequency

tasks = []
sys_conf = None
policy = None
energy_efficient = None

scheduleTime_RM = 1
scheduleList_RM = []
idleTime_RM = 0
joulesTotal_RM = 0
stopScheduling_RM = False

def RM_scheduler():
	print("Running RM Scheduler")
	

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
			CPU_Freq = "IDLE"
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

def EDF_scheduler(task_modes=None):
    # Map task names -> frequency mode
    if task_modes is None:
        task_modes = {task.name: 1188 for task in tasks}
    else:
        task_modes = {tasks[i].name: task_modes[i] for i in range(len(tasks))}

    # Reset tasks to a clean initial state
    for task in tasks:
        task.time_remaining = 0          # no job active yet
        task.next_deadline = task.period # first job deadline at end of first period
        task.status = "ready"

    # calculating and using hyperperiod
    periods = [task.period for task in tasks]
    hyper_period = math.lcm(*periods)
    sim_horizon = hyper_period

    schedule = []

    for t in range(sim_horizon):  # t = 0, 1, ..., time_limit - 1

        #Deadline check BEFORE releasing new jobs:
        #If any job has reached or passed its deadline and is not finished, schedule is invalid.
        for task in tasks:
            if t >= task.next_deadline and task.time_remaining > 0:
                return "No valid schedule"

        #Release new jobs at their release times (t multiples of period)
        for task in tasks:
            if t % task.period == 0:
                task.time_remaining = task.wcet[task_modes[task.name]]
                task.next_deadline = t + task.period
                task.status = "ready"

        #Pick ready task with earliest deadline
        ready_tasks = [
            task for task in tasks
            if task.status == "ready" and task.time_remaining > 0
        ]

        if not ready_tasks:
            #CPU is idle for this time unit
            schedule.append(("IDLE", 0))
            continue

        current_task = min(ready_tasks, key=lambda tk: tk.next_deadline)
        freq = task_modes[current_task.name]
        schedule.append((current_task.name, freq))

        #Execute 1 time unit
        current_task.time_remaining -= 1
        if current_task.time_remaining == 0:
            current_task.status = "completed"

    return schedule



def EE_EDF_scheduler():
	#print("Running Energy Efficient EDF Scheduler")
	values = [1188, 918, 648, 384]
	schedule = []
	best_energy = sys.maxsize
	best_schedule = []
	for combo in itertools.product(values, repeat = sys_conf.task_quantity):
		reset_tasks()
		modes_list = list(combo)
		print(f" Testing: {modes_list}")
		schedule = EDF_scheduler(modes_list)
		schedule = schedule[:1501]
	
		if isinstance(schedule, list):
			result = executor(schedule, 0)
			if result[0] < best_energy:
				best_energy = result[0]
				print(f"{best_energy}")
				best_schedule = schedule
	return best_schedule

scheduleTime_RMEE = 1
scheduleList_RMEE = []
idleTime_RMEE = 0
joulesTotal_RMEE = 0
stopScheduling_RMEE = False

indexW0 = 5
indexW1 = 5
indexW2 = 5
indexW3 = 5
indexW4 = 5

def EE_RM_scheduler():
	print("Running Energy Efficient RM Scheduler")



	def schedule_RMEE(taskName, runTime, CPU_Power = 625, CPU_Freq_index = 2):
		#CPU_Power given in mW
		#CPU_Freq given in MHz
		global scheduleTime_RMEE
		global scheduleList_RMEE
		global idleTime_RMEE
		global joulesTotal_RMEE
		global stopScheduling_RMEE

		match CPU_Freq_index:
			case 2:
				CPU_Freq = 1188
			case 3:
				CPU_Freq = 918
			case 4:
				CPU_Freq = 648
			case 5:
				CPU_Freq = 384
			case _:
				CPU_Freq = 1188

		if taskName == "IDLE":
			joules = (taskInfo_RMEE[0][6] * 0.001) * runTime #taskInfo_RMEE[0][6] is IDLE CPU_Power at lowest freq
			CPU_Freq = "IDLE"
			idleTime_RMEE += runTime
		else:
			joules = (CPU_Power * 0.001) * runTime      #CPU_power given in mW

		

		if scheduleTime_RMEE + runTime >= 1000 and (not stopScheduling_RMEE): #1000 is given max execution time
			scheduleList_RMEE.append([scheduleTime_RMEE, taskName, CPU_Freq, 1000 - scheduleTime_RMEE, round(joules, 3)]) #1000 is given max execution time
			scheduleList_RMEE.append(["EXECUTION TIME ENDS, VALUES BELOW ARE TOTALS"])
			scheduleList_RMEE.append(["Execution Time: ", 1000]) #1000 is given max execution time
			scheduleList_RMEE.append(["Percentage Idle Time: ", round(((idleTime_RMEE / 1000) * 100), 3), "%"]) #1000 is given max execution time
			scheduleList_RMEE.append(["Total Energy Consumption: ", (round(joulesTotal_RMEE, 3)), "J"])
			stopScheduling_RMEE = True
		elif not stopScheduling_RMEE:
			scheduleList_RMEE.append([scheduleTime_RMEE, taskName, CPU_Freq, runTime, round(joules, 3)])

		scheduleTime_RMEE += runTime
		joulesTotal_RMEE += joules
	


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
	lockRMEE = False
	lockRMEETime = 0

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

		RMEEtaskList = []
		curr_index = [indexW0, indexW1, indexW2, indexW3, indexW4]

		for i in range(len(taskList_RMEE)):
			task_row = []  
			for j in range(3):
				if j != 2:
					task_row.append(taskList_RMEE[i][j])
				else:
					task_row.append(taskList_RMEE[i][curr_index[i]])
			RMEEtaskList.append(task_row) 

		print(RMEEtaskList) 

		RMEEtaskList.sort(key= lambda task: task[1])    #sort by earliest deadline first
		nextTaskIndex = 1

		# for i in range(taskInfo_RMEE[0][1]):
		#     if (i % RMEEtaskList[0][1]) == 0:   #earliest deadline has highest priority to preempt
		#         if
		#         schedule_RMEE(RMEEtaskList[currentTaskIndex_RMEE][0], RMEEtaskList[currentTaskIndex_RMEE][2], taskInfo_RMEE[0][curr_index[currentTaskIndex_RMEE]], curr_index[currentTaskIndex_RMEE])
		#         nextTaskIndex = 1
		#         currentTaskIndex_RMEE = nextTaskIndex
			
			

		for i in range(taskInfo_RMEE[0][1]):

			if (i % RMEEtaskList[0][1]) == 0:
				if lockRMEE:
					nextTaskIndex = currentTaskIndex_RMEE
				currentTaskIndex_RMEE = 0
				schedule_RMEE(RMEEtaskList[currentTaskIndex_RMEE][0], RMEEtaskList[currentTaskIndex_RMEE][2], taskInfo_RMEE[0][curr_index[currentTaskIndex_RMEE]], curr_index[currentTaskIndex_RMEE])
				lockRMEE = True
				lockRMEETime = RMEEtaskList[currentTaskIndex_RMEE][2]   #lock the schedule for the duration of task
				if not lockRMEE:
					nextTaskIndex = currentTaskIndex_RMEE + 1
				currentTaskIndex_RMEE = nextTaskIndex

			elif (not lockRMEE) and (currentTaskIndex_RMEE <= 4):
				schedule_RMEE(RMEEtaskList[currentTaskIndex_RMEE][0], RMEEtaskList[currentTaskIndex_RMEE][2], taskInfo_RMEE[0][curr_index[currentTaskIndex_RMEE]], curr_index[currentTaskIndex_RMEE])
				lockRMEE = True
				lockRMEETime = RMEEtaskList[currentTaskIndex_RMEE][2]   #lockRMEE the schedule for the duration of task
				nextTaskIndex = currentTaskIndex_RMEE + 1
				currentTaskIndex_RMEE = nextTaskIndex
			
			elif (not lockRMEE) and (currentTaskIndex_RMEE > 4):
				idleTime_RMEEScheduled = RMEEtaskList[0][1] - i % RMEEtaskList[0][1]
				schedule_RMEE("IDLE", idleTime_RMEEScheduled)
				lockRMEE = True
				lockRMEETime = idleTime_RMEEScheduled   #lockRMEE the schedule for the duration of task
				currentTaskIndex_RMEE = 0
			
			lockRMEETime = lockRMEETime - 1
			if lockRMEETime == 0:
				lockRMEE = False

		for line in scheduleList_RMEE:
			for index, item in enumerate(line):
				line[index] = str(item)
			print(" ".join(line))
		
		print(taskList_RMEE)



	else:
		pass


	input1.close()

def reset_tasks():
	for task in tasks:
		task.next_deadline = task.period
		task.time_remaining = 0
		task.status = "ready"

dispatch = {
	("RM", None):RM_scheduler,
	("EDF", None): EDF_scheduler,
	("EDF", "EE"): EE_EDF_scheduler,
	("RM", "EE"): EE_RM_scheduler
}

def system_constructor(system_line) -> SystemConfig:
	parts = system_line.split()
	
	task_quantity = int(parts[0])
	time_limit = int(parts[1])
	active_power = {
		1188:int(parts[2]), 
		918:int(parts[3]), 
		648:int(parts[4]), 
		384:int(parts[5]),
		0:int(parts[6])
	}

	return SystemConfig(
		task_quantity = task_quantity,
		time_limit=time_limit,
		active_power = active_power
	)

def task_constructor(task_line) -> Task:
	parts = task_line.split()

	name = parts[0]
	period = int(parts[1])
	next_deadline = int(parts[1])
	status = "ready"
	wcet = {
		1188:int(parts[2]),
		918:int(parts[3]),
		648:int(parts[4]),
		384:int(parts[5])
	}

	return Task(
		name = name,
		period = period,
		next_deadline = next_deadline,
		time_remaining = 0,
		status = status,
		wcet = wcet
	)

def executor(schedule, output=1):
	total_energy = 0	#total energy consumed during full 1000 seconds
	c_t_energy = 0		#energy consumed by currently/most recently run taks
	c_t_exec_time = 0	#how long currently/most recently run task ran for
	c_t_start_time = 0	#when the current/most recently run task started
	c_t_name = None
	time_spent_idle = 0
	for i in range(1, 1002):
		if i == 1:
			c_t_name = schedule[0][0]
			c_t_start_time = i-1
			c_t_exec_time += 1
			c_t_energy = sys_conf.active_power[schedule[0][1]]
			total_energy += c_t_energy
		else:
			if schedule[i-1][0] != c_t_name or i > 1000:
				if output == 1:
					c_t_e_j = c_t_energy / 1000.000
					if c_t_name == "IDLE":
						print(f"{c_t_start_time} {c_t_name} IDLE {c_t_exec_time} {c_t_e_j}")
					else:
						print(f"{c_t_start_time} {c_t_name} {schedule[i-2][1]} {c_t_exec_time} {c_t_e_j}")
				if c_t_name == "IDLE":
					time_spent_idle += c_t_exec_time
				c_t_name = schedule[i-1][0]
				c_t_start_time = i-1
				c_t_exec_time = 0
				c_t_energy = 0
			c_t_exec_time += 1
			c_t_energy += sys_conf.active_power[schedule[i-1][1]]
			total_energy += sys_conf.active_power[schedule[i-1][1]]

	percent_idle = (time_spent_idle / 1000) * 100
	total_sys_exec_time = 1000 - time_spent_idle	
	total_energy = total_energy / 1000.000
	ept = [total_energy, percent_idle, total_sys_exec_time]

	return ept


input_file = sys.argv[1]
policy = sys.argv[2]

if len(sys.argv) > 3:
	energy_efficient = sys.argv[3]

with open(input_file, "r") as f:
	system_line = f.readline()
	sys_conf = system_constructor(system_line)

	for line in f:
		tasks.append(task_constructor(line))

#print(sys_conf)
#print(tasks)

schedule = []

scheduler = dispatch[(policy, energy_efficient)]
schedule = scheduler()

result = []

if policy == "EDF":
	if (isinstance(schedule, list)):
		result = executor(schedule)
	else:
		print(schedule)

	print(f"{result[0]} {result[1]}% {result[2]}")
