# this Python script loads in the actigraphy data regarding number of movements

# import libraries
import os
import sys

# get file name
filename = raw_input('Enter a file name: ')

# open file
data = open(filename, 'r')

# import data
all_lines = data.readlines()

# ignore first line (column label)
all_lines.pop(0)

# record number of movements data into array
movement_num = []

for line in all_lines:

    movement_num.append(line.split()[5])
    
# exit
data.close()
