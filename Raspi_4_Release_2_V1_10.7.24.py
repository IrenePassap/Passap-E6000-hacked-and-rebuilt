""" 9.7.24: DB Fehler korrigiert, Einzug war nicht korrekt. Jetzt funktioniert alles tiptop

    29.4.24: Reihenfolge col und row_end_stopp geändert: Code Zeile 1766

    Neue Version 20.8.23: Alles portiert auf Raspberry pi 4:
    Ich habe den Code überarbeitet
    Ich habe keine Arduino IDE installiert. Bewusst nicht. Hatte Probleme. Es gibt eine neue IDE 2.0 für 64bit.
    Vorläufig brauche ich keine Arduino IDE, da der Code auf den Arduinos problemlos läuft. So hoffe ich.
    Nach der Reise werde ich die Kommunikation überarbeiten.

    Information: Siehe Arduino VNB
    neue Version 14.7.22: Habe Zeile geändert:
    if Var.col_change == 0 and Var.needle_pos_vnb ≤ (int(Var.right_end_data_vnb)-15) and Var.flag_right == 1:
    auf: if Var.col_change == 0 and Var.needle_pos_vnb ≤ (int(Var.right_end_data_vnb)-5) and Var.flag_right == 1:
    Warum: Wenn right end < 15, dann fährt der Schlitten nicht in den Farbwechsler
    neue Version 13.5.23: Habe DB geändert.
    Es gab Probleme beim Kreieren eines neuen DB Files. Die Routine hat die exception nicht ausgeführt.
    Daher musste ich den Code anpassen "exception as e": Jetzt funktioniert die Routine.
    Wenn ein neues DB File erzeugt wird, wird eine exception geworfen (value = NULL).
    Eine Message Box informiert. Auf Bestätigung wird die Exception ausgeführt: return tab_ID = 0
"""

import csv
import datetime
import sqlite3
import sys
import time
import os

import PyCmdMessenger
import RPi.GPIO as GPIO
from PIL import Image
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QRect, QElapsedTimer
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QGridLayout, QDialog, QTableWidgetItem, QMessageBox, \
    QHBoxLayout, QTableWidget, \
    QTabWidget, QVBoxLayout, QWidget, QTextEdit, QAction, QLabel

"""--------------------------------------------------
Setup Pin for interrupt
----------------------------------------------------"""

# GPIO Pin to get signals form Arduino front lock


"""---------------------------------------------------
Class Variables
Unique Variablennamen verwenden
Alle Variablennamen durchgängig klein schreiben und mit underline lesbar machen
------------------------------------------------------"""

# Tests waren bisher erfolgreich, 28.12.21

print("Arduino_running_M0_VNB_Version_12.2_beta_27.12.2021")
print("Arduino_M0_Pro_HNB_Version_12.1_beta_27.12.21")

timer = QElapsedTimer()

# Setze den Pfad dynamisch basierend auf dem aktuellen Verzeichnis
base_path = os.path.dirname(__file__)  # Pfad zur aktuellen Datei
icon_path_right = os.path.join(base_path, "Icon_drive_right.png")
icon_path_left = os.path.join(base_path, "icon_drive_left.png")


class Var:
    pat_num_vnb = 201
    pat_num_hnb = 202

    # height of knitting pattern
    height_vnb = 0
    height_hnb = 0

    # count knitted row
    row_count = 0

    # count knitted row vnb, hnb
    row_count_vnb = 0
    row_count_hnb = 0

    # position
    needle_pos_vnb = 1
    needle_pos_hnb = 1

    # stich size
    mg_vnb = 0.0
    mg_hnb = 0.0

    # default left end knitting, right end knitting
    right_end_data_vnb = 30
    left_end_data_vnb = 120
    right_end_data_hnb = 30
    left_end_data_hnb = 120

    # counts each direction change
    direction_changed = 0

    errorValue = 0

    # FORM ----------------------------------------------------

    # count knitted form rows
    row_count_form = 0
    # counter counts row in form file
    count_form_line = 0

    # form = default form
    form = '1'
    form_array = []
    end_knit_error = 0

    # Counter used for form repeat and jump
    repeat_from_line_x = 0
    repeat_from_line_0 = 0
    jump_counter = 0

    decrease_left = 0
    decrease_right = 0

    increase_left = 0
    increase_right = 0

    # Info
    info_form = ""

    # for DB
    table_id = 1

    # TECH --------------------------------------------------

    # Counter for technique file
    count_tech = 0

    # tech = default technik
    tech = ""
    tech_array = []
    lock_side_is = ""

    # flags
    flag_left = 1
    flag_right = 0

    # tech settings
    color_setting = ""
    lock_setting_vnb = ""
    lock_setting_hnb = ""

    # futur use
    rack = 0
    rack_left = 0
    rack_right = 0

    # Info
    info_tech = ""

    # Array for knit pattern
    knitpat_black_vnb = []
    knitpat_white_vnb = []
    knitpat_green_vnb = []
    knitpat_blue_vnb = []
    knitpat_red_vnb = []
    knitpat_yellow_vnb = []

    knitpat_black_white_vnb = []
    knitpat_black_green_vnb = []
    knitpat_black_blue_vnb = []
    knitpat_black_red_vnb = []
    knitpat_black_yellow_vnb = []

    knitpat_black_white_green_vnb = []
    knitpat_black_white_blue_vnb = []
    knitpat_black_white_red_vnb = []
    knitpat_black_white_yellow_vnb = []

    knitpat_black_green_blue_vnb = []
    knitpat_black_green_red_vnb = []
    knitpat_black_green_yellow_vnb = []

    knitpat_black_blue_red_vnb = []
    knitpat_black_blue_yellow_vnb = []
    knitpat_black_red_yellow_vnb = []

    knitpat_black_white_green_blue_vnb = []
    knitpat_black_white_green_red_vnb = []
    knitpat_black_white_green_yellow_vnb = []
    knitpat_black_white_blue_red_vnb = []
    knitpat_black_white_blue_yellow_vnb = []
    knitpat_black_white_red_yellow_vnb = []

    knitpat_black_green_blue_red_vnb = []
    knitpat_black_green_blue_yellow_vnb = []
    knitpat_black_green_red_yellow_vnb = []
    knitpat_black_blue_red_yellow_vnb = []

    knitpat_white_green_vnb = []
    knitpat_white_blue_vnb = []
    knitpat_white_red_vnb = []
    knitpat_white_yellow_vnb = []

    knitpat_white_green_blue_vnb = []
    knitpat_white_green_red_vnb = []
    knitpat_white_green_yellow_vnb = []

    knitpat_white_blue_red_vnb = []
    knitpat_white_blue_yellow_vnb = []
    knitpat_white_red_yellow_vnb = []

    knitpat_white_green_blue_red_vnb = []
    knitpat_white_green_blue_yellow_vnb = []
    knitpat_white_blue_red_yellow_vnb = []

    knitpat_green_blue_vnb = []
    knitpat_green_red_vnb = []
    knitpat_green_yellow_vnb = []

    knitpat_green_blue_red_vnb = []
    knitpat_green_blue_yellow_vnb = []

    knitpat_green_red_yellow_vnb = []

    knitpat_green_blue_red_yellow_vnb = []

    knitpat_blue_red_vnb = []
    knitpat_blue_yellow_vnb = []

    knitpat_blue_red_yellow_vnb = []

    knitpat_red_yellow_vnb = []

    # -----------------------------------------------------

    knitpat_black_hnb = []
    knitpat_white_hnb = []
    knitpat_green_hnb = []
    knitpat_blue_hnb = []
    knitpat_red_hnb = []
    knitpat_yellow_hnb = []

    knitpat_black_white_hnb = []
    knitpat_black_green_hnb = []
    knitpat_black_blue_hnb = []
    knitpat_black_red_hnb = []
    knitpat_black_yellow_hnb = []

    knitpat_black_white_green_hnb = []
    knitpat_black_white_blue_hnb = []
    knitpat_black_white_red_hnb = []
    knitpat_black_white_yellow_hnb = []

    knitpat_black_green_blue_hnb = []
    knitpat_black_green_red_hnb = []
    knitpat_black_green_yellow_hnb = []

    knitpat_black_blue_red_hnb = []
    knitpat_black_blue_yellow_hnb = []
    knitpat_black_red_yellow_hnb = []

    knitpat_black_white_green_blue_hnb = []
    knitpat_black_white_green_red_hnb = []
    knitpat_black_white_green_yellow_hnb = []
    knitpat_black_white_blue_red_hnb = []
    knitpat_black_white_blue_yellow_hnb = []
    knitpat_black_white_red_yellow_hnb = []

    knitpat_black_green_blue_red_hnb = []
    knitpat_black_green_blue_yellow_hnb = []
    knitpat_black_green_red_yellow_hnb = []
    knitpat_black_blue_red_yellow_hnb = []

    knitpat_white_green_hnb = []
    knitpat_white_blue_hnb = []
    knitpat_white_red_hnb = []
    knitpat_white_yellow_hnb = []

    knitpat_white_green_blue_hnb = []
    knitpat_white_green_red_hnb = []
    knitpat_white_green_yellow_hnb = []

    knitpat_white_blue_red_hnb = []
    knitpat_white_blue_yellow_hnb = []
    knitpat_white_red_yellow_hnb = []

    knitpat_white_green_blue_red_hnb = []
    knitpat_white_green_blue_yellow_hnb = []
    knitpat_white_blue_red_yellow_hnb = []

    knitpat_green_blue_hnb = []
    knitpat_green_red_hnb = []
    knitpat_green_yellow_hnb = []

    knitpat_green_blue_red_hnb = []
    knitpat_green_blue_yellow_hnb = []

    knitpat_green_red_yellow_hnb = []

    knitpat_green_blue_red_yellow_hnb = []

    knitpat_blue_red_hnb = []
    knitpat_blue_yellow_hnb = []

    knitpat_blue_red_yellow_hnb = []

    knitpat_red_yellow_hnb = []

    # -----------------------------------------------------

    knitpat_full_row = [128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128,
                        128, 128, 128, 128, 128, 128, 128]
    knitpat_empty_row = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                         255, 255, 255, 255, 255, 255, 255]

    knitpat_rib10 = [85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170,
                     85, 170, 85, 170]
    knitpat_rib01 = [170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85, 170, 85,
                     170, 85, 170, 85]

    # MOTOR ________________________________________________

    # used for Input GPIO drive left: if cursor_pos == 100 and col_change == 1: poti speed, tech_array()
    cursor_pos = 0

    # speed until now two state: O = poti, 1 = speed color changer
    speed = 0

    # end_stopp
    end_stopp = 0
    # form_stopp same function as end_stopp
    form_stopp = 0

    change_drive_left = ""
    change_drive_right = ""
    slow_speed = 0
    speed_value = 0
    row_end = 0
    # col_change has two state: 0 = no color change, 1 = color change
    col_change = 0

    # GUI ____________________________________________________

    numb = ""
    new_num = ""
    done_n = False

    table1 = None
    table2 = None
    table3 = None
    table4 = None
    table5 = None
    table6 = None
    table7 = None

    icon_color_change = QLabel
    icon_stopp = QLabel
    icon_drive = QLabel

    # futur use
    icon_col_1 = QLabel
    icon_col_2 = QLabel
    icon_col_3 = QLabel
    icon_col_4 = QLabel
    icon_decrease_right = QLabel
    icon_decrease_left = QLabel
    icon_increase_right = QLabel
    icon_increase_left = QLabel
    icon_rack = QLabel


"""---------------------------------------------------------------------------
classes
---------------------------------------------------------------------"""


