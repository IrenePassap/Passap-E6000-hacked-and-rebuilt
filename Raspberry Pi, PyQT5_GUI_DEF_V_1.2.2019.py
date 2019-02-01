
import random, sys
import PyCmdMessenger
import struct
import RPi.GPIO as GPIO
import time
import sqlite3
import time
import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QLineEdit, QMessageBox, QLabel, QFileDialog, QDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore, QtWidgets, QtGui

import csv


from PIL import Image

# Setup Pin for interrupt
switchGPIO = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(switchGPIO, GPIO.IN)

patNum = 11

rowCount = 0
rowCount_VNB = 0
rowCount_HNB = 0

# Default pattern number
patNum_VNB = 201
patNum_HNB = 202

# Counter for technique file
countTech = 0
tech = 2
tech_Array = []

needlePos_VNB = 1
needlePos_HNB = 1

directionChanged = 0

# Array for knit pattern
knitpattern_VNB = []
knitpattern_HNB = []

flagRight = 0
flagLeft = 1

# left and right end of the knitting
rightEndData = 0
leftEndData = 180

# height of knitting pattern
height_VNB = 0
height_HNB = 0

# settings
colorSetting = ""
lockSetting_VNB = ""
lockSetting_HNB = ""

mg_VNB = 0.0
mg_HNB = 0.0

infoTech = ""




# connect to VNB Arduino M0 (front lock)
a = PyCmdMessenger.ArduinoBoard('/dev/ttyUSB-ArduinoVNB',115200)
a.enable_dtr=False
a.int_bytes=4
connectionVNB = PyCmdMessenger.CmdMessenger(a, [["sPat", "b*"],["sbPat", "b*"],
                                             ["setEmptyPat", "b*"], ["sbEmptyPat", "b*"],
                                             ["setNPos", "l"],["sbNPos", "l*"],
                                             ["getNPos", ""],["sendNPos", "l"],   
                                             ["sRowCount", "i"], ["sbRowCount", "l*"],
                                             ["setLeEnd", "i"], ["sbLeEnd", "l"],
                                             ["setRiEnd", "i"], ["sbRiEnd", "l"],
                                             ])

# connect to HNB Arduino M0 Pro (back lock)
b = PyCmdMessenger.ArduinoBoard('/dev/ttyUSB-ArduinoHNB',115200)
b.enable_dtr=False
b.int_bytes=4
connectionHNB = PyCmdMessenger.CmdMessenger(b, [["sPat", "b*"],["sbPat", "b*"],
                                             ["setEmptyPat", "b*"], ["sbEmptyPat", "b*"],                                              
                                             ["setNPos", "l"],["sbNPos", "l*"],  
                                             ["getNPos", ""],["sendNPos", "l"],
                                             ["sRowCount", "i"], ["sbRowCount", "l*"],  
                                             ["setLeEnd", "i"], ["sbLeEnd", "l"],
                                             ["setRiEnd", "i"], ["sbRiEnd", "l"],
                                             ])    

# =================================================
# SQLite Table
# =================================================

print("")
print("========================================")


tableID = 1

def create_table():

    global tableID
    
    conn = sqlite3.connect('passapProject.db')
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS stuffToPlot(tabID INTEGER,datestamp TEXT, rV INTEGER, rH INTEGER,'
              'dirC INTEGER, neV INTEGER, neH INTEGER,'
              'tec INTEGER, cTec INTEGER)')

    c.execute('CREATE TABLE IF NOT EXISTS staticSettings(tabID INTEGER,datestamp TEXT, rV INTEGER, rH INTEGER,'
              'dirC INTEGER, neV INTEGER, neH INTEGER,'
              'patV INTEGER, patH INTEGER, tec INTEGER, cTec INTEGER, leE INTEGER, riE INTEGER, mgV REAL, mgH REAL)')


    tableID = max_tabID(c)

    
    def execute_tableID_info(c):
        c.execute("SELECT tabID, datestamp, rV, rH, dirC, neV, neH, tec, cTec FROM stuffToPlot WHERE tabID = :tabID", {"tabID": tableID})

        result = c.fetchone()

        print("{:<6s}{:>4d}".format("tabID:", result[0]))
        print("{:<6s}{:>4s}".format("date:",result[1]))
        print("{:<6s}{:>4d}".format("rV:",result[2]))
        print("{:<6s}{:>4d}".format("rH:",result[3]))
        print("{:<6s}{:>4d}".format("dirC:",result[4]))
        print("{:<6s}{:>4d}".format("neV:", result[5]))
        print("{:<6s}{:>4d}".format("neH:", result[6]))
        print("{:<6s}{:>4d}".format("tec:", result[7]))
        print("{:<6s}{:>4d}".format("cTec:", result[8]))
       

    try:
        execute_tableID_info(c)
        tableID += 1
        print("new tabID: ", tableID)
        print("========================================")
        print("")
    except:
        pass
    
    c.close()
    conn.close()
    

def max_tabID(cursor):

    try:    
        cursor.execute("SELECT MAX(tabID) FROM stuffToPlot")

        result = cursor.fetchone()
        value = result[0]
        return int(value)

    except:
        return 0

    # print ("max_tabID is: ", value)

    



create_table()

