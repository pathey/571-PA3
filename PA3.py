import numpy as np
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SystemConfig:
	task_quantity: int		#of tasks in the system
	time_limit: int			#how long the system should run for
	active_power: Dict[int, int]	#active CPU power at a given frequency
	idle_power: int			#idle CPU power at the lowest frequency

@dataclass
class Task:
	name: str			#task name (duh)
	period: int			#deadline/period
	wcet: Dict[int, int]		#worst-case execution time at a given frequency

def EDF_schedule():
	pass

def RM_scheduler():
	pass

def EE_EDF_scheduler():
	pass

def EE_RM_scheduler():
	pass

def system_constructor():
	pass

def task_constructor():
	pass

with open("input1.txt", "r") as f:
	lines1 = f.readlines()

with open("input2.txt", "r") as f:
	lines2 = f.readlines()



