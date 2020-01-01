
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
knitpat_black_VNB = []
knitpat_white_VNB = []
knitpat_green_VNB = []
knitpat_blue_VNB = []
knitpat_blg_VNB = []

knitpat_black_HNB = []
knitpat_white_HNB = []
knitpat_green_HNB = []
knitpat_blue_HNB = []
knitpat_blg_HNB = []


knitpat_fullRow =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
knitpat_emptyRow = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
knitpat_rib10 = [170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170]
knitpat_rib01 = [85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85]

flagRight = 0
flagLeft = 1

# left and right end of the knitting
# msg num for right end: 90-num, num max 89
# msg num for left end: 180-(num - 90), num max 179
rightEndData = 0
leftEndData = 180

# on Display: left and right end
# count from center to left or right, max 90 from center
display_rightEnd = 0
display_leftEnd = 0

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


print("")
print("========================================")


# =================================================
# Original Pattern
# =================================================

def pattern_Array(listMy,data):

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


def get_pattern(data):
    filename = Image.open(data)

    global heightMy

    widthMy = filename.size[0]
    heightMy = filename.size[1]

    count = 0;
    #listMy = []
    listMy_black = []
    listMy_white = []
    listMy_green = []
    listMy_blue = []

    listMy_blg = []

    for x in range(0, heightMy):


        row_black = []
        row_white = []
        row_green = []
        row_blue = []

        row_blg = []



        for y in range(0, widthMy):
            pixel = (y, x)

            redMy, greenMy, blueMy = filename.getpixel(
                pixel)
            
            if redMy == 0 and greenMy == 0 and blueMy == 0:
                row_black.append(0)
            else:
                row_black.append(1)

            if redMy == 255 and greenMy == 255 and blueMy == 255:
                row_white.append(0)
            else:
                row_white.append(1)

            if redMy < 20 and greenMy > 200 and blueMy < 20:
                row_green.append(0)
            else:
                row_green.append(1)

            if redMy < 20 and greenMy < 20 and blueMy > 200:
                row_blue.append(0)
            else:
                row_blue.append(1)

            if redMy < 20 and greenMy > 200 or blueMy > 200:
                row_blg.append(0)
            else:
                row_blg.append(1)
                

        listMy_black.append(row_black)
        listMy_white.append(row_white)
        listMy_green.append(row_green)
        listMy_blue.append(row_blue)

        listMy_blg.append(row_blg)


    knitpat_black = []
    knitpat_white = []
    knitpat_green = []
    knitpat_blue = []

    knitpat_blg = []



    for i in range(0, heightMy):
        pattern_black = pattern_Array(listMy_black,i)
        knitpat_black.append(pattern_black)

    for i in range(0, heightMy):
        pattern_white = pattern_Array(listMy_white,i)
        knitpat_white.append(pattern_white)

    for i in range(0, heightMy):
        pattern_green = pattern_Array(listMy_green,i)
        knitpat_green.append(pattern_green)

    for i in range(0, heightMy):
        pattern_blue = pattern_Array(listMy_blue,i)
        knitpat_blue.append(pattern_blue)

    for i in range(0, heightMy):
        pattern_blg = pattern_Array(listMy_blg,i)
        knitpat_blg.append(pattern_blg)

    n = 0


    return knitpat_black, knitpat_white, knitpat_green, knitpat_blue, knitpat_blg



#//////////////////////////////////////////////////////////////////////


# good to know: the received list (received_cmd) is a two-dimensional list and the
# values can therefore only be read out with name [1] [0]
# get needle position from arduino front lock, rear lock

def get_needlePos_VNB():
    global needlePos_VNB
    connectionVNB.send("getNPos")       
    received_VNB = connectionVNB.receive()
    needlePos_VNB = received_VNB[1][0]

def get_needlePos_HNB():
    global needlePos_HNB
    connectionHNB.send("getNPos")       
    received_HNB = connectionHNB.receive()  
    needlePos_HNB = received_HNB[1][0]   
  

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