def dynamic_date_entry_settings():

    global tableID

    conn = sqlite3.connect('passapProject.db')
    c = conn.cursor()

    rV = rowCount_VNB
    rH = rowCount_HNB
    dirC = directionChanged
    neV = needlePos_VNB
    neH = needlePos_HNB
    tec = tech
    cTec = countTech
    tabID = tableID

    unix = time.time()
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%d-%m-%Y %H:%M:%S'))

    c.execute("INSERT INTO stuffToPlot(tabID, datestamp, rV, rH, dirC, neV, neH, tec, cTec) VALUES (?,?,?,?,?,?,?,?,?)",(tableID, date, rowCount_VNB, rowCount_HNB, directionChanged, needlePos_VNB, needlePos_HNB, tech, countTech))
       
    conn.commit()

    tableID +=1
    print("tabID: ", tableID)
    
    c.close()
    conn.close()

def static_date_entry_settings():

    global tableID

    conn = sqlite3.connect('passapProject.db')
    c = conn.cursor()

    rV = rowCount_VNB
    rH = rowCount_HNB
    dirC = directionChanged
    neV = needlePos_VNB
    neH = needlePos_HNB
    patV = patNum_VNB
    patH = patNum_HNB
    tec = tech
    cTec = countTech
    leE = leftEndData
    riE = rightEndData
    mgV = mg_VNB
    mgH = mg_HNB
    tabID = tableID
   
    unix = time.time()
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%d-%m-%Y %H:%M:%S'))

    c.execute("INSERT INTO staticSettings(tabID, datestamp, rV, rH, dirC, neV, neH, patV, patH, tec, cTec, leE, riE, mgV, mgH) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(tableID, date, rowCount_VNB, rowCount_HNB, directionChanged, needlePos_VNB, needlePos_HNB, patNum_VNB, patNum_HNB,tech, countTech, leftEndData, rightEndData, mg_VNB, mg_HNB))

    conn.commit()

    tableID +=1
    
    c.close()
    conn.close()

    print("static tabID: ", tableID)
    
    
def drop_index():
    conn = sqlite3.connect('passapProject.db')
    c = conn.cursor()

    c.execute("DROP INDEX [IF EXISTS] index_tabID")

# =================================================
# Original Pattern
# =================================================

def get_pattern(data):
    filename = Image.open(data)

    global heightMy

    widthMy = filename.size[0]
    heightMy = filename.size[1]

    count = 0;
    listMy = []

    for x in range(0, heightMy):

        row = []

        for y in range(0, widthMy):
            pixel = (y, x)
            rgbMy, *wast = filename.getpixel(
                pixel)  # I only read the first value, the other two values are passed to the variable * wast

            if rgbMy == 0:
                row.append(0)
            else:
                row.append(1)

        listMy.append(row)
    

    # gets array row by row
    def pattern_Array(data):

        pattern_data = listMy[data]

        n = 0
        m = 0
        pattern = [0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0, 0b0,
                   0b0, 0b0, 0b0]

        while m < 22:

            for y in range(0, 8):

                val = pattern_data[n]
                n += 1

                if val == 0:
                    pattern[m] = pattern[m].__lshift__(1)
                else:
                    pattern[m] = pattern[m].__lshift__(1)
                    pattern[m] |= 1
            m += 1

        return pattern

    knitpattern = []

    for i in range(0, heightMy):
        pattern_new = pattern_Array(i)
        knitpattern.append(pattern_new)

    n = 0

    return knitpattern



#//////////////////////////////////////////////////////////////////////


# good to know: the received list (received_cmd) is a two-dimensional list and the
# values can therefore only be read out with name [1] [0]

# get needle position from arduino front lock, rear lock

def get_needlePos_VNB():
    global needlePos_VNB
    connectionVNB.send("getNPos")       
    received_VNB = connectionVNB.receive()
    needlePos_VNB = received_VNB[1][0]
    #print("needle VNB: ", needlePos_VNB)

def get_needlePos_HNB():
    global needlePos_HNB
    connectionHNB.send("getNPos")       
    received_HNB = connectionHNB.receive()  
    needlePos_HNB = received_HNB[1][0]   
    #print("needle HNB: ", needlePos_HNB)

  

def returnTechData(number):

    data = []

    with open(str(number)+".txt") as f:
        reader = csv.reader(f)
        for r in reader:
            data.append(r)
        data.pop(0)

    return data

# sets technique values
def techArray():
    
    global rowCount_VNB
    global rowCount_HNB
    global countTech 

    if countTech >= len(tech_Array):
        countTech = 0

    x = tech_Array[countTech][0]
    x = int(x)
    rowCount_VNB = int(rowCount_VNB) + x

    if rowCount_VNB >= height_VNB:
        rowCount_VNB = 0


    y = tech_Array[countTech][1]
    y = int(y) 
    rowCount_HNB = int(rowCount_HNB) + y    

    if rowCount_HNB >= height_HNB:
        rowCount_HNB = 0

    techSet[tech_Array[countTech][2]]()
    techSet[tech_Array[countTech][3]]()

    # new settings
    global lockSetting_VNB
    global lockSetting_HNB
    global colorSetting
    global infoTech
 
    lockSetting_VNB = tech_Array[countTech][4]   
    lockSetting_HNB = tech_Array[countTech][5]
  
    colorSetting = tech_Array[countTech][6]

    infoTech = tech_Array[countTech][7]
    
    countTech += 1
    
    newLabelText()
    
    newSettings()

    dynamic_date_entry_settings()
    
    print("end: ", time.clock())
    

# Raspberry Pi interrupt        
def inputChange(switchGPIO):

    print("start: ", time.clock())

    get_needlePos_VNB()
    
    global flagRight
    global flagLeft
    global directionChanged

    #print("dirC:", directionChanged)

    if (flagRight == 1 and needlePos_VNB < int(rightEndData)):
        flagRight = 0
        flagLeft = 1
        directionChanged +=1      
        techArray()
        print("dirC right:", directionChanged)

    elif (flagLeft == 1 and needlePos_VNB > int(leftEndData)):
        flagLeft = 0
        flagRight = 1
        directionChanged +=1
        techArray()
        print("dirC left:", directionChanged)

# interrupt
GPIO.add_event_detect(switchGPIO, GPIO.RISING, callback=inputChange, bouncetime=200)


#//////////////////////////////////////////////////////////////////////
    
def sendRow_toArduino():
    
    for h in range(1):

        num_args=len(knitpattern_VNB[rowCount_VNB])

        connectionVNB.send("sPat", num_args, *knitpattern_VNB[rowCount_VNB][:]) 
        received_cmd = connectionVNB.receive()
        #cmd = received_cmd[0]

        received = received_cmd[1]
        #received_time = received_cmd[2]
        success = 1

        for i in range (1):
           
            if knitpattern_VNB[rowCount_VNB][i] == received[i]:
                success *= 1
            else:
                success = 0

            if success == 0:
                success = "FAIL"
            else:
                success = "PASS"

        print("VNB: ",rowCount_VNB,success)
      

        
    
def sendRow_toArduino_HNB():
    
    for h in range(1):

        num_args=len(knitpattern_HNB[rowCount_HNB])

        connectionHNB.send("sPat", num_args, *knitpattern_HNB[rowCount_HNB][:]) 
        received_cmd = connectionHNB.receive()
        #cmd = received_cmd[0]
  
        received = received_cmd[1]
        #received_time = received_cmd[2]
        success = 1

        for i in range (1):
           
            if knitpattern_HNB[rowCount_HNB][i] == received[i]:

                success *= 1
            else:
                success = 0

            if success == 0:
                success = "FAIL"
            else:
                success = "PASS"

        print("HNB: ",rowCount_HNB, success)

      
def send_emptyRow_toArduino():
    send_emptyRow_VNB()
    send_emptyRow_HNB()

def send_emptyRow_VNB():

    pattern = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]

    num_args = len(pattern)
    connectionVNB.send("setEmptyPat", num_args, *pattern)

    received_cmd = connectionVNB.receive()

    #cmd = received_cmd[0]
    received = received_cmd[1]
    #received_time = received_cmd[2]

    try:
        if received!=None:
            pass
    except:
        print("No value")

    success = 1

    for i in range (num_args):
        if pattern[i] == received[i]:
            success *= 1
        else:
            success = 0

    if success == 0:
        success = "FAIL"
    else:
        success = "PASS"

    print("EmptyRow VNB: ", success)


