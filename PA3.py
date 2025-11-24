import numpy as np
import time
from dataclasses import dataclass
from typing import Dict, List
import sys
import math

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

def RM_scheduler():
	print("Running RM Scheduler")
		

def EDF_scheduler():
	print("Running EDF Scheduler")
	periods = []
	for task in tasks:
		task.time_remaining = task.wcet[1188]
		periods.append(task.period)
		#print(task)
	hyper_period = math.lcm(*periods)
	upcoming_deadline = sys.maxsize
	current_task = None 
	schedule = []				#2D array that stores the task executed at a given second and the CPU frequency it is executed at
	sys_status = None
	
	for i in range(1, hyper_period):
		for task in tasks:
			if i < task.next_deadline and task.next_deadline <= upcoming_deadline and task.status == "ready":
				upcoming_deadline = task.next_deadline
				current_task = task
				sys_status = "BUSY"
			elif i >= task.next_deadline:
				task.next_deadline += task.period
				task.status = "ready"
		
		if sys_status == "IDLE":
			schedule.append((sys_status, 0))
		else:
			#print(f"Current Task: {current_task.name}")
			schedule.append((current_task.name, 1188))
			
			if current_task.time_remaining > 1:
				current_task.time_remaining -= 1
				#print(f"{current_task.name} time remaining: {current_task.time_remaining}")
			else:
				current_task.time_remaining = current_task.wcet[1188]
				current_task.status = "completed"
				upcoming_deadline = sys.maxsize
				sys_status = "IDLE"
				#print(f"{current_task.name} next deadline: {current_task.next_deadline}")

	#print(schedule)
	return schedule

def EE_EDF_scheduler():
	print("Running Energy Efficient EDF Scheduler")

def EE_RM_scheduler():
	print("Running Energy Efficient RM Scheduler")

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

def executor(schedule):
	total_energy = 0	#total energy consumed during full 1000 seconds
	c_t_energy = 0		#energy consumed by currently/most recently run taks
	c_t_exec_time = 0	#how long currently/most recently run task ran for
	c_t_start_time = 0	#when the current/most recently run task started
	c_t_name = None
	for i in range(1, 1002):
		if i == 1:
			c_t_name = schedule[0][0]
			c_t_start_time = i-1
			c_t_exec_time += 1
			c_t_energy = sys_conf.active_power[schedule[0][1]]
			total_energy += c_t_energy
		else:
			if schedule[i-1][0] != c_t_name or i > 1000:
				if c_t_name == "IDLE":
					print(f"{c_t_start_time} {c_t_name} IDLE {c_t_exec_time} {c_t_energy}mJ")
				else:
					print(f"{c_t_start_time} {c_t_name} {schedule[i-2][1]} {c_t_exec_time} {c_t_energy}mJ")
				c_t_name = schedule[i-1][0]
				c_t_start_time = i-1
				c_t_exec_time = 0
				c_t_energy = 0
			c_t_exec_time += 1
			c_t_energy += sys_conf.active_power[schedule[i-1][1]]
			total_energy += sys_conf.active_power[schedule[i-1][1]]
	print(f"Total Energy: {total_energy}")


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

executor(schedule)
