__author__ = 'apoorvsgaur'

import os

N = 2 #Number of the nights this algorithm is going to be run on. Half to get the thresholds using
       #actigraph. Half to test those thresholds
name_of_main_text_file = "Sleep Status Thresholds.txt" #Name of the file with results

def delegate_list_of_motion_activity(motion_activity):

    if (not(os.path.exists(name_of_main_text_file))):
        number_of_nights_processed = 0
        lines_of_file = []
        current_fiveMinAvg = 0
        current_PointsofInterest = 0
    else:
        (lines_of_file, number_of_nights_processed, current_fiveMinAvg, current_PointsofInterest) = reading_relevant_data()

        #If less than half the number of nights available have been analysed, use actigraph to
        #come up with thresholds, else use thresholds on motion activity data
    if(number_of_nights_processed < (N/2)):
        #Analysis on given night's of video
        (fiveMinSum, sleep_count) = testing_phase(motion_activity)
        total_fiveMinSum = (current_fiveMinAvg * current_PointsofInterest) + fiveMinSum
        total_PointsofInterest = current_PointsofInterest + sleep_count

        current_fiveMinAvg = total_fiveMinSum / total_PointsofInterest
        write_sleep_status_testing_file(number_of_nights_processed + 1, current_fiveMinAvg, total_PointsofInterest, fiveMinSum/sleep_count, sleep_count,lines_of_file)
    else:
        (sleep_status, correct_percentage) = independent_sleep_assigning(motion_activity, current_fiveMinAvg)
        write_sleep_status_processing_file(number_of_nights_processed + 1, correct_percentage, lines_of_file)

def write_sleep_status_testing_file(number_of_nights_processed, current_fiveMinAvg, total_PointsofInterest, fiveMinAvg, sleep_count,lines_of_file):

    file_pointer = open(name_of_main_text_file, 'w')
    file_pointer.write("Number of nights processed: " + str(number_of_nights_processed) + "\n")
    file_pointer.write("5 Minute Average: " + str(current_fiveMinAvg) + " Points of Interest: " + str(total_PointsofInterest) + "\n\n")
    file_pointer.write("Testing Phase\n\n")
    if len(lines_of_file) != 0:
        for x in range(4, len(lines_of_file)):
            file_pointer.write(lines_of_file[x])
        file_pointer.write("\nNight " + str(number_of_nights_processed) + " Sleep Data\n")
        file_pointer.write("5 Minute Average: " + str(fiveMinAvg) + " Points of Interest: " + str(sleep_count) + "\n")
    else:
        file_pointer.write("Night 1 Sleep Data\n")
        file_pointer.write("5 Minute Average: " + str(fiveMinAvg) + " Points of Interest: " + str(sleep_count) + "\n")

    file_pointer.close()

def write_sleep_status_processing_file(number_of_nights_processed, correct_percentage, lines_of_file):
    file_pointer = open(name_of_main_text_file, 'w')
    file_pointer.write("Number of nights processed: " + str(number_of_nights_processed) + "\n")
    for x in range(0, len(lines_of_file)):
        file_pointer.write(lines_of_file[x])

    if (number_of_nights_processed == ((N/2) + 1)):
        file_pointer.write("\nIndependent Processing Phase\n")
        file_pointer.write("\nNight " + str(number_of_nights_processed) + " Sleep Data\n")
        file_pointer.write("Correct Percentage: " + str(correct_percentage) + "\n")
    else:
        file_pointer.write("\nNight " + str(number_of_nights_processed) + " Sleep Data\n")
        file_pointer.write("Correct Percentage: " + str(correct_percentage) + "\n")

    file_pointer.close()

def reading_relevant_data():

    #First line of main file will always be number of files processed
    file_pointer = open(name_of_main_text_file, 'r')
    first_line_of_file = file_pointer.readline()
    lines_of_file = file_pointer.readlines() #Rest of lines in file

    number_of_nights_processed = first_line_of_file.replace("\n", "").split(":")[-1].strip() #Line will be of format: "Number of nights processed: xx"
    current_fiveMinAvg = lines_of_file[0].split(":")[1].strip().split(" ")[0] #Line will be of format: "Five Minute Average: xx Points of Interest: xxx"
    current_PointsofInterest = lines_of_file[0].split(":")[-1].strip()

    file_pointer.close()

    return (lines_of_file, int(number_of_nights_processed), float(current_fiveMinAvg), float(current_PointsofInterest))


