import sys
import glob
#print(sys.argv[1])
files = glob.glob(sys.argv[1]+"*/*.AVI")
#print(len(files))
files.sort()
fp = sys.argv[1].split("/")
#print("/".join(fp[:-1])+"/mylist.txt")
if(len(files) > 0):
    f = open("/".join(fp[:-1])+"/mylist.txt",'w')
    for fn in files:
        f.write("file '"+fn+"'\n")
    f.close()