class PatternArray:

    def __init__(self):
        print("PatternArray start")

    @classmethod
    def get_pat_array(cls, data):

        filename = Image.open(data)
        # print("filename", filename)

        width_local = filename.size[0]
        height_local = filename.size[1]

        list_col_red = []
        list_col_green = []
        list_col_blue = []
        list_col_white = []
        list_col_black = []
        list_col_yellow = []

        for x in range(0, height_local):
            row_col_red = []
            row_col_green = []
            row_col_blue = []
            row_col_white = []
            row_col_black = []
            row_col_yellow = []

            for y in range(0, width_local):
                pixel = (y, x)
                red, green, blue = filename.getpixel(pixel)

                row_col_red.append(0) if red > 230 and green < 20 and blue < 20 else row_col_red.append(1)
                row_col_green.append(0) if green > 230 and red < 20 and blue < 20 else row_col_green.append(1)
                row_col_blue.append(0) if blue > 230 and red < 20 and green < 20 else row_col_blue.append(1)
                row_col_white.append(0) if red > 230 and green > 230 and blue > 230 else row_col_white.append(1)
                row_col_black.append(0) if red < 20 and green < 20 and blue < 20 else row_col_black.append(1)
                row_col_yellow.append(0) if red > 230 and green > 230 and blue < 20 else row_col_yellow.append(1)

            list_col_red.append(row_col_red)
            list_col_green.append(row_col_green)
            list_col_blue.append(row_col_blue)
            list_col_white.append(row_col_white)
            list_col_black.append(row_col_black)
            list_col_yellow.append(row_col_yellow)

        # print("row_col_black: ", row_col_black)
        # print("row_col_white: ", row_col_white)
        # print("row_col_green: ", row_col_green)
        # print("row_col_blue: ", row_col_blue)
        # print("row_col_red: ", row_col_red)
        # print("row_col_yellow: ", row_col_yellow)

        def multi_color_list(num, *args):
            if not (1 < num <= 4):  # Überprüfen, ob 'num' zwischen 2 und 4 liegt
                print('Zu viele oder zu wenige Argumente')
                return []

            list_mixed_col = []
            for x_point in range(0, height_local):
                mixed_color = []
                for y_point in range(0, width_local):
                    # Überprüfen, ob irgendein Wert in args[x][y] 0 ist
                    mixed_color.append(0 if any(arg[x_point][y_point] == 0 for arg in args) else 1)
                list_mixed_col.append(mixed_color)

            return list_mixed_col

        def pattern_array(list_col):

            pattern_data_local = list_col
            n = 0
            m = 0
            pattern_local = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

            while m < 25:
                for val in range(0, 7):
                    val_local = pattern_data_local[n]
                    n += 1

                    if val_local == 0:
                        pattern_local[m] = pattern_local[m].__lshift__(1)
                    else:
                        pattern_local[m] = pattern_local[m].__lshift__(1)
                        pattern_local[m] |= 1
                m += 1
            return pattern_local

        def process_knitpat(color_list):
            knitpat = []

            for i in range(0, height_local):
                pattern_local = pattern_array(color_list[i])
                knitpat.append(pattern_local)

            # print("knitpat: ", knitpat)
            return knitpat

        knitpat_black = process_knitpat(list_col_black)
        knitpat_white = process_knitpat(list_col_white)
        knitpat_green = process_knitpat(list_col_green)
        knitpat_blue = process_knitpat(list_col_blue)
        knitpat_red = process_knitpat(list_col_red)
        knitpat_yellow = process_knitpat(list_col_yellow)

        knitpat_black_white = process_knitpat(multi_color_list(2, list_col_black, list_col_white))
        knitpat_black_green = process_knitpat(multi_color_list(2, list_col_black, list_col_green))
        knitpat_black_blue = process_knitpat(multi_color_list(2, list_col_black, list_col_blue))
        knitpat_black_red = process_knitpat(multi_color_list(2, list_col_black, list_col_red))
        knitpat_black_yellow = process_knitpat(multi_color_list(2, list_col_black, list_col_yellow))

        knitpat_black_white_green = process_knitpat(multi_color_list(3, list_col_black, list_col_white,
                                                                     list_col_green))
        knitpat_black_white_blue = process_knitpat(multi_color_list(3, list_col_black, list_col_white,
                                                                    list_col_blue))
        knitpat_black_white_red = process_knitpat(multi_color_list(3, list_col_black, list_col_white,
                                                                   list_col_red))
        knitpat_black_white_yellow = process_knitpat(multi_color_list(3, list_col_black, list_col_white,
                                                                      list_col_yellow))

        knitpat_black_green_blue = process_knitpat(multi_color_list(3, list_col_black, list_col_green,
                                                                    list_col_blue))
        knitpat_black_green_red = process_knitpat(multi_color_list(3, list_col_black, list_col_green,
                                                                   list_col_red))
        knitpat_black_green_yellow = process_knitpat(multi_color_list(3, list_col_black, list_col_green,
                                                                      list_col_yellow))

        knitpat_black_blue_red = process_knitpat(multi_color_list(3, list_col_black, list_col_blue,
                                                                  list_col_red))
        knitpat_black_blue_yellow = process_knitpat(multi_color_list(3, list_col_black, list_col_blue,
                                                                     list_col_yellow))
        knitpat_black_red_yellow = process_knitpat(multi_color_list(3, list_col_black, list_col_red,
                                                                    list_col_yellow))

        knitpat_black_white_green_blue = process_knitpat(
            multi_color_list(4, list_col_black, list_col_white, list_col_green, list_col_blue))
        knitpat_black_white_green_red = process_knitpat(
            multi_color_list(4, list_col_black, list_col_white, list_col_green, list_col_red))
        knitpat_black_white_green_yellow = process_knitpat(
            multi_color_list(4, list_col_black, list_col_white, list_col_green, list_col_yellow))

        knitpat_black_white_blue_red = process_knitpat(
            multi_color_list(4, list_col_black, list_col_white, list_col_blue, list_col_red))
        knitpat_black_white_blue_yellow = process_knitpat(
            multi_color_list(4, list_col_black, list_col_white, list_col_blue, list_col_yellow))
        knitpat_black_white_red_yellow = process_knitpat(
            multi_color_list(4, list_col_black, list_col_white, list_col_red, list_col_yellow))

        knitpat_black_green_blue_red = process_knitpat(
            multi_color_list(4, list_col_black, list_col_green, list_col_blue, list_col_red))
        knitpat_black_green_blue_yellow = process_knitpat(
            multi_color_list(4, list_col_black, list_col_green, list_col_blue, list_col_yellow))
        knitpat_black_green_red_yellow = process_knitpat(
            multi_color_list(4, list_col_black, list_col_green, list_col_red, list_col_yellow))
        knitpat_black_blue_red_yellow = process_knitpat(
            multi_color_list(4, list_col_black, list_col_blue, list_col_red, list_col_yellow))

        knitpat_white_green = process_knitpat(multi_color_list(2, list_col_white, list_col_green))
        knitpat_white_blue = process_knitpat(multi_color_list(2, list_col_white, list_col_blue))
        knitpat_white_red = process_knitpat(multi_color_list(2, list_col_white, list_col_red))
        knitpat_white_yellow = process_knitpat(multi_color_list(2, list_col_white, list_col_yellow))

        knitpat_white_green_blue = process_knitpat(multi_color_list(3, list_col_white, list_col_green,
                                                                    list_col_blue))
        knitpat_white_green_red = process_knitpat(multi_color_list(3, list_col_white, list_col_green,
                                                                   list_col_red))
        knitpat_white_green_yellow = process_knitpat(multi_color_list(3, list_col_white, list_col_green,
                                                                      list_col_yellow))

        knitpat_white_blue_red = process_knitpat(multi_color_list(3, list_col_white, list_col_blue, list_col_blue))
        knitpat_white_blue_yellow = process_knitpat(multi_color_list(3, list_col_white, list_col_blue,
                                                                     list_col_yellow))
        knitpat_white_red_yellow = process_knitpat(multi_color_list(3, list_col_white, list_col_red,
                                                                    list_col_yellow))

        knitpat_white_green_blue_red = process_knitpat(
            multi_color_list(4, list_col_white, list_col_green, list_col_blue, list_col_red))
        knitpat_white_green_blue_yellow = process_knitpat(
            multi_color_list(4, list_col_white, list_col_green, list_col_blue, list_col_yellow))
        knitpat_white_blue_red_yellow = process_knitpat(
            multi_color_list(4, list_col_white, list_col_blue, list_col_red, list_col_yellow))

        knitpat_green_blue = process_knitpat(multi_color_list(2, list_col_green, list_col_blue))
        knitpat_green_red = process_knitpat(multi_color_list(2, list_col_green, list_col_red))
        knitpat_green_yellow = process_knitpat(multi_color_list(2, list_col_green, list_col_yellow))

        knitpat_green_blue_red = process_knitpat(multi_color_list(3, list_col_green, list_col_blue,
                                                                  list_col_red))
        knitpat_green_blue_yellow = process_knitpat(multi_color_list(3, list_col_green, list_col_blue,
                                                                     list_col_yellow))
        knitpat_green_red_yellow = process_knitpat(multi_color_list(3, list_col_green, list_col_red,
                                                                    list_col_yellow))

        knitpat_green_blue_red_yellow = process_knitpat(
            multi_color_list(4, list_col_green, list_col_blue, list_col_red, list_col_yellow))

        knitpat_blue_red = process_knitpat(multi_color_list(2, list_col_blue, list_col_red))
        knitpat_blue_yellow = process_knitpat(multi_color_list(2, list_col_blue, list_col_yellow))

        knitpat_blue_red_yellow = process_knitpat(multi_color_list(3, list_col_blue, list_col_red,
                                                                   list_col_yellow))

        knitpat_red_yellow = process_knitpat(multi_color_list(2, list_col_red, list_col_yellow))

        return (knitpat_black,
                knitpat_white,
                knitpat_green,
                knitpat_blue,
                knitpat_red,
                knitpat_yellow,
                knitpat_black_white,
                knitpat_black_green,
                knitpat_black_blue,
                knitpat_black_red,
                knitpat_black_yellow,
                knitpat_black_white_green,
                knitpat_black_white_blue,
                knitpat_black_white_red,
                knitpat_black_white_yellow,
                knitpat_black_green_blue,
                knitpat_black_green_red,
                knitpat_black_green_yellow,
                knitpat_black_blue_red,
                knitpat_black_blue_yellow,
                knitpat_black_red_yellow,
                knitpat_black_white_green_blue,
                knitpat_black_white_green_red,
                knitpat_black_white_green_yellow,
                knitpat_black_white_blue_red,
                knitpat_black_white_blue_yellow,
                knitpat_black_white_red_yellow,
                knitpat_black_green_blue_red,
                knitpat_black_green_blue_yellow,
                knitpat_black_green_red_yellow,
                knitpat_black_blue_red_yellow,
                knitpat_white_green,
                knitpat_white_blue,
                knitpat_white_red,
                knitpat_white_yellow,
                knitpat_white_green_blue,
                knitpat_white_green_red,
                knitpat_white_green_yellow,
                knitpat_white_blue_red,
                knitpat_white_blue_yellow,
                knitpat_white_red_yellow,
                knitpat_white_green_blue_red,
                knitpat_white_green_blue_yellow,
                knitpat_white_blue_red_yellow,
                knitpat_green_blue,
                knitpat_green_red,
                knitpat_green_yellow,
                knitpat_green_blue_red,
                knitpat_green_blue_yellow,
                knitpat_green_red_yellow,
                knitpat_green_blue_red_yellow,
                knitpat_blue_red,
                knitpat_blue_yellow,
                knitpat_blue_red_yellow,
                knitpat_red_yellow)

    @classmethod
    def set_array_vnb(cls, file_name_pat_vnb):
        (Var.knitpat_black_vnb,
         Var.knitpat_white_vnb,
         Var.knitpat_green_vnb,
         Var.knitpat_blue_vnb,
         Var.knitpat_red_vnb,
         Var.knitpat_yellow_vnb,
         Var.knitpat_black_white_vnb,
         Var.knitpat_black_green_vnb,
         Var.knitpat_black_blue_vnb,
         Var.knitpat_black_red_vnb,
         Var.knitpat_black_yellow_vnb,
         Var.knitpat_black_white_green_vnb,
         Var.knitpat_black_white_blue_vnb,
         Var.knitpat_black_white_red_vnb,
         Var.knitpat_black_white_yellow_vnb,
         Var.knitpat_black_green_blue_vnb,
         Var.knitpat_black_green_red_vnb,
         Var.knitpat_black_green_yellow_vnb,
         Var.knitpat_black_blue_red_vnb,
         Var.knitpat_black_blue_yellow_vnb,
         Var.knitpat_black_red_yellow_vnb,
         Var.knitpat_black_white_green_blue_vnb,
         Var.knitpat_black_white_green_red_vnb,
         Var.knitpat_black_white_green_yellow_vnb,
         Var.knitpat_black_white_blue_red_vnb,
         Var.knitpat_black_white_blue_yellow_vnb,
         Var.knitpat_black_white_red_yellow_vnb,
         Var.knitpat_black_green_blue_red_vnb,
         Var.knitpat_black_green_blue_yellow_vnb,
         Var.knitpat_black_green_red_yellow_vnb,
         Var.knitpat_black_blue_red_yellow_vnb,
         Var.knitpat_white_green_vnb,
         Var.knitpat_white_blue_vnb,
         Var.knitpat_white_red_vnb,
         Var.knitpat_white_yellow_vnb,
         Var.knitpat_white_green_blue_vnb,
         Var.knitpat_white_green_red_vnb,
         Var.knitpat_white_green_yellow_vnb,
         Var.knitpat_white_blue_red_vnb,
         Var.knitpat_white_blue_yellow_vnb,
         Var.knitpat_white_red_yellow_vnb,
         Var.knitpat_white_green_blue_red_vnb,
         Var.knitpat_white_green_blue_yellow_vnb,
         Var.knitpat_white_blue_red_yellow_vnb,
         Var.knitpat_green_blue_vnb,
         Var.knitpat_green_red_vnb,
         Var.knitpat_green_yellow_vnb,
         Var.knitpat_green_blue_red_vnb,
         Var.knitpat_green_blue_yellow_vnb,
         Var.knitpat_green_red_yellow_vnb,
         Var.knitpat_green_blue_red_yellow_vnb,
         Var.knitpat_blue_red_vnb,
         Var.knitpat_blue_yellow_vnb,
         Var.knitpat_blue_red_yellow_vnb,
         Var.knitpat_red_yellow_vnb) = cls.get_pat_array(file_name_pat_vnb)

        print("done pat_array vnb")

    @classmethod
    def set_array_hnb(cls, file_name_pat_hnb):
        (Var.knitpat_black_hnb,
         Var.knitpat_white_hnb,
         Var.knitpat_green_hnb,
         Var.knitpat_blue_hnb,
         Var.knitpat_red_hnb,
         Var.knitpat_yellow_hnb,
         Var.knitpat_black_white_hnb,
         Var.knitpat_black_green_hnb,
         Var.knitpat_black_blue_hnb,
         Var.knitpat_black_red_hnb,
         Var.knitpat_black_yellow_hnb,
         Var.knitpat_black_white_green_hnb,
         Var.knitpat_black_white_blue_hnb,
         Var.knitpat_black_white_red_hnb,
         Var.knitpat_black_white_yellow_hnb,
         Var.knitpat_black_green_blue_hnb,
         Var.knitpat_black_green_red_hnb,
         Var.knitpat_black_green_yellow_hnb,
         Var.knitpat_black_blue_red_hnb,
         Var.knitpat_black_blue_yellow_hnb,
         Var.knitpat_black_red_yellow_hnb,
         Var.knitpat_black_white_green_blue_hnb,
         Var.knitpat_black_white_green_red_hnb,
         Var.knitpat_black_white_green_yellow_hnb,
         Var.knitpat_black_white_blue_red_hnb,
         Var.knitpat_black_white_blue_yellow_hnb,
         Var.knitpat_black_white_red_yellow_hnb,
         Var.knitpat_black_green_blue_red_hnb,
         Var.knitpat_black_green_blue_yellow_hnb,
         Var.knitpat_black_green_red_yellow_hnb,
         Var.knitpat_black_blue_red_yellow_hnb,
         Var.knitpat_white_green_hnb,
         Var.knitpat_white_blue_hnb,
         Var.knitpat_white_red_hnb,
         Var.knitpat_white_yellow_hnb,
         Var.knitpat_white_green_blue_hnb,
         Var.knitpat_white_green_red_hnb,
         Var.knitpat_white_green_yellow_hnb,
         Var.knitpat_white_blue_red_hnb,
         Var.knitpat_white_blue_yellow_hnb,
         Var.knitpat_white_red_yellow_hnb,
         Var.knitpat_white_green_blue_red_hnb,
         Var.knitpat_white_green_blue_yellow_hnb,
         Var.knitpat_white_blue_red_yellow_hnb,
         Var.knitpat_green_blue_hnb,
         Var.knitpat_green_red_hnb,
         Var.knitpat_green_yellow_hnb,
         Var.knitpat_green_blue_red_hnb,
         Var.knitpat_green_blue_yellow_hnb,
         Var.knitpat_green_red_yellow_hnb,
         Var.knitpat_green_blue_red_yellow_hnb,
         Var.knitpat_blue_red_hnb,
         Var.knitpat_blue_yellow_hnb,
         Var.knitpat_blue_red_yellow_hnb,
         Var.knitpat_red_yellow_hnb) = cls.get_pat_array(file_name_pat_hnb)

        print("done pat array hnb")


