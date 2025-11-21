import numpy as np
import time
from dataclasses import dataclass
from typing import Dict, List
import sys

@dataclass
class SystemConfig:
	task_quantity: int		#of tasks in the system
	time_limit: int			#how long the system should run for in seconds
	active_power: Dict[int, int]	#active CPU power in mW at a given frequency
	idle_power: int			#idle CPU power at the lowest frequency

@dataclass
class Task:
	name: str			#task name (duh)
	period: int			#deadline/period in seconds
	wcet: Dict[int, int]		#worst-case execution time at a given frequency

def RM_scheduler():
	print("Running RM Scheduler")

def EDF_scheduler():
	print("Running EDF Scheduler")

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
		384:int(parts[5])
	}
	idle_power = int(parts[6])

	return SystemConfig(
		task_quantity = task_quantity,
		time_limit=time_limit,
		active_power = active_power,
		idle_power = idle_power
	)

def task_constructor(task_line) -> Task:
	parts = task_line.split()

	name = parts[0]
	period = int(parts[1])
	wcet = {
		1188:int(parts[2]),
		918:int(parts[3]),
		648:int(parts[4]),
		384:int(parts[5])
	}

	return Task(
		name = name,
		period = period,
		wcet = wcet
	)



input_file = sys.argv[1]
policy = sys.argv[2]
energy_efficient = None

tasks = []

if len(sys.argv) > 3:
	energy_efficient = sys.argv[3]

with open(input_file, "r") as f:
	system_line = f.readline()
	sys_conf = system_constructor(system_line)

	for line in f:
		tasks.append(task_constructor(line))

#print(sys_conf)
#print(tasks)

scheduler = dispatch[(policy, energy_efficient)]
scheduler()