def send_emptyRow_HNB():

    pattern = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]

    num_args = len(pattern)

    connectionHNB.send("setEmptyPat", num_args, *pattern)

    received_cmd = connectionHNB.receive()

    #cmd = received_cmd[0]
    received = received_cmd[1]
    #received_time = received_cmd[2]

    try:
        if received!=None:
            pass
    except:
        print("No value")

    success = 1

    for i in range (num_args):
        if pattern[i] == received[i]:
            success *= 1
        else:
            success = 0

    if success == 0:
        success = "FAIL"
    else:
        success = "PASS"

    print("EmptyRow HNB: ", success)


def send_fullRow_VNB():

    pattern = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    num_args = len(pattern)
    connectionVNB.send("setEmptyPat", num_args, *pattern)

    received_cmd = connectionVNB.receive()

    #cmd = received_cmd[0]
    received = received_cmd[1]
    #received_time = received_cmd[2]

    try:
        if received!=None:
            pass
    except:
        print("No value")

    success = 1

    for i in range (num_args):
        if pattern[i] == received[i]:
            success *= 1
        else:
            success = 0

    if success == 0:
        success = "FAIL"
    else:
        success = "PASS"

    print("fullRow VNB: ", success)


def send_fullRow_HNB():

    pattern = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    num_args = len(pattern)

    connectionHNB.send("setEmptyPat", num_args, *pattern)

    received_cmd = connectionHNB.receive()

    #cmd = received_cmd[0]
    received = received_cmd[1]
    #received_time = received_cmd[2]

    try:
        if received!=None:
            pass
    except:
        print("No value")

    success = 1

    for i in range (num_args):
        if pattern[i] == received[i]:
            success *= 1
        else:
            success = 0

    if success == 0:
        success = "FAIL"
    else:
        success = "PASS"

    print("fullRow HNB: ", success)

def send_none():
    pass

# enum
techSet = {'kV': sendRow_toArduino, 'eV': send_emptyRow_VNB, 'nV': send_fullRow_VNB, 'kH': sendRow_toArduino_HNB, 'eH': send_emptyRow_HNB, 'nH': send_fullRow_HNB, '0': send_none}