# class end -------------------------------------------------------
# GPIO Pin to get signals form Arduino front lock
right_GPIO = 4
left_GPIO = 17
direction_change_GPIO = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(right_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(left_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(direction_change_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


class GPIOStart:

    def __init__(self):
        print("GPIO start")

    @classmethod
    def act(cls):
        # interrupt, bounce time 1 ms
        GPIO.add_event_detect(right_GPIO, GPIO.RISING, callback=cls.input_change_right, bouncetime=200)
        GPIO.add_event_detect(left_GPIO, GPIO.RISING, callback=cls.input_change_left, bouncetime=200)
        GPIO.add_event_detect(direction_change_GPIO, GPIO.RISING, callback=cls.input_change_direction_change,
                              bouncetime=500)

    # Raspberry Pi interrupt
    # Row end: Next commands according to tech Array
    # According to needlePos_vnb and formArray send new motorState to Arduino_Motor

    @classmethod
    def input_change_right(cls, channel):
        """
            Callback method to handle GPIO events for direction change.

            This method is called automatically when a rising edge is detected on the GPIO pin
            specified for direction changes. It logs the channel number where the event occurred.

            Parameters:
            - channel (int): The GPIO number where the event was detected. """

        print(f"Event detected on channel {channel}")

        data_transfer.get_needle_pos_vnb()

        if Var.col_change == 0 and Var.needle_pos_vnb <= (int(Var.right_end_data_vnb) - 5) and Var.flag_right == 1:
            print("right side: ", Var.needle_pos_vnb)

            data_transfer.drive_left()
            TechArray.tech_array()

            print("drive left, no col_change", Var.needle_pos_vnb)

            Var.flag_left = 1
            Var.flag_right = 0
            Var.direction_changed += 1

        if Var.col_change == 1:
            data_transfer.col_speed()

            # print("col speed", needlePos_vnb)

    @classmethod
    def input_change_left(cls, channel):

        print(f"Event detected on channel {channel}")

        data_transfer.get_needle_pos_vnb()
        data_transfer.get_cursor_pos()

        # print("cursorPos: ", Var.cursor_pos)

        if Var.needle_pos_vnb >= (int(Var.left_end_data_vnb) + 15) and Var.flag_left == 1:
            print("left side: ", Var.needle_pos_vnb)

            data_transfer.drive_right()
            TechArray.tech_array()

            print("drive right at needlePos_vnb", Var.needle_pos_vnb)

            Var.flag_left = 0
            Var.flag_right = 1
            Var.direction_changed += 1

    @classmethod
    def input_change_direction_change(cls, channel):

        print(f"Event detected on channel {channel}")

        data_transfer.get_needle_pos_vnb()

        if Var.needle_pos_vnb <= (int(Var.right_end_data_vnb) - 18) and Var.col_change == 1 and Var.flag_right == 1:
            print("right side: ", Var.needle_pos_vnb)

            data_transfer.poti_speed()
            TechArray.tech_array()
            print("drive left, col_change: ", Var.needle_pos_vnb)

            Var.flag_left = 1
            Var.flag_right = 0
            Var.direction_changed += 1
            # print("dirC right", direction_changed)


class ArduinoConnectionSingleton:
    _instance = None

    connection_motor = None
    connection_vnb = None
    connection_hnb = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating Arduino Connection Singleton")
            cls._instance = super(ArduinoConnectionSingleton, cls).__new__(cls)
            cls._connect_to_arduino()
        return cls._instance

    @staticmethod
    def _connect_to_arduino():
        """
        Establishes the connection to multiple Arduino boards.
        This method is designed to be called once during the singleton initialization.
        """

        # Connect to Motor Arduino Nano
        # For baud rate: Max 19200 with Arduino Serial
        motor_board = PyCmdMessenger.ArduinoBoard('/dev/ttyUSB-ArduinoMotor', baud_rate=19200)
        motor_board.enable_dtr = False
        motor_board.int_bytes = 4

        motor_commands = [["slowDownSpeed", "i"], ["sbSlowDownSpeed", "i"],
                          ["setcolorChange", "?"], ["sbcolorChange", "?"],
                          ["setRowEndStopp", "?"], ["sbRowEndStopp", "?"],
                          ["setform_stopp", "?"], ["sbform_stopp", "s"],
                          ["setDrive_left", ""], ["sbDrive_left", "s"],
                          ["setDrive_right", ""], ["sbDrive_right", "s"],
                          ["setStopp", ""], ["sbStopp", "s"]]

        ArduinoConnectionSingleton.connection_motor = PyCmdMessenger.CmdMessenger(motor_board, motor_commands)

        # Connect to VNB Arduino M0 (front lock)
        vnb_board = PyCmdMessenger.ArduinoBoard('/dev/ttyUSB-ArduinoVNB', 115200)
        vnb_board.enable_dtr = False
        vnb_board.int_bytes = 4

        vnb_commands = [["sPat", "b*"], ["sbPat", "b*"],
                        ["setEmptyPat", "b*"], ["sbEmptyPat", "b*"],
                        ["setNPos", "l"], ["sbNPos", "l*"],
                        ["getNPos", ""], ["sendNPos", "l"],
                        ["setLeEnd", "i"], ["sbLeEnd", "l"],
                        ["setRiEnd", "i"], ["sbRiEnd", "l"],
                        ["getcursor_pos", ""], ["sendcursor_pos", "l"]]

        ArduinoConnectionSingleton.connection_vnb = PyCmdMessenger.CmdMessenger(vnb_board, vnb_commands)

        # Connect to HNB Arduino M0 Pro (back lock)
        hnb_board = PyCmdMessenger.ArduinoBoard('/dev/ttyUSB-ArduinoHNB', 115200)
        hnb_board.enable_dtr = False
        hnb_board.int_bytes = 4

        hnb_commands = [["sPat", "b*"], ["sbPat", "b*"],
                        ["setEmptyPat", "b*"], ["sbEmptyPat", "b*"],
                        ["setNPos", "l"], ["sbNPos", "l*"],
                        ["getNPos", ""], ["sendNPos", "l"],
                        ["setLeEnd", "i"], ["sbLeEnd", "l"],
                        ["setRiEnd", "i"], ["sbRiEnd", "l"]]

        ArduinoConnectionSingleton.connection_hnb = PyCmdMessenger.CmdMessenger(hnb_board, hnb_commands)

        print("Connecting to Arduino...")

    print("")
    print("========================================")


class DataTransferArduino:

    def __init__(self, arduino_connection_in):
        self.arduino_connection = arduino_connection_in

    def get_needle_pos_vnb(self):
        self.arduino_connection.connection_vnb.send("getNPos")
        received_vnb = self.arduino_connection.connection_vnb.receive()
        Var.needle_pos_vnb = received_vnb[1][0]
        print(Var.needle_pos_vnb)

    def get_needle_pos_hnb(self):
        self.arduino_connection.connection_hnb.send("getNPos")
        received_hnb = self.arduino_connection.connection_hnb.receive()
        Var.needle_pos_hnb = received_hnb[1][0]
        print(Var.needle_pos_hnb)

    def get_cursor_pos(self):
        self.arduino_connection.connection_vnb.send("getcursor_pos")
        received_vnb = self.arduino_connection.connection_vnb.receive()
        Var.cursor_pos = received_vnb[1][0]
        print("cursor_pos get ", Var.cursor_pos)

    def drive_left(self):
        self.arduino_connection.connection_motor.send("setDrive_left")
        received_motor = self.arduino_connection.connection_motor.receive()
        Var.change_drive_left = received_motor[1][0]
        # print("drive_left: ", Var.change_drive_left)

    def drive_right(self):
        self.arduino_connection.connection_motor.send("setDrive_right")
        received_motor_r = self.arduino_connection.connection_motor.receive()
        Var.change_drive_right = received_motor_r[1][0]
        # print("drive_right: ", Var.change_drive_right)

    def stopp(self):
        print("failure stopp")
        self.arduino_connection.connection_motor.send("setStopp")
        received_motor_stopp = self.arduino_connection.connection_motor.receive()
        msg = received_motor_stopp[1][0]
        print("msg: ", msg)

    def row_end_stopp(self):
        # print("reached row_end_stopp")
        # print("rowEnd: ", Var.end_stopp)
        self.arduino_connection.connection_motor.send("setRowEndStopp", Var.end_stopp)
        received_motor_end_stopp = self.arduino_connection.connection_motor.receive()
        Var.row_end = received_motor_end_stopp[1][0]
        # print("rowEndStopp: ", Var.row_end)

    def col_speed(self):
        Var.speed = 1
        self.arduino_connection.connection_motor.send("slowDownSpeed", Var.speed)
        received_motor_speed = self.arduino_connection.connection_motor.receive()
        Var.slow_speed = received_motor_speed[1][0]
        # print("rec_color speed: ", Var.slow_speed)

    def poti_speed(self):
        Var.speed = 0
        self.arduino_connection.connection_motor.send("slowDownSpeed", Var.speed)
        received_motor_speed = self.arduino_connection.connection_motor.receive()
        Var.speed_value = received_motor_speed[1][0]
        # print("rec_poti speed: ", Var.speed_value)

    def color_change(self):
        self.arduino_connection.connection_motor.send("setcolorChange", Var.col_change)
        received_motor_col = self.arduino_connection.connection_motor.receive()
        print("colorChange: ", received_motor_col[1][0])

    def form_stopp(self):
        Var.form_stopp = 1
        self.arduino_connection.connection_motor.send("setRowEndStopp", Var.form_stopp)
        received_form_stopp = self.arduino_connection.connection_motor.receive()
        print("form_stopp: ", received_form_stopp[1][0])

    def no_form_stopp(self):
        Var.form_stopp = 0
        self.arduino_connection.connection_motor.send("setRowEndStopp", Var.form_stopp)
        received_form_stopp = self.arduino_connection.connection_motor.receive()
        print("form_stopp: ", received_form_stopp[1][0])

    def send_row_color_to_arduino(self, knit, color):

        knit = knit[Var.row_count_vnb]
        num_args = int(len(knit))

        try:
            self.arduino_connection.connection_vnb.send("sPat", num_args, *knit)
            received_cmd = self.arduino_connection.connection_vnb.receive()
            received = received_cmd[1]
            print('received vnb', received)

            # Überprüfen Sie, ob alle Elemente übereinstimmen.
            success = all(k == r for k, r in zip(knit, received))

            if not success:
                raise ValueError("Mismatch between sent and received data.")

            print("vnb_pattern, color: ", color, ", success: ", success)

        except Exception as e:  # Fangen Sie eine allgemeine Ausnahme ab, aber drucken Sie die spezifische Nachricht.
            self.stopp()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("send pat row pat vnb")
            msg.setText(f"Error: {str(e)}")
            msg.exec_()
            print("pattern vnb failed")

    def send_row_color_to_arduino_hnb(self, knit, color):

        knit = knit[Var.row_count_hnb]
        num_args = int(len(knit))

        try:
            self.arduino_connection.connection_hnb.send("sPat", num_args, *knit)
            received_cmd = self.arduino_connection.connection_hnb.receive()
            received = received_cmd[1]
            print('received hnb', received)

            # Überprüfen Sie, ob alle Elemente übereinstimmen.
            success = all(k == r for k, r in zip(knit, received))

            if not success:
                raise ValueError("Mismatch between sent and received data.")

            print("hnb_pattern, color: ", color, ", success: ", success)

        except Exception as e:  # Fangen Sie eine allgemeine Ausnahme ab, aber drucken Sie die spezifische Nachricht.
            self.stopp()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("send pat row pat hnb")
            msg.setText(f"Error: {str(e)}")
            msg.exec_()
            print("pattern hnb failed")

    def send_row_pat_vnb(self, knit, info):

        num_args = int(len(knit))

        try:
            self.arduino_connection.connection_vnb.send("setEmptyPat", num_args, *knit)
            received_cmd = self.arduino_connection.connection_vnb.receive()
            received = received_cmd[1]
            print('received emptyPat vnb', received)

            # Überprüfen Sie, ob alle Elemente übereinstimmen.
            success = all(k == r for k, r in zip(knit, received))

            if not success:
                raise ValueError("Mismatch between sent and received data.")

            print(info, " vnb:", success)

        except Exception as e:  # Fangen Sie eine allgemeine Ausnahme ab, aber drucken Sie die spezifische Nachricht.
            self.stopp()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("send pat row empty pat vnb")
            msg.setText(f"Error: {str(e)}")
            msg.exec_()
            print("No value emptyRow vnb")

    def send_row_pat_hnb(self, knit, info):

        num_args = int(len(knit))

        try:
            self.arduino_connection.connection_hnb.send("setEmptyPat", num_args, *knit)
            received_cmd = self.arduino_connection.connection_hnb.receive()
            received = received_cmd[1]
            print('received emptyPat hnb', received)

            # Checks whether the sent pattern row was read correctly
            success = all(k == r for k, r in zip(knit, received))

            if not success:
                raise ValueError("Mismatch between sent and received data.")

            print(info, " hnb:", success)

        except Exception as e:  # error message, no pattern row was sent
            self.stopp()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("send pat row empty pat hnb")
            msg.setText(f"Error: {str(e)}")
            msg.exec_()
            print("No value emptyRow hnb")

    def set_left_end_vnb(self, data):
        Var.left_end_vnb = int(data)
        self.arduino_connection.connection_vnb.send("setLeEnd", int(Var.left_end_vnb))
        received = self.arduino_connection.connection_vnb.receive()
        print("vnb left end Arduino: ", received[1][0])

    def set_left_end_hnb(self, data):
        Var.left_end_hnb = int(data)
        self.arduino_connection.connection_hnb.send("setLeEnd", int(Var.left_end_hnb))
        received = self.arduino_connection.connection_hnb.receive()
        print("hnb left end Arduino: ", received[1][0])

    def set_right_end_vnb(self, data):
        Var.right_end_vnb = int(data)
        self.arduino_connection.connection_vnb.send("setRiEnd", int(Var.right_end_vnb))
        received_vnb = self.arduino_connection.connection_vnb.receive()
        print("vnb right end Arduino: ", received_vnb[1][0])

    def set_right_end_hnb(self, data):
        Var.right_end_hnb = int(data)
        self.arduino_connection.connection_hnb.send("setRiEnd", int(Var.right_end_hnb))
        received = self.arduino_connection.connection_hnb.receive()
        print("hnb right end Arduino: ", received[1][0])

    def send_data_vnb(self):
        self.set_left_end_vnb(Var.left_end_data_vnb)
        self.set_right_end_vnb(Var.right_end_data_vnb)

    def send_data_hnb(self):
        self.set_left_end_hnb(Var.left_end_data_hnb)
        self.set_right_end_hnb(Var.right_end_data_hnb)

    def send_data(self):
        self.send_data_vnb()
        self.send_data_hnb()

    def set_null_pos(self):
        self.arduino_connection.connection_vnb.send("setNPos", 100)
        received_cmd = self.arduino_connection.connection_vnb.receive()
        received = received_cmd[1][0] if received_cmd else None

        try:
            if received is None:
                raise ValueError("No value received")
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("set null pos")
            msg.setText("no value vnb")
            msg.exec_()
            print("No value")

        received_vnb = received
        print("VNB 0Pos: ", received)

        self.arduino_connection.connection_hnb.send("setNPos", 100)
        received_cmd = self.arduino_connection.connection_hnb.receive()
        received = received_cmd[1][0] if received_cmd else None

        try:
            if received is None:
                raise ValueError("No value received")
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("set null pos")
            msg.setText("no value hnb")
            msg.exec_()
            print("No value hnb")

        print("HNB 0Pos:", received)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("set 0Pos")
        msg.setText("VNB: " + str(received_vnb) + " HNB: " + str(received))
        msg.exec_()

        Var.flag_left = 1
        Var.flag_right = 0

        # print("flags done")

        self.send_data()
        # TechArray.tech_array()


class TechArray:

    def __init__(self):
        print("start TechArray")

    @classmethod
    def return_tech_data(cls, number):

        data_local = []

        name_tech = str(number) + "_tech.txt"
        # print("name_tech: " + name_tech)

        file_name = ("/home/irene/Passap/Tech/" + name_tech)
        # print("file_name " + file_name)

        with open(file_name) as f:
            reader = csv.reader(f)
            for r in reader:
                data_local.append(r)
            data_local.pop(0)

        # print("data_local", data_local)

        return data_local

    @classmethod
    def tech_array(cls):
        # print("flag_right ", Var.flag_right)
        # print("flag_left ", Var.flag_left)

        def send_none():
            pass

        # Dictionary functions vnb
        def send_row_color_black():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_vnb, "black")

        def send_row_color_black_white():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_vnb, "black_white")

        def send_row_color_black_green():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_green_vnb, "black_green")

        def send_row_color_black_blue():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_blue_vnb, "black_blue")

        def send_row_color_black_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_red_vnb, "black_red")

        def send_row_color_black_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_yellow_vnb, "black_yellow")

        def send_row_color_black_white_green():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_green_vnb, "black_white_green")

        def send_row_color_black_white_blue():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_blue_vnb, "black_white_blue")

        def send_row_color_black_white_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_red_vnb, "black_white_red")

        def send_row_color_black_white_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_yellow_vnb, "black_white_yellow")

        def send_row_color_black_green_blue():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_green_blue_vnb, "black_green_blue")

        def send_row_color_black_green_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_green_red_vnb, "black_green_red")

        def send_row_color_black_green_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_green_yellow_vnb, "black_green_yellow")

        def send_row_color_black_blue_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_blue_red_vnb, "black_blue_red")

        def send_row_color_black_blue_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_blue_yellow_vnb, "black_blue_yellow")

        def send_row_color_black_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_red_yellow_vnb, "black_red_yellow")

        def send_row_color_black_white_green_blue():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_green_blue_vnb,
                                                    "black_white_green_blue")

        def send_row_color_black_white_green_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_green_red_vnb,
                                                    "black_white_green_red")

        def send_row_color_black_white_green_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_green_yellow_vnb,
                                                    "black_white_green_yellow")

        def send_row_color_black_white_blue_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_blue_red_vnb,
                                                    "black_white_blue_red")

        def send_row_color_black_white_blue_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_blue_yellow_vnb,
                                                    "black_white_blue_yellow")

        def send_row_color_black_white_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_white_red_yellow_vnb,
                                                    "black_white_red_yellow")

        def send_row_color_black_green_blue_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_green_blue_red_vnb,
                                                    "black_green_blue_red")

        def send_row_color_black_green_blue_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_green_blue_yellow_vnb,
                                                    "black_green_blue_yellow")

        def send_row_color_black_green_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_green_red_yellow_vnb,
                                                    "black_green_red_yellow")

        def send_row_color_black_blue_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_black_blue_red_yellow_vnb,
                                                    "black_blue_red_yellow")

        def send_row_color_white():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_vnb, "white")

        def send_row_color_white_green():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_green_vnb, "white_green")

        def send_row_color_white_blue():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_blue_vnb, "white_blue")

        def send_row_color_white_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_red_vnb, "white_red")

        def send_row_color_white_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_yellow_vnb, "white_yellow")

        def send_row_color_white_green_blue():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_green_blue_vnb, "white_green_blue")

        def send_row_color_white_green_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_green_red_vnb, "white_green_red")

        def send_row_color_white_green_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_green_yellow_vnb, "white_green_yellow")

        def send_row_color_white_blue_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_blue_red_vnb, "white_blue_red")

        def send_row_color_white_blue_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_blue_yellow_vnb, "white_blue_yellow")

        def send_row_color_white_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_red_yellow_vnb, "white_red_yellow")

        def send_row_color_white_green_blue_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_green_blue_red_vnb,
                                                    "white_green_blue_red")

        def send_row_color_white_green_blue_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_green_blue_yellow_vnb,
                                                    "white_green_blue_yellow")

        def send_row_color_white_blue_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_white_blue_red_yellow_vnb,
                                                    "white_blue_red_yellow")

        def send_row_color_green():
            data_transfer.send_row_color_to_arduino(Var.knitpat_green_vnb, "green")

        def send_row_color_green_blue():
            data_transfer.send_row_color_to_arduino(Var.knitpat_green_blue_vnb, "green_blue")

        def send_row_color_green_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_green_red_vnb, "green_red")

        def send_row_color_green_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_green_yellow_vnb, "green_yellow")

        def send_row_color_green_blue_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_green_blue_red_vnb, "green_blue_red")

        def send_row_color_green_blue_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_green_blue_yellow_vnb, "green_blue_yellow")

        def send_row_color_green_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_green_red_yellow_vnb, "green_red_yellow")

        def send_row_color_green_blue_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_green_blue_red_yellow_vnb, "green_blue_red_yellow")

        def send_row_color_blue():
            data_transfer.send_row_color_to_arduino(Var.knitpat_blue_vnb, "blue")

        def send_row_color_blue_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_blue_red_vnb, "blue_red")

        def send_row_color_blue_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_blue_yellow_vnb, "blue_yellow")

        def send_row_color_blue_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_blue_red_yellow_vnb, "blue_red_yellow")

        def send_row_color_red():
            data_transfer.send_row_color_to_arduino(Var.knitpat_red_vnb, "red")

        def send_row_color_red_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_red_yellow_vnb, "red_yellow")

        def send_row_color_yellow():
            data_transfer.send_row_color_to_arduino(Var.knitpat_yellow_vnb, "yellow")

        def send_empty_row_vnb():
            data_transfer.send_row_pat_vnb(Var.knitpat_empty_row, "emptyRow")

        def send_full_row_vnb():
            data_transfer.send_row_pat_vnb(Var.knitpat_full_row, "fullRow")

        def send_rib10_vnb():
            data_transfer.send_row_pat_vnb(Var.knitpat_rib10, "Ribpat 10 vnb")

        def send_rib01_vnb():
            data_transfer.send_row_pat_vnb(Var.knitpat_rib01, "Ribpat 01 vnb")

        # Dictionary functions hnb
        def send_row_color_black_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_hnb, "black_H")

        def send_row_color_black_white_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_hnb, "black_white_H")

        def send_row_color_black_green_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_green_hnb, "black_green_H")

        def send_row_color_black_blue_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_blue_hnb, "black_blue_H")

        def send_row_color_black_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_red_hnb, "black_red_H")

        def send_row_color_black_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_yellow_hnb, "black_yellow_H")

        def send_row_color_black_white_green_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_green_hnb,
                                                        "black_white_green_H")

        def send_row_color_black_white_blue_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_blue_hnb, "black_white_blue_H")

        def send_row_color_black_white_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_red_hnb, "black_white_red_H")

        def send_row_color_black_white_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_yellow_hnb,
                                                        "black_white_yellow_H")

        def send_row_color_black_green_blue_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_green_blue_hnb, "black_green_blue_H")

        def send_row_color_black_green_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_green_red_hnb, "black_green_red_H")

        def send_row_color_black_green_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_green_yellow_hnb,
                                                        "black_green_yellow_H")

        def send_row_color_black_blue_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_blue_red_hnb, "black_blue_red_H")

        def send_row_color_black_blue_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_blue_yellow_hnb,
                                                        "black_blue_yellow_H")

        def send_row_color_black_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_red_yellow_hnb, "black_red_yellow_H")

        def send_row_color_black_white_green_blue_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_green_blue_hnb,
                                                        "black_white_green_blue_H")

        def send_row_color_black_white_green_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_green_red_hnb,
                                                        "black_white_green_red_H")

        def send_row_color_black_white_green_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_green_yellow_hnb,
                                                        "black_white_green_yellow_H")

        def send_row_color_black_white_blue_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_blue_red_hnb,
                                                        "black_white_blue_red_H")

        def send_row_color_black_white_blue_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_blue_yellow_hnb,
                                                        "black_white_blue_yellow_H")

        def send_row_color_black_white_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_white_red_yellow_hnb,
                                                        "black_white_red_yellow_H")

        def send_row_color_black_green_blue_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_green_blue_red_hnb,
                                                        "black_green_blue_red_H")

        def send_row_color_black_green_blue_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_green_blue_yellow_hnb,
                                                        "black_green_blue_yellow_H")

        def send_row_color_black_green_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_green_red_yellow_hnb,
                                                        "black_green_red_yellow_H")

        def send_row_color_black_blue_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_black_blue_red_yellow_hnb,
                                                        "black_blue_red_yellow_H")

        def send_row_color_white_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_hnb, "white_H")

        def send_row_color_white_green_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_green_hnb, "white_green_H")

        def send_row_color_white_blue_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_blue_hnb, "white_blue_H")

        def send_row_color_white_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_red_hnb, "white_red_H")

        def send_row_color_white_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_yellow_hnb, "white_yellow_H")

        def send_row_color_white_green_blue_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_green_blue_hnb, "white_green_blue_H")

        def send_row_color_white_green_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_green_red_hnb, "white_green_red_H")

        def send_row_color_white_green_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_green_yellow_hnb,
                                                        "white_green_yellow_H")

        def send_row_color_white_blue_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_blue_red_hnb, "white_blue_red_H")

        def send_row_color_white_blue_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_blue_yellow_hnb,
                                                        "white_blue_yellow_H")

        def send_row_color_white_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_red_yellow_hnb, "white_red_yellow_H")

        def send_row_color_white_green_blue_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_green_blue_red_hnb,
                                                        "white_green_blue_red_H")

        def send_row_color_white_green_blue_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_green_blue_yellow_hnb,
                                                        "white_green_blue_yellow_H")

        def send_row_color_white_blue_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_white_blue_red_yellow_hnb,
                                                        "white_blue_red_yellow_H")

        def send_row_color_green_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_green_hnb, "green_H")

        def send_row_color_green_blue_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_green_blue_hnb, "green_blue_H")

        def send_row_color_green_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_green_red_hnb, "green_red_H")

        def send_row_color_green_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_green_yellow_hnb, "green_yellow_H")

        def send_row_color_green_blue_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_green_blue_red_hnb, "green_blue_red_H")

        def send_row_color_green_blue_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_green_blue_yellow_hnb,
                                                        "green_blue_yellow_H")

        def send_row_color_green_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_green_red_yellow_hnb, "green_red_yellow_H")

        def send_row_color_green_blue_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_green_blue_red_yellow_hnb,
                                                        "green_blue_red_yellow_H")

        def send_row_color_blue_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_blue_hnb, "blue_H")

        def send_row_color_blue_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_blue_red_hnb, "blue_red_H")

        def send_row_color_blue_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_blue_yellow_hnb, "blue_yellow_H")

        def send_row_color_blue_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_blue_red_yellow_hnb, "blue_red_yellow_H")

        def send_row_color_red_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_red_hnb, "red_H")

        def send_row_color_red_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_red_yellow_hnb, "red_yellow_H")

        def send_row_color_yellow_hnb():
            data_transfer.send_row_color_to_arduino_hnb(Var.knitpat_yellow_hnb, "yellow_H")

        def send_empty_row_hnb():
            data_transfer.send_row_pat_hnb(Var.knitpat_empty_row, "emptyRow_H")

        def send_full_row_hnb():
            data_transfer.send_row_pat_hnb(Var.knitpat_full_row, "fullRow_H")

        def send_rib01_hnb():
            data_transfer.send_row_pat_hnb(Var.knitpat_rib01, "Ribpat 01 hnb")

        def send_rib10_hnb():
            data_transfer.send_row_pat_hnb(Var.knitpat_rib10, "Ribpat 10 hnb")

        # def send_empty_row_to_arduino():
        #     send_empty_row_vnb()
        #     send_empty_row_hnb()

        # enum
        techSet = {'bV': send_row_color_black,
                   'wV': send_row_color_white,
                   'gV': send_row_color_green,
                   'blV': send_row_color_blue,
                   'rV': send_row_color_red,
                   'yV': send_row_color_yellow,
                   'bwV': send_row_color_black_white,
                   'bgV': send_row_color_black_green,
                   'bblV': send_row_color_black_blue,
                   'brV': send_row_color_black_red,
                   'byV': send_row_color_black_yellow,
                   'bwgV': send_row_color_black_white_green,
                   'bwblV': send_row_color_black_white_blue,
                   'bwrV': send_row_color_black_white_red,
                   'bwyV': send_row_color_black_white_yellow,
                   'bgblV': send_row_color_black_green_blue,
                   'bgrV': send_row_color_black_green_red,
                   'bgyV': send_row_color_black_green_yellow,
                   'bblrV': send_row_color_black_blue_red,
                   'bblyV': send_row_color_black_blue_yellow,
                   'bryV': send_row_color_black_red_yellow,
                   'bwgblV': send_row_color_black_white_green_blue,
                   'bwgrV': send_row_color_black_white_green_red,
                   'bwgyV': send_row_color_black_white_green_yellow,
                   'bwblrV': send_row_color_black_white_blue_red,
                   'bwblyV': send_row_color_black_white_blue_yellow,
                   'bwryV': send_row_color_black_white_red_yellow,
                   'bgblrV': send_row_color_black_green_blue_red,
                   'bgblyV': send_row_color_black_green_blue_yellow,
                   'bgryV': send_row_color_black_green_red_yellow,
                   'bblryV': send_row_color_black_blue_red_yellow,
                   'wgV': send_row_color_white_green,
                   'wblV': send_row_color_white_blue,
                   'wrV': send_row_color_white_red,
                   'wyV': send_row_color_white_yellow,
                   'wgblV': send_row_color_white_green_blue,
                   'wgrV': send_row_color_white_green_red,
                   'wgyV': send_row_color_white_green_yellow,
                   'wblrV': send_row_color_white_blue_red,
                   'wblyV': send_row_color_white_blue_yellow,
                   'wryV': send_row_color_white_red_yellow,
                   'wgblrV': send_row_color_white_green_blue_red,
                   'wgblyV': send_row_color_white_green_blue_yellow,
                   'wblryV': send_row_color_white_blue_red_yellow,
                   'gblV': send_row_color_green_blue,
                   'grV': send_row_color_green_red,
                   'gyV': send_row_color_green_yellow,
                   'gblrV': send_row_color_green_blue_red,
                   'gblyV': send_row_color_green_blue_yellow,
                   'gryV': send_row_color_green_red_yellow,
                   'gblryV': send_row_color_green_blue_red_yellow,
                   'blrV': send_row_color_blue_red,
                   'blyV': send_row_color_blue_yellow,
                   'blryV': send_row_color_blue_red_yellow,
                   'ryV': send_row_color_red_yellow,
                   'eV': send_empty_row_vnb, 'nV': send_full_row_vnb,
                   'rib10V': send_rib10_vnb, 'rib01V': send_rib01_vnb,
                   'bH': send_row_color_black_hnb,
                   'wH': send_row_color_white_hnb,
                   'gH': send_row_color_green_hnb,
                   'blH': send_row_color_blue_hnb,
                   'rH': send_row_color_red_hnb,
                   'yH': send_row_color_yellow_hnb,
                   'bwH': send_row_color_black_white_hnb,
                   'bgH': send_row_color_black_green_hnb,
                   'bblH': send_row_color_black_blue_hnb,
                   'brH': send_row_color_black_red_hnb,
                   'byH': send_row_color_black_yellow_hnb,
                   'bwgH': send_row_color_black_white_green_hnb,
                   'bwblH': send_row_color_black_white_blue_hnb,
                   'bwrH': send_row_color_black_white_red_hnb,
                   'bwyH': send_row_color_black_white_yellow_hnb,
                   'bgblH': send_row_color_black_green_blue_hnb,
                   'bgrH': send_row_color_black_green_red_hnb,
                   'bgyH': send_row_color_black_green_yellow_hnb,
                   'bblrH': send_row_color_black_blue_red_hnb,
                   'bblyH': send_row_color_black_blue_yellow_hnb,
                   'bryH': send_row_color_black_red_yellow_hnb,
                   'bwgblH': send_row_color_black_white_green_blue_hnb,
                   'bwgrH': send_row_color_black_white_green_red_hnb,
                   'bwgyH': send_row_color_black_white_green_yellow_hnb,
                   'bwblrH': send_row_color_black_white_blue_red_hnb,
                   'bwblyH': send_row_color_black_white_blue_yellow_hnb,
                   'bwryH': send_row_color_black_white_red_yellow_hnb,
                   'bgblrH': send_row_color_black_green_blue_red_hnb,
                   'bgblyH': send_row_color_black_green_blue_yellow_hnb,
                   'bgryH': send_row_color_black_green_red_yellow_hnb,
                   'bblryH': send_row_color_black_blue_red_yellow_hnb,
                   'wgH': send_row_color_white_green_hnb,
                   'wblH': send_row_color_white_blue_hnb,
                   'wrH': send_row_color_white_red_hnb,
                   'wyH': send_row_color_white_yellow_hnb,
                   'wgblH': send_row_color_white_green_blue_hnb,
                   'wgrH': send_row_color_white_green_red_hnb,
                   'wgyH': send_row_color_white_green_yellow_hnb,
                   'wblrH': send_row_color_white_blue_red_hnb,
                   'wblyH': send_row_color_white_blue_yellow_hnb,
                   'wryH': send_row_color_white_red_yellow_hnb,
                   'wgblrH': send_row_color_white_green_blue_red_hnb,
                   'wgblyH': send_row_color_white_green_blue_yellow_hnb,
                   'wblryH': send_row_color_white_blue_red_yellow_hnb,
                   'gblH': send_row_color_green_blue_hnb,
                   'grH': send_row_color_green_red_hnb,
                   'gyH': send_row_color_green_yellow_hnb,
                   'gblrH': send_row_color_green_blue_red_hnb,
                   'gblyH': send_row_color_green_blue_yellow_hnb,
                   'gryH': send_row_color_green_red_yellow_hnb,
                   'gblryH': send_row_color_green_blue_red_yellow_hnb,
                   'blrH': send_row_color_blue_red_hnb,
                   'blyH': send_row_color_blue_yellow_hnb,
                   'blryH': send_row_color_blue_red_yellow_hnb,
                   'ryH': send_row_color_red_yellow_hnb,
                   'eH': send_empty_row_hnb, 'nH': send_full_row_hnb,
                   'rib01H': send_rib01_hnb, 'rib10H': send_rib10_hnb,
                   '0': send_none}

        if Var.count_tech >= len(Var.tech_array):
            Var.count_tech = 0

        vnb = Var.tech_array[Var.count_tech][0]
        vnb = int(vnb)

        Var.row_count_vnb = int(Var.row_count_vnb) + vnb
        if Var.row_count_vnb >= Var.height_vnb:
            Var.row_count_vnb = 0

        hnb = Var.tech_array[Var.count_tech][1]
        hnb = int(hnb)
        Var.row_count_hnb = int(Var.row_count_hnb) + hnb
        if Var.row_count_hnb >= Var.height_hnb:
            Var.row_count_hnb = 0

        techSet[Var.tech_array[Var.count_tech][2]]()

        techSet[Var.tech_array[Var.count_tech][3]]()

        Var.lock_setting_vnb = Var.tech_array[Var.count_tech][4]

        Var.lock_setting_hnb = Var.tech_array[Var.count_tech][5]

        Var.col_change = int(Var.tech_array[Var.count_tech][7])
        data_transfer.color_change()
        # if Var.col_change:
        #     MyTableWidget.set_icon_state(Var.icon_color_change, "../Icon_color.png")
        # else:
        #     MyTableWidget.set_icon_state(Var.icon_color_change, "../Icon_button.png")

        print(timer.nsecsElapsed())

        Var.end_stopp = int(Var.tech_array[Var.count_tech][6])
        print("row_end_stopp new: ", Var.end_stopp)
        data_transfer.row_end_stopp()

        # if Var.end_stopp:
        #     MyTableWidget.set_icon_state(Var.icon_stopp, "Icon_stopp.png")
        # else:
        #     MyTableWidget.set_icon_state(Var.icon_stopp, "Icon_button.png")

        Var.color_setting = Var.tech_array[Var.count_tech][8]

        Var.lock_side_is = Var.tech_array[Var.count_tech][9]
        print(timer.nsecsElapsed())

        if Var.lock_side_is == "right":
            try:
                MyTableWidget.set_icon_state(Var.icon_drive, icon_path_left)
            except Exception as icon_left:
                print(f"Error with icon: {icon_left}")
        elif Var.lock_side_is == "left":
            try:
                MyTableWidget.set_icon_state(Var.icon_drive, icon_path_right)
            except Exception as icon_right:
                print(f"Error with icon: {icon_right}")

        print(timer.nsecsElapsed())

        Var.info_tech = Var.tech_array[Var.count_tech][10]

        Var.count_tech += 1
        print("Var.count_tech: ", Var.count_tech)

        FormArray.read_form_array()
        MyTableWidget.set_values()