##    c.execute('CREATE TABLE IF NOT EXISTS stuffToPlot(tabID INTEGER,datestamp TEXT, rV INTEGER, rH INTEGER,'
##              'dirC INTEGER, lockV TEXT, lockH TEXT,'
##              'patV INTEGER, patH INTEGER, tec INTEGER, cTec INTEGER, leE INTEGER, riE INTEGER, mgV REAL, mgH REAL'
##              'display_leE INTEGER, display_riE INTEGER)')

    c.execute('CREATE TABLE IF NOT EXISTS stuffToPlot(tabID INTEGER,datestamp TEXT, rV INTEGER, rH INTEGER,'
              'dirC INTEGER, lockV TEXT, lockH TEXT,'
              'patV INTEGER, patH INTEGER, tec INTEGER, cTec INTEGER, leE INTEGER, riE INTEGER, mgV REAL, mgH REAL, display_leE INTEGER, display_riE INTEGER)')


    tableID = max_tabID(c)

    
    def execute_tableID_info(c):

        global rowCount_VNB
        global rowCount_HNB
        global directionChanged
        global lockSetting_VNB
        global lockSetting_HNB
        global patNum_VNB
        global patNum_HNB
        global tech
        global countTech
        global leftEndData
        global rightEndData     
        global mg_VNB
        global mg_HNB
        global display_leftEnd
        global display_rightEnd

        global tech_Array
        global height_VNB
        global height_HNB

        global knitpat_black_VNB
        global knitpat_white_VNB
        global knitpat_green_VNB
        global knitpat_blue_VNB
        global knitpat_blg_VNB

        global knitpat_black_HNB
        global knitpat_white_HNB
        global knitpat_green_HNB
        global knitpat_blue_HNB
        global knitpat_blg_HNB
        
        
        c.execute('SELECT tabID, datestamp, rV, rH, dirC, lockV, lockH, patV, patH, tec, cTec,'
                  'leE, riE, mgV, mgH, display_leE, display_riE FROM stuffToPlot WHERE tabID = :tabID', {"tabID": tableID})



        result = c.fetchone()

        print("{:<6s}{:>4d}".format("tabID:", result[0]))
        print("{:<6s}{:>4s}".format("date:",result[1]))

        rowCount_VNB = result[2]
        print("{:<6s}{:>4d}".format("rV:",rowCount_VNB))      

        rowCount_HNB = result[3]
        print("{:<6s}{:>4d}".format("rH:",rowCount_HNB))

        directionChanged = result[4]
        print("{:<6s}{:>4d}".format("dirC:",directionChanged))

        lockSetting_VNB = result[5]
        print("{:<6s}{:>4s}".format("lock_V:", lockSetting_VNB))

        lockSetting_HNB = result[6]
        print("{:<6s}{:>4s}".format("lock_H:", lockSetting_HNB))
        

    # When new started, import the last used pat and create the pattern array

        patNum_VNB = result[7]
        print("{:<6s}{:>4d}".format("patV:", patNum_VNB))
        
        try:
            knitpat_black_VNB, knitpat_white_VNB, knitpat_green_VNB, knitpat_blue_VNB, knitpat_blg_VNB = get_pattern(str(patNum_VNB)+".bmp")
            height_VNB = len(knitpat_black_VNB)

        except IOError:
            self.errorDialog("!no knitpattern VNB")
            
        patNum_HNB = result[8]
        print("{:<6s}{:>4d}".format("patH:", patNum_HNB))      

        try:
            knitpat_black_HNB, knitpat_white_HNB, knitpat_green_HNB, knitpat_blue_HNB, knitpat_blg_HNB = get_pattern(str(patNum_HNB)+".bmp")
            height_HNB = len(knitpat_black_HNB)

        except IOError:
            self.errorDialog("!no knitpattern HNB")
        
    # When new started import last used technique and create the tech array

        tech = result[9]
        print("{:<6s}{:>4d}".format("tec:", tech))
        
        try:
            tech_Array=returnTechData(tech)
             
            countTech = result[10]
            print("{:<6s}{:>4d}".format("cTec:", countTech))

        except IOError:
            self.errorDialog("!TechArray or count Tech error")      
        
        leftEndData = result[11]
        print("{:<6s}{:>4d}".format("leE:", leftEndData))

        rightEndData = result[12]
        print("{:<6s}{:>4d}".format("riE:", rightEndData))
        
        mg_VNB = result[13]
        print("mgV:  ", mg_VNB)

        mg_HNB = result[14]
        print("mgH:  ", mg_HNB)

        display_leftEnd = result[15]
        display_rightEnd = result[16]

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
    lockV = lockSetting_VNB
    lockH = lockSetting_HNB
    patV = patNum_VNB
    patH = patNum_HNB
    tec = tech
    cTec = countTech
    leE = leftEndData
    riE = rightEndData
    mgV = mg_VNB
    mgH = mg_HNB
    tabID = tableID
    display_leE = display_leftEnd
    display_riE = display_rightEnd

    unix = time.time()
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%d-%m-%Y %H:%M:%S'))

    c.execute("INSERT INTO stuffToPlot(tabID, datestamp, rV, rH, dirC, lockV, lockH, patV, patH,tec, cTec, leE, riE, mgV, mgH, display_leE, display_riE) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(tableID, date, rowCount_VNB, rowCount_HNB, directionChanged, lockSetting_VNB, lockSetting_HNB, patNum_VNB, patNum_HNB, tech, countTech, leftEndData, rightEndData, mg_VNB, mg_HNB, display_leftEnd, display_rightEnd))
       
    conn.commit()

    tableID +=1
    print("tabID: ", tableID)
    
    c.close()
    conn.close()


def read_from_db(dirC_num):

    global rowCount_VNB
    global rowCount_HNB
    global directionChanged
    global lockSetting_VNB
    global lockSetting_HNB
    global patNum_VNB
    global patNum_HNB
    global tech
    global countTech
    global leftEndData
    global rightEndData     
    global mg_VNB
    global mg_HNB
    global display_leftEnd
    global display_rightEnd

    conn = sqlite3.connect('passapProject.db')
    c = conn.cursor()
                           
    c.execute("SELECT tabID, datestamp, rV, rH, dirC, lockV, lockH, patV, patH,"
              "tec, cTec, leE, riE, mgV, mgH, display_leE,display_riE FROM stuffToPlot WHERE dirC = :dirC", {"dirC": dirC_num})
    
    result = c.fetchone()

    try:      
        rowCount_VNB = result[2]
        rowCount_HNB = result[3]
        directionChanged = result[4]
        lockSetting_VNB = result[5]
        lockSetting_HNB = result[6]
        patNum_VNB = result[7]
        patNum_HNB = result[8]
        tech = result[9]
        countTech = result[10]
        leftEndData = result[11]
        rightEndData = result[12]
        mg_VNB = result[13]
        mg_HNB = result[14]
        display_leftEnd = result[15]
        display_rightEnd = result[16]
        
    except:
        print("No value")
		
    c.close()
    conn.close()
    
    
def drop_index():
    conn = sqlite3.connect('passapProject.db')
    c = conn.cursor()

    c.execute("DROP INDEX [IF EXISTS] index_tabID")



#/////////////////////////////////////////////////////////////////////

# Communication with Arduino, sending pattern rows

#//////////////////////////////////////////////////////////////////////

# Arduino VNB
    
def sendRow_color_toArduino(knit, colour):

    #print(colour)

    try:

        for h in range(1):

            num_args=len(knit[rowCount_VNB])

            connectionVNB.send("sPat", num_args, *knit[rowCount_VNB][:]) 

            received_cmd = connectionVNB.receive()
            received = received_cmd[1] 

            # print('received ', received)

            success = 1

            for i in range (1):           
                if knit[rowCount_VNB][i] == received[i]:
                    success *= 1
                else:
                    success = 0
                if success == 0:
                    success = "FAIL"
                else:
                    success = "PASS"

            print("VNB row:",rowCount_VNB,colour,success)

    except:
        print('Pattern failed', colour)



def sendRow_pat_VNB(knit, info):

    #print(info)

    num_args = len(knit)

    connectionVNB.send("setEmptyPat", num_args, *knit)

    received_cmd = connectionVNB.receive()
    received = received_cmd[1]
    
    #print('received ', received)

    try:
        if received!=None:
            pass
    except:
        print("No value")

    success = 1

    for i in range (num_args):
        if knit[i] == received[i]:
            success *= 1
        else:
            success = 0

    if success == 0:
        success = "FAIL"
    else:
        success = "PASS"

    print(info,success)


# Arduino HNB
    

def sendRow_color_toArduino_HNB(knit, colour):

    # print(colour)

    try:

        for h in range(1):

            num_args=len(knit[rowCount_HNB])

            connectionHNB.send("sPat", num_args, *knit[rowCount_HNB][:]) 

            received_cmd = connectionHNB.receive()
            received = received_cmd[1] 

            # print('received ', received)

            success = 1

            for i in range (1):           
                if knit[rowCount_HNB][i] == received[i]:
                    success *= 1
                else:
                    success = 0
                if success == 0:
                    success = "FAIL"
                else:
                    success = "PASS"

            print("HNB row:",rowCount_HNB,colour,success)

    except:
        print('Pattern failed', colour)
        


def sendRow_pat_HNB(knit, info):

    # print(info)

    num_args = len(knit)

    connectionHNB.send("setEmptyPat", num_args, *knit)

    received_cmd = connectionHNB.receive()

    received = received_cmd[1]
    #print('received ', received)

    try:
        if received!=None:
            pass
    except:
        print("No value")

    success = 1

    for i in range (num_args):
        if knit[i] == received[i]:
            success *= 1
        else:
            success = 0

    if success == 0:
        success = "FAIL"
    else:
        success = "PASS"

    print(info,success)


#*************************************************************
      
def send_emptyRow_toArduino():
    send_emptyRow_VNB()
    send_emptyRow_HNB()


def send_none():
    pass



# Dictionary functions VNB


def sendRow_colour_black():
    #print ('sending black')
    sendRow_color_toArduino(knitpat_black_VNB, "black")

def sendRow_colour_white():
    #print ('arrived sendRow_colour white')
    sendRow_color_toArduino(knitpat_white_VNB, "white")

def sendRow_colour_green():
    #print ('arrived sendRow_colour green')
    sendRow_color_toArduino(knitpat_green_VNB, "green")

def sendRow_colour_blue():
    #print ('arrived sendRow_colour blue')
    sendRow_color_toArduino(knitpat_blue_VNB, "blue")

def sendRow_colour_blue_green():
    sendRow_color_toArduino(knitpat_blg_VNB, 'blue_green')

def send_emptyRow_VNB():
    #print('send emptyRow')
    sendRow_pat_VNB(knitpat_emptyRow,"emptyRow")

def send_fullRow_VNB():
    #print('send fullRow')
    sendRow_pat_VNB(knitpat_fullRow,"fullRow")

def send_rib10_VNB():
    sendRow_pat_VNB(knitpat_rib10,"Ribpat 10 VNB")
def send_rib01_VNB():
    sendRow_pat_VNB(knitpat_rib01, "Ribpat 01 VNB")

 
# Dictionary functions HNB

def sendRow_colour_black_HNB():
    #print ('sending black HNB')
    sendRow_color_toArduino_HNB(knitpat_black_HNB, "black")

def sendRow_colour_white_HNB():
    #print ('sending white HNB')
    sendRow_color_toArduino_HNB(knitpat_white_HNB, "white")

def sendRow_colour_green_HNB():
    #print ('sending green HNB')
    sendRow_color_toArduino_HNB(knitpat_green_HNB, "green")

def sendRow_colour_blue_HNB():
    #print ('sending blue HNB')
    sendRow_color_toArduino_HNB(knitpat_blue_HNB, "blue")

def sendRow_colour_blue_green_HNB():
    sendRow_color_toArduino_HNB(knitpat_blg_HNB, 'blue_green')

def send_emptyRow_HNB():
    #print('send emptyRow')
    sendRow_pat_HNB(knitpat_emptyRow,"emptyRow")

def send_fullRow_HNB():
    #print('send fullRow')
    sendRow_pat_HNB(knitpat_fullRow,"fullRow")
    
def send_rib01_HNB():
    sendRow_pat_HNB(knitpat_rib01,"Ribpat 01 HNB")
def send_rib10_HNB():
    sendRow_pat_HNB(knitpat_rib10,"Ribpat 10 HNB")
 
    

# enum
techSet = {'bV':sendRow_colour_black,'wV':sendRow_colour_white,
           'gV':sendRow_colour_green, 'blV':sendRow_colour_blue,
           'blgV':sendRow_colour_blue_green,
           'eV':send_emptyRow_VNB, 'nV':send_fullRow_VNB,
           'rib10V':send_rib10_VNB, 'rib01V':send_rib01_VNB,
           'bH':sendRow_colour_black_HNB, 'wH':sendRow_colour_white_HNB,
           'gH':sendRow_colour_green_HNB,'blH':sendRow_colour_blue_HNB,
           'blgH':sendRow_colour_blue_green_HNB,
           'eH':send_emptyRow_HNB, 'nH':send_fullRow_HNB,
           'rib01H':send_rib01_HNB, 'rib10H':send_rib10_HNB,
           '0':send_none}


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
        saveFile.triggered.connect(self.file_save)

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

    def save_settings(self): pass
        


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

        # SX brings the pusher in the right knitting position
        # Uneven numbers: Lock on the left hand side 
        # Even numbers: Lock on the right hand side

        def start_SX_Row():
            
            global directionChanged
          
            try:
                directionChanged != 0

                if directionChanged >= 2 and directionChanged % 2 == 0:
                    directionChanged -= 2
                    read_from_db(directionChanged)
                elif directionChanged >= 1 and directionChanged % 2 == 1:
                    directionChanged -= 1
                    read_from_db(directionChanged)
                
            except:
                print("no dirChange: ", directionChanged)


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
        self.numPad_process = QtWidgets.QPushButton('SX Row', self.tab1)
        self.numPad_process.setStyleSheet("background-color:rgb(204,255,229)")
        self.numPad_process.setEnabled(True)
        self.numPad_process.setGeometry(QtCore.QRect(230, 20, 100, 60))
        self.numPad_process.clicked.connect(start_SX_Row)


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

            # Display number is different from number which is sent to arduino,
            # negativ numbers mean right of the middle,
            # positiv numbers mean left of the middle
            self.label_left.setText("leftEnd: " + str(display_leftEnd))          
            self.label_right.setText("rightEnd: " + str(display_rightEnd))
            
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
        global display_rightEnd
        global display_leftEnd
        
        sender = self.sender()
        msg = sender.text()

        if msg == "LeE":

            x = int(numb)

            try:
                if x < 90:
                    display_leftEnd = x
                    leftEndData = 90+x

                    print("Knit left End: ", display_leftEnd)
                    print("left end: ", leftEndData)

                elif x > 90 and x < 180:
                    display_leftEnd = 90-x
                    leftEndData = 180-x
                
                    print("Knit left End: ", display_leftEnd)
                    print("left end: ", leftEndData)

                else:
                    raise ValueError

            except ValueError:
                        print("Value error leftEndData more than 180")

            numb = ""
                
          

# hier sollte ich etwas ändern, ich brauche 2Variablen
        if msg == "RiE":

            x = int(numb)
            
            try:

                if x < 90:
                    display_rightEnd = -x
                    rightEndData = 90-x

                    print("Knit right End: ", display_rightEnd)
                    print("Right end: ", rightEndData)

                elif x > 90 and x < 180:
                    display_rightEnd = x-90
                    rightEndData = x

                    print("Knit right End: ", display_rightEnd)
                    print("Right end: ", rightEndData)

                else:
                    raise ValueError

            except ValueError:
                print("Value error rightEndData more than 180")
                    
            numb = ""

            

        if msg == "RowV":
            rowCount_VNB = numb
            print("RowCount_VNB: " + rowCount_VNB)
            numb = ""

        if msg == "RowH":
            rowCount_HNB = numb
            print("RowCount_HNB: " + rowCount_HNB)
            numb = ""

        if msg == "Dir":
            dirChange = numb
            read_from_db(dirChange)        
            print("directionChanged is: " + dirChange)
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


            global knitpat_black_VNB
            global knitpat_white_VNB
            global knitpat_green_VNB
            global knitpat_blue_VNB
            global knitpat_blg_VNB


            try:
                knitpat_black_VNB,knitpat_white_VNB,knitpat_green_VNB,knitpat_blue_VNB,knitpat_blg_VNB = get_pattern(str(patNum_VNB) + ".bmp")
                
                global height_VNB
                height_VNB = len(knitpat_black_VNB)
                print("height VNB: ", height_VNB)

            except IOError:
                print("no such pattern number")
                self.errorDialog("! No such pattern number: " + patNum_VNB) 



        if msg == "PatH":
            patNum_HNB = numb
            print("pat_HNB is: " + patNum_HNB)
            numb = ""

            global knitpat_black_HNB
            global knitpat_white_HNB
            global knitpat_green_HNB
            global knitpat_blue_HNB
            global knitpat_blg_HNB

            try:
                knitpat_black_HNB, knitpat_white_HNB, knitpat_green_HNB, knitpat_blue_HNB, knitpat_blg_HNB = get_pattern(str(patNum_HNB) + ".bmp")

                global height_HNB
                height_HNB = len(knitpat_black_HNB)
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

