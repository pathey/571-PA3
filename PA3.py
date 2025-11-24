import numpy as np
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

def EE_RM_scheduler():
	#print("Running Energy Efficient RM Scheduler")
	pass	

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