class FormArray:

    def __init__(self):
        print("PatternArray start")

    @classmethod
    def return_form_data(cls, number):
        number = str(number)
        data_local = []
        name_form = number + "_form.txt"
        # print("name_form: " + name_form)

        file_name_form = ("/home/irene/Passap/Form/" + name_form)
        # print("file_name " + file_name_form)

        with open(file_name_form) as f:
            reader = csv.reader(f)
            for r in reader:
                data_local.append(r)
            data_local.pop(0)
        return data_local

    @classmethod
    def set_end_lr(cls):
        Var.left_end_data_vnb = int(Var.form_array[Var.count_form_line][4])
        Var.left_end_data_hnb = int(Var.form_array[Var.count_form_line][4])

        Var.right_end_data_vnb = int(Var.form_array[Var.count_form_line][5])
        Var.right_end_data_hnb = int(Var.form_array[Var.count_form_line][5])

        data_transfer.send_data()

    @classmethod
    def set_end_lr_vnb(cls):
        Var.left_end_data_vnb = int(Var.form_array[Var.count_form_line][4])
        Var.right_end_data_vnb = int(Var.form_array[Var.count_form_line][5])

        data_transfer.send_data_vnb()

    @classmethod
    def set_end_lr_hnb(cls):
        Var.left_end_data_hnb = int(Var.form_array[Var.count_form_line][4])
        Var.right_end_data_hnb = int(Var.form_array[Var.count_form_line][5])

        data_transfer.send_data_hnb()

    @classmethod
    def decrease(cls):
        # print("decrease: ", Var.count_form_line)

        # hier ist es schwierig eine Begrenzung zu machen
        Var.decrease_left = int(Var.form_array[Var.count_form_line][4])
        Var.left_end_data_vnb -= Var.decrease_left
        Var.left_end_data_hnb -= Var.decrease_left

        Var.decrease_right = int(Var.form_array[Var.count_form_line][5])
        Var.right_end_data_vnb += Var.decrease_right
        Var.right_end_data_hnb += Var.decrease_right

        data_transfer.send_data()

    @classmethod
    def decrease_vnb(cls):
        # print("decrease_vnb: ", Var.count_form_line)

        Var.decrease_left = int(Var.form_array[Var.count_form_line][4])
        Var.left_end_data_vnb -= Var.decrease_left

        Var.decrease_right = int(Var.form_array[Var.count_form_line][5])
        Var.right_end_data_vnb += Var.decrease_right

        data_transfer.send_data_vnb()

    @classmethod
    def decrease_hnb(cls):
        # print("decrease_hnb: ", Var.count_form_line)

        Var.decrease_left = int(Var.form_array[Var.count_form_line][4])
        Var.left_end_data_hnb -= Var.decrease_left

        Var.decrease_right = int(Var.form_array[Var.count_form_line][5])
        Var.right_end_data_hnb += Var.decrease_right

        data_transfer.send_data_hnb()

    @classmethod
    def increase(cls):
        # print("increase: ", Var.count_form_line)

        Var.increase_left = int(Var.form_array[Var.count_form_line][4])
        Var.left_end_data_vnb += Var.increase_left
        Var.left_end_data_hnb += Var.increase_left

        Var.increase_right = int(Var.form_array[Var.count_form_line][5])
        Var.right_end_data_vnb -= Var.increase_right
        Var.right_end_data_hnb -= Var.increase_right

        data_transfer.send_data()

    @classmethod
    def increase_vnb(cls):
        # print("increase_vnb: ", Var.count_form_line)

        Var.increase_left = int(Var.form_array[Var.count_form_line][4])
        Var.left_end_data_vnb += Var.increase_left

        Var.increase_right_vnb = int(Var.form_array[Var.count_form_line][5])
        Var.right_end_data_vnb -= Var.increase_right

        data_transfer.send_data_vnb()

    @classmethod
    def increase_hnb(cls):
        # print("increase_hnb: ", Var.count_form_line)

        Var.increase_left = int(Var.form_array[Var.count_form_line][4])
        Var.left_end_data_hnb += Var.increase_left

        Var.increase_right = int(Var.form_array[Var.count_form_line][5])
        Var.right_end_data_hnb -= Var.increase_right

        data_transfer.send_data_hnb()

    # for futur use
    @classmethod
    def set_short_row(cls):
        print("future use")

    # wenn ich weiterstricke, wird ein Fehler aufgerufen
    @classmethod
    def end_knit(cls):
        data_transfer.form_stopp()
        Var.end_knit_error = 1
        # print("End of knitting form")

    @classmethod
    def repeat_from_line_0_endless(cls):
        Var.row_count_form = -1
        Var.count_form_line = -1
        Var.end_knitError = 0

        # print("endless repeat")
        # print("reset end_knitError to 0")

    @classmethod
    def repeat_from_line_0(cls):
        if Var.repeat_from_line_0 >= int(Var.form_array[Var.count_form_line][8]):
            return
        else:
            Var.row_count_form = -1
            Var.count_form_line = -1
            Var.repeat_from_line_0 += 1
            Var.end_knitError = 0

            # print("repeat line from 0", Var.repeat_from_line_0)
            # print("reset end_knitError to 0")

    @classmethod
    def repeat_from_line_x(cls):
        if Var.repeat_from_line_x >= int(Var.form_array[Var.count_form_line][8]):
            return
        else:
            Var.count_form_line = int(Var.form_array[Var.count_form_line][7])
            Var.row_count_form = int(Var.form_array[Var.count_form_line][1]) - 1
            Var.repeat_from_line_x += 1
            Var.count_form_line -= 1

            Var.end_knitError = 0
            # print("reset end_knitError to 0")

    @classmethod
    def jump_to_line(cls):
        if Var.jump_counter >= int(Var.form_array[Var.count_form_line][8]):
            return

        else:
            Var.count_form_line = int(Var.form_array[Var.count_form_line][7])
            # print("jump to count_form_line ", Var.count_form_line)
            Var.row_count_form = int(Var.form_array[Var.count_form_line][1]) - 1
            Var.jump_counter += 1
            Var.count_form_line -= 1
            Var.end_knitError = 0
            # print("reset end_knitError to 0")

    @classmethod
    def end_line(cls):
        print("go on")

    @classmethod
    def set_tech_array_form(cls):
        # print("arrived setTechArrayForm")
        numb_local = 0

        try:
            numb_local = Var.form_array[Var.count_form_line][7]
            Var.tech_array = TechArray.return_tech_data(numb_local)
            Var.count_tech = int(Var.form_array[Var.count_form_line][8])

            # print("Tech is: ", numb_local)
            # print("tech_array: ", Var.tech_array)
            # print("count Tech new: ", Var.count_tech)

        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("set tech array form")
            msg.setText("no such tech array (form) number")
            msg.exec_()
            print("no such pattern number: ", numb_local)

    @classmethod
    def set_form_array(cls):
        numb_local = 0

        try:
            numb_local = int(Var.form_array[Var.count_form_line][7])
            Var.form_array = cls.return_form_data(numb_local)

            Var.count_form_line = int(Var.form_array[Var.count_form_line][8])
            Var.row_count_form = int(Var.form_array[Var.count_form_line][1])

        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("set form array")
            msg.setText("no such form array")
            msg.exec_()
            print("no such form_array: ", numb_local)

    @classmethod
    def pat_vnb(cls):
        # print("reached pat_vnb")
        numb_local = Var.form_array[Var.count_form_line][7]
        MyTableWidget.set_pat_vnb(numb_local)
        Var.row_count_vnb = Var.form_array[Var.count_form_line][8]

        # print("form_set_pat_vnb is: " + numb_local)

    @classmethod
    def pat_hnb(cls):
        # print("reached pat_vnb")
        numb_local = Var.form_array[Var.count_form_line][7]
        MyTableWidget.set_pat_hnb(numb_local)
        Var.row_count_hnb = Var.form_array[Var.count_form_line][8]

        # print("form_set_pat_hnb is: " + numb_local)

    @classmethod
    def read_form_array(cls):
        """Var.count_form_line = counter counts row in form file
            Var.row_count_form = counts knitted row
            Var.info_form = data displayed"""

        # enum
        form_set = {'enR': cls.set_end_lr,
                    'eRV': cls.set_end_lr_vnb,
                    'eRH': cls.set_end_lr_hnb,
                    'dec': cls.decrease,
                    'deV': cls.decrease_vnb,
                    'deH': cls.decrease_hnb,
                    'inc': cls.increase,
                    'inV': cls.increase_vnb,
                    'inH': cls.increase_hnb,
                    'sRow': cls.set_short_row,
                    'endK': cls.end_knit,
                    're0': cls.repeat_from_line_0_endless,
                    'r0?': cls.repeat_from_line_0,
                    'rL?': cls.repeat_from_line_x,
                    'goL': cls.jump_to_line,
                    'sMo': data_transfer.form_stopp,
                    'noS': data_transfer.no_form_stopp,
                    'enL': cls.end_line,
                    'teA': cls.set_tech_array_form,
                    'foA': cls.set_form_array,
                    'paV': cls.pat_vnb,
                    'paH': cls.pat_hnb}

        if Var.end_knit_error == 1:
            print('end knit error')
            data_transfer.form_stopp()
            return

        elif Var.count_form_line >= len(Var.form_array):
            print('end knit reached')
            data_transfer.form_stopp()
            return

        elif Var.row_count_form == int(Var.form_array[Var.count_form_line][1]):

            # form Stopp
            form_set[Var.form_array[Var.count_form_line][2]]()
            form_set[Var.form_array[Var.count_form_line][3]]()
            form_set[Var.form_array[Var.count_form_line][6]]()
            Var.info_form = Var.form_array[Var.count_form_line][9]
            Var.count_form_line += 1

            # print(Var.info_form)

        Var.row_count_form += 1
        print("row_count_form end function", Var.row_count_form)


