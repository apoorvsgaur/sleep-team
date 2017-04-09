import time
import datetime
import glob
import os
import subprocess
import shutil
import mainwindow as mw
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, QFileInfo, QTimer, QTime
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from matplotlib import dates as dates
from matplotlib.figure import Figure


def makemylist(output,vidList): #this function is used to make the mylist.txt file which is sent to ffmpeg to merge video.
    if(len(vidList) > 0): #I just pass it the particular array of video filepaths now. 
        f = open(output,'w')
        for fn in vidList:
            if(fn[0] == "/"):
                f.write("file '"+fn+"'\n")
            else:
                f.write("file '"+fn.replace("/","\\")+"'\n") #this is for windows systems. I built it on a Linux system, hence the if-else
        f.close()

def trp(l, n): #for padding a string with 0s to the right
    print("padding string of length "+str(len(l))+" to "+str(n))
    return l[:n] + [0]*(n-len(l))

class MyMplCanvas(FigureCanvas): #a custom canvas class so that matplotlib graphs can be displayed within a qt framework. This is the generic one
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plotBars(self,data,labels):
        pass


class MyDynamicMplCanvas(MyMplCanvas): #this is the more specific class. For plotting histograms
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def plotBars(self,data,labels,title):
        print("plotting")
        numMins = len(data)
        r = range(numMins)
        width = 1
        self.axes.bar(r,data,width,color="blue",tick_label=labels,label='fit')
        for label in self.axes.xaxis.get_ticklabels()[::1]:
            label.set_visible(False)
        for label in self.axes.xaxis.get_ticklabels()[::100]:
            label.set_visible(True)
        for label in self.axes.xaxis.get_minorticklocs():
            label.set_visible(False)
        for label in self.axes.xaxis.get_minorticklocs():
            label.set_visible(False)
        self.axes.set_xlabel("Time") #I've hard coded the axis labels, but if you would prefer to pass that in you can certainly do that. I did with the title
        self.axes.set_ylabel("Act\nper\nMin",rotation=0)
        self.axes.axis('tight')
        self.axes.grid(False)
        self.axes.set_title(title)
        self.draw()
        print("Done plotting")