# ...     

def set_back_Row_VNB(data):
    global rowCount_VNB
    rowCount_VNB = int(data)

def set_back_Row_HNB(data):
    global rowCount_HNB
    rowCount_HNB = int(data)  


def show_height():
    pass

def set_null_pos():
    connectionVNB.send("setNPos", 100)

    received_cmd = connectionVNB.receive()
    received = received_cmd[1][0]

    try:
        if received!=None:
            pass
    except:
        print("No value")

    print("VNB 0Pos: ", received)

    #///

    connectionHNB.send("setNPos", 100)

    received_cmd = connectionHNB.receive()
    received = received_cmd[1][0]

    try:
        if received!=None:
            pass
    except:
        print("No value HNB")

    print("HNV 0Pos: ", received)

# set the row counter Arduino back, until now it has no spezific function only information and synchronisation with Raspi
# first number ist the Arduino counter, second number is the changed Arduino counter, thired number is the sent counter
def get_rowCount(data_VNB, data_HNB):

    connectionVNB.send("sRowCount", int(data_VNB))       
    received = connectionVNB.receive()
    print("VNB rowCount: ", received[1][0], received[1][1], data_VNB)

    #///
    
    connectionHNB.send("sRowCount", int(data_HNB))       
    received = connectionHNB.receive()
    print("HNB rowCount: ", received[1][0], received[1][1], data_HNB)
    

def set_dirChange_to_0():
    global directionChange
    directionChange = 0
    print("directionChange: ", directionChange)

def get_rowCount_back():
    get_rowCount(rowCount_VNB, rowCount_HNB)
    
def setLeftEnd(data):
    leftEnd = int(data)
    connectionVNB.send("setLeEnd", int(leftEnd))
    received = connectionVNB.receive()
    print("VNB left end Arduino: ", received[1][0])

    #///

    connectionHNB.send("setLeEnd", int(leftEnd))
    received = connectionHNB.receive()
    print("HNB left end Arduino: ", received[1][0])
  

def setRightEnd(data):
    rightEnd = int(data)
    connectionVNB.send("setRiEnd", int(rightEnd))
    received = connectionVNB.receive()
    print("VNB right end Arduino: ", received[1][0])

    #////

    connectionHNB.send("setRiEnd", int(rightEnd))
    received = connectionHNB.receive()
    print("HNB right end Arduino: ", received[1][0])




#======================================================================
# GUI PyQT5
#======================================================================
numb = ""
newNum = ""
doneN = False