#Testing phase
def testing_phase(motion_activity):

    fiveMinSum = 0
    sleep_count = 0

    list_of_actigraph_data = data_from_ebe_file()
    print("Length of .ebe file: " + str(len(list_of_actigraph_data)))
    print("Length of motion activity: " + str(len(motion_activity)))
    for index in range(0, len(list_of_actigraph_data) - 1):
        if(list_of_actigraph_data[index] == 0):
            if(index >= 4):
                fiveMinSum += motion_activity[index - 4] + motion_activity[index - 3] + motion_activity[index - 2] + motion_activity[index - 1] + motion_activity[index]
            elif(index == 3):
                fiveMinSum += motion_activity[index - 3] + motion_activity[index - 2] + motion_activity[index - 1] + motion_activity[index]
            elif(index == 2):
                fiveMinSum += motion_activity[index - 2] + motion_activity[index - 1] + motion_activity[index]
            elif(index == 1):
                fiveMinSum += motion_activity[index - 1] + motion_activity[index]
            elif(index == 0):
                fiveMinSum = motion_activity[index]

            sleep_count += 1

    return (fiveMinSum, sleep_count)


def data_from_ebe_file():

    ebe_File_Path = "/Users/apoorvsgaur/Desktop/Apoorv/Classes/Spring 2016/EPICS/epics-sleep-video/Sleep Night 2/23055_9M_Sleep.ebe"

    fp = open(ebe_File_Path, 'r')
    data = fp.readline()
    list_of_motion_activity = []
    count = 0
    while (True):
        data = fp.readline()
        if (data != ""):
            #print(data)
            motion_activity_data = data.split()[6]
            #print(motion_activity_data)
            list_of_motion_activity.append(int(motion_activity_data))
        else:
            break

    return list_of_motion_activity

#Independent Sleep Assigning
def independent_sleep_assigning(motion_activity, calculated_fiveMinAvg):

    sleep_status = []
    list_of_actigraph_data = data_from_ebe_file()

    #awake_detect = 0
    awake_detect = 1
    awake_actigraph_detect = 0

    for index in range(0, len(motion_activity) - 1):
        if(index >=4):
            fiveMinAvg = (motion_activity[index - 4] + motion_activity[index - 3] + motion_activity[index - 2] + motion_activity[index - 1] + motion_activity[index]) / 5
            if (fiveMinAvg > calculated_fiveMinAvg):
                sleep_status.append(0)
                if(list_of_actigraph_data[index] == 0):
                    awake_actigraph_detect += 1
                awake_detect += 1
            else:
                sleep_status.append(1)
        elif (index == 3):
            fiveMinAvg = (motion_activity[index - 3] + motion_activity[index - 2] + motion_activity[index - 1] + motion_activity[index]) / 4
            if (fiveMinAvg > calculated_fiveMinAvg):
                sleep_status.append(0)
                if(list_of_actigraph_data[index] == 0):
                    awake_actigraph_detect += 1
                awake_detect += 1
            else:
                sleep_status.append(1)
        elif (index == 2):
            fiveMinAvg = (motion_activity[index - 2] + motion_activity[index - 1] + motion_activity[index]) / 3
            if (fiveMinAvg > calculated_fiveMinAvg):
                sleep_status.append(0)
                if(list_of_actigraph_data[index] == 0):
                    awake_actigraph_detect += 1
                awake_detect += 1
            else:
                sleep_status.append(1)
        elif (index == 1):
            fiveMinAvg = (motion_activity[index - 1] + motion_activity[index]) / 2
            if (fiveMinAvg > calculated_fiveMinAvg):
                sleep_status.append(0)
                if(list_of_actigraph_data[index] == 0):
                    awake_actigraph_detect += 1
                awake_detect += 1
            else:
                sleep_status.append(1)
        elif (index == 0):
            fiveMinAvg = motion_activity[index]
            if (fiveMinAvg > calculated_fiveMinAvg):
                sleep_status.append(0)
                if(list_of_actigraph_data[index] == 0):
                    awake_actigraph_detect += 1
                awake_detect += 1
            else:
                sleep_status.append(1)

    correct_percentage = awake_actigraph_detect / awake_detect
    return (sleep_status, correct_percentage)