class Ui_MainWindow(object):
    def handleButton(self): #now the entry point for actual video processing. Called by "Import" button
        test = QFileInfo(self.curFp)
        if(test.isDir() == False): #if it's not a directory then it must be an individual file and thus should only be imported, not processed.
            self.importFile()
        else: #first we build the arrays holding the video filepaths
            temp = glob.glob(self.curFp+"/*") #gets all the files/folders in the selected directory
            temp = [x for x in temp if os.path.isdir(x) == True] #pairs it down to only directories
            temp.sort() #the glob function is not gaurenteed to return a sorted list, so sort it
            for r in temp: #list comprehension was acting finicky, so I just did a loop. Temp is a short list anyways
                self.folList.append(r.split("/")[-1]) #you may have to switch this to \\ for windows systems
            oneHalf = []
            secHalf = []
            i = 0
            for fol in temp:
                test = QFileInfo(fol)
                if(test.isDir() == True): #all fol should be directories, since temp was paired down, but hey, better safe than frustrated
                    if(secHalf == [] and oneHalf == []): #first pass
                        secHalf = glob.glob(fol+"/*.AVI") #all the videos, regardless fo time, are the first half of the first night
                        secHalf.sort()
                        self.startTimes.append([self.folList[i],secHalf[0].split("/")[-1].split("_")[0]]) #the first video is considered the start time.
                    else:
                        oneHalf = glob.glob(fol+"/0*.AVI") + glob.glob(fol+"/10*.AVI") + glob.glob(fol+"/11*.AVI") #the morning videos in the current folder
                        oneHalf.sort()
                        full = secHalf+oneHalf #the night of the previous day, and then the morning of the current day
                        self.vidList.append([self.folList[i],full]) #stores the array of video filepaths connected with the date (of the first video, so the night before)
                        i = i + 1;
                        secHalf = glob.glob(fol+"/1*.AVI") + glob.glob(fol+"/2*.AVI") #All the videos not before 10 am
                        secHalf = [x for x in secHalf if x not in glob.glob(fol+"/10*.AVI")] #remove the videos in the 10 o'clock hour
                        secHalf = [x for x in secHalf if x not in glob.glob(fol+"/11*.AVI")] #remove the videos in the 11 o'clock hour
                        secHalf.sort()
                        if(i < len(self.folList) and len(secHalf) > 0):
                            self.startTimes.append([self.folList[i],secHalf[0].split("/")[-1].split("_")[0]]) #adds the first time for the current day beign procesed
            self.time.setHMS(int(self.startTimes[0][1][:2]),int(self.startTimes[0][1][2:4]),int(self.startTimes[0][1][4:])) #for importing data
            self.startTime.setHMS(int(self.startTimes[0][1][:2]),int(self.startTimes[0][1][2:4]),int(self.startTimes[0][1][4:])) #for videos
            self.timeEdit.setTime(self.time) #connecting the two
            self.pb() #now actually process the video


    def importing(self):
        try:
            test = QFileInfo(self.curFp+".txt")
            while(test.exists() == False):
                if(self.run == 0):
                    break
                test = QFileInfo(self.curFp+".txt")
            self.progressBar.setRange(0,1)
            self.pblabel.setText('                 Complete')
            self.pbclose.setText('Close')
        except Exception as e:
            pass

    def pb(self):
        print("pb")
        self.mergePart = 1 
        i = 0
        mainFp = [self.curFp + "/" + x[0] for x in self.vidList] #a list of filepaths; the folders containing the videos, not the videos themselves
        #most of the stuff between here and the next for loop are designed to draw the dialog box, but are not effective. please fix
        self.progressBar.setRange(0,0)
        self.pbmsg.hide()
        self.pbyes.move(1,25)
        self.pbno.move(102,25)
        self.pbyes.hide()
        self.pbno.hide()
        self.pbclose.hide()
        self.dialog.show()
        for path in mainFp: #iterate over each folder
            print(path+".AVI")
            test = QFileInfo(path+".AVI")
            print(test.exists())
            self.dialog.repaint()
            if(test.exists() == False): #if the merged video doesn't exist
                self.pbShown=1
                self.mergePart = 1
                self.dialog.repaint()
                self.pbrun(path,i) #merge videos. i is the index for refrencing vidList.
            url = QUrl.fromLocalFile(path+".AVI")
            self.playlist.addMedia(QMediaContent(url)) #Now add the merged video to the playlist
            self.txtFN = self.curFp+"/"+self.curFp.split("/")[-1]+"_"+path.split("/")[-1] #set the filepath for resultant text files. eg: folder/ID_Date.txt
            test = QFileInfo(self.txtFN+".txt")
            print(test.exists())
            if(test.exists() == False): #no output yet?
                self.pbmsg.show()
                self.pbmsg.setText(' Processing Files. May take hours')
                self.pbPro(i) #better process those videos!
            i += 1
        self.importFile() #all done processing. Head on over to import it all
        
    def yeschoose(self): #for the dialog box. Not used since the dialog box doesn't display buttons atm :(
        if(self.mergePart):
            self.pbrun()
        else:
            self.pbPro()


    def pbPro(self,vidnum): #video processing function
        print("pbPro")
        #more dialog box drawing functions :(
        self.pbmsg.hide()
        self.pblabel.setText(' Working. May take several hours')
        self.progressBar.show()
        self.pbclose.setText('Cancel')
        self.pbclose.move(52,25)
        self.pbyes.hide()
        self.pbno.hide()    
        self.dialog.repaint()
        if(self.curFp[0] == "/"): #on a unix system - call python (2.7 hopefully), if you want a different backend change it here!
            self.a = subprocess.Popen(['python', 'image_contouring.py', self.curFp,self.txtFN,str(vidnum)],universal_newlines=True,bufsize=1) #filepath, output filepath, and index for vidList (which it builds itself. Passing arrays through a terminal would be.... painful)
        else: #on a windows system. Same gig
            self.a = subprocess.Popen(['C:\Python27\python.exe', 'image_contouring.py', self.curFp,self.txtFN,str(vidnum)],universal_newlines=True,bufsize=1)
        self.progressBar.setValue(0)
        self.progressBar.setRange(0,1)
        while(self.a.poll() == None): #wait for subprocess a to finish
            pass
        self.progressBar.setValue(1)
        self.pblabel.setText('Done')
        self.pbclose.setText('Close') #all done! Go back to pb; check another video, or start importing



    def pbexit(self):
        self.run = 0
        if(self.a != 0):
            self.a.kill()
        self.dialog.hide()

    def pbrun(self,output,vidnum): #merging video function
        print("pbrun")
        print(self.mergePart)
        test = QFileInfo(output+".AVI")
        if(test.exists() == True): #remove old merged video. This used to happen, but shouldn't ever anymore
            os.remove(output+".AVI")
        test = QFileInfo(self.curFp+"/mylist.txt")
        if(test.exists() == True): #mylist, however, is cleaned up basically every time, since a new one needs to be generated for each night
            os.remove(self.curFp+"/mylist.txt")
        self.pbmsg.hide()
        self.progressBar.show()
        self.pbyes.move(522,25)
        self.pbno.move(522,25)
        
        self.pbclose.move(52,25)
        self.dialog.repaint()
        makemylist(self.curFp+"/mylist.txt",self.vidList[vidnum][1]) #call fucntion to make text file
        if(test.exists() == True): #if it doesn't exists now... a filesystem access issue? Or worse.
            self.progressBar.setRange(0,1)
            #while(test.exists() == False):
            #    self.dialog.repaint()
            #    time.sleep(1)

            command = "ffmpeg -f concat -safe 0 -i "+self.curFp+"/mylist.txt -c copy "+output+".AVI" #for debuging
            
            print("Command: " + command) #buggy squashy tooly
            #print("MainFol: " + mainFol)
            #print("mainFp: " + mainFp)
            #os.system(command)
            if(self.curFp[0] == "/"): #against, unix system
                b = subprocess.Popen(['ffmpeg', '-f', 'concat','-safe', '0', '-i', self.curFp+"/mylist.txt", '-c', 'copy', output+".AVI"]) #concat command. uses Ffmpeg. Look up the concat command for ffmpeg to understand all these (annoying/stupid/weird/etc) parameters
            else: #yeah, Windows #sarcasm
                b = subprocess.Popen(['ffmpeg', '-f', 'concat','-safe', '0', '-i', self.curFp.replace("/","\\")+"\mylist.txt", '-c', 'copy', output.replace("/","\\")+".AVI"])
            b.poll()
            while(b.returncode == None): #wait for subprocess to finish
                time.sleep(5) #don't overtax the pc - let it rest for 5 secs since the process will take hours...
                b.poll()
            self.progressBar.hide()
            self.pbmsg.show() #all done, back to pb()

    def importFile(self):
        self.dialog.hide()
        print("import file")
        try: #sometimes fails on certain filepaths. Hopefully fixed, but you never know...
            test = QFileInfo(self.curFp)
            if(self.curFp.lower().endswith('.avi')): #user wants to load a single video. Let them
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.curFp)))
            elif(test.isDir() == True): #this is the main (and recommended) way to import data
                print("is dir")
                idx = 0
                mainFp = [self.curFp + "/" + x[0] for x in self.vidList] #again, folderpaths of folders with videos directly in them
                for path in mainFp:
                    print(path)
                    self.txtFN = self.curFp+"/"+self.curFp.split("/")[-1]+"_"+path.split("/")[-1] #set output filepath to current day being imported
                    test = QFileInfo(self.txtFN+'.ebe') #does it exist? If not processign failed miserably :(
                    # if(test.exists()):
                    #     self.teList.clear()
                    #     self.treeWidget.clear()
                    #     self.mcList.clear()
                    #     ebeFile = open(mainFp+'.ebe','r')
                    #     ebeFile.readline()
                    #     l = []
                    #     l.append(QtWidgets.QTreeWidgetItem([self.curFp.split("/")[-1]]))
                    #     self.treeWidget.addTopLevelItems(l)
                    #     l = []
                    #     for line in ebeFile:
                    #         sline = line.split()
                    #         self.treeWidget.topLevelItem(0).addChild(QtWidgets.QTreeWidgetItem([sline[4],sline[5],sline[6],sline[7],sline[8]]))
                    #         self.teList.append(sline[4].split(":")[0])
                    #         self.mcList.append(sline[5])
                    #     self.treeWidget.expandAll()
                    #     self.ebeList = [int(i) for i in self.mcList]
                    #     self.graphicsView_5.plotBars(self.ebeList,trp(self.teList,len(self.ebeList)))
                    test = QFileInfo(self.txtFN+'.txt') #the above was around when .ebe files were automatically loaded. Feel free to reimplement that, but be aware of the actual filestructure
                    if(test.exists()): #Yay! Import that text data!
                        self.taList.clear()
                        self.mcList.clear()
                        txtFile = open(self.txtFN+'.txt','r')
                        print(self.txtFN+'.txt')
                        txtFile.readline()
                        curhead = QtWidgets.QTreeWidgetItem([path.split("/")[-1]]) #make a new top-level item in the actigraph data tree - call it the date
                        l = []
                        l.append(curhead)
                        self.treeWidget_2.addTopLevelItems(l) #add it
                        i = 0
                        sList = []
                        self.time.setHMS(int(self.startTimes[idx][1][:2]),int(self.startTimes[idx][1][2:4]),int(self.startTimes[idx][1][4:])) #set time to start for this day
                        for line in txtFile:
                            sline = line.split() #split on whitespace
                            self.treeWidget_2.topLevelItem(idx).addChild(QtWidgets.QTreeWidgetItem([self.time.toString(),sline[1],sline[2]])) #time.toString() for consistency. This has a flaw - depends on consecutive videos. Can be fixed with more processing. Good luck!
                            self.time = self.time.addSecs(60) #increment time object
                            self.taList.append(self.time.toString().split(":")[0]) #store data for later use *cough* graphing *cough*
                            self.mcList.append(sline[1]) #see previous comment
                            sList.append(sline[2])
                        txtFile.close()
                        self.txtList = [int(float(i)) for i in self.mcList] #convert list to ints. necessary for graphing
                        self.infoList.append([self.txtList,trp(self.taList,len(self.txtList))]) #save data to an associative array
                        self.graphicsView_6.plotBars(self.txtList,trp(self.taList,len(self.txtList)),self.folList[idx]) #plot
                        self.treeWidget_2.expandAll() #show the user the data!
                    idx += 1 #next folder
                self.time.setHMS(int(self.startTimes[0][1][:2]),int(self.startTimes[0][1][2:4]),int(self.startTimes[0][1][4:])) #set video time to start of the first video
                self.tabWidget.setCurrentIndex(1) #open the video tab, since processing is done!
                # elif(self.curFp.lower().endswith('.ebe')):
                #     self.treeWidget.clear()
                #     ebeFile = open(self.curFp,'r')
                #     ebeFile.readline()
                #     l = []
                #     l.append(QtWidgets.QTreeWidgetItem([self.curFp.split("/")[-1]]))
                #     self.treeWidget.addTopLevelItems(l)
                #     l = []
                #     for line in ebeFile:
                #         sline = line.split()
                #         self.treeWidget.topLevelItem(0).addChild(QtWidgets.QTreeWidgetItem([sline[4],sline[5],sline[6],sline[7],sline[8]]))
                #         self.teList.append(sline[4].split(":")[0])
                #         self.mcList.append(sline[5])
                #     self.treeWidget.expandAll()
                #     self.ebeList = [int(i) for i in self.mcList]
                #     self.graphicsView_5.plotBars(self.ebeList,trp(self.teList,len(self.ebeList)))
                #     test = QFileInfo(mainFp+'.txt')
                #     if(test.exists()):
                #         self.taList.clear()
                #         self.mcList.clear()
                #         txtFile = open(mainFp+'.txt','r')
                #         txtFile.readline()
                #         l = []
                #         l.append(QtWidgets.QTreeWidgetItem([mainFp.split("/")[-1]]))
                #         self.treeWidget_2.addTopLevelItems(l)
                #         l = []
                #         i = 0
                #         sList = []
                #         tempTime = self.time
                #         for line in txtFile:
                #             sline = line.split()
                #             if(self.min < len(self.teList)):
                #                 self.treeWidget_2.topLevelItem(self.numAdded).addChild(QtWidgets.QTreeWidgetItem([self.time.toString(),sline[1],sline[2]]))
                #                 self.time = self.time.addSecs(60)
                #             self.min = self.min + 1
                #             self.taList.append(self.time.toString().split(":")[0])
                #             self.mcList.append(sline[1])
                #             sList.append(sline[2])
                #     self.txtList = [int(float(i)) for i in self.mcList]
                #     self.graphicsView_6.plotBars(self.txtList,trp(self.taList,len(self.txtList)))
                #     self.numAdded = self.numAdded + 1
                #     self.time = tempTime
                #     self.treeWidget_2.expandAll()
            elif(self.curFp.lower().endswith('.ebe')): #loading a single .ebe file - needs work, but does display those files...
                self.treeWidget.clear()
                ebeFile = open(self.curFp,'r')
                ebeFile.readline()
                print("3rd if")
                l = []
                l.append(QtWidgets.QTreeWidgetItem([self.curFp.split("/")[-1]])) #Put data within a head item
                self.treeWidget.addTopLevelItems(l)
                l = []
                for line in ebeFile:
                    sline = line.split()
                    self.treeWidget.topLevelItem(0).addChild(QtWidgets.QTreeWidgetItem([sline[4],sline[5],sline[6],sline[7],sline[8]])) #there are lots of fields in the ebe files. You will probably need to add more, especially the date field. If not for display atleast for parsing.
                    self.teList.append(sline[4])
        except Exception as e:
                print (e) #how did it fail? :(
            
                    
    def pickEbeGraph(self): #the ebe graph is no longer made with normal operation - This would hide the processed data histogram to show it
        self.graphicsView_6.show()

    def pickTxtGraph(self): #covers ebe histogram with the processed data one
        self.graphicsView_6.hide()

    def pickFile(self,index): #called when somethign is clicked in the file tree
        try: #fails on some filepaths. Will happen, but not for anything we can actually use it seems
            self.curFp = self.model.filePath(index)
            print(self.curFp) #will have to be changed to \\ for windows system
            self.txtFN = str("/".join(self.curFp.split("/")[:-1])) + "/" +str(self.curFp.split("/")[-2].split("-")[0]) + "_" + str(self.curFp.split("/")[-1].split("-")[0]) #overwritten later, but hey, good for debuging
            print(self.txtFN)
            print()
            # test = QFileInfo(self.curFp)
            # if(test.isDir()):
            #     fileList = os.listdir(self.curFp)
            #     fileList.sort()
            #     time = fileList[0].split('_')[0]
            #     self.time.setHMS(int(time[:2]),int(time[2:4]),int(time[4:]))
            #     self.startTime.setHMS(int(time[:2]),int(time[2:4]),int(time[4:]))
            #     self.timeEdit.setTime(self.time)
        except Exception as e:
            pass #since it fails when navigating to the desired folder no reason to scare the users, although they shouldn't see print statemetns anyways...


    def playVideo(self): #play button function zzzzzz
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.playing = False
        else:
            self.player.play()
            self.playing = True

    def stopVideo(self): #does the same thing as the play button except doesn't start the video. This probably should reset the tiem too...
        self.player.pause()
        self.playing = False

    def changeVideoSpeed(self): #allows the user to play the video up to 16x speeds. Simply changes the multiplier used to play the video
        if(self.playbackRate > 0):
            if(self.comboBox_4.currentIndex() == 0):
                self.playbackRate = 1
            elif(self.comboBox_4.currentIndex() == 1):
                self.playbackRate = 4
            elif(self.comboBox_4.currentIndex() == 2):
                self.playbackRate = 8
            elif(self.comboBox_4.currentIndex() == 3):
                self.playbackRate = 16
        elif(self.playbackRate < 0):
            self.comboBox_4.setCurrentIndex(0)
            if(self.comboBox_4.currentIndex() == 0):
                self.playbackRate = -1
        self.player.setPlaybackRate(self.playbackRate)

    def reversePlayback(self): #sort fo buggy. You may just want to get rid of this as seeking sort of makes this pointless
        if(self.playbackRate > 0):
            self.playbackRate = -1
        else:
            self.playbackRate = 1
        self.player.setPlaybackRate(self.playbackRate)

    def incCount(self): #called to increment the timer. I don't think it's used. Probably...
        self.time = self.startTime.addMSecs(self.player.position())
        self.timeEdit.setTime(self.time)

    def setTime(self): #called when clicking the video data list - seeks in the video
        try:
            # self.treeWidget_2.topLevelItem(0).text(0)
            # print(self.treeWidget_2.topLevelItem(0).indexOfChild(self.treeWidget_2.currentIndex()))
            a = self.treeWidget_2.currentItem().parent().data(0,0)
            b = self.folList.index(a)
            if(b != self.playlist.currentIndex()): #don't reload the video if the correct one is already loaded
                self.playlist.setCurrentIndex(self.folList.index(a)) #change playlist to seleted day's video
                self.graphicsView_6.plotBars(self.infoList[self.folList.index(a)][0],self.infoList[self.folList.index(a)][1],self.folList[self.folList.index(a)]) #plot the new graph for the selected day
            time = self.treeWidget_2.currentItem().data(0,0).split(':') #within the loaded video, set the time to the selected time
            self.time.setHMS(int(time[0]),int(time[1]),int(time[2])) #update display to match
            msOffset = self.startTime.msecsTo(self.time) #get the millisecodn offset, so you can set the video position
            if(msOffset >= 0): #the time is before midnight, so easy 
                self.player.setPosition(msOffset)
                print(msOffset)
            else: #time is after midnight - adjust for different merged video start times
                self.player.setPosition(86400000-self.startTime.msecsSinceStartOfDay()+self.time.msecsSinceStartOfDay())
                print(86400000-self.startTime.msecsSinceStartOfDay()+self.time.msecsSinceStartOfDay())
        except Exception as e:
            print(e) #shouldn't fail. Does sometimes in odd situations

    def setTime2(self): #called when clicking the actigraphy data list - seeks in the video - will probably fail with new file structure setup until new ebe loading is done
        try:
            a = self.treeWidget.currentItem().parent().data(0,0)
            b = self.folList.index(a)
            if(b != self.playlist.currentIndex()): #don't reload the video if the correct one is already loaded
                self.playlist.setCurrentIndex(self.folList.index(a)) #change playlist to seleted day's video
                self.graphicsView_6.plotBars(self.infoList[self.folList.index(a)][0],self.infoList[self.folList.index(a)][1],self.folList[self.folList.index(a)]) #plot the new graph for the selected day
            time = self.treeWidget.currentItem().data(0,0).split(':') #within the loaded video, set the time to the selected time
            self.time.setHMS(int(time[0]),int(time[1]),int(time[2])) #update display to match
            msOffset = self.startTime.msecsTo(self.time) #get the millisecodn offset, so you can set the video position
            if(msOffset >= 0): #the time is before midnight, so easy 
                self.player.setPosition(msOffset)
                print(msOffset)
            else: #time is after midnight - adjust for different merged video start times
                self.player.setPosition(86400000-self.startTime.msecsSinceStartOfDay()+self.time.msecsSinceStartOfDay())
                print(86400000-self.startTime.msecsSinceStartOfDay()+self.time.msecsSinceStartOfDay())
        except Exception as e:
            print(e)

    def changeDrive(self): #allows the user to select a specific drive in a windows environment. Probably unnecessary, but option are always good
        if(self.comboBox_1.currentIndex() == 0):
            self.listView2.setRootIndex(self.model.index(""))
        elif(self.comboBox_1.currentIndex() == 1):
            self.listView2.setRootIndex(self.model.index("C:"))
        elif(self.comboBox_1.currentIndex() == 2):
            self.listView2.setRootIndex(self.model.index("G:"))
        elif(self.comboBox_1.currentIndex() == 3):
            self.listView2.setRootIndex(self.model.index("H:"))
        elif(self.comboBox_1.currentIndex() == 3):
            self.listView2.setRootIndex(self.model.index("I:"))
        elif(self.comboBox_1.currentIndex() == 4):
            self.listView2.setRootIndex(self.model.index("J:"))

    def clear(self): #function to clear the video tab and any stored data - NOT CONNECTED TO ANYTHING YET
        self.a = 0
        self.playing = False
        self.txtFN = ''
        self.teList = []
        self.taList = []
        self.mcList = []
        self.vidList = []
        self.startTimes = []
        self.infoList = []
        self.folList = []
        self.pbShown = 0
        self.run = 1
        self.min = 0
        self.numAdded = 0
        self.mergePart = 0
        self.treeWidget_2.clear()
        self.treeWidget.clear()


    def linkUi(self, MainWindow): #comments here show which button is actually calling the function
        self.pushButton.clicked.connect(self.handleButton) #import button
        self.listView2.clicked.connect(self.pickFile) #click in file tree
        self.pushButton_6.clicked.connect(self.playVideo) #play button
        #self.counter.timeout.connect(self.incCount)
        self.pushButton_7.clicked.connect(self.stopVideo) #stop button
        self.pushButton_8.clicked.connect(self.reversePlayback) #reverse button
        self.comboBox_4.currentIndexChanged.connect(self.changeVideoSpeed) #video speed combo box, when changed
        self.comboBox_1.currentIndexChanged.connect(self.changeDrive) #drive selector combo box, when changed
        self.pbclose.clicked.connect(self.pbexit) #close button - in dialog
        self.pbyes.clicked.connect(self.yeschoose) #yes button - in dialog
        self.player.positionChanged.connect(self.incCount) #called any time the video is playing - every second or thereabouts
        self.treeWidget_2.clicked.connect(self.setTime) #called on click in video data list
        self.treeWidget.clicked.connect(self.setTime2) #called on click in actigraphy data list
        self.vidSom.clicked.connect(self.pickEbeGraph) #Video Somnography button
        self.acti.clicked.connect(self.pickTxtGraph) #Actigraphy button

    def setupUi(self, MainWindow): #this is where all the UI elements are made
        #this section has most of the data structure initilizations here
        self.a = 0
        self.playing = False
        self.txtFN = ''
        self.teList = []
        self.taList = []
        self.mcList = []
        self.vidList = []
        self.startTimes = []
        self.infoList = []
        self.folList = []
        self.pbShown = 0
        self.run = 1
        self.min = 0
        self.numAdded = 0
        self.mergePart = 0
        #Most of what follow was automatically generated by an initial Qt designer file.
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 700)
        self.dialog = QtWidgets.QDialog(MainWindow)
        self.dialog.setWindowTitle("Importing")
        self.dialog.setGeometry(30, 40, 500, 100)
        self.dialogGrid = QtWidgets.QGridLayout(self.dialog)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralWidget.sizePolicy().hasHeightForWidth())
        self.centralWidget.setSizePolicy(sizePolicy)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        #all the dialog box stuff was aded by hand - sorry
        self.progressBar = QtWidgets.QProgressBar(self.dialog)
        self.progressBar.setRange(0,1)
        self.progressBar.setWindowTitle('Merging Videos')
        font = QtGui.QFont()
        font.setBold(True)
        self.pbmsg = QtWidgets.QLabel(self.dialog)
        self.pbmsg.setText('Output Info Here')
        self.pbmsg.setFont(font)
        self.pbmsg.setGeometry(0, 0, 200, 25)
        self.pblabel = QtWidgets.QLabel(self.progressBar)
        self.pblabel.setText(' Working. May take several mins')
        self.pblabel.setFont(font)
        self.progressBar.setGeometry(0, 0, 500, 25)
        self.progressBar.hide()
        self.pbclose = QtWidgets.QPushButton('Cancel',self.dialog)
        self.pbclose.move(52,25)
        self.pbyes = QtWidgets.QPushButton('Yes',self.dialog)
        self.pbyes.move(520,20)
        self.pbno = QtWidgets.QPushButton('No',self.dialog)
        self.pbno.move(520,20)
        #self.pblabel.setGeometry(30, 40, 200, 25)



        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QtCore.QSize(40, 40))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.frame_2 = QtWidgets.QFrame(self.tab)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pushButton_3 = QtWidgets.QPushButton(self.frame_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_3.addWidget(self.pushButton_3, 2, 2, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.frame_2)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout_3.addWidget(self.pushButton, 2, 0, 1, 1)
        self.model = QFileSystemModel()
        self.model.setRootPath("/home")
        self.listView2 = QtWidgets.QTreeView(self.frame_2)
        self.listView2.setObjectName("listView2")
        self.listView2.setModel(self.model)
        self.listView2.setRootIndex(self.model.index("")) #this is where the default file tree filepath is set
        self.listView2.header().setDefaultSectionSize(300)
        self.gridLayout_3.addWidget(self.listView2, 0, 0, 2, 3)
        self.gridLayout_2.addWidget(self.frame_2, 0, 0, 1, 1)

        self.comboBox_1 = QtWidgets.QComboBox(self.frame_2)
        self.comboBox_1.setObjectName("comboBox_1") #add one item for each possible drive letter - tailored to the epics laptop atm
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.comboBox_1.addItem("")
        self.gridLayout_3.addWidget(self.comboBox_1, 2, 1, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout.setObjectName("gridLayout")
        self.frame_4 = QtWidgets.QFrame(self.tab_2)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.frame_4)
        self.gridLayout_7.setObjectName("gridLayout_7")
 
        #The video stuff was added by hand too 0 again, sorry for the pain in editing
        self.playbackRate = 1
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.video = QVideoWidget(self.frame_4)
        self.player.setVideoOutput(self.video)
        self.video.setObjectName("video")
        self.gridLayout_7.addWidget(self.video, 3, 5, 9, 5)

        self.vidSom = QtWidgets.QPushButton('Video Somnography', self.frame_4)
        self.gridLayout_7.addWidget(self.vidSom, 12, 6)
        self.acti = QtWidgets.QPushButton('Actigraphy',self.frame_4)
        self.gridLayout_7.addWidget(self.acti, 12, 5)
        self.vidNorm = QtWidgets.QPushButton('Normal Video',self.frame_4)
        self.gridLayout_7.addWidget(self.vidNorm, 9, 10)
        self.vidThresh = QtWidgets.QPushButton('Difference Video',self.frame_4)
        self.gridLayout_7.addWidget(self.vidThresh, 10, 10)
        self.vidThresh.setEnabled(False)

        self.pushButton_6 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout_7.addWidget(self.pushButton_6, 3, 10, 1, 1)
        self.comboBox_4 = QtWidgets.QComboBox(self.frame_4)
        self.comboBox_4.setObjectName("comboBox_4")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.gridLayout_7.addWidget(self.comboBox_4, 7, 10, 1, 1)
        self.pushButton_8 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_8.setObjectName("pushButton_8")
        self.gridLayout_7.addWidget(self.pushButton_8, 5, 10, 1, 1)
        self.pushButton_7 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_7.setObjectName("pushButton_7")
        self.gridLayout_7.addWidget(self.pushButton_7, 4, 10, 1, 1)
        self.counter = QTimer()
        self.counter.start(1000)
        self.time = QTime(0,0)
        self.startTime = QTime(0,0)
        self.timeEdit = QtWidgets.QTimeEdit(self.time,self.frame_4)
        self.timeEdit.setMaximumDateTime(QtCore.QDateTime(QtCore.QDate(2000, 1, 1), QtCore.QTime(23, 59, 59)))
        self.timeEdit.setMinimumTime(QtCore.QTime(0, 0, 0))
        self.timeEdit.setCurrentSection(QtWidgets.QDateTimeEdit.HourSection)
        self.timeEdit.setDisplayFormat("hh:mm:ss")
        self.timeEdit.setObjectName("timeEdit")
        self.gridLayout_7.addWidget(self.timeEdit, 8, 10, 1, 1)
        self.label_24 = QtWidgets.QLabel(self.frame_4)
        self.label_24.setAlignment(QtCore.Qt.AlignCenter)
        self.label_24.setObjectName("label_24")
        self.gridLayout_7.addWidget(self.label_24, 6, 10, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.frame_4)
        self.label_10.setText("")
        self.label_10.setObjectName("label_10")
        self.gridLayout_7.addWidget(self.label_10, 0, 4, 1, 1)
        
        #here is where I connect the custom class to allow matplotlib graphs to be displayed. This is why I ended up doing most of the UI by hand. Feel free to change this
        self.graphicsView_5 = MyDynamicMplCanvas(self.frame_4, width=5, height=4, dpi=100)
        self.graphicsView_5.setObjectName("graphicsView_5")
        self.gridLayout_7.addWidget(self.graphicsView_5, 13, 5, 1, 6)
        self.graphicsView_6 = MyDynamicMplCanvas(self.frame_4, width=5, height=4, dpi=100)
        self.graphicsView_6.setObjectName("graphicsView_6")
        self.gridLayout_7.addWidget(self.graphicsView_6, 13, 5, 1, 6)
        spacerItem3 = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem3, 11, 10, 1, 1)
        self.treeWidget = QtWidgets.QTreeWidget(self.frame_4)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setAutoScroll(False)
        self.treeWidget.header().setDefaultSectionSize(40)
        self.gridLayout_7.addWidget(self.treeWidget, 3, 0, 11, 2)
        self.treeWidget_2 = QtWidgets.QTreeWidget(self.frame_4)
        self.treeWidget_2.setObjectName("treeWidget_2")
        self.gridLayout_7.addWidget(self.treeWidget_2, 3, 2, 11, 2)
        self.label_2 = QtWidgets.QLabel(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout_7.addWidget(self.label_2, 0, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(120, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem4, 0, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.gridLayout_7.addWidget(self.label_7, 0, 2, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(120, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem5, 0, 3, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem6, 0, 6, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.frame_4)
        self.label_8.setObjectName("label_8")
        self.gridLayout_7.addWidget(self.label_8, 0, 5, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.frame_4)
        self.label_9.setObjectName("label_9")
        self.gridLayout_7.addWidget(self.label_9, 0, 10, 1, 1)
        self.gridLayout.addWidget(self.frame_4, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 771, 25))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow): #this is where you set the default text of many of the buttons, etc
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Sleep Assessment Tool"))
        self.pushButton_3.setText(_translate("MainWindow", "Clear"))
        self.pushButton.setText(_translate("MainWindow", "Import"))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Files"))
        self.pushButton_6.setText(_translate("MainWindow", "Play/Pause"))
        self.comboBox_4.setItemText(0, _translate("MainWindow", "1x"))
        self.comboBox_4.setItemText(1, _translate("MainWindow", "4x"))
        self.comboBox_4.setItemText(2, _translate("MainWindow", "8x"))
        self.comboBox_4.setItemText(3, _translate("MainWindow", "16x"))
        self.comboBox_1.setItemText(0, _translate("MainWindow", ""))
        self.comboBox_1.setItemText(1, _translate("MainWindow", "C:"))
        self.comboBox_1.setItemText(2, _translate("MainWindow", "G:"))
        self.comboBox_1.setItemText(3, _translate("MainWindow", "H:"))
        self.comboBox_1.setItemText(4, _translate("MainWindow", "I:"))
        self.comboBox_1.setItemText(5, _translate("MainWindow", "J:"))
        self.pushButton_8.setText(_translate("MainWindow", "Rewind"))
        self.pushButton_7.setText(_translate("MainWindow", "Stop"))
        self.label_24.setText(_translate("MainWindow", "Speed:"))
        self.label_2.setText(_translate("MainWindow", "Actigraphy"))
        self.label_7.setText(_translate("MainWindow", "Video Activity"))
        self.label_8.setText(_translate("MainWindow", "Video"))
        self.label_9.setText(_translate("MainWindow", "Controls"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Video"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Time"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Act"))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Sleep"))
        self.treeWidget.headerItem().setText(3, _translate("MainWindow", "Down"))
        self.treeWidget.headerItem().setText(4, _translate("MainWindow", "Bad"))
        self.treeWidget_2.headerItem().setText(0, _translate("MainWindow", "Time"))
        self.treeWidget_2.headerItem().setText(1, _translate("MainWindow", "Act"))
        self.treeWidget_2.headerItem().setText(2, _translate("MainWindow", "Sleep"))



if __name__ == "__main__": #this program uses python 3.5+, even though the subprocess mostly use python 2.7
    import sys
    app = QtWidgets.QApplication(sys.argv) #make the app object
    MainWindow = QtWidgets.QMainWindow() #make the window object
    ui = Ui_MainWindow() 
    ui.setupUi(MainWindow) #setup the ui
    ui.linkUi(MainWindow) #link the ui with the functions they should call
    MainWindow.show() #show it in all its glory!
    app.exec_() #and.... run!
    sys.exit(1) #all done. If it made it this far it probably exited successfully
