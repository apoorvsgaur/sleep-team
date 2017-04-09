import sys
import copy
import os
import glob

def compare_r(l1,l2):
    x=0
    w=0
    for a in l1:
        if a==l2[x]:
            w=w+1
        x=x+1
    return [w,len(l1),float(w)/float(len(l1))]

def create_range(r,b,step):
    l=[]
    while r<=b:
        r=r+step
        l.append(r)
    return l

def format_printer(result,path):
    with open(path,'a') as outfile:
        for a in result:
             outfile.write("%s\n"% a)

def read_actigraph(path):
    with open(path,'r') as myfile:
            all_lines=myfile.readlines()
            time=0
            move=[]
            temp=[]
            sleep=[]
            for num,line in enumerate(all_lines):
                if num==0:
                    title=line.split()
                    print title
                else:
                    temp=line.split()
                    if int(temp[7])==1: #and int(temp[6])==0:
                        move.append(int(temp[5]))
                        sleep.append(int(temp[6]))
    return [move,sleep]

def find_ma(l):
    ma1=max(l)
    l.remove(ma1)
    ma2=max(l)
    l.remove(ma2)
    ma3=max(l)
    l.remove(ma3)
    ma4=max(l)
    l.remove(ma4)
    ma5=max(l)
    return int((ma1+ma2+ma3+ma4+ma5)/5)

def identify_category(l):
    maax=find_ma(l)
    mmm=sum(l)/len(l)
    return [mmm*1000/maax,mmm]

def generate_sleep_state(window,coef1,coef2,mmm,move):
    result=[]
    threshold=coef1*mmm
    threshol2=threshold*coef2
    index=0
    sflag=0
    for a in range(0,len(move)-window):
        mean=0
        for ww in range(window):
            mean=mean+move[index+ww]
        mean=mean/window
        if sflag==0:
            if mean>=threshold:
                result.append(0)
                sflag=0
            else:
                result.append(1)
                sflag=1
        else:
            if mean>=threshol2:
                result.append(0)
                sflag=0
            else:
                result.append(1)
                sflag=1
        index=index+1
    for w in range(window):
        result.append(0)
    return result

def trainning():
    file_list=glob.glob("*.ebe")
    category_list=[]
    for ff in file_list:
        [move,sleep]=read_actigraph(ff)
        l=[]
        result_list=[]
        haha=[]
        threshold_list=[]
        [category,mmm]=identify_category(copy.deepcopy(move))
        coef1_list=create_range(0.8*mmm,3*mmm,0.1)
        coef2_list=create_range(1,3.5,0.1)
        window_list=range(1,2)
        for window in window_list:
            for coef1 in coef1_list:
                for coef2 in coef2_list:
                    result=[]
                    threshold=coef1
                    threshol2=threshold*coef2
                    index=0
                    sflag=0
                    threshold_list.append([window,coef1/mmm,coef2])
                    for a in range(0,len(move)-window):
                        mean=0
                        for ww in range(window):
                            mean=mean+move[index+ww]
                        mean=mean/window
                        if sflag==0:
                            if mean>=threshold:
                                result.append(0)
                                sflag=0
                            else:
                                result.append(1)
                                sflag=1
                        else:
                            if mean>=threshol2:
                                result.append(0)
                                sflag=0
                            else:
                                result.append(1)
                                sflag=1
                        index=index+1
                    for w in range(window):
                        result.append(0)
                    bb=[]
                    bb=compare_r(sleep,result)
                    result_list.append(bb)
                    haha.append(bb[2])
        print max(haha)
        print len(result_list)
        index=haha.index(max(haha))
        category_list.append([category,threshold_list[index]])
        print category_list
    return category_list

def read_contouring(path):
    with open(path,'r') as myfile:
        all_lines=myfile.readlines()
        move=[]
        temp=[]
        for num,line in enumerate(all_lines):
            if num!=0:
                temp=line.split()
                move.append(int(temp[1]))
    return move

def read_optical(path):
    with open(path,'r') as myfile:
        all_lines=myfile.readlines()
        move=[]
        temp=[]
        for num,line in enumerate(all_lines):
            if num!=0:
                temp=line.split()
                move.append(int(float(temp[1])*100))

def using_data(category_list,path):
    #[move,sleep]=read_actigraph("23021_30M.ebe")
    move=read_contouring(path)
    [category,mmm]=identify_category(copy.deepcopy(move))
    index=0
    i=0
    diff_previous=float("inf")
    for cc in category_list:
        ccc=cc[0]
        diff=abs(int(category)-int(ccc))
        print diff
        if diff<diff_previous:
            diff_previous=diff
            index=i
        i=i+1
    print category_list[index]
    selected=category_list[index]
    parameters=selected[1]
    result=generate_sleep_state(parameters[0],parameters[1],parameters[2],mmm,move)
    return result

if __name__=="__main__":
    category_list=trainning()
    result=using_data(category_list,"130903-whole2.txt")
    print category_list
    print result
    format_printer(result,"130903-whole2.txt")