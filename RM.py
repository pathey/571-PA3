import time
import sys


print("Total arguments:", len(sys.argv))

input1 = open("./input1.txt")

print(input1.read())

input1.close()