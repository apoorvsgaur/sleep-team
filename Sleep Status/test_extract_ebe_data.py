__author__ = 'apoorvsgaur'


ebe_File_Path = "/Users/apoorvsgaur/Desktop/Apoorv/Classes/Spring 2016/EPICS/epics-sleep-video/23001_24M/23001_24M Sleep Videos/23001_24M_Sleep.ebe"

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
        #count += 1
    #except:
    #    print(count)

print(len(list_of_motion_activity))
print(str(list_of_motion_activity))