# =================================================
# SQLite Table
# =================================================

print("")
print("========================================")


def create_table():
    conn = sqlite3.connect('passapProject.db')
    db_cursor = conn.cursor()
    db_cursor.execute('CREATE TABLE IF NOT EXISTS stuffToPlot(tabID INTEGER PRIMARY KEY AUTOINCREMENT,'
                      'datestamp TEXT, rV INTEGER, rH INTEGER,'
                      'dirC INTEGER, lockV TEXT, lockH TEXT, patV INTEGER, patH INTEGER, tec INTEGER, cTec INTEGER,'
                      'fo INTEGER, cForm INTEGER, fLine INTEGER, '
                      'leEV INTEGER, riEV INTEGER, leEH INTEGER, riEH INTEGER, mgV REAL, mgH REAL)')

    # Wichtig: Wenn die DB noch nicht existiert, wird eine exception geworfen.
    # tabID wird auf null gesetzt,
    # wenn die DB bereits existiert, ist etwas schiefgegangen.
    def max_tab_id(cursor):
        try:
            cursor.execute("SELECT MAX(tabID) FROM stuffToPlot")
            result = cursor.fetchone()
            print(result)
            value = result[0] if result[0] is not None else 0
            return int(value)
        except Exception as max_id_err:
            msg_as_e = QMessageBox()
            msg_as_e.setIcon(QMessageBox.Warning)
            msg_as_e.setWindowTitle("max tabID")
            msg_as_e.setText("An error occurred: " + str(max_id_err) +
                             ", if new DB go on, max_tabID = 0, else a problem occurred")
            msg_as_e.exec_()
            value = 0
            print("max_tabID is: ", value)
            return value

    Var.table_id = max_tab_id(db_cursor)

    def execute_table_id_info(info_in):

        info_in.execute('SELECT tabID, datestamp,rV, rH, dirC, lockV, lockH, patV, patH,tec, cTec,'
                        'fo, cForm, fLine, leEV, riEV, leEH,riEH,mgV, mgH FROM stuffToPlot WHERE tabID = :tabID',
                        {'tabID': Var.table_id})

        result = info_in.fetchone()

        if result is not None:
            print("{:<6s}{:>4d}".format("tabID:", result[0]))
            print("{:<6s}{:>4s}".format("date:", result[1]))

            Var.row_count_vnb = result[2]
            print("{:<6s}{:>4d}".format("rV:", Var.row_count_vnb))

            Var.row_count_hnb = result[3]
            print("{:<6s}{:>4d}".format("rH:", Var.row_count_hnb))

            Var.direction_changed = result[4]
            print("{:<6s}{:>4d}".format("dirC:", Var.direction_changed))

            Var.lock_setting_vnb = result[5]
            print("{:<6s}{:>4s}".format("lock_V:", Var.lock_setting_vnb))

            Var.lock_setting_hnb = result[6]
            print("{:<6s}{:>4s}".format("lock_H:", Var.lock_setting_hnb))

            # When new started, import the last used pat and create the pattern array

            Var.pat_num_vnb = result[7]
            print("{:<6s}{:>4d}".format("patV:", Var.pat_num_vnb))

            temp_pat_numb_vnb = str(Var.pat_num_vnb) + "_Pat.bmp"
            file_name_pat_vnb = ("/home/irene/Passap/Pat/" + temp_pat_numb_vnb)

            try:
                PatternArray.set_array_vnb(file_name_pat_vnb)
                # print('file_name_pat_vnb', file_name_pat_vnb)
                # print(Var.knitpat_black_vnb)

                Var.height_vnb = len(Var.knitpat_black_vnb)

            except IOError:
                msg_no_pat = QMessageBox()
                msg_no_pat.setIcon(QMessageBox.Warning)
                msg_no_pat.setWindowTitle("create table")
                msg_no_pat.setText("no knit pattern vnb")
                msg_no_pat.exec_()
                print("!no knit pattern vnb")

            Var.pat_num_hnb = result[8]
            print("{:<6s}{:>4d}".format("patH:", Var.pat_num_hnb))

            temp_pat_numb_hnb = str(Var.pat_num_hnb) + "_Pat.bmp"
            file_name_pat_hnb = ("/home/irene/Passap/Pat/" + temp_pat_numb_hnb)

            try:
                PatternArray.set_array_hnb(file_name_pat_hnb)
                # print('file_name_pat_hnb', file_name_pat_hnb)
                # print(Var.knitpat_black_hnb)

                Var.height_hnb = len(Var.knitpat_black_hnb)

            except IOError:
                msg_no_pat_hnb = QMessageBox()
                msg_no_pat_hnb.setIcon(QMessageBox.Warning)
                msg_no_pat_hnb.setWindowTitle("create table")
                msg_no_pat_hnb.setText("no knit pattern hnb")
                msg_no_pat_hnb.exec_()
                print("!no knit pattern hnb")

            Var.tech = result[9]
            print("{:<6s}{:>4d}".format("tec:", int(Var.tech)))

            try:
                Var.tech_array = TechArray.return_tech_data(Var.tech)
                Var.count_tech = result[10]
                print("{:<6s}{:>4d}".format("cTec:", Var.count_tech))

            except IOError:
                msg_tech = QMessageBox()
                msg_tech.setIcon(QMessageBox.Warning)
                msg_tech.setWindowTitle("create table")
                msg_tech.setText("TechArray or count Tech error")
                msg_tech.exec_()
                print("!TechArray or count Tech error")

            Var.form = result[11]
            print("{:<6s}{:>4d}".format("form:", int(Var.form)))

            try:
                Var.form_array = FormArray.return_form_data(Var.form)
                Var.row_count_form = result[12]
                print("{:<6s}{:>4d}".format("cForm:", Var.row_count_form))
                Var.count_form_line = result[13]
                print("{:<6s}{:>4d}".format("fLine:", Var.count_form_line))

            except IOError:
                msg_io_error = QMessageBox()
                msg_io_error.setIcon(QMessageBox.Warning)
                msg_io_error.setWindowTitle("create table")
                msg_io_error.setText("formArray or countForm_line error")
                msg_io_error.exec_()
                print("!formArray or countForm_line error")

            Var.left_end_data_vnb = result[14]
            print("{:<6s}{:>4d}".format("leEV:", Var.left_end_data_vnb))

            Var.right_end_data_vnb = result[15]
            print("{:<6s}{:>4d}".format("riEV:", Var.right_end_data_vnb))

            Var.left_end_data_hnb = result[16]
            print("{:<6s}{:>4d}".format("leEH:", Var.left_end_data_hnb))

            Var.right_end_data_hnb = result[17]
            print("{:<6s}{:>4d}".format("riEH:", Var.right_end_data_hnb))

            Var.mg_vnb = result[18]
            print("mgV:", Var.mg_vnb)

            Var.mg_hnb = result[19]
            print("mgH:", Var.mg_hnb)

            # print("Var.knitpat_black_white_green_vnb: ", Var.knitpat_black_white_green_vnb)
            # print("Var.knitpat_black_white_blue_vnb: ", Var.knitpat_black_white_blue_vnb)
            # print("Var.knitpat_black_white_blue_red_vnb: ", Var.knitpat_black_white_blue_red_vnb)
            # print("Var.knitpat_white_green_blue_red_vnb: ", Var.knitpat_white_green_blue_red_vnb)
        else:
            print("No data found für tabID: ", Var.table_id)

    try:
        execute_table_id_info(db_cursor)
        print("reached table id", Var.table_id)
        Var.table_id += 1
        print("Var.table id", Var.table_id)
        print("new tabID: ", Var.table_id)
        print("========================================")
        print("")

    except IOError as execute_table_err:
        msg_table_id = QMessageBox()
        msg_table_id.setIcon(QMessageBox.Warning)
        msg_table_id.setWindowTitle("create table")
        msg_table_id.setText("An error occurred: " + str(execute_table_err))
        msg_table_id.exec_()

    db_cursor.close()
    conn.close()


