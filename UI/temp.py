import time #used in video playing
import datetime #also used in video playing
import glob #used in marging videos
import os #used in calling processes - may be obsolete
import subprocess #used in calling algorithms - very useful
import shutil
import mainwindow as mw #pyqt stuff 
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, QFileInfo, QTimer, QTime
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import *
import numpy as np #for histograms, as is the matplotlib stuff
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from matplotlib import dates as dates
from matplotlib.figure import Figure


def trp(l, n): #for padding a list with zeros to the desired length
    return l[:n] + [0]*(n-len(l))

class MyMplCanvas(FigureCanvas): #this, and the other Mpl class, is for displaying histograms within a pyqt5 gui
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi) #figure, and default features
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plotBars(self,data,labels): #a virtual function
        pass


class MyDynamicMplCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def plotBars(self,data,labels): #the plotBars we care about
        numMins = len(data) #to get the correct number fo bins
        r = range(numMins)
        width = 1
        self.axes.bar(r,data,width,color="blue",tick_label=labels,label='fit')
        
        #to display only every hundredth label - reduces clutter along the x axis
        for label in self.axes.xaxis.get_ticklabels()[::1]:
            label.set_visible(False)
        for label in self.axes.xaxis.get_ticklabels()[::100]:
            label.set_visible(True)
        for label in self.axes.xaxis.get_minorticklocs():
            label.set_visible(False)
        for label in self.axes.xaxis.get_minorticklocs():
            label.set_visible(False)
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("Act\nper\nMin",rotation=0)
        self.axes.axis('tight')
        self.axes.grid(False) #grid on makes everything unreadable
        self.draw()


