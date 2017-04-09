__author__ = 'apoorvsgaur'

import os

N = 14 #Number of the nights this algorithm is going to be run on. Half to get the thresholds using
       #actigraph. Half to test those thresholds

def delegate_list_of_motion_activity(motion_activity):

    name_of_main_text_file = "Sleep Status Thresholds"
    if (not(os.path.exists(name_of_main_text_file))):
        testing_phase(motion_activity, 0)
    else:

        #First line of main file will always be number of files processed
        file_pointer = open(name_of_main_text_file, 'r')
        first_line_of_file = file_pointer.readline()
        file_pointer.close()
        number_of_files_processed = first_line_of_file.replace("\n", "").split(":")[-1].strip()

        #If less than half the number of nights available have been analysed, use actigraph to
        #come up with thresholds, else use thresholds on motion activity data
        if(number_of_files_processed <= (N/2)):
            testing_phase(motion_activity, number_of_files_processed)
        else:
            independent_sleep_assigning(motion_activity)


#Testing
def testing_phase(motion_activity, number_of_nights_tested):
    pass


#
def independent_sleep_assigning(motion_activity):
    pass