def dynamic_date_entry_settings():
    conn = sqlite3.connect('passapProject.db')
    db_cursor = conn.cursor()

    # dynamic
    # rV = Var.row_count_vnb
    # rH = Var.row_count_hnb
    # dirC = Var.direction_changed

    # static
    # lockV = Var.lock_setting_vnb
    # lockH = Var.lock_setting_hnb
    # patV = Var.pat_num_vnb
    # patH = Var.pat_num_hnb
    # tec = Var.tech

    # dynamic
    # cTec = Var.count_tech

    # static
    # fo = Var.form

    # dynamic
    # cForm = Var.row_count_form
    # fLine = Var.count_form_line

    # static
    # leEV = Var.left_end_data_vnb
    # riEV = Var.right_end_data_vnb
    # leEH = Var.left_end_data_hnb
    # riEH = Var.right_end_data_hnb
    # mgV = Var.mg_vnb
    # mgH = Var.mg_hnb

    # dynamic
    # tabID = Var.table_id

    unix = time.time()
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%d-%m-%Y %H:%M:%S'))

    db_cursor.execute(
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
        (Var.table_id, date,
         Var.row_count_vnb, Var.row_count_hnb,
         Var.direction_changed,
         Var.lock_setting_vnb, Var.lock_setting_hnb,
         Var.pat_num_vnb, Var.pat_num_hnb,
         Var.tech, Var.count_tech,
         Var.form, Var.row_count_form, Var.count_form_line,
         Var.left_end_data_vnb, Var.right_end_data_vnb,
         Var.left_end_data_hnb, Var.right_end_data_hnb,
         Var.mg_vnb, Var.mg_hnb))

    conn.commit()

    Var.table_id += 1
    # print("tabID: ", Var.table_id)

    db_cursor.close()
    conn.close()