#main ui class. This holds pretty much everything gui related.
class Ui_MainWindow(object):
        
    def pb(self): #this is the main entry into the dialog 
        mainFp = self.curFp.split()[0] #filename and path, except extension
        self.progressBar.setRange(0,0) #sets progress bar to the working animation
        self.pbmsg.hide()
        self.dialog.show() #helps if you can see it
        test = QFileInfo(mainFp+".AVI") #should we jump right into merging the video?
        if(test.exists() == False): #yes
            self.pbShown=1
            self.mergePart = 1 #flag, for buttons to react approprietly
            self.pbrun() #go to merging videos
        else: #no
            self.pbShown=0
            self.progressBar.hide()
            self.pbmsg.show() #asking if videos should be remerged
            self.pbmsg.setText('Merged file found. Overwrite?')
            self.pbyes.move(1,25)
            self.pbno.move(102,25)
            self.pbclose.move(520,25)
        self.mergePart = 1
            
    def pbint(self): #this is where we descide if we need to process the videos
        self.mergePart = 0 #no longer merging
        mainFp = self.curFp.split()[0] #filename and path, minus extension
        test = QFileInfo(mainFp+".txt")
        self.progressBar.hide() #don't show progress bar, yet
        self.pbmsg.show()
        self.pbyes.move(1,25) #move buttons, instead of changing functionality
        self.pbno.move(502,25)
        self.pbclose.setText('No')
        self.pbclose.move(102,25) #same text, but now goes closes dialog
        temp = glob.glob(mainFp+"*/*.AVI") #get list of avi files in folders
        self.progressBar.setRange(0,len(temp)) #sets progress bar too n/videos
        self.progressBar.setValue(1) #we're doing the first video
        if(test.exists() == True):
            self.pbmsg.setText('Old results found. Overwrite?') #dialog already set up to ask this
        else: #set stuff to start processng the video, then...
            self.progressBar.show()
            self.pbmsg.hide()
            self.dialog.setWindowTitle("Processing Video")
            self.pblabel.hide()
            self.pbclose.setText('Cancel')
            self.pbclose.move(52,25)
            self.pbyes.hide()
            self.pbno.hide()
            self.pbPro() #jump to processing the video files
            
            
    def pbPro(self): #we're here! Processing.....
        self.progressBar.show()
        self.dialog.repaint()
        mainFp = self.curFp.split()[0]
        #self.a = subprocess.Popen('top', stdout=subprocess.PIPE,universal_newlines=True,bufsize=1)
        self.a = subprocess.Popen(['python', 'image_contouring.py', mainFp], stdout=subprocess.PIPE,universal_newlines=True,bufsize=1) #this calls the image contouring algorithm. Takes filename and path variable because it uses that to glob for folders
        
        
        self.a.stdout.flush() #trying to grab piped output... (unsuccessfully)
        i = 0
        while(True): #pressing cancel will get you out of this
            
            print(i)
            self.progressBar.setValue(i) #sets the progress bar to show progress
            time.sleep(120) #timed, not from output of the algorithm :(
            i = i + 1
            
        
        
    def pbexit(self): #closes the dialog and kills any running processes
        self.run = 0
        if(self.a != 0):
            self.a.kill() #kill!!
        self.dialog.hide() #the dialog isn't actually destroyed until the program quits.  
        
    def pbrun(self): #main function to merge videos into one
        mainFp = self.curFp.split()[0] #filename and path, again
        mainFol = "/".join(mainFp.split("/")[:-1]) #this is to get just the filepath
        progDir = os.getcwd() #i like pwd, but...
        test = QFileInfo(mainFp+".AVI") #cleans out the directory of old files, if they exist
        if(test.exists() == True):
            os.remove(mainFp+'.AVI')
        test = QFileInfo(mainFol+"/mylist.txt")
        if(test.exists() == True):
            os.remove(mainFol+"/mylist.txt")
        self.pbmsg.hide()
        self.progressBar.show()
        self.pbyes.move(522,25)
        self.pbno.move(522,25)
        self.pbclose.move(52,25)
        self.dialog.repaint() #these repaint functions are important as the force redrawing of the dialog. Subprocess calls seem to make the dialog delay otherwise
        os.system("python3 "+progDir+'/concat.py \''+mainFp+'\'') #old school os style
        if(test.exists() == True):
            self.progressBar.setRange(0,1) #there be progress!
            while(test.exists() == False): #process still running apparently
                self.dialog.repaint()
                time.sleep(1)
            b = subprocess.Popen(['ffmpeg', '-f', 'concat', '-i', mainFol+"/mylist.txt", '-c', 'copy', mainFp+".AVI"],stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #new style! Classyer
            b.poll() #need to check if b is over
            while(b.returncode == None): #nope?
                time.sleep(5)
                b.poll()    #try again in 5
            test = QFileInfo(mainFp+".txt")
            self.progressBar.hide()
            self.pbmsg.show()
        if(test.exists() == True): #oh hey, you're already here!
            self.pbmsg.setText('Old results found. Overwrite?')
            self.pbno.move(1,25)
            self.pbclose.move(102,25)
            self.pbno.setText('Yes') #buttons already linked
            self.pbclose.setText('No') #pick me *wink*
            self.pbyes.hide()
        else:
            self.pbmsg.setText('Processing Files. May take hours') #ouch, will indeed take hours
            self.pbyes.hide()
            self.pbno.hide()
        
    def importFile(self): #imports the data! Who knew?
        try: #don't fail me :(
            mainFp = self.curFp.split()[0]
            test = QFileInfo(self.curFp)
            if(self.curFp.lower().endswith('.avi')): #user selected a video directly - old
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.curFp)))
            elif(test.isDir() == True): #user selected a folder - prefered method - hopefully the right folder
                self.pb() #make the files, will be quick if they already exist
                test = QFileInfo(mainFp+'.ebe')
                if(test.exists()): #load ebe (actigraphy) file
                    self.teList.clear()
                    self.treeWidget.clear()
                    self.mcList.clear()
                    ebeFile = open(mainFp+'.ebe','r')
                    ebeFile.readline()
                    l = []
                    l.append(QtWidgets.QTreeWidgetItem([self.curFp.split("/")[-1]])) #makes tree parent item
                    self.treeWidget.addTopLevelItems(l)
                    l = []
                    for line in ebeFile: #adds the data to the tree widget as it comes out of the file
                        sline = line.split()
                        self.treeWidget.topLevelItem(0).addChild(QtWidgets.QTreeWidgetItem([sline[4],sline[5],sline[6],sline[7],sline[8]]))
                        self.teList.append(sline[4].split(":")[0]) #also appends it to a list, for storage and histogramming
                        self.mcList.append(sline[5]) #this is the actual movement, the above is the time stamp
                    self.treeWidget.expandAll()
                    self.ebeList = [int(i) for i in self.mcList] #changing format
                    self.graphicsView_5.plotBars(self.ebeList,trp(self.teList,len(self.ebeList))) #plot!
                test = QFileInfo(mainFp+'.txt')
                if(test.exists()): #load generated data
                    self.taList.clear() #new times
                    self.mcList.clear() #new movements
                    txtFile = open(mainFp+'.txt','r')
                    txtFile.readline()
                    l = []
                    l.append(QtWidgets.QTreeWidgetItem([mainFp.split("/")[-1]]))
                    self.treeWidget_2.addTopLevelItems(l)
                    l = []
                    i = 0
                    sList = []
                    tempTime = self.time
                    for line in txtFile: #same idea as above. Appends to tree and lists, graphs, in this version
                        sline = line.split()
                        if(self.min < len(self.teList)):
                            self.treeWidget_2.topLevelItem(self.numAdded).addChild(QtWidgets.QTreeWidgetItem([self.time.toString(),sline[1],sline[2]]))
                            self.time = self.time.addSecs(60)
                        self.min = self.min + 1
                        self.taList.append(self.time.toString().split(":")[0])
                        self.mcList.append(sline[1])
                        sList.append(sline[2])
                    self.txtList = [int(float(i)) for i in self.mcList]
                    self.graphicsView_6.plotBars(self.txtList,trp(self.taList,len(self.txtList)))
                    self.numAdded = self.numAdded + 1
                    self.time = tempTime
                    self.treeWidget_2.expandAll()
                test = QFileInfo(mainFp+'.AVI')
                if(test.exists()): #loads video
                    self.player.setMedia(QMediaContent(QUrl.fromLocalFile(mainFp+'.AVI')))
            elif(self.curFp.lower().endswith('.ebe')): #onlt loading ebe file
                self.treeWidget.clear()
                ebeFile = open(self.curFp,'r')
                ebeFile.readline()
                l = []
                l.append(QtWidgets.QTreeWidgetItem([self.curFp.split("/")[-1]]))
                self.treeWidget.addTopLevelItems(l)
                l = []
                for line in ebeFile:
                    sline = line.split()
                    self.treeWidget.topLevelItem(0).addChild(QtWidgets.QTreeWidgetItem([sline[4],sline[5],sline[6],sline[7],sline[8]]))
                    self.teList.append(sline[4])
        except Exception as e:
            pass
        
    def pickEbeGraph(self): #chose ebe data as graph
        self.graphicsView_6.show()
        
    def pickTxtGraph(self): #chose txt data as graph
        self.graphicsView_6.hide()
        
    def pickFile(self,index): #function called when someone selects a fiel i nthe file tree view. Sets paths and extracts time 
        try:
            self.curFp = self.model.filePath(index)
            test = QFileInfo(self.curFp)
            if(test.isDir()):
                fileList = os.listdir(self.curFp)
                fileList.sort()
                time = fileList[0].split('_')[0]
                self.time.setHMS(int(time[:2]),int(time[2:4]),int(time[4:]))
                self.startTime.setHMS(int(time[:2]),int(time[2:4]),int(time[4:]))
                self.timeEdit.setTime(self.time)
        except Exception as e:
            pass
        
        
    def playVideo(self): #toggles play/pause of video
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.playing = False
        else:
            self.player.play()
            self.playing = True
            
    def stopVideo(self): #stop video button func
        self.player.pause()
        self.playing = False
        
    def changeVideoSpeed(self): #selecter for the video speed multiplyer
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
            
    def reversePlayback(self): #button to reverse video playback multiplyer
        if(self.playbackRate > 0):
            self.playbackRate = -1
        else:
            self.playbackRate = 1
        self.player.setPlaybackRate(self.playbackRate)
            
    def incCount(self): #function to increment video time counter
        self.time = self.startTime.addMSecs(self.player.position())
        self.timeEdit.setTime(self.time)
            
    def setTime(self): #sets the time of the video player when the video somnography tree is clicked
        time = self.treeWidget_2.currentItem().data(0,0).split(':')
        self.time.setHMS(int(time[0]),int(time[1]),int(time[2]))
        msOffset = self.startTime.msecsTo(self.time)
        if(msOffset >= 0):
            self.player.setPosition(msOffset)
        else:
            self.player.setPosition(86400000-self.startTime.msecsSinceStartOfDay()+self.time.msecsSinceStartOfDay())
            
    def setTime2(self): #sets the time of the video player when the actigrapy tree is clicked
        time = self.treeWidget.currentItem().data(0,0).split(':')
        self.time.setHMS(int(time[0]),int(time[1]),int(time[2]))
        msOffset = self.startTime.msecsTo(self.time)
        if(msOffset >= 0):
            self.player.setPosition(msOffset)
        else:
            self.player.setPosition(86400000-self.startTime.msecsSinceStartOfDay()+self.time.msecsSinceStartOfDay())
                   

    def linkUi(self, MainWindow): #links buttons to functions!
        self.pushButton.clicked.connect(self.importFile)
        self.listView2.clicked.connect(self.pickFile)
        self.pushButton_6.clicked.connect(self.playVideo)
        self.pushButton_7.clicked.connect(self.stopVideo)
        self.pushButton_8.clicked.connect(self.reversePlayback)
        self.comboBox_4.currentIndexChanged.connect(self.changeVideoSpeed)
        self.pbclose.clicked.connect(self.pbexit)
        self.pbno.clicked.connect(self.pbint)
        self.pbyes.clicked.connect(self.pbrun)
        self.player.positionChanged.connect(self.incCount)
        self.treeWidget_2.clicked.connect(self.setTime)
        self.treeWidget.clicked.connect(self.setTime2)
        self.vidSom.clicked.connect(self.pickEbeGraph)
        self.acti.clicked.connect(self.pickTxtGraph)

    def setupUi(self, MainWindow): #everything below here is simply the gui widget declarations. Boring stuff
        self.a = 0
        self.playing = False
        self.teList = []
        self.taList = []
        self.mcList = []
        self.pbShown = 0
        self.run = 1
        self.min = 0
        self.numAdded = 0
        self.mergePart = 0
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
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
        self.listView2.setRootIndex(self.model.index("/home/erich"))
        self.listView2.header().setDefaultSectionSize(300)
        self.gridLayout_3.addWidget(self.listView2, 0, 0, 2, 3)
        self.gridLayout_2.addWidget(self.frame_2, 0, 0, 1, 1)


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
        
        self.playbackRate = 1
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
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

    def retranslateUi(self, MainWindow):
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
        


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.linkUi(MainWindow)
    MainWindow.show()
    app.exec_()
    sys.exit(1)