# interface
class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Passap'
        self.left = 150
        self.top = 70
        self.width = 600
        self.height = 380
        self.autoFillBackground()

        self.initUI()

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.show()

    # pop up to confirm action
    
    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, 'Extract!', "You want to close?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            print("Extracting Now")
            QT.Core.QCoreApplication.instance().quit
        else:
            pass


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        extractAction = QtWidgets.QAction("&Quit", self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip('Leave the App')
        extractAction.triggered.connect(self.close_application)

        extractActionEdit = QtWidgets.QAction("&Edit", self)
        extractActionEdit.setShortcut("Ctrl+E")
        extractActionEdit.setStatusTip('Edit the App')

        openEditor = QtWidgets.QAction("&Editor new", self)
        openEditor.setShortcut("Ctrl+E")
        openEditor.setStatusTip('Open Editor')
        openEditor.triggered.connect(self.editor)

        openFile = QtWidgets.QAction("&Open File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Open File Editor')
        openFile.triggered.connect(self.file_open)

        saveFile = QtWidgets.QAction("&Save Settings", self)
        saveFile.setShortcut("Ctrl+S")
        saveFile.setStatusTip('Save File Editor')
        saveFile.triggered.connect(self.save_static_settings)

        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(extractActionEdit)
        fileMenu.addAction(extractAction)
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

        editorMenu = mainMenu.addMenu("&Editor")
        editorMenu.addAction(extractActionEdit)
        editorMenu.addAction(openEditor)

        viewMenu = mainMenu.addMenu('View')
        searchMenu = mainMenu.addMenu('Search')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        self.show()


    def editor(self):
        self.textEdit = QtWidgets.QTextEdit()
        self.setCentralWidget(self.textEdit)

    def file_open(self): pass

    def file_save(self): pass

    def save_static_settings(self):
        static_date_entry_settings() 


class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tabWidget screen
        self.tabWidget = QtWidgets.QTabWidget()
        font = QFont()
        font.setPointSize(14)
        self.tabWidget.setFont(font)

        self.tab1 = QtWidgets.QWidget(self)
        self.tab2 = QtWidgets.QWidget(self)
        self.tabWidget.resize(600, 380)

        # Add tabs
        self.tabWidget.addTab(self.tab1, "Settings")
        self.tabWidget.addTab(self.tab2, "Process")

        ########################################################################## Tab1 PushButton

        def set_static_settings():
            static_date_entry_settings()    

        # Add buttons

        # Number pad for all settings
        self.numPad = QtWidgets.QPushButton('NumbPad', self.tab1)
        self.numPad.setStyleSheet("background-color:rgb(204,255,229)")
        self.numPad.setEnabled(True)
        self.numPad.setGeometry(QtCore.QRect(10, 20, 100, 60))
        self.numPad.clicked.connect(self.showdialog)

        self.nPos = QtWidgets.QPushButton('0Pos', self.tab1)
        self.nPos.setEnabled(True)
        self.nPos.setGeometry(QtCore.QRect(10, 90, 100, 60))
        self.nPos.clicked.connect(set_null_pos)
        
        self.emptyRowBtn = QtWidgets.QPushButton('EmptyRow', self.tab1)
        self.emptyRowBtn.setEnabled(True)
        self.emptyRowBtn.setGeometry(QtCore.QRect(10, 160, 100, 60))
        self.emptyRowBtn.clicked.connect(send_emptyRow_toArduino)

        self.rowCountArduino = QtWidgets.QPushButton('RowCount', self.tab1)
        self.rowCountArduino.setEnabled(True)
        self.rowCountArduino.setGeometry(QtCore.QRect(10, 230, 100, 60))
        self.rowCountArduino.clicked.connect(get_rowCount_back)

        self.directionBtn = QtWidgets.QPushButton('DirC_0', self.tab1)
        self.directionBtn.setEnabled(True)
        self.directionBtn.setGeometry(QtCore.QRect(120, 90, 100, 60))
        #self.directionBtn.clicked.connect(set_dirChange)
        self.directionBtn.clicked.connect(set_dirChange_to_0)

        self.musterBtn = QtWidgets.QPushButton('SendPat', self.tab1)
        self.musterBtn.setEnabled(True)
        self.musterBtn.setGeometry(QtCore.QRect(120, 160, 100, 60))
        self.musterBtn.clicked.connect(techArray)    

        # static settings
        self.numPad_process = QtWidgets.QPushButton('StaticData', self.tab1)
        self.numPad_process.setStyleSheet("background-color:rgb(204,255,229)")
        self.numPad_process.setEnabled(True)
        self.numPad_process.setGeometry(QtCore.QRect(230, 20, 100, 60))
        self.numPad_process.clicked.connect(set_static_settings)


        # Add labels
        self.label_left = QLabel("Left end", self.tab1)
        self.label_left.setGeometry(QtCore.QRect(410, 0, 120, 60))
        self.label_left.setBaseSize(QtCore.QSize(30, 30))
        self.label_left.show()

        self.label_right = QLabel("Right end", self.tab1)
        self.label_right.setGeometry(QtCore.QRect(410, 25, 120, 60))
        self.label_right.setBaseSize(QtCore.QSize(30, 30))
        self.label_right.show()

        self.label_height_VNB = QLabel("HeightVNB", self.tab1)
        self.label_height_VNB.setGeometry(QtCore.QRect(410, 50, 170, 60))
        self.label_height_VNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_height_VNB.show()

        self.label_height_HNB = QLabel("HeightHNB", self.tab1)
        self.label_height_HNB.setGeometry(QtCore.QRect(410, 75, 170, 60))
        self.label_height_HNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_height_HNB.show()

        self.label_row_VNB = QLabel("Set row", self.tab1)
        self.label_row_VNB.setGeometry(QtCore.QRect(410, 100, 120, 60))
        self.label_row_VNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_row_VNB.show()

        self.label_row_HNB = QLabel("Set row", self.tab1)
        self.label_row_HNB.setGeometry(QtCore.QRect(410, 125, 120, 60))
        self.label_row_HNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_row_HNB.show()
        
        self.label_direction = QLabel("dirChange", self.tab1)
        self.label_direction.setGeometry(QtCore.QRect(410, 150, 220, 60))
        self.label_direction.setBaseSize(QtCore.QSize(30, 30))
        self.label_direction.show()

        self.label_pat_VNB = QLabel("Pat_VNB", self.tab1)
        self.label_pat_VNB.setGeometry(QtCore.QRect(410, 175, 220, 60))
        self.label_pat_VNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_pat_VNB.show()

        self.label_pat_HNB = QLabel("Pat_HNB", self.tab1)
        self.label_pat_HNB.setGeometry(QtCore.QRect(410, 200, 220, 60))
        self.label_pat_HNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_pat_HNB.show()

        self.label_tech = QLabel("Tech", self.tab1)      
        self.label_tech.setGeometry(QtCore.QRect(410, 225, 220, 60))
        self.label_tech.setBaseSize(QtCore.QSize(30, 30))
        self.label_tech.show()

        self.fontlab = QFont ('Consolas bold', 16)
        self.fontlab.setBold(True)

        

        # Add labels Processing Data
        self.label_col = QLabel("Color", self.tab2)
        self.label_col.setGeometry(QtCore.QRect(150, 20, 220, 60))
        self.label_col.setBaseSize(QtCore.QSize(30, 30))
        self.label_col.setFont(self.fontlab)
        self.label_col.setStyleSheet("color:rgb(200,50,0)")
        self.label_col.setStyleSheet("background-color:rgb(230,230,230)")
        self.label_col.show()

        self.label_direction_2 = QLabel("dirChange", self.tab2)
        self.label_direction_2.setGeometry(QtCore.QRect(150,65, 220, 60))
        self.label_direction_2.setBaseSize(QtCore.QSize(30, 30))
        self.label_direction_2.show()
        

        self.label_lock_VNB = QLabel("Lock_V", self.tab2)
        self.label_lock_VNB.setGeometry(QtCore.QRect(150, 95, 220, 60))
        self.label_lock_VNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_lock_VNB.show()

        self.label_lock_HNB = QLabel("Lock_H", self.tab2)
        self.label_lock_HNB.setGeometry(QtCore.QRect(150, 125, 220, 60))
        self.label_lock_HNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_lock_HNB.show()

        self.label_row_VNB_2 = QLabel("Set row", self.tab2)
        self.label_row_VNB_2.setGeometry(QtCore.QRect(150, 155, 220, 60))
        self.label_row_VNB_2.setBaseSize(QtCore.QSize(30, 30))
        self.label_row_VNB_2.show()

        self.label_row_HNB_2 = QLabel("Set row", self.tab2)
        self.label_row_HNB_2.setGeometry(QtCore.QRect(150, 185, 220, 60))
        self.label_row_HNB_2.setBaseSize(QtCore.QSize(30, 30))
        self.label_row_HNB_2.show()

        self.label_text = QLabel("Info", self.tab2)
        self.label_text.setGeometry(QtCore.QRect(150, 230, 400, 60))
        self.label_text.setBaseSize(QtCore.QSize(30, 30))
        self.label_text.setFont(self.fontlab)
        self.label_text.setStyleSheet("color:rgb(200,50,0)")
        self.label_text.setStyleSheet("background-color:rgb(230,230,230)")
        self.label_text.show()

        ###

        self.label_MG_VNB = QLabel("MG_VNB", self.tab2)
        self.label_MG_VNB.setGeometry(QtCore.QRect(410, 20, 220, 60))
        self.label_MG_VNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_MG_VNB.show()

        self.label_MG_HNB = QLabel("MG_HNB", self.tab2)
        self.label_MG_HNB.setGeometry(QtCore.QRect(410, 50, 220, 60))
        self.label_MG_HNB.setBaseSize(QtCore.QSize(30, 30))
        self.label_MG_HNB.show()

        self.label_pat_VNB_2 = QLabel("Pat_VNB", self.tab2)
        self.label_pat_VNB_2.setGeometry(QtCore.QRect(410, 80, 220, 60))
        self.label_pat_VNB_2.setBaseSize(QtCore.QSize(30, 30))
        self.label_pat_VNB_2.show()

        self.label_pat_HNB_2 = QLabel("Pat_HNB", self.tab2)
        self.label_pat_HNB_2.setGeometry(QtCore.QRect(410, 110, 220, 60))
        self.label_pat_HNB_2.setBaseSize(QtCore.QSize(30, 30))
        self.label_pat_HNB_2.show()

        self.label_tech_2 = QLabel("Tech", self.tab2)      
        self.label_tech_2.setGeometry(QtCore.QRect(410, 140, 220, 60))
        self.label_tech_2.setBaseSize(QtCore.QSize(30, 30))
        self.label_tech_2.show()

        

        def sendData():
            print("send start")
            setLeftEnd(leftEndData)
            setRightEnd(rightEndData)


        global newLabelText
        global newSettings

        def newLabelText():
            self.label_left.setText("leftEnd: " + str(leftEndData))
            self.label_right.setText("rightEnd: " + str(rightEndData))
            self.label_row_VNB.setText("rowVNB: " + str(rowCount_VNB))
            self.label_row_HNB.setText("rowHNB: " + str(rowCount_HNB))
            self.label_height_VNB.setText("height_VNB: " + str(height_VNB))
            self.label_height_HNB.setText("height_HNB: " + str(height_HNB))
            self.label_direction.setText("dirChange: " + str(directionChanged))
            self.label_pat_VNB.setText("pattern_VNB: " + str(patNum_VNB))
            self.label_pat_HNB.setText("pattern_HNB: " + str(patNum_HNB))
            self.label_tech.setText("Tech: " + str(tech))
          

        def newSettings():
            self.label_col.setText("Change to " + colorSetting)
            self.label_lock_VNB.setText("Lock_VNB: " + lockSetting_VNB)
            self.label_lock_HNB.setText("Lock_HNB: " + lockSetting_HNB)
            self.label_row_VNB_2.setText("rowVNB: " + str(rowCount_VNB))
            self.label_row_HNB_2.setText("rowHNB: " + str(rowCount_HNB))
            self.label_text.setText("Info: " + infoTech)
            self.label_direction_2.setText("dirChange: " + str(directionChanged))
            self.label_pat_VNB_2.setText("pattern_VNB: " + str(patNum_VNB))
            self.label_pat_HNB_2.setText("pattern_HNB: " + str(patNum_HNB))
            self.label_MG_VNB.setText("MG_VNB: " + str(mg_VNB))
            self.label_MG_HNB.setText("MG_HNB: " + str(mg_HNB))
            self.label_tech_2.setText("Tech: " + str(tech))

        # Shows data, button
        self.showData = QtWidgets.QPushButton('Data', self.tab1)
        self.showData.setEnabled(True)
        self.showData.setGeometry(QtCore.QRect(120, 20, 100, 60))
        self.showData.clicked.connect(newLabelText)

        # send data, button
        self.showData = QtWidgets.QPushButton('Send', self.tab1)
        self.showData.setEnabled(True)
        self.showData.setGeometry(QtCore.QRect(120, 230, 100, 60))
        self.showData.clicked.connect(sendData)
            




        #======================== Tab 2


        # Number pad settings knit process
        self.numPad_process = QtWidgets.QPushButton('NumbPad', self.tab2)
        self.numPad_process.setStyleSheet("background-color:rgb(204,255,229)")
        self.numPad_process.setEnabled(True)
        self.numPad_process.setGeometry(QtCore.QRect(10, 20, 100, 60))
        self.numPad_process.clicked.connect(self.showdialog)

        # Shows data, button
        self.showSettings = QtWidgets.QPushButton('Settings', self.tab2)
        self.showSettings.setEnabled(True)
        self.showSettings.setGeometry(QtCore.QRect(10, 90, 100, 60))
        self.showSettings.clicked.connect(newSettings)



        
        #==============================================
        
 
        # Wichtig, sonst funktioniert nichts mehr!!!! Add tabWidget to widget
        self.layout.addWidget(self.tabWidget)
        self.setLayout(self.layout)


    def getNumX(self):
        global numb
        global newNum
        global allNum

        #print("connected " + newNum)
        numb += newNum
        #print("New number " + numb)

    def clickedMe(self):
        global newNum
        sender = self.sender()
        msg = sender.text()
        newNum = msg
        #print ("I was clicked: " + msg)
        self.getNumX()

    def doneNumb(self):
        global  doneN
        global allNum
        print(allNum)
        allNum = True
        #print("Done number: " + str(allNum))

    def setNumb(self):
        global leftEndData
        global rightEndData
        global numb
        global rowCount_VNB
        global rowCount_HNB
        global directionChanged
        global patNum_VNB
        global patNum_HNB
        global mg_VNB
        global mg_HNB
        global tech
        
        sender = self.sender()
        msg = sender.text()

        if msg == "LeE":
            leftEndData = numb
            print("Left end: " + leftEndData)
            numb = ""

        if msg == "RiE":
            rightEndData = numb
            print("Right end: " + rightEndData)
            numb = ""

        if msg == "RowV":
            rowCount_VNB = numb
            print("RowCount_VNB: " + rowCount_VNB)
            numb = ""

        if msg == "RowH":
            rowCount_HNB = numb
            print("RowCounr_HNB: " + rowCount_HNB)
            numb = ""

        if msg == "Dir":
            global directionChanged
            directionChanged = numb
            print("directionChanged is: " + directionChanged)
            numb = ""

        if msg == "MgV":
            mg_VNB = float(numb)*0.01
            print("MG_VNB is: ", mg_VNB)
            numb = ""

        if msg == "MgH":
            mg_HNB = float(numb)*0.01
            print("MG_HNB is: ", mg_HNB)
            numb = ""
            
        if msg == "PatV":
            patNum_VNB = numb
            print("pat_VNB is: " + patNum_VNB)
            numb = ""
            global knitpattern_VNB

            try:
                knitpattern_VNB = get_pattern(str(patNum_VNB) + ".bmp")
                global height_VNB
                height_VNB = len(knitpattern_VNB)
                print("height VNB: ", height_VNB)

            except IOError:
                print("no such pattern number")
                self.errorDialog("! No such pattern number: " + patNum_VNB)
                
                                       

        if msg == "PatH":
            patNum_HNB = numb
            print("pat_HNB is: " + patNum_HNB)
            numb = ""
            global knitpattern_HNB

            try:
                knitpattern_HNB = get_pattern(str(patNum_HNB) + ".bmp")
                global height_HNB
                height_HNB = len(knitpattern_HNB)
                print("height HNB: ", height_HNB)
            except IOError:
                self.errorDialog("! No such pattern number: " + patNum_HNB)
                

        if msg == "Tech":
            tech = numb
            print("tech is: " + tech)
            numb = ""

            global tech_Array
            global countTech        

            try:
                tech_Array = returnTechData(tech)
                countTech = 0
                print("Tech is: " + tech)
                print("tech_Array", tech_Array)
                print("countTech: ", countTech)
                numb = ""

            except IOError:
                self.errorDialog("! No such tech number: " + tech)
                


    def errorDialog(self, data):

        print("reached")
        
        d = QDialog()

        self.layout2=QGridLayout(self)

        def doneAll(self):
            d.destroy()
     
        self.error = QtWidgets.QPushButton("&"+data, d)
        self.error.setStyleSheet("background-color:rgb(255,125,50)")
        self.error.setEnabled(True)
        

        self.fontBtn = QFont ('Consolas bold', 16)
        self.fontBtn.setBold(True)
        self.error.setFont(self.fontBtn)
        self.error.setFixedHeight(150)
        self.error.setFixedWidth(400)

        self.error.clicked.connect(doneAll)

        self.layout2.addWidget(self.error, 0, 0)

        d.setLayout(self.layout2)        
        d.setWindowTitle("Error message")
        d.exec_()


    def showdialog(self):

        #print("first step")

        d = QDialog()

        self.layout2 = QGridLayout(self)

        #print("second step")

        def resetNumb():
            global numb
            numb = ""

        def doneAll(self):
            resetNumb()
            d.destroy()

        self.b1 = QtWidgets.QPushButton("1", d)
        self.b2 = QtWidgets.QPushButton("2", d)
        self.b3 = QtWidgets.QPushButton("3", d)
        self.b4 = QtWidgets.QPushButton("4", d)
        self.b5 = QtWidgets.QPushButton("5", d)
        self.b6 = QtWidgets.QPushButton("6", d)
        self.b7 = QtWidgets.QPushButton("7", d)
        self.b8 = QtWidgets.QPushButton("8", d)
        self.b9 = QtWidgets.QPushButton("9", d)
        self.b0 = QtWidgets.QPushButton("0", d)

        self.leEnd = QtWidgets.QPushButton("LeE", d)
        self.leEnd.setStyleSheet("background-color:rgb(0,155,155)")
        self.riEnd = QtWidgets.QPushButton("RiE", d)
        self.riEnd.setStyleSheet("background-color:rgb(0,155,155)")        
        self.rowBack_VNB = QtWidgets.QPushButton("RowV", d)
        self.rowBack_VNB.setStyleSheet("background-color:rgb(127,127,127)")
        self.rowBack_HNB = QtWidgets.QPushButton("RowH", d)
        self.rowBack_HNB.setStyleSheet("background-color:rgb(127,127,127)")
        self.direction = QtWidgets.QPushButton("Dir", d)
        self.direction.setStyleSheet("background-color:rgb(127,127,127)")
        self.pattern_VNB = QtWidgets.QPushButton("PatV", d)
        self.pattern_VNB.setStyleSheet("background-color:rgb(0,155,155)")        
        self.pattern_HNB = QtWidgets.QPushButton("PatH", d)
        self.pattern_HNB.setStyleSheet("background-color:rgb(0,155,155)")
        self.MG_VNB = QtWidgets.QPushButton("MgV", d)
        self.MG_VNB.setStyleSheet("background-color:rgb(0,155,105)")        
        self.MG_HNB = QtWidgets.QPushButton("MgH", d)
        self.MG_HNB.setStyleSheet("background-color:rgb(0,155,105)")    
        self.tech = QtWidgets.QPushButton("Tech", d)
        self.tech.setStyleSheet("background-color:rgb(255,190,0)")
        self.bQuit = QtWidgets.QPushButton("Quit", d)
        self.bQuit.setStyleSheet("background-color:rgb(255,125,50)")


        nums = [self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8, self.b9, self.b0]
        oper = [self.leEnd, self.riEnd, self.rowBack_VNB, self.rowBack_HNB, self.direction, self.pattern_VNB, self.pattern_HNB, self.MG_VNB, self.MG_HNB, self.tech, self.bQuit]

        self.fontBtn = QFont ('Consolas bold', 16)
        self.fontBtn.setBold(True)

        for i, item in enumerate(nums):
            item.setFont(self.fontBtn)
            item.setFixedHeight(80)
            item.setFixedWidth(80)

        for i, item in enumerate(oper):
            item.setFont(self.fontBtn)
            item.setFixedHeight(80)
            item.setFixedWidth(80)

        for i, item in enumerate(nums):
            item.clicked.connect(self.clickedMe)

        self.bQuit.clicked.connect(doneAll)
        self.leEnd.clicked.connect(self.setNumb)
        self.riEnd.clicked.connect(self.setNumb)
        self.rowBack_VNB.clicked.connect(self.setNumb)
        self.rowBack_HNB.clicked.connect(self.setNumb)
        self.direction.clicked.connect(self.setNumb)
        self.pattern_VNB.clicked.connect(self.setNumb)
        self.pattern_HNB.clicked.connect(self.setNumb)
        self.MG_VNB.clicked.connect(self.setNumb)
        self.MG_HNB.clicked.connect(self.setNumb)        
        self.tech.clicked.connect(self.setNumb)


        self.layout2.addWidget(self.b1, 0, 1)
        self.layout2.addWidget(self.b2, 0, 2)
        self.layout2.addWidget(self.b3, 0, 3)
        self.layout2.addWidget(self.b4, 1, 1)
        self.layout2.addWidget(self.b5, 1, 2)
        self.layout2.addWidget(self.b6, 1, 3)
        self.layout2.addWidget(self.b7, 2, 1)
        self.layout2.addWidget(self.b8, 2, 2)
        self.layout2.addWidget(self.b9, 2, 3)
        self.layout2.addWidget(self.b0, 3, 2)

        self.layout2.addWidget(self.pattern_VNB, 0, 0)
        self.layout2.addWidget(self.pattern_HNB, 0, 4)

        self.layout2.addWidget(self.rowBack_VNB, 0, 5)
        self.layout2.addWidget(self.rowBack_HNB, 0, 6)
        
        self.layout2.addWidget(self.leEnd, 1, 0)      
        self.layout2.addWidget(self.riEnd, 1, 4)    
        
        self.layout2.addWidget(self.direction, 1, 6)

        self.layout2.addWidget(self.MG_VNB, 2, 0)
        self.layout2.addWidget(self.MG_HNB, 2, 4)

        self.layout2.addWidget(self.tech, 3, 3)
        self.layout2.addWidget(self.bQuit, 3, 6)



        d.setLayout(self.layout2)
        d.setWindowTitle("NumPad")
        d.exec_()


#======================================================================
# End GUI PyQT5
#======================================================================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