def read_from_db(dirC_num):
    conn = sqlite3.connect('passapProject.db')
    db_cursor = conn.cursor()
    db_cursor.execute("SELECT tabID, datestamp, rV, rH, dirC, lockV, lockH, patV, patH, tec, cTec,"
                      "fo, cForm, fLine, leEV, riEV, leEH, riEH, mgV, mgH FROM stuffToPlot WHERE dirC = :dirC",
                      {"dirC": dirC_num})

    result = db_cursor.fetchone()

    try:
        Var.row_count_vnb = result[2]
        Var.row_count_hnb = result[3]
        Var.direction_changed = result[4]
        Var.lock_setting_vnb = result[5]
        Var.lock_setting_hnb = result[6]
        Var.pat_num_vnb = result[7]
        Var.pat_num_hnb = result[8]
        Var.tech = result[9]
        Var.count_tech = result[10]
        Var.form = result[11]
        Var.row_count_form = result[12]
        Var.count_form_line = result[13]
        Var.left_end_data_vnb = result[14]
        Var.right_end_data_vnb = result[15]
        Var.left_end_data_hnb = result[16]
        Var.right_end_data_hnb = result[17]
        Var.mg_vnb = result[18]
        Var.mg_hnb = result[19]

    except ValueError:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("read from db")
        msg.setText("Read from DB no value")
        msg.exec_()
        # Var.errorValue = 1
        print("No value")

    db_cursor.close()
    conn.close()


def drop_index():
    conn = sqlite3.connect('passapProject.db')
    db_cursor = conn.cursor()
    db_cursor.execute("DROP INDEX [IF EXISTS] index_tabID")


# ======================================================================
# GUI PyQT5
# ======================================================================

