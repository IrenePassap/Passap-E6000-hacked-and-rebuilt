# Version 31
# Passap E6000 rebuilt and replaced console, Electra 4600 rebuilt

# created by Irene Wolf, 20.6.2020

# Python code for Raspberry Pi 3


import random, sys
import PyCmdMessenger
import struct
import RPi.GPIO as GPIO
import time
import sqlite3
import time
import datetime
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QWidget, QLineEdit, QMessageBox, QLabel, QFileDialog, QDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore, QtWidgets, QtGui

import csv

from PIL import Image


# --------------------------------------------------------------------------
# Setup Pin for interrupt
# --------------------------------------------------------------------------

# GPIO Pin to get signals form Arduino front lock
right_GPIO = 7
left_GPIO = 11
directionchange_GPIO = 13

GPIO.setmode(GPIO.BOARD)

GPIO.setup(right_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(left_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(directionchange_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------


# Default pattern number
patNum_VNB = 201
patNum_HNB = 202



# count knitted row
rowCount = 0
# count knitted row VNB, HNB
rowCount_VNB = 0
rowCount_HNB = 0
# counts each direction change
directionChanged = 0
# count knitted form rows
rowCountForm = 0
# counter counts row in form file 
countForm_line = 0
countForm_line2 = 0
# Counter used for form repead and jump
repeadFromLineX = 0
repeadFromLine0 = 0
jumpCounter = 0
# Counter for technique file
countTech = 0

# form = default form 
form = '1'
form_Array = []

endKniterror = 0

# tech = default techik 
tech = '2'
tech_Array = []


# position
needlePos_VNB = 1
needlePos_HNB = 1

# left end knitting, right end knitting
rightEndData_VNB = 30
leftEndData_VNB = 120

rightEndData_HNB = 30
leftEndData_HNB = 120

flag_left = 1
flag_right = 0


# height of knitting pattern
height_VNB = 0
height_HNB = 0


# settings
colorSetting = ""
lockSetting_VNB = ""
lockSetting_HNB = ""

# stich size
mg_VNB = 0.0
mg_HNB = 0.0

infoTech = ""
infoForm = ""

# Array for knit pattern
knitpat_black_VNB = []
knitpat_white_VNB = []
knitpat_green_VNB = []
knitpat_blue_VNB = []
knitpat_blg_VNB = []
knitpat_blgb_VNB = []

knitpat_black_HNB = []
knitpat_white_HNB = []
knitpat_green_HNB = []
knitpat_blue_HNB = []
knitpat_blg_HNB = []
knitpat_blgb_HNB = []

knitpat_fullRow =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
knitpat_emptyRow = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
knitpat_rib10 = [170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170,170]
knitpat_rib01 = [85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85]

#--------------------------------------------------------------------------
# Variables used for motor
#--------------------------------------------------------------------------

# used for Input GPIO drive left: if cursorPos == 100 and col == 1: poti speed, tech_Array()  
cursorPos = 0

# speed until now two state: O = poti, 1 = speed colour changer
speed = 0

# endStopp
endStopp = 0

# col hat two state: 0 = no colour change, 1 = colour change
col = 0


#--------------------------------------------------------------------------
# Communication Arduino - Raspi
#--------------------------------------------------------------------------


# connect to Motor Arduino Uno
# baud rate max 19200 with Arduino Serial
motor = PyCmdMessenger.ArduinoBoard('/dev/ttyUSB-ArduinoMotor',19200)
motor.enable_dtr=False
motor.int_bytes=4

commands =[["slowDownSpeed", "i"],["sbSlowDownSpeed", "i"],
           ["setColourChange", "?"],["sbColourChange", "?"],
           ["setRowEndStopp", "?"],["sbRowEndStopp", "?"],
           ["setFormStopp", ""],["sbFormStopp", "s"],
           ["setDrive_left", ""], ["sbDrive_left", "s"],
           ["setDrive_right", ""], ["sbDrive_right", "s"]]

connectionMotor= PyCmdMessenger.CmdMessenger(motor,commands)


# connect to VNB Arduino M0 (front lock)
a = PyCmdMessenger.ArduinoBoard('/dev/ttyUSB-ArduinoVNB',115200)
a.enable_dtr=False
a.int_bytes=4
connectionVNB = PyCmdMessenger.CmdMessenger(a, [["sPat", "b*"],["sbPat", "b*"],
                                             ["setEmptyPat", "b*"], ["sbEmptyPat", "b*"],
                                             ["setNPos", "l"],["sbNPos", "l*"],
                                             ["getNPos", ""],["sendNPos", "l"],   
                                             ["setLeEnd", "i"], ["sbLeEnd", "l"],
                                             ["setRiEnd", "i"], ["sbRiEnd", "l"],
                                             ["getCursorPos", ""], ["sendCursorPos", "l"],                                           
                                             ])


# connect to HNB Arduino M0 Pro (back lock)
b = PyCmdMessenger.ArduinoBoard('/dev/ttyUSB-ArduinoHNB',115200)
b.enable_dtr=False
b.int_bytes=4
connectionHNB = PyCmdMessenger.CmdMessenger(b, [["sPat", "b*"],["sbPat", "b*"],
                                             ["setEmptyPat", "b*"], ["sbEmptyPat", "b*"],                                              
                                             ["setNPos", "l"],["sbNPos", "l*"],  
                                             ["getNPos", ""],["sendNPos", "l"],  
                                             ["setLeEnd", "i"], ["sbLeEnd", "l"],
                                             ["setRiEnd", "i"], ["sbRiEnd", "l"],
                                             ])    


print("")
print("========================================")


# =================================================
# Original Pattern
# =================================================


# returns a pattern array
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

    nameTech = str(number)+".txt"

    print("nameTech: " + nameTech)

    file_name = ("/home/pi/PyIrene/ProgrammCode/Tech/"+(nameTech))

    print("file_name " + file_name)
    
    with open(file_name) as f:
        reader = csv.reader (f)
        for r in reader:
            data.append(r)
        data.pop(0)
    return data


# returns for each colour in the pattern drawing a seperat pattern array
def get_pattern(data):
    
    filename = Image.open(data)

    global heightMy

    widthMy = filename.size[0]
    heightMy = filename.size[1]

    listMy_black = []
    listMy_white = []
    listMy_green = []
    listMy_blue = []

    listMy_blg = []
    listMy_blgb = []

    for x in range(0, heightMy):

        row_black = []
        row_white = []
        row_green = []
        row_blue = []

        row_blg = []
        row_blgb = []


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

            if redMy < 20 and (greenMy > 200 or blueMy > 200):
                row_blg.append(0)
            else:
                row_blg.append(1)

            if (redMy < 20 and greenMy > 200 and blueMy < 20) or (redMy < 20 and greenMy < 20 and blueMy > 200) or (redMy == 0 and greenMy == 0 and blueMy == 0):
                row_blgb.append(0)
            else:
                row_blgb.append(1)
                

        listMy_black.append(row_black)
        listMy_white.append(row_white)
        listMy_green.append(row_green)
        listMy_blue.append(row_blue)

        listMy_blg.append(row_blg)
        listMy_blgb.append(row_blgb)

    knitpat_black = []
    knitpat_white = []
    knitpat_green = []
    knitpat_blue = []

    knitpat_blg = []
    knitpat_blgb = []


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

    for i in range(0, heightMy):
        pattern_blgb = pattern_Array(listMy_blgb,i)
        knitpat_blgb.append(pattern_blgb)

    n = 0


    return knitpat_black, knitpat_white, knitpat_green, knitpat_blue, knitpat_blg, knitpat_blgb



#//////////////////////////////////////////////////////////////////////

# Tech_Array

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


def get_cursorPos():
    global cursorPos
    connectionVNB.send("getCursorPos")       
    received_VNB = connectionVNB.receive()
    cursorPos = received_VNB[1][0]
    #print("cursorPos get ", cursorPos)


def drive_left():
    connectionMotor.send("setDrive_left")
    received_Motor = connectionMotor.receive()
    #print("rec_left: ", received_Motor[1][0])
   

def drive_right():
    connectionMotor.send("setDrive_right")
    received_Motor_R = connectionMotor.receive()
    #print("rec_right: ", received_Motor_R[1][0])
    

def col_speed():
    global speed
    speed = 1
    connectionMotor.send("slowDownSpeed", speed)   
    received_Motor_Speed=connectionMotor.receive()    
    #print("rec_colour speed: ", received_Motor_Speed[1][0])
    
def poti_speed():
    global speed
    speed = 0
    connectionMotor.send("slowDownSpeed", speed)   
    received_Motor_Speed=connectionMotor.receive()    
    #print("rec_poti speed: ", received_Motor_Speed[1][0])

def rowEndStopp():
    global endStopp
    connectionMotor.send("setRowEndStopp", endStopp)   
    received_Motor_endStopp=connectionMotor.receive()    
    #print("rec_rowEndStopp: ", received_Motor_endStopp[1][0])

def colourChange(): 
    connectionMotor.send("setColourChange", col)   
    received_Motor_Col=connectionMotor.receive()    
    #print("rec_colourChange: ", received_Motor_Col[1][0])
     

def returnTechData(number):

    data = []

    nameTech = str(number)+".txt"

    #print("nameTech: " + nameTech)

    file_name = ("/home/pi/PyIrene/ProgrammCode/Tech/"+(nameTech))

    #print("file_name " + file_name)
    
    with open(file_name) as f:
        reader = csv.reader (f)
        for r in reader:
            data.append(r)
        data.pop(0)
    return data
    


# sets technique values
def techArray():

    #print("techArray try")

    # new settings
    global lockSetting_VNB
    global lockSetting_HNB
    global colorSetting
    global infoTech
    global endStopp
    global col
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
 
    lockSetting_VNB = tech_Array[countTech][4]   
    lockSetting_HNB = tech_Array[countTech][5]

    endStopp = int(tech_Array[countTech][6])
    rowEndStopp()

    col = int(tech_Array[countTech][7])
    colourChange()
   
    colorSetting = tech_Array[countTech][8]    

    infoTech = tech_Array[countTech][9]
    print(infoTech)
    
    countTech += 1

    formArray()

    newLabelText()
    newSettings()

    dynamic_date_entry_settings()

    print("end: ", time.clock())
    

#--------------------------------------------------------------
#           Form
#-------------------------------------------------------------


def returnFormData(number):

    data = []

    nameForm = str(number)+"F.txt"

    #print("nameForm: " + nameForm)

    file_name_form = ("/home/pi/PyIrene/ProgrammCode/Form/"+(nameForm))

    #print("file_name " + file_name_form)
    
    with open(file_name_form) as f:
        reader = csv.reader (f)
        for r in reader:
            data.append(r)
        data.pop(0)
    return data


def setEnd_lr():
    global countForm_line
    global leftEndData_VNB
    global leftEndData_HNB
    global rightEndData_VNB    
    global rightEndData_HNB

    leftEndData_VNB = int(form_Array[countForm_line][4])
    leftEndData_HNB = int(form_Array[countForm_line][4])
    
    rightEndData_VNB = int(form_Array[countForm_line][5])
    rightEndData_HNB = int(form_Array[countForm_line][5])

    sendData()
    
    
    

def setEnd_lr_VNB():
    global rightEndData_VNB
    global leftEndData_VNB
    global countForm_line
   
    leftEndData_VNB = int(form_Array[countForm_line][4])
    rightEndData_VNB = int(form_Array[countForm_line][5])    

    sendData_VNB()
    


def setEnd_lr_HNB():
    global rightEndData_HNB
    global leftEndData_HNB
    global countForm_line
   
    leftEndData_HNB = int(form_Array[countForm_line][4])
    rightEndData_HNB = int(form_Array[countForm_line][5])    

    sendData_HNB()
    
    
    
def decrease():
    global leftEndData_VNB
    global leftEndData_HNB
    global rightEndData_VNB
    global rightEndData_HNB
    global countForm_line

    print("decrease: ", countForm_line)

    # hier ist es schwierig eine Begrenzung zu machen

    decrease_left = int(form_Array[countForm_line][4])
    leftEndData_VNB -= decrease_left
    leftEndData_HNB -= decrease_left
    
    decrease_right = int(form_Array[countForm_line][5])
    rightEndData_VNB += decrease_right
    rightEndData_HNB += decrease_right

    sendData()
    

def decrease_VNB():
    global leftEndData_VNB
    global rightEndData_VNB
    global countForm_line

    print("decrease_VNB: ", countForm_line)

    decrease_left = int(form_Array[countForm_line][4])
    leftEndData_VNB -= decrease_left
    
    decrease_right = int(form_Array[countForm_line][5])
    rightEndData_VNB += decrease_right

    sendData_VNB()
    

def decrease_HNB():
    global leftEndData_HNB
    global rightEndData_HNB
    global countForm_line

    print("decrease_HNB: ", countForm_line)

    decrease_left = int(form_Array[countForm_line][4])
    leftEndData_HNB -= decrease_left
    
    decrease_right = int(form_Array[countForm_line][5])
    rightEndData_HNB += decrease_right

    sendData_HNB()
    
    
def increase():
    global leftEndData_VNB
    global leftEndData_HNB
    global rightEndData_VNB
    global rightEndData_HNB
    global countForm_line

    print("increase: ", countForm_line)

    increase_left = int(form_Array[countForm_line][4])
    leftEndData_VNB += increase_left
    leftEndData_HNB += increase_left
        
    increase_right = int(form_Array[countForm_line][5])
    rightEndData_VNB -= increase_right
    rightEndData_HNB -= increase_right

    sendData()


def increase_VNB():
    global leftEndData_VNB
    global rightEndData_VNB
    global countForm_line

    print("increase_VNB: ", countForm_line)

    increase_left = int(form_Array[countForm_line][4])
    leftEndData_VNB += increase_left
        
    increase_right = int(form_Array[countForm_line][5])
    rightEndData_VNB -= increase_right

    sendData_VNB()


def increase_HNB():
    global leftEndData_HNB
    global rightEndData_HNB
    global countForm_line

    print("increase_HNB: ", countForm_line)

    increase_left = int(form_Array[countForm_line][4])
    leftEndData_HNB += increase_left
        
    increase_right = int(form_Array[countForm_line][5])
    rightEndData_HNB -= increase_right

    sendData_HNB()


# for futur use
def setShortRow():
    print("future use")


def form_stopp():
    connectionMotor.send("setFormStopp")
    received_formStopp = connectionMotor.receive()
    print("rec_formStopp: ", received_formStopp[1][0])

def noForm_stopp():
    print("no form stopp")

def endKnit():
    global endKniterror
    form_stopp()
    endKniterror = 1
    print("End of knitting form")

def repead_fromLine0_endless():
    global rowCountForm
    global countForm_line

    rowCountForm = -(1)
    countForm_line = -(1)

    print("endless repead")


def repead_fromLine0():
    global rowCountForm
    global countForm_line
    global repeadFromLine0

    if repeadFromLine0 >= int(form_Array[countForm_line][8]):   
        return
        
    else:
        rowCountForm = -(1)
        countForm_line = -(1)
        repeadFromLine0 += 1
        
        print("repead line from 0", repeadFromLine0)
        

def repead_fromLineX():
    global rowCountForm
    global countForm_line
    global repeadFromLineX

    if repeadFromLineX >= int(form_Array[countForm_line][8]):
        return
        
    else:
        countForm_line = int(form_Array[countForm_line][7])
        rowCountForm = int(form_Array[countForm_line][1]) -1
        repeadFromLineX += 1
        countForm_line -= 1
        

def jump_toLine():
    global rowCountForm
    global countForm_line
    global jumpCounter


    if jumpCounter >= int(form_Array[countForm_line][8]):
        return
    
    else:
        countForm_line = int(form_Array[countForm_line][7])
        print("jump to countForm_line ", countForm_line)
        rowCountForm = int(form_Array[countForm_line][1]) -1
        jumpCounter += 1
        countForm_Line -= 1

def endLine():
    print("go on")

def setTechArrayForm():
    global countTech
    global tech_Array
    global countForm_line

    #print("arrived setTechArrayForm")

    try:
        numb = form_Array[countForm_line][7]

        tech_Array = returnTechData(numb)
        
        countTech = int(form_Array[countForm_line][8])

        print("Tech is: ", numb)
        print("tech_Array: ", tech_Array)
        print("count Tech new: ", countTech)

    except ValueError:
        self.errorDialog("no such pattern number: ", numb)


def setFormArray():
    global form_Array
    global countForm_line
    global rowCountForm

    try:
        numb = int(form_Array[countForm_line][7])
        form_Array = returnFormData(numb)

        countform_line = int(form_Array[countForm_line][8])
        rowCountForm = int(form_Array[countForm_line][1])

    except ValueError:
        self.errorDialog("no such form_Array: ", numb)



def pat_VNB():

    global rowCount_VNB
    global countForm_line
    
    numb = form_Array[countForm_line][7]
      
    setPat_VNB(numb)
    
    rowCount_VNB = form_Array[countForm_line][8]
    
    print("formSet_pat_VNB is: " + numb)


def pat_HNB():

    global rowCount_HNB
    global countForm_line
    
    numb = form_Array[countForm_line][7]

    setPat_HNB(numb)

    rowcount_HNB = form_Array[countForm_line][8]
    
    print("formSet_pat_HNB is: " + numb)


# enum
formSet = {'enR': setEnd_lr,
           'eRV': setEnd_lr_VNB,
           'eRH': setEnd_lr_HNB,
           'dec': decrease,
           'deV': decrease_VNB,
           'deH': decrease_HNB,
           'inc': increase,
           'inV': increase_VNB,
           'inH': increase_HNB,
           'sRow': setShortRow,
           'endK': endKnit,
           're0': repead_fromLine0_endless,
           'r0?': repead_fromLine0,
           'rL?': repead_fromLineX,
           'goL': jump_toLine,
           'sMo': form_stopp,
           'noS': noForm_stopp,
           'enL': endLine,
           'teA': setTechArrayForm,
           'foA': setFormArray,
           'paV': pat_VNB,
           'paH': pat_HNB,
           }
           

def formArray():

    # counter counts row in form file
    global countForm_line
    # counts knitted row
    global rowCountForm    
    # data displayed        
    global infoForm


    if endKniterror == 1:
        print('end knit error')
        form_stopp()
        return

    elif countForm_line >= len(form_Array):
       #print('end knit reached')
       form_stopp()
       return

    elif rowCountForm == int(form_Array[countForm_line][1]):
       
        # form Stopp
        formSet[form_Array[countForm_line][2]]()

        formSet[form_Array[countForm_line][3]]()

        formSet[form_Array[countForm_line][6]]()

        infoForm = form_Array[countForm_line][9]

        countForm_line += 1
        
        print(infoForm)
    
        #print("end: ", time.clock())"""
        
    rowCountForm += 1
    print("rowCountForm end function", rowCountForm)



# Raspberry Pi interrupt
# Row end: Next commands according to tech Array
# According to needlePos_VNB and formArray send new motorState to Arduino_Motor
def inputChange_right(right_GPIO):

    get_needlePos_VNB()
         
    global directionChanged
    global flag_left
    global flag_right
    
    print("GPIO_ri: ", needlePos_VNB)
        
    if col == 0 and needlePos_VNB <= (int(rightEndData_VNB)-15) and flag_right == 1:       

        drive_left()
        techArray()

        print("drive left, col 0", needlePos_VNB)

        flag_left = 1
        flag_right = 0
        
        directionChanged +=1


    if (col == 1):                
        col_speed()
        print("col speed", needlePos_VNB) 
       

def inputChange_left(left_GPIO):

    get_needlePos_VNB()
    get_cursorPos()

    global directionChanged
    global flag_left
    global flag_right

    print("GPI0_le: ", needlePos_VNB)
    #print("cursorPos: ", cursorPos)

    if needlePos_VNB >= (int(leftEndData_VNB) + 15) and flag_left == 1:

        print("drive right at needlePos_VNB", needlePos_VNB)

        drive_right()
        techArray()

        flag_left = 0
        flag_right = 1

        directionChanged +=1



def inputChange_directionChange(directionchange_GPIO):
    
    get_needlePos_VNB()

    global directionChanged
    global flag_left
    global flag_right

    print("GPI0_directionChange: ", needlePos_VNB)

    if (needlePos_VNB <= (int(rightEndData_VNB)-18)  and col == 1 and flag_right == 1):

        poti_speed()
        techArray()
        print("after colour change: ", needlePos_VNB)      
    
        flag_left = 1
        flag_right = 0
        
        directionChanged +=1
        #print("dirC right", directionChanged)


    

# interrupt, bouncetime 1 ms
GPIO.add_event_detect(right_GPIO, GPIO.RISING, callback=inputChange_right, bouncetime=200)
GPIO.add_event_detect(left_GPIO, GPIO.RISING, callback=inputChange_left, bouncetime=200)
GPIO.add_event_detect(directionchange_GPIO, GPIO.RISING, callback=inputChange_directionChange, bouncetime=500)



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

    c.execute('CREATE TABLE IF NOT EXISTS stuffToPlot(tabID INTEGER,datestamp TEXT,'
              'rV INTEGER, rH INTEGER,'
              'dirC INTEGER,'
              'lockV TEXT, lockH TEXT,'
              'patV INTEGER, patH INTEGER,'
              'tec INTEGER, cTec INTEGER,'
              'fo INTEGER, cForm INTEGER, fLine INTEGER,'
              'leEV INTEGER, riEV INTEGER,'
              'leEH INTEGER, riEH INTEGER,'
              'mgV REAL, mgH REAL)')

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
        global form
        global rowCountForm
        global countForm_line
        global leftEndData_VNB
        global rightEndData_VNB
        global leftEndData_HNB
        global rightEndData_HNB
        global mg_VNB
        global mg_HNB


        global tech_Array
        global form_Array
        global height_VNB
        global height_HNB

        global knitpat_black_VNB
        global knitpat_white_VNB
        global knitpat_green_VNB
        global knitpat_blue_VNB
        global knitpat_blg_VNB
        global knitpat_blgb_VNB

        global knitpat_black_HNB
        global knitpat_white_HNB
        global knitpat_green_HNB
        global knitpat_blue_HNB
        global knitpat_blg_HNB
        global knitpat_blgb_HNB

        c.execute('SELECT tabID, datestamp,'
                  'rV, rH,'
                  'dirC,'
                  'lockV, lockH,'
                  'patV, patH,'
                  'tec, cTec,'
                  'fo, cForm, fLine,'
                  'leEV, riEV,'
                  'leEH,riEH,'
                  'mgV, mgH FROM stuffToPlot WHERE tabID = :tabID',
                  {'tabID': tableID})

        result = c.fetchone()

        print("{:<6s}{:>4d}".format("tabID:", result[0]))
        print("{:<6s}{:>4s}".format("date:", result[1]))

        rowCount_VNB = result[2]
        print("{:<6s}{:>4d}".format("rV:", rowCount_VNB))

        rowCount_HNB = result[3]
        print("{:<6s}{:>4d}".format("rH:", rowCount_HNB))

        directionChanged = result[4]
        print("{:<6s}{:>4d}".format("dirC:", directionChanged))

        lockSetting_VNB = result[5]
        print("{:<6s}{:>4s}".format("lock_V:", lockSetting_VNB))

        lockSetting_HNB = result[6]
        print("{:<6s}{:>4s}".format("lock_H:", lockSetting_HNB))

        # When new started, import the last used pat and create the pattern array

        patNum_VNB = result[7]
        print("{:<6s}{:>4d}".format("patV:", patNum_VNB))

        temp_patNumb_VNB = str(patNum_VNB) + ".bmp"
        file_name_pat_VNB = ("/home/pi/PyIrene/ProgrammCode/Pat/" + temp_patNumb_VNB)

        try:
            (knitpat_black_VNB,knitpat_white_VNB,knitpat_green_VNB,
            knitpat_blue_VNB,knitpat_blg_VNB,knitpat_blgb_VNB) = get_pattern(file_name_pat_VNB)
            height_VNB = len(knitpat_black_VNB)         

        except IOError:
            self.errorDialog("!no knitpattern VNB")

        patNum_HNB = result[8]
        print("{:<6s}{:>4d}".format("patH:", patNum_HNB))


        temp_patNumb_HNB = str(patNum_HNB) + ".bmp"
        file_name_pat_HNB = ("/home/pi/PyIrene/ProgrammCode/Pat/" + temp_patNumb_HNB)

        try:
            (knitpat_black_HNB, knitpat_white_HNB, knitpat_green_HNB, knitpat_blue_HNB,
            knitpat_blg_HNB, knitpat_blgb_HNB) = get_pattern(file_name_pat_HNB)
            height_HNB = len(knitpat_black_HNB)

        except IOError:
            self.errorDialog("!no knitpattern HNB")

        # When new started import last used technique and create the tech array

        tech = result[9]
        print("{:<6s}{:>4d}".format("tec:", tech))

        try:
            
            tech_Array = returnTechData(tech)

            countTech = result[10]
            
            print("{:<6s}{:>4d}".format("cTec:", countTech))

        except IOError:
            self.errorDialog("!TechArray or count Tech error")


        form = result[11]
        print("{:<6s}{:>4d}".format("form:", form))

        try:
            form_Array = returnFormData(form)

            rowCountForm = result[12]
            print("{:<6s}{:>4d}".format("cForm:", rowCountForm))
            countForm_line = result[13]
            print("{:<6s}{:>4d}".format("fLine:", countForm_line))
            
        except IOError:
            self.errorDialog("!formArray or countForm_line error")


        leftEndData_VNB = result[14]
        print("{:<6s}{:>4d}".format("leEV:", leftEndData_VNB))

        rightEndData_VNB = result[15]
        print("{:<6s}{:>4d}".format("riEV:", rightEndData_VNB))

        leftEndData_HNB = result[16]
        print("{:<6s}{:>4d}".format("leEH:", leftEndData_HNB))

        rightEndData_HNB = result[17]
        print("{:<6s}{:>4d}".format("riEH:", rightEndData_HNB))

        mg_VNB = result[18]
        print("mgV:", mg_VNB)

        mg_HNB = result[19]
        print("mgH:", mg_HNB)

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
    fo = form
    cForm = rowCountForm
    fLine = countForm_line
    leEV = leftEndData_VNB
    riEV = rightEndData_VNB
    leEH = leftEndData_HNB
    riEH = rightEndData_HNB
    mgV = mg_VNB
    mgH = mg_HNB
    tabID = tableID

    unix = time.time()
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%d-%m-%Y %H:%M:%S'))

    c.execute(
        'INSERT INTO stuffToPlot(tabID,datestamp,'
        'rV,rH,'
        'dirC,'
        'lockV,lockH,'
        'patV,patH,'
        'tec,cTec,'
        'fo,cForm,fLine,'
        'leEV,riEV,'
        'leEH,riEH,'
        'mgV,mgH) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (tableID, date,
         rowCount_VNB, rowCount_HNB,
         directionChanged,
         lockSetting_VNB, lockSetting_HNB,
         patNum_VNB, patNum_HNB,tech,
         countTech,form, rowCountForm,countForm_line,
         leftEndData_VNB, rightEndData_VNB,
         leftEndData_HNB, rightEndData_HNB,
         mg_VNB, mg_HNB))

    conn.commit()

    tableID += 1
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
    global form
    global rowCountForm
    global countForm_line
    global leftEndData_VNB
    global rightEndData_VNB
    global leftEndData_HNB
    global rightEndData_HNB
    global mg_VNB
    global mg_HNB


    conn = sqlite3.connect('passapProject.db')
    c = conn.cursor()

    c.execute("SELECT tabID, datestamp,"
              "rV, rH,"
              "dirC,"
              "lockV, lockH,"
              "patV, patH,"
              "tec, cTec,"
              "fo, cForm, fLine,"
              "leEV, riEV,"
              "leEH, riEH,"
              "mgV, mgH FROM stuffToPlot WHERE dirC = :dirC",
              {"dirC": dirC_num})

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
        form = result[11]
        rowCountForm = result[12]
        countForm_line = result[13]
        leftEndData_VNB = result[14]
        rightEndData_VNB = result[15]
        leftEndData_HNB = result[16]
        rightEndData_HNB = result[17]
        mg_VNB = result[18]
        mg_HNB = result[19]


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

def sendRow_colour_blue_green_black():
    sendRow_color_toArduino(knitpat_blgb_VNB, 'blue_green_black')

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

def sendRow_colour_blue_green_black_HNB():
    sendRow_color_toArduino_HNB(knitpat_blgb_HNB, 'blue_green_black')

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
           'blgbV':sendRow_colour_blue_green_black,
           'eV':send_emptyRow_VNB, 'nV':send_fullRow_VNB,
           'rib10V':send_rib10_VNB, 'rib01V':send_rib01_VNB,
           'bH':sendRow_colour_black_HNB, 'wH':sendRow_colour_white_HNB,
           'gH':sendRow_colour_green_HNB,'blH':sendRow_colour_blue_HNB,
           'blgH':sendRow_colour_blue_green_HNB,
           'blgbH':sendRow_colour_blue_green_black_HNB,
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

    connectionHNB.send("setNPos", 100)

    received_cmd = connectionHNB.receive()
    received = received_cmd[1][0]

    try:
        if received!=None:
            pass
    except:
        print("No value HNB")

    print("HNV 0Pos: ", received)

    sendData()

    
def set_dirChange_to_0():
    global directionChanged
    directionChanged = 0
    print("directionChanged: ", directionChanged)

def setLeftEnd_VNB(data):
    leftEnd_VNB = int(data) 
    connectionVNB.send("setLeEnd", int(leftEnd_VNB))
    received = connectionVNB.receive()
    print("VNB left end Arduino: ", received[1][0])

def setLeftEnd_HNB(data):
    leftEnd_HNB = int(data)
    connectionHNB.send("setLeEnd", int(leftEnd_HNB))
    received = connectionHNB.receive()
    print("HNB left end Arduino: ", received[1][0]) 


def setRightEnd_VNB(data):
    rightEnd_VNB = int(data)

    connectionVNB.send("setRiEnd", int(rightEnd_VNB))
    received_VNB = connectionVNB.receive()
    print("VNB right end Arduino: ", received_VNB[1][0])  
    
def setRightEnd_HNB(data):
    rightEnd_HNB = int(data)
    
    connectionHNB.send("setRiEnd", int(rightEnd_HNB))   
    received = connectionHNB.receive()
    print("HNB right end Arduino: ", received[1][0])





#======================================================================
# GUI PyQT5
#======================================================================
numb = ""
newNum = ""
doneN = False


# interface
class App(QtWidgets.QMainWindow):

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
            QtWidgets.QApplication.instance(self).quit
            
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
        font.setPointSize(12)
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
                if directionChanged >= 2 and directionChanged % 2 == 0:
                    directionChanged -= 2
                    read_from_db(directionChanged)
                elif directionChanged >= 1 and directionChanged % 2 == 1:
                    directionChanged -= 1
                    read_from_db(directionChanged)
                
            except:
                print("no dirChanged: ", directionChanged)
                

        global sendData

        def sendData():
            sendData_VNB()
            sendData_HNB()

        def sendData_VNB():
            setLeftEnd_VNB(leftEndData_VNB)
            setRightEnd_VNB(rightEndData_VNB)

        def sendData_HNB():
            setLeftEnd_HNB(leftEndData_HNB)
            setRightEnd_HNB(rightEndData_HNB)

        global newSettings
        global newLabelText


        # sets the information in the process window
        def newSettings():
            self.label_col.setText("Change to " + colorSetting)
            self.label_lock_VNB.setText("Lock_V: " + lockSetting_VNB)
            self.label_lock_HNB.setText("Lock_H: " + lockSetting_HNB)
            self.label_row_VNB_2.setText("rowCPat_V: " + str(rowCount_VNB) + " / " + str(height_VNB))
            self.label_row_HNB_2.setText("rowCPat_H: " + str(rowCount_HNB) + " / " + str(height_HNB))
            self.label_text.setText("InfoTech: " + infoTech)
            self.label_textForm.setText("InfoForm: " + infoForm)
            self.label_direction_2.setText("dirChanged: " + str(directionChanged))
            self.label_pat_VNB_2.setText("pat_V: " + str(patNum_VNB))
            self.label_pat_HNB_2.setText("pat_H: " + str(patNum_HNB))
            self.label_MG_VNB.setText("MG_V: " + str(mg_VNB))
            self.label_MG_HNB.setText("MG_H: " + str(mg_HNB))
            self.label_tech_2.setText("Tech: " + str(tech) + "     countTech: " + str(countTech))
            self.label_form_2.setText("Form: " + str(form) + "     Line: " + str(countForm_line) + "    Row: " + str(rowCountForm))

        def newLabelText():

            # Display number is different from number which is sent to arduino,
            # negativ numbers mean right of the middle,
            # positiv numbers mean left of the middle
            #self.label_left.setText("LeEnd: " + str(leftEndData))
            self.label_left_VNB.setText("LeEnd_V: " + str(leftEndData_VNB))
            self.label_left_HNB.setText("LeEnd_H: " + str(leftEndData_HNB))
            self.label_right_VNB.setText("RiEnd_V: " + str(rightEndData_VNB))
            self.label_right_HNB.setText("RiEnd_H: " + str(rightEndData_HNB))
            self.label_row_VNB.setText("rowCPat_V: " + str(rowCount_VNB))
            self.label_row_HNB.setText("rowCPat_H: " + str(rowCount_HNB))
            self.label_height_VNB.setText("height_V: " + str(height_VNB))
            self.label_height_HNB.setText("height_H: " + str(height_HNB))
            self.label_direction.setText("dirChanged: " + str(directionChanged))
            self.label_pat_VNB.setText("pat_V: " + str(patNum_VNB))
            self.label_pat_HNB.setText("pat_H: " + str(patNum_HNB))
            self.label_tech.setText("Tech: " + str(tech))
            self.label_form.setText("Form: " + str(form))

            newSettings()
          




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


                # Shows data, button
        self.showData = QtWidgets.QPushButton('Data', self.tab1)
        self.showData.setEnabled(True)
        self.showData.setGeometry(QtCore.QRect(120, 20, 100, 60))
        self.showData.clicked.connect(newLabelText)

        # send data, button
        self.sendData = QtWidgets.QPushButton('SetEndP', self.tab1)
        self.sendData.setEnabled(True)
        self.sendData.setGeometry(QtCore.QRect(230, 90, 100, 60))
        self.sendData.clicked.connect(sendData)

        # send data, button
        self.sendData_VNB = QtWidgets.QPushButton('SetEnd_VNB', self.tab1)
        self.sendData_VNB.setEnabled(True)
        self.sendData_VNB.setGeometry(QtCore.QRect(230, 160, 100, 60))
        self.sendData_VNB.clicked.connect(sendData_VNB)

        # send data, button
        self.sendData_HNB = QtWidgets.QPushButton('SetEnd_HNB', self.tab1)
        self.sendData_HNB.setEnabled(True)
        self.sendData_HNB.setGeometry(QtCore.QRect(230, 230, 100, 60))
        self.sendData_HNB.clicked.connect(sendData_HNB)

        self.directionBtn = QtWidgets.QPushButton('DirC_0', self.tab1)
        self.directionBtn.setEnabled(True)
        self.directionBtn.setGeometry(QtCore.QRect(120, 90, 100, 60))
        self.directionBtn.clicked.connect(set_dirChange_to_0)        

        # static settings
        self.numPad_process = QtWidgets.QPushButton('SX Row', self.tab1)
        self.numPad_process.setStyleSheet("background-color:rgb(204,255,229)")
        self.numPad_process.setEnabled(True)
        self.numPad_process.setGeometry(QtCore.QRect(230, 20, 100, 60))
        self.numPad_process.clicked.connect(start_SX_Row)


        # Add labels
        self.label_left_VNB = QLabel("LeEnd_V", self.tab1)
        self.label_left_VNB.setGeometry(QtCore.QRect(350, 120, 120, 60))
        self.label_left_VNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_left_VNB.show()

        self.label_left_HNB = QLabel("LeEnd_H", self.tab1)
        self.label_left_HNB.setGeometry(QtCore.QRect(480, 120, 120, 60))
        self.label_left_HNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_left_HNB.show()

        self.label_right_VNB = QLabel("RiEnd_V", self.tab1)
        self.label_right_VNB.setGeometry(QtCore.QRect(350, 150, 120, 60))
        self.label_right_VNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_right_VNB.show()

        self.label_right_HNB = QLabel("RiEnd_H", self.tab1)
        self.label_right_HNB.setGeometry(QtCore.QRect(480, 150, 120, 60))
        self.label_right_HNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_right_HNB.show()

        self.label_height_VNB = QLabel("Height_V", self.tab1)
        self.label_height_VNB.setGeometry(QtCore.QRect(350, 30, 170, 60))
        self.label_height_VNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_height_VNB.show()

        self.label_height_HNB = QLabel("Height_H", self.tab1)
        self.label_height_HNB.setGeometry(QtCore.QRect(480, 30, 170, 60))
        self.label_height_HNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_height_HNB.show()

        self.label_row_VNB = QLabel("rowCPat-V", self.tab1)
        self.label_row_VNB.setGeometry(QtCore.QRect(350, 60, 120, 60))
        self.label_row_VNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_row_VNB.show()

        self.label_row_HNB = QLabel("rowCPat-H", self.tab1)
        self.label_row_HNB.setGeometry(QtCore.QRect(480, 60, 120, 60))
        self.label_row_HNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_row_HNB.show()
        
        self.label_direction = QLabel("dirChange", self.tab1)
        self.label_direction.setGeometry(QtCore.QRect(350, 180, 220, 60))
        self.label_direction.setBaseSize(QtCore.QSize(30, 20))
        self.label_direction.show()

        self.label_pat_VNB = QLabel("Pat_V", self.tab1)
        self.label_pat_VNB.setGeometry(QtCore.QRect(350, 0, 220, 60))
        self.label_pat_VNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_pat_VNB.show()

        self.label_pat_HNB = QLabel("Pat_H", self.tab1)
        self.label_pat_HNB.setGeometry(QtCore.QRect(480, 0, 220, 60))
        self.label_pat_HNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_pat_HNB.show()

        self.label_tech = QLabel("Tech", self.tab1)      
        self.label_tech.setGeometry(QtCore.QRect(350, 210, 220, 60))
        self.label_tech.setBaseSize(QtCore.QSize(30, 20))
        self.label_tech.show()

        self.label_form = QLabel("Form", self.tab1)
        self.label_form.setGeometry(QtCore.QRect(350, 240, 220, 60))
        self.label_form.setBaseSize(QtCore.QSize(30, 20))
        self.label_form.show()

        self.fontlab = QFont ('Arial Narrow bold', 14)
        self.fontlab.setBold(False)

        

        # Add labels Processing Data
        self.label_col = QLabel("Color", self.tab2)
        self.label_col.setGeometry(QtCore.QRect(130, 20, 220, 40))
        self.label_col.setBaseSize(QtCore.QSize(30, 20))
        self.label_col.setFont(self.fontlab)
        self.label_col.setStyleSheet("color:rgb(200,50,0)")
        self.label_col.setStyleSheet("background-color:rgb(230,230,230)")
        self.label_col.show()

        self.label_tech_2 = QLabel("Tech", self.tab2)      
        self.label_tech_2.setGeometry(QtCore.QRect(130, 60, 220, 40))
        self.label_tech_2.setBaseSize(QtCore.QSize(30, 30))
        self.label_tech_2.show()

        self.label_form_2 = QLabel("Form", self.tab2)      
        self.label_form_2.setGeometry(QtCore.QRect(130, 90, 220, 40))
        self.label_form_2.setBaseSize(QtCore.QSize(30, 30))
        self.label_form_2.show()

        self.label_direction_2 = QLabel("dirChange", self.tab2)
        self.label_direction_2.setGeometry(QtCore.QRect(130,120, 220, 40))
        self.label_direction_2.setBaseSize(QtCore.QSize(30, 20))
        self.label_direction_2.show()

        self.label_MG_VNB = QLabel("MG_V", self.tab2)
        self.label_MG_VNB.setGeometry(QtCore.QRect(130, 150, 220, 40))
        self.label_MG_VNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_MG_VNB.show()

        self.label_MG_HNB = QLabel("MG_H", self.tab2)
        self.label_MG_HNB.setGeometry(QtCore.QRect(130, 180, 220, 40))
        self.label_MG_HNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_MG_HNB.show()

        self.label_text = QLabel("Info Tech", self.tab2)
        self.label_text.setGeometry(QtCore.QRect(15, 250, 320, 40))
        self.label_text.setBaseSize(QtCore.QSize(30, 20))
        self.label_text.setFont(self.fontlab)
        self.label_text.setStyleSheet("color:rgb(200,50,0)")
        self.label_text.setStyleSheet("background-color:rgb(230,230,230)")
        self.label_text.show()

        self.label_textForm = QLabel("Info Form", self.tab2)
        self.label_textForm.setGeometry(QtCore.QRect(340, 250, 220, 40))
        self.label_textForm.setBaseSize(QtCore.QSize(30, 20))
        self.label_textForm.setFont(self.fontlab)
        self.label_textForm.setStyleSheet("color:rgb(200,50,0)")
        self.label_textForm.setStyleSheet("background-color:rgb(200,230,230)")
        self.label_textForm.show()

        ###

        self.label_pat_VNB_2 = QLabel("Pat_V", self.tab2)
        self.label_pat_VNB_2.setGeometry(QtCore.QRect(390, 0, 220, 60))
        self.label_pat_VNB_2.setBaseSize(QtCore.QSize(30, 20))
        self.label_pat_VNB_2.show()

        self.label_pat_HNB_2 = QLabel("Pat_H", self.tab2)
        self.label_pat_HNB_2.setGeometry(QtCore.QRect(390, 30, 220, 60))
        self.label_pat_HNB_2.setBaseSize(QtCore.QSize(30, 20))
        self.label_pat_HNB_2.show()

        self.label_lock_VNB = QLabel("Lock_V", self.tab2)
        self.label_lock_VNB.setGeometry(QtCore.QRect(390, 60, 220, 60))
        self.label_lock_VNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_lock_VNB.show()

        self.label_lock_HNB = QLabel("Lock_H", self.tab2)
        self.label_lock_HNB.setGeometry(QtCore.QRect(390, 90, 220, 60))
        self.label_lock_HNB.setBaseSize(QtCore.QSize(30, 20))
        self.label_lock_HNB.show()

        self.label_row_VNB_2 = QLabel("rowVNB", self.tab2)
        self.label_row_VNB_2.setGeometry(QtCore.QRect(390, 120, 220, 60))
        self.label_row_VNB_2.setBaseSize(QtCore.QSize(30, 20))
        self.label_row_VNB_2.show()

        self.label_row_HNB_2 = QLabel("rowHNB", self.tab2)
        self.label_row_HNB_2.setGeometry(QtCore.QRect(390, 150, 220, 60))
        self.label_row_HNB_2.setBaseSize(QtCore.QSize(30, 20))
        self.label_row_HNB_2.show()






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

        global setPat_VNB
        global setPat_HNB

        def setPat_VNB(data):

            global patNum_VNB
            global knitpat_black_VNB
            global knitpat_white_VNB
            global knitpat_green_VNB
            global knitpat_blue_VNB
            global knitpat_blg_VNB
            global knitpat_blgb_VNB

            patNum_VNB = data

            temp_patNumb_VNB = str(patNum_VNB) + ".bmp"
            file_name_pat_VNB = ("/home/pi/PyIrene/ProgrammCode/Pat/" + temp_patNumb_VNB)

            try:
                (knitpat_black_VNB,knitpat_white_VNB,knitpat_green_VNB,knitpat_blue_VNB,
                 knitpat_blg_VNB, knitpat_blgb_VNB) = get_pattern(file_name_pat_VNB)
            
                global height_VNB
                height_VNB = len(knitpat_black_VNB)
                print("height VNB: ", height_VNB)
                print("pat_VNB is: " + patNum_VNB)

            except IOError:
                print("no such pattern number")
                self.errorDialog("! No such pattern number: " + patNum_VNB) 


        def setPat_HNB(data):

            global patNum_HNB
            global knitpat_black_HNB
            global knitpat_white_HNB
            global knitpat_green_HNB
            global knitpat_blue_HNB
            global knitpat_blg_HNB
            global knitpat_blgb_HNB

            patNum_HNB = data

            temp_patNumb_HNB = str(patNum_HNB) + ".bmp"
            file_name_pat_HNB = ("/home/pi/PyIrene/ProgrammCode/Pat/" + temp_patNumb_HNB)

            try:
                (knitpat_black_HNB, knitpat_white_HNB, knitpat_green_HNB, knitpat_blue_HNB,
                 knitpat_blg_HNB, knitpat_blgb_HNB) = get_pattern(file_name_pat_HNB)

                global height_HNB
                height_HNB = len(knitpat_black_HNB)
                print("height HNB: ", height_HNB)
                print("pat_HNB is: " + patNum_HNB)

            except IOError:
                print("no such pattern number")
                self.errorDialog("! No such pattern number: " + patNum_VNB)


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
        global leftEndData_VNB
        global rightEndData_VNB
        global leftEndData_HNB
        global rightEndData_HNB
        global numb
        global rowCount_VNB
        global rowCount_HNB
        global directionChanged
        global patNum_VNB
        global patNum_HNB
        global mg_VNB
        global mg_HNB
        global tech
        global countTech
        global form
        global countForm_line
        global rowCountForm
        global countForm_line
        global rowCountForm
        global endKniterror
        
        sender = self.sender()
        msg = sender.text()

        if msg == "LeE":

            x = int(numb)
            
            if x < 180 and x > 0:
                leftEndData_VNB = x
                leftEndData_HNB = x

                print("left end VNB: ", leftEndData_VNB)

            else:
                print("Value error leftEndData")

            numb = ""

        if msg == "LeEV":

            x = int(numb)
            
            if x < 180 and x > 0:
                leftEndData_VNB = x

                print("left end_VNB: ", leftEndData_VNB)

            else:
                print("Value error leftEndData_VNB")

            numb = ""

        if msg == "LeEH":

            x = int(numb)
            
            if x < 180 and x > 0:
                leftEndData_HNB = x

                print("left end_HNB: ", leftEndData_HNB)

            else:
                print("Value error leftEndData_HNB")

            numb = ""
                
          

# hier sollte ich etwas ändern, ich brauche 2Variablen
        if msg == "RiE":

            x = int(numb)

            if x < 180 and x > 0:
                rightEndData_VNB = x
                rightEndData_HNB = x

                print("Right end VNB: ", rightEndData_VNB)

            else:
                print("Value error rightEndData")
                    
            numb = ""


        if msg == "RiEV":

            x = int(numb)

            if x < 180 and x > 0:
                rightEndData_VNB = x

                print("Right end VNB: ", rightEndData_VNB)

            else:
                print("Value error rightEndData_VNB")
                    
            numb = ""

        
        if msg == "RiEH":

            x = int(numb)

            if x < 180 and x > 0:
                rightEndData_HNB = x

                print("Right end HNB: ", rightEndData_HNB)

            else:
                print("Value error rightEndData_HNB")
                    
            numb = ""
            

        if msg == "RowV":
            rowCount_VNB = numb
            print("RowCount_VNB: " + rowCount_VNB)
            numb = ""

        if msg == "RowH":
            rowCount_HNB = numb
            print("RowCount_HNB: " + rowCount_HNB)
            numb = ""

        # Dir ermöglicht auf eine bestimmte Reihe in der DB zurückzuspringen
        if msg == "Dir":
            dirChange = numb
            read_from_db(dirChange)
            directionChanged = dirChange
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

            temp_numb_VNB = numb
            numb = ""
            setPat_VNB(temp_numb_VNB)           
            print("pat_numpad_VNB is: " + temp_numb_VNB)


        if msg == "PatH":
            temp_numb_HNB = numb
            numb = ""
            setPat_HNB(temp_numb_HNB)           
            print("pat_numpad_HNB is: " + temp_numb_HNB)
            
                        

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

        if msg == "cTec":
            countTech = int(numb)
            print("countTech is: ", countTech)
            numb = ""

        if msg == "Form":
            form = numb
            print("form is: " + form)
            numb = ""

            global form_Array
            global countForm_line
            global rowCountForm
            global jumpCounter
            global repeadFromLineX
            global repead_fromLine0

            try:
                form_Array = returnFormData(form)
                countForm_line = 0
                rowCountForm = 0
                repead_fromLine0 = 0
                repeadFromLineX = 0
                jumpCounter = 0
                print("Form is: " + form)
                print("form_Array", form_Array)
                print("countForm_line: ", countForm_line)
                print("rowCountForm: ", rowCountForm)
                numb = ""
            except IOError:
                self.errorDialog("! No such form number: " + form)

        if msg == "formC":
            rowCountForm = int(numb)
            print("rowCountForm is: ", rowCountForm)
            numb = ""

        if msg == "fLine":
            countForm_line = int(numb)
            print("countForm_line is: ", countForm_line)

            endKniterror = 0
            print("reset endKnitError to 0")
            
            numb = ""

        dynamic_date_entry_settings()
        newLabelText()
        newSettings()           


    def errorDialog(self, data):

##      print("reached")
        
        d = QDialog()

        self.layout2=QGridLayout(self)

        def doneAll(self):
            d.destroy()
     
        self.error = QtWidgets.QPushButton("&"+data, d)
        self.error.setStyleSheet("background-color:rgb(255,125,50)")
        self.error.setEnabled(True)
        

        self.fontBtn = QFont ('Arial Narrow', 14)
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
        self.countTech = QtWidgets.QPushButton("cTec", d)
        self.countTech.setStyleSheet("background-color:rgb(255,255,200)")
        self.bQuit = QtWidgets.QPushButton("Quit", d)
        self.bQuit.setStyleSheet("background-color:rgb(180,0,0)")
        self.form = QtWidgets.QPushButton("Form", d)
        self.form.setStyleSheet("background-color:rgb(255,100,0)")
        self.formLine = QtWidgets.QPushButton("fLine", d)
        self.formLine.setStyleSheet("background-color:rgb(255,200,150)")
        self.formCounter = QtWidgets.QPushButton("formC", d)
        self.formCounter.setStyleSheet("background-color:rgb(255,230,200)")


        nums = [self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8, self.b9, self.b0]
        oper = [self.leEnd, self.riEnd, self.rowBack_VNB, self.rowBack_HNB, self.direction,
                self.pattern_VNB,self.pattern_HNB, self.MG_VNB, self.MG_HNB, self.tech,self.countTech,
                self.bQuit,self.form,self.formLine,self.formCounter]
        self.fontBtn = QFont ('Arial Narrow bold', 14)
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
        self.countTech.clicked.connect(self.setNumb)
        self.form.clicked.connect(self.setNumb)
        self.formLine.clicked.connect(self.setNumb)
        self.formCounter.clicked.connect(self.setNumb)


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

        self.layout2.addWidget(self.tech, 3, 1)
        self.layout2.addWidget(self.countTech, 3, 0)

        self.layout2.addWidget(self.bQuit, 3, 6)

        self.layout2.addWidget(self.form, 3, 3)        
        self.layout2.addWidget(self.formLine, 3, 4)
        self.layout2.addWidget(self.formCounter, 3, 5)



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