class MyMain(QtWidgets.QMainWindow):

    def __init__(self):
        super(MyMain, self).__init__()

        self.title = 'Passap'
        self.left = 10
        self.top = 40
        self.width = 780
        self.height = 430
        self.autoFillBackground()

        self.init_ui()

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.show()

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, 'Extract!', "You want to close?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            print("Extracting Now")
            QtWidgets.QApplication.instance().quit()
        else:
            pass

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Dynamisches Setzen von Widgets (z.B. Buttons) basierend auf den Fensterdimensionen
        # self.initDynamicWidgets()

        self.init_menu_actions()

    def init_menu_actions(self):
        extractAction = QAction("&Quit", self)
        extractAction.setShortcut("Ctrl+Q")
        extractAction.setStatusTip('Leave the App')
        extractAction.triggered.connect(self.close_application)

        extractActionEdit = QAction("&Edit", self)
        extractActionEdit.setShortcut("Ctrl+E")
        extractActionEdit.setStatusTip('Edit the App')

        openEditor = QAction("&Editor new", self)
        openEditor.setShortcut("Ctrl+E")
        openEditor.setStatusTip('Open Editor')
        openEditor.triggered.connect(self.editor)

        openFile = QAction("&Open File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Open File Editor')
        openFile.triggered.connect(self.file_open)

        saveFile = QAction("&Save Settings", self)
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

        # viewMenu = mainMenu.addMenu('View')
        # searchMenu = mainMenu.addMenu('Search')
        # toolsMenu = mainMenu.addMenu('Tools')
        # helpMenu = mainMenu.addMenu('Help')

    def editor(self):
        textEdit = QTextEdit()
        self.setCentralWidget(textEdit)

    def file_open(self):
        pass

    def file_save(self):
        pass

    def save_settings(self):
        pass


class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabWidget = None
        self.setLayout(QVBoxLayout())
        self.init_ui()
        self.init_label()

    def init_ui(self):
        self.init_tabs()
        self.init_create_table_widget()
        self.init_buttons()
        self.init_label()
        self.add_widgets_to_layout()

    @staticmethod
    def set_drive_icon(label_in, state):
        icon_path = "icon_drive_left.png" if state else "Icon_drive_right.png"  # Ensure these files exist
        pixmap = QPixmap(icon_path)

        # Check if pixmap is null
        if pixmap.isNull():
            print(f"Failed to load image from {icon_path}")
            return

        label_in.setPixmap(pixmap.scaled(50, 50))  # Change 50, 50 to the dimensions you want

    @staticmethod
    def set_icon_state(label_in, icon_path):
        # icon_path = "Icon_color.png" if state else "Icon_button.png"  # Ensure these files exist
        pixmap = QPixmap(icon_path)

        # Check if pixmap is null
        if pixmap.isNull():
            print(f"Failed to load image for color from {icon_path}")
            return

        label_in.setPixmap(pixmap.scaled(50, 50))  # Change 50, 50 to the dimensions you want

    def init_tabs(self):
        self.tabWidget = QTabWidget()
        font = QFont()
        font.setPointSize(12)
        self.tabWidget.setFont(font)

        self.tabWidget.addTab(self.tab1, "Settings")
        self.tabWidget.addTab(self.tab2, "Process")
        self.tabWidget.addTab(self.tab3, "new")

    def init_create_table_widget(self):
        def create_table_widget(rows, columns, parent, x, y, width, height, style):
            tableWidget = QTableWidget(rows, columns, parent)
            tableWidget.setGeometry(QtCore.QRect(x, y, int(width), int(height)))
            tableWidget.setStyleSheet(style)
            tableWidget.verticalHeader().setVisible(False)
            tableWidget.horizontalHeader().setVisible(False)
            tableWidget.setShowGrid(False)
            tableWidget.setFont(QFont('Arial Narrow', 13))
            tableWidget.setAlternatingRowColors(True)
            return tableWidget

        # Verwendung der Funktion
        Var.table1 = create_table_widget(6, 2, self.tab1, 260, 10, 120, 210,
                                         "alternate-background-color: rgb(220, 220, 240); "
                                         "background-color: rgb(210, 210, 235); border: none")

        Var.table2 = create_table_widget(6, 2, self.tab1, 385, 10, 120, 210,
                                         "alternate-background-color: rgb(210, 210, 230); "
                                         "background-color: rgb(200, 200, 225); border: none")

        Var.table3 = create_table_widget(4, 2, self.tab1, 510, 10, 120, 140,
                                         "alternate-background-color: rgb(210, 210, 230); "
                                         "background-color: rgb(200, 200, 225); border: none")

        Var.table4 = create_table_widget(4, 2, self.tab1, 635, 10, 120, 140,
                                         "alternate-background-color: rgb(210, 210, 230); "
                                         "background-color: rgb(200, 200, 225); border: none")
        Var.table5 = create_table_widget(2, 2, self.tab1, 260, 225, 245, 70,
                                         "alternate-background-color: rgb(210, 210, 230); "
                                         "background-color: rgb(200, 200, 225); border: none")
        Var.table6 = create_table_widget(5, 2, self.tab1, 510, 155, 120, 175,
                                         "alternate-background-color: rgb(210, 210, 230); "
                                         "background-color: rgb(200, 200, 225); border: none")
        Var.table7 = create_table_widget(5, 2, self.tab1, 635, 155, 120, 175,
                                         "alternate-background-color: rgb(210, 210, 230); "
                                         "background-color: rgb(200, 200, 225); border: none")

        list_widget = [Var.table1, Var.table2, Var.table3, Var.table4, Var.table5,
                       Var.table6, Var.table7]

        number_of_rows = [6, 6, 4, 4, 2, 5, 5]
        row_num = 0

        # layout cell of table widget
        for i in range(len(list_widget)):
            item = list_widget[i]
            item.verticalHeader().setVisible(False)
            item.horizontalHeader().setVisible(False)
            item.setShowGrid(False)
            item.setFont(QFont('Arial Narrow', 13))
            item.setAlternatingRowColors(True)

            for cell in range(number_of_rows[row_num]):
                item.setRowHeight(cell, 35)

            row_num += 1

            if i == 1:
                item.setColumnWidth(0, 50)
                item.setColumnWidth(1, 70)
            elif i == 4:
                item.setColumnWidth(0, 60)
                item.setColumnWidth(1, 185)
            else:
                item.setColumnWidth(0, 70)
                item.setColumnWidth(1, 50)

            list_pat_vnb = ["Pat_V", "height_V", "rowPat_V", "LeEnd_V", "RiEnd_V", "mg_V"]
            list_pat_hnb = ["Pat_H", "height_H", "rowPat_H", "LeEnd_H", "RiEnd_H", "mg_H"]
            list_tech = ["Tech", "Count_T", "lock_VNB", "lock_HNB"]
            list_form = ["Form", "Line_F", "Count_F", "End Err"]
            list_info = ["Info_T", "Info_F"]
            list_motor = ["EStopp", "FStopp", "Col_C", "Col", "dirC"]
            list_dec_inc_rack = ["Dec_R", "Dec_L", "Inc_R", "Inc_L", "Rack"]

            def set_label_in_table(pos, list_local, sent_table):
                for i_list in range(len(list_local)):
                    item_list = QTableWidgetItem(list_local[i_list])
                    sent_table.setItem(i_list, pos, item_list)

            list_of_list = [list_pat_vnb, list_pat_hnb, list_tech,
                            list_form, list_info, list_motor,
                            list_dec_inc_rack]

            zip_list = zip(list_of_list, list_widget)

            for lists, w in zip_list:
                if w == Var.table2:
                    set_label_in_table(1, lists, w)
                else:
                    set_label_in_table(0, lists, w)

            for item_in_list in range(len(list_widget)):
                item = list_widget[item_in_list]
                item.show()

            list_widget = [Var.table1, Var.table2, Var.table3, Var.table4, Var.table5,
                           Var.table6, Var.table7]

            for item_in_list in range(len(list_widget)):
                item = list_widget[item_in_list]
                item.show()

    def init_buttons(self):

        def create_button(name, x, y, width, height, rgb_col, parent):
            try:
                btn = QtWidgets.QPushButton(name, parent)
                btn.setGeometry(QRect(int(x), int(y), int(width), int(height)))
                btn.setStyleSheet("font: bold; background-color: rgb" + str(rgb_col) + "; border: none")
                btn.setCheckable(True)
                return btn
            except Exception as e:
                print(f"Fehler beim Erstellen des Buttons: {e}")
                return None

        numPad = create_button('NumPad', 10, 10, 100, 45, "(160, 230, 160)", self.tab1)
        numPad.clicked.connect(self.showdialog)

        nullPos = create_button('0Pos', 10, 65, 100, 45, "(160, 224, 224)", self.tab1)
        nullPos.clicked.connect(data_transfer.set_null_pos)

        def send_empty_row():
            data_transfer.send_row_pat_vnb(Var.knitpat_empty_row, "emptyRow")
            data_transfer.send_row_pat_hnb(Var.knitpat_empty_row, "emptyRow")

        emptyRow = create_button('EmptyRow', 10, 120, 100, 45, "(200, 224, 224)", self.tab1)
        emptyRow.clicked.connect(send_empty_row)

        sxProcess = create_button('SX Row', 10, 175, 100, 45, "(200, 224, 224)", self.tab1)
        sxProcess.clicked.connect(self.start_sx_row)

        countDirection = create_button('Dir=0', 10, 230, 100, 45, "(200, 224, 224)",
                                       self.tab1)
        countDirection.clicked.connect(self.set_dir_change_to_0)

        showData = create_button('Data', 130, 10, 100, 45, "(240, 240, 180)",
                                 self.tab1)
        showData.clicked.connect(self.set_values)

        sendData = create_button('SetEndP', 130, 65, 100, 45, "(240, 240, 180)",
                                 self.tab1)
        sendData.clicked.connect(self.send_data)

        sendDataVNB = create_button('SetEndVNB', 130, 120, 100, 45, "(255, 255, 220)",
                                    self.tab1)
        sendDataVNB.clicked.connect(self.send_data_vnb)

        sendDataHNB = create_button('SetEndHNB', 130, 175, 100, 45, "(255, 255, 220)", self.tab1)
        sendDataHNB.clicked.connect(self.send_data_hnb)

    def init_label(self):
        Var.icon_drive = QLabel(self.tab1)
        Var.icon_drive.move(10, 300)
        Var.icon_color_change = QLabel(self.tab1)
        Var.icon_color_change.move(70, 300)
        Var.icon_stopp = QLabel(self.tab1)
        Var.icon_stopp.move(130, 300)

    def add_widgets_to_layout(self):
        self.layout().addWidget(self.tabWidget)
        self.tab1.layout = QHBoxLayout()
        self.tab1.setLayout(self.tab1.layout)

    """ ============================================================
    function
    ============================================================="""

    """ SX brings the pusher in the right knitting position
    Uneven numbers: Lock on the left hand side 
    Even numbers: Lock on the right hand side"""

    """ SX brings the pusher in the right knitting position
        Uneven numbers: Lock on the left hand side 
        Even numbers: Lock on the right hand side"""

    def start_sx_row(self):
        try:
            if Var.direction_changed >= 2 and Var.direction_changed % 2 == 0:
                Var.direction_changed -= 2
                read_from_db(Var.direction_changed)
            elif Var.direction_changed >= 1 and Var.direction_changed % 2 == 1:
                Var.direction_changed -= 1
                read_from_db(Var.direction_changed)
        except ValueError:  # Ersetzen Sie dies durch den spezifischen Fehler, den Sie erwarten
            self._show_warning("start sx row", "no dirChanged")
            print("no dirChanged:", Var.direction_changed)

    # Methode kann nur innerhalb der Klasse verwendet werden.
    @staticmethod
    def _show_warning(title, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec_()

    def send_data(self):
        self.send_data_vnb()
        self.send_data_hnb()

    @staticmethod
    def send_data_vnb():
        data_transfer.set_left_end_vnb(Var.left_end_data_vnb)
        data_transfer.set_right_end_vnb(Var.right_end_data_vnb)

    @staticmethod
    def send_data_hnb():
        data_transfer.set_left_end_hnb(Var.left_end_data_hnb)
        data_transfer.set_right_end_hnb(Var.right_end_data_hnb)

    @staticmethod
    def set_dir_change_to_0():
        Var.direction_changed = 0
        data_transfer.get_needle_pos_vnb()
        data_transfer.get_needle_pos_hnb()

    @classmethod
    def set_values(cls):

        list_value_vnb = [Var.pat_num_vnb, Var.height_vnb, Var.row_count_vnb,
                          Var.left_end_data_vnb, Var.right_end_data_vnb, Var.mg_vnb]
        list_value_hnb = [Var.pat_num_hnb, Var.height_hnb, Var.row_count_hnb,
                          Var.left_end_data_hnb, Var.right_end_data_hnb, Var.mg_hnb]
        list_value_tech = [Var.tech, Var.count_tech, Var.lock_setting_vnb,
                           Var.lock_setting_hnb]
        list_value_form = [Var.form, Var.count_form_line, Var.row_count_form,
                           Var.end_knit_error]
        list_value_info = [Var.info_tech, Var.info_form]
        list_value_motor = [Var.end_stopp, Var.form_stopp, Var.col_change,
                            Var.color_setting, Var.direction_changed]
        list_value_motor2 = [Var.decrease_right, Var.decrease_left,
                             Var.increase_right, Var.increase_left, Var.rack]

        list_of_list_of_val = [list_value_vnb, list_value_hnb, list_value_tech, list_value_form, list_value_info,
                               list_value_motor, list_value_motor2]
        list_of_widget = [Var.table1, Var.table2, Var.table3, Var.table4, Var.table5, Var.table6, Var.table7]

        zip_list = zip(list_of_list_of_val, list_of_widget)

        for l_val, widget_local in zip_list:
            if widget_local == Var.table2:
                for i in range(len(l_val)):
                    widget_local.setItem(i, 0, QTableWidgetItem(str(l_val[i])))
            else:
                for i in range(len(l_val)):
                    widget_local.setItem(i, 1, QTableWidgetItem(str(l_val[i])))

        dynamic_date_entry_settings()

    @classmethod
    def set_pat_vnb(cls, data_in):
        Var.pat_num_vnb = data_in
        temp_patNumb_vnb = str(Var.pat_num_vnb) + "_Pat.bmp"
        file_name_pat_vnb = ("/home/irene/Passap/Pat/" + temp_patNumb_vnb)
        try:
            PatternArray.set_array_vnb(file_name_pat_vnb)
            Var.height_vnb = len(Var.knitpat_black_vnb)
        except IOError:
            cls.error_dialog("! No such pattern number: " + data_in)
            Var.numb = ""

    @classmethod
    def set_pat_hnb(cls, data_in):
        try:
            Var.pat_num_hnb = data_in
            temp_pat_numb_hnb = str(Var.pat_num_hnb) + "_Pat.bmp"
            file_name_pat_hnb = ("/home/irene/Passap/Pat/" + temp_pat_numb_hnb)
            PatternArray.set_array_hnb(file_name_pat_hnb)
            Var.height_hnb = len(Var.knitpat_black_hnb)
        except IOError:
            cls.error_dialog("! No such pattern number: " + data_in)
            Var.numb = ""

    @staticmethod
    def get_num_x():
        Var.numb += Var.new_num
        # print("numb", Var.numb)

    def clicked_me(self):
        # print("clicked")
        sender = self.sender()
        msg = sender.text()
        Var.new_num = msg
        self.get_num_x()

    @staticmethod
    def done_numb():
        Var.all_num = True

    def set_numb(self):
        sender = self.sender()
        msg = str(sender.text())
        # print(msg)

        if msg == "LeE":
            x = int(Var.numb)
            if 180 > x > 0:
                Var.left_end_data_vnb = x
                Var.left_end_data_hnb = x
            else:
                print("Value error left_end_data")
            Var.numb = ""

        if msg == "LeEV":
            x = int(Var.numb)
            if 180 > x > 0:
                Var.left_end_data_vnb = x
            else:
                print("Value error left_end_data_vnb")
            Var.numb = ""

        if msg == "LeEH":
            x = int(Var.numb)
            if 180 > x > 0:
                Var.left_end_data_hnb = x
            else:
                print("Value error left_end_data_hnb")
            Var.numb = ""

            # hier sollte ich etwas ändern, ich brauche 2 Variablen → Zukunft
        if msg == "RiE":
            x = int(Var.numb)

            if 180 > x > 0:
                Var.right_end_data_vnb = x
                Var.right_end_data_hnb = x
                # print("Right end vnb: ", Var.right_end_data_vnb)
            else:
                print("Value error right_end_data")
            Var.numb = ""

        if msg == "RiEV":
            x = int(Var.numb)
            if 180 > x > 0:
                Var.right_end_data_vnb = x
            else:
                print("Value error right_end_data_vnb")
            Var.numb = ""

        if msg == "RiEH":
            x = int(Var.numb)

            if 180 > x > 0:
                Var.right_end_data_hnb = x
            else:
                print("Value error right_end_data_hnb")
            Var.numb = ""

        if msg == "RowV":
            Var.row_count_vnb = Var.numb
            Var.numb = ""

        if msg == "RowH":
            Var.row_count_hnb = Var.numb
            Var.numb = ""

        # Dir ermöglicht auf eine bestimmte Reihe in der DB zurückzuspringen
        if msg == "Dir":
            dir_change = Var.numb
            read_from_db(dir_change)
            Var.direction_changed = int(dir_change)
            Var.numb = ""

        if msg == "MgV":
            Var.mg_vnb = float(Var.numb) * 0.01
            Var.numb = ""

        if msg == "MgH":
            Var.mg_hnb = float(Var.numb) * 0.01
            Var.numb = ""

        if msg == "PatV":
            temp_numb_vnb = Var.numb
            Var.numb = ""
            self.set_pat_vnb(temp_numb_vnb)

        if msg == "AddPatV":
            temp_numb_vnb = Var.numb
            Var.numb = ""
            self.add_pat_vnb(temp_numb_vnb)

        if msg == "PatH":
            temp_numb_hnb = Var.numb
            Var.numb = ""
            self.set_pat_hnb(temp_numb_hnb)

        if msg == "AddPatH":
            temp_numb_hnb = Var.numb
            Var.numb = ""
            self.add_pat_hnb(temp_numb_hnb)

        if msg == "Tech":
            Var.tech = Var.numb
            Var.numb = ""
            try:
                Var.tech_array = TechArray.return_tech_data(Var.tech)
                Var.count_tech = 0
                Var.numb = ""
            except IOError:
                self.error_dialog("! No such tech number: " + Var.tech)
                Var.numb = ""

        if msg == "cTec":
            Var.count_tech = int(Var.numb)
            Var.numb = ""

        if msg == "Form":
            Var.form = Var.numb
            Var.numb = ""

            try:
                Var.form_array = FormArray.return_form_data(Var.form)
                Var.count_form_line = 0
                Var.row_count_form = 0
                Var.repeat_from_line_0 = 0
                Var.repeat_from_line_x = 0
                Var.jump_counter = 0
                Var.end_knit_error = 0
                Var.numb = ""
            except IOError:
                self.error_dialog("! No such form number: " + Var.form)
                Var.numb = ""

        if msg == "formC":
            Var.row_count_form = int(Var.numb)
            Var.numb = ""
            Var.end_knit_error = 0

        if msg == "fLine":
            Var.count_form_line = int(Var.numb)
            Var.end_knit_error = 0
            Var.numb = ""

        self.set_values()

    @staticmethod
    def error_dialog(data):
        d = QDialog()
        error = QtWidgets.QPushButton(f"&{data}", d)
        error.setStyleSheet("background-color: Hsl(10,70%,70%); border: none")
        error.setEnabled(True)
        error.setFont(QFont('Arial Narrow', 14, QFont.Bold))
        error.setFixedHeight(150)
        error.setFixedWidth(400)
        error.clicked.connect(lambda: d.done(2))
        d.setWindowTitle("Error message")
        d.exec_()

    def showdialog(self):
        d2 = QDialog()
        showdialog_layout = QGridLayout()

        fontBtn = QFont('Arial Narrow bold', 14)
        fontBtn.setBold(True)

        def reset_numb():
            Var.numb = ""

        def done_all():
            reset_numb()
            d2.accept()  # Verwenden von accept() anstelle von done(2)

        # Definition und Gestaltung der Nummer-Buttons
        nums = [QtWidgets.QPushButton(str(i), d2) for i in range(1, 10)] + [QtWidgets.QPushButton("0", d2)]
        for btn in nums:
            btn.setFont(fontBtn)
            btn.setFixedHeight(80)
            btn.setFixedWidth(80)
            btn.setStyleSheet("background-color: rgb(230, 231, 234); border: none")
            btn.clicked.connect(self.clicked_me)

        # Definition und Gestaltung der Functions-Buttons
        open_styles = [
            ("PatV", "rgb(150, 200, 255)"),
            ("LeE", "rgb(200, 235, 200)"),
            ("PatH", "rgb(150, 200, 255)"),
            ("RowV", "rgb(210, 235, 235)"),
            ("RowH", "rgb(210, 235, 235)"),
            ("RiE", "rgb(200, 235, 200)"),
            ("Dir", "rgb(195, 220, 220)"),
            ("MgV", "rgb(200, 235, 200)"),
            ("MgH", "rgb(200, 235, 200)"),
            ("Tech", "rgb(180, 180, 210)"),
            ("cTec", "rgb(210, 210, 230)"),
            ("Quit", "rgb(255, 100, 100)"),
            ("Form", "rgb(230, 210, 130)"),
            ("fLine", "rgb(240, 230, 150)"),
            ("formC", "rgb(255, 245, 170)")
        ]

        opens = []
        for label, color in open_styles:
            btn = QtWidgets.QPushButton(label, d2)
            btn.setFont(fontBtn)
            btn.setFixedHeight(80)
            btn.setFixedWidth(80)
            btn.setStyleSheet(f"background-color: {color}; border: none")
            btn.clicked.connect(self.set_numb)
            opens.append(btn)

        opens[11].clicked.connect(done_all)  # Dies ist der Quit-Button

        # Layout Positionierung
        for i, btn in enumerate(nums[:3]):
            showdialog_layout.addWidget(btn, 0, i + 1)
        for i, btn in enumerate(nums[3:6]):
            showdialog_layout.addWidget(btn, 1, i + 1)
        for i, btn in enumerate(nums[6:9]):
            showdialog_layout.addWidget(btn, 2, i + 1)
        showdialog_layout.addWidget(nums[-1], 3, 2)

        # Positionierung der Functions-Buttons
        positions = [(0, 0), (1, 0), (0, 4), (0, 5), (0, 6), (1, 4), (1, 6), (2, 0), (2, 4), (3, 1), (3, 0), (3, 6),
                     (3, 3), (3, 4), (3, 5)]
        for btn, (row, col) in zip(opens, positions):
            showdialog_layout.addWidget(btn, row, col)

        d2.setLayout(showdialog_layout)
        d2.setWindowTitle("NumPad")
        d2.exec_()


# ------------------------------------END

if __name__ == '__main__':
    # Erzeugung der Singleton-Instanz für Arduino-Verbindung
    arduino_connection_singleton = ArduinoConnectionSingleton()
    # Datenübertragungsobjekt mit der Singleton-Verbindung
    data_transfer = DataTransferArduino(arduino_connection_singleton)

    app = QtWidgets.QApplication(sys.argv)

    window = MyMain()
    window.show()

    GPIOStart.act()
    create_table()

    sys.exit(app.exec_())
