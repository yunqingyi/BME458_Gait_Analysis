import pyqtgraph as pg
import pyqtgraph.exporters
import array
import serial
import threading
import numpy as np
from queue import Queue
import time

import sys
import random
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QTextBrowser, QLabel, QLineEdit\
    , QPushButton
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPalette
from collections import defaultdict

portx = 'COM14' # Check device manager for COM port number
system_freq = 100 # freq of data collection, 100Hz = 10 ms

i = 0
#queue
Pressure_L_F_Queue = Queue(maxsize=0)
Pressure_L_B_Queue = Queue(maxsize=0)
EMG_L_Queue = Queue(maxsize=0)
Velocity_L_X_Queue = Queue(maxsize=0)
Velocity_L_Z_Queue = Queue(maxsize=0)

Pressure_R_F_Queue = Queue(maxsize=0)
Pressure_R_B_Queue = Queue(maxsize=0)
EMG_R_Queue = Queue(maxsize=0)
Velocity_R_X_Queue = Queue(maxsize=0)
Velocity_R_Z_Queue = Queue(maxsize=0)

#Data array
Pressure_L_F_Data = array.array('i')  # variable size array
Pressure_L_B_Data = array.array('i')
EMG_L_Data = array.array('i')
Velocity_L_X_Data = array.array('i')
Velocity_L_Z_Data = array.array('i')

Pressure_R_F_Data = array.array('i')  # variable size array
Pressure_R_B_Data = array.array('i')
EMG_R_Data = array.array('i')
Velocity_R_X_Data = array.array('i')
Velocity_R_Z_Data = array.array('i')

historyLength = 200

Pressure_L_F_Data = np.zeros(historyLength).__array__('d')  # fix the array size
Pressure_L_B_Data = np.zeros(historyLength).__array__('d')
EMG_L_Data = np.zeros(historyLength).__array__('d')
Velocity_L_X_Data = np.zeros(historyLength).__array__('d')
Velocity_L_Z_Data = np.zeros(historyLength).__array__('d')

Pressure_R_F_Data = np.zeros(historyLength).__array__('d')  # fix the array size
Pressure_R_B_Data = np.zeros(historyLength).__array__('d')
EMG_R_Data = np.zeros(historyLength).__array__('d')
Velocity_R_X_Data = np.zeros(historyLength).__array__('d')
Velocity_R_Z_Data = np.zeros(historyLength).__array__('d')

Velocity_Offset_L_X = 0
Velocity_Offset_L_Z = 0
Velocity_Offset_R_X = 0
Velocity_Offset_R_Z = 0

# arrays used to store data for analysis
Pressure_L_F_rec = []
Pressure_L_B_rec = []
deltaVx_L_rec = []
deltaVz_L_rec = []
emg_L_rec = []
Pressure_R_F_rec = []
Pressure_R_B_rec = []
deltaVx_R_rec = []
deltaVz_R_rec = []
emg_R_rec = []


class Win(QWidget):
    def __init__(self):
        super(Win,self).__init__()
        self.setWindowTitle("DataCollection1129")
        self.resize(1920,1080)

        #Left
        self.Pressure_L_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Pressure_L_pw.resize(400,225)
        self.Pressure_L_pw.move(130,30)
        self.Pressure_L_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Pressure_L_pw.setRange(xRange=[0, historyLength], yRange=[-0.3, 1.3], padding=0)
        self.Pressure_L_F_Curve = self.Pressure_L_pw.plot(Pressure_L_F_Data, pen='r')  # plot in the widget
        self.Pressure_L_B_Curve = self.Pressure_L_pw.plot(Pressure_L_B_Data, pen='b')  # plot in the widget

        self.EMG_L_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.EMG_L_pw.resize(400,225)
        self.EMG_L_pw.move(130, 270)
        self.EMG_L_pw.showGrid(x=True, y=True)  # Turn on grid
        self.EMG_L_pw.setRange(xRange=[0, historyLength], yRange=[-100, 800], padding=0)
        self.EMG_L_Curve = self.EMG_L_pw.plot(EMG_L_Data, pen='r')  # plot in the widget

        self.Velocity_L_X_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Velocity_L_X_pw.resize(400, 225)
        self.Velocity_L_X_pw.move(130, 510)
        self.Velocity_L_X_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Velocity_L_X_pw.setRange(xRange=[0, historyLength], yRange=[-0.3, 0.3], padding=0)
        self.Velocity_L_X_Curve = self.Velocity_L_X_pw.plot(Velocity_L_X_Data, pen='r')  # plot in the widget

        self.Velocity_L_Z_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Velocity_L_Z_pw.resize(400, 225)
        self.Velocity_L_Z_pw.move(130, 760)
        self.Velocity_L_Z_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Velocity_L_Z_pw.setRange(xRange=[0, historyLength], yRange=[-0.3, 0.3], padding=0)
        self.Velocity_L_Z_Curve = self.Velocity_L_Z_pw.plot(Velocity_L_Z_Data, pen='r')  # plot in the widget

        #Right
        self.Pressure_R_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Pressure_R_pw.resize(400, 225)
        self.Pressure_R_pw.move(600, 30)
        self.Pressure_R_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Pressure_R_pw.setRange(xRange=[0, historyLength], yRange=[-0.3, 1.3], padding=0)
        self.Pressure_R_F_Curve = self.Pressure_R_pw.plot(Pressure_R_F_Data, pen='r')  # plot in the widget
        self.Pressure_R_B_Curve = self.Pressure_R_pw.plot(Pressure_R_B_Data, pen='b')  # plot in the widget

        self.EMG_R_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.EMG_R_pw.resize(400, 225)
        self.EMG_R_pw.move(600, 270)
        self.EMG_R_pw.showGrid(x=True, y=True)  # Turn on grid
        self.EMG_R_pw.setRange(xRange=[0, historyLength], yRange=[-100, 800], padding=0)
        self.EMG_R_Curve = self.EMG_R_pw.plot(EMG_R_Data, pen='r')  # plot in the widget

        self.Velocity_R_X_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Velocity_R_X_pw.resize(400, 225)
        self.Velocity_R_X_pw.move(600, 510)
        self.Velocity_R_X_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Velocity_R_X_pw.setRange(xRange=[0, historyLength], yRange=[-0.3, 0.3], padding=0)
        self.Velocity_R_X_Curve = self.Velocity_R_X_pw.plot(Velocity_R_X_Data, pen='r')  # plot in the widget

        self.Velocity_R_Z_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Velocity_R_Z_pw.resize(400, 225)
        self.Velocity_R_Z_pw.move(600, 760)
        self.Velocity_R_Z_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Velocity_R_Z_pw.setRange(xRange=[0, historyLength], yRange=[-0.3, 0.3], padding=0)
        self.Velocity_R_Z_Curve = self.Velocity_R_Z_pw.plot(Velocity_R_Z_Data, pen='r')  # plot in the widget

        self.Label_left = QLabel(self)
        self.Label_left.setText("LEFT")
        self.Label_left.resize(100, 20)
        self.Label_left.move(300, 10)
        self.Label_left.setStyleSheet("QLabel{font-size:16px;font-weight:normal;font-family:Arial;}")

        self.Label_right = QLabel(self)
        self.Label_right.setText("RIGHT")
        self.Label_right.resize(100, 20)
        self.Label_right.move(775, 10)
        self.Label_right.setStyleSheet("QLabel{font-size:16px;font-weight:normal;font-family:Arial;}")

        self.Label_right = QLabel(self)
        self.Label_right.setText("Pressure \r\n Sensor")
        self.Label_right.resize(100, 50)
        self.Label_right.move(30, 150)
        self.Label_right.setStyleSheet("QLabel{font-size:16px;font-weight:normal;font-family:Arial;}")

        self.Label_right = QLabel(self)
        self.Label_right.setText("EMG")
        self.Label_right.resize(100, 20)
        self.Label_right.move(40, 390)
        self.Label_right.setStyleSheet("QLabel{font-size:16px;font-weight:normal;font-family:Arial;}")

        self.Label_right = QLabel(self)
        self.Label_right.setText("Horizontal \r\n Velocity")
        self.Label_right.resize(100, 50)
        self.Label_right.move(30, 640)
        self.Label_right.setStyleSheet("QLabel{font-size:16px;font-weight:normal;font-family:Arial;}")

        self.Label_right = QLabel(self)
        self.Label_right.setText("Vertical \r\n Velocity")
        self.Label_right.resize(100, 50)
        self.Label_right.move(30, 880)
        self.Label_right.setStyleSheet("QLabel{font-size:16px;font-weight:normal;font-family:Arial;}")

        self.B_SaveImage = QPushButton(self)
        self.B_SaveImage.setText("Get Stride Time")
        self.B_SaveImage.resize(400, 50)
        self.B_SaveImage.move(1500, 900)
        self.B_SaveImage.setStyleSheet("QPushButton{font-size:30px;font-weight:normal;}")
        self.B_SaveImage.clicked.connect(self.pressure_analysis)

        self.Label_Strd_time_l = QLabel(self)
        self.Label_Strd_time_l.setText("Average Stride Time(Left):")
        self.Label_Strd_time_l.resize(600, 100)
        self.Label_Strd_time_l.move(1100, 50)
        self.Label_Strd_time_l.setStyleSheet("QLabel{color:rgb(0,0,0,255);font-size:28px;font-weight:normal;font-family:Arial;}")

        self.Label_Strd_time_r = QLabel(self)
        self.Label_Strd_time_r.setText("Average Stride Time(Right):")
        self.Label_Strd_time_r.resize(600, 100)
        self.Label_Strd_time_r.move(1100, 150)
        self.Label_Strd_time_r.setStyleSheet("QLabel{color:rgb(0,0,0,255);font-size:28px;font-weight:normal;font-family:Arial;}")


    def plotData(self):
        global i;

        if i < historyLength:
            Pressure_L_F_Data[i] = Pressure_L_F_Queue.get()
            Pressure_L_B_Data[i] = Pressure_L_B_Queue.get()
            Pressure_R_F_Data[i] = Pressure_R_F_Queue.get()
            Pressure_R_B_Data[i] = Pressure_R_B_Queue.get()
            EMG_L_Data[i] = EMG_L_Queue.get()
            EMG_R_Data[i] = EMG_R_Queue.get()
            Velocity_L_X_Data[i] = Velocity_L_X_Queue.get()
            Velocity_L_Z_Data[i] = Velocity_L_Z_Queue.get()
            Velocity_R_X_Data[i] = Velocity_R_X_Queue.get()
            Velocity_R_Z_Data[i] = Velocity_R_Z_Queue.get()

            # Data collection for data analysis
            Pressure_L_F_rec.append(Pressure_L_F_Data[i])
            Pressure_L_B_rec.append(Pressure_L_B_Data[i])
            deltaVx_L_rec.append(Velocity_L_X_Data[i])
            deltaVz_L_rec.append(Velocity_L_Z_Data[i])
            emg_L_rec.append(EMG_L_Data[i])
            Pressure_R_F_rec.append(Pressure_R_F_Data[i])
            Pressure_R_B_rec.append(Pressure_R_B_Data[i])
            deltaVx_R_rec.append(Velocity_R_X_Data[i])
            deltaVz_R_rec.append(Velocity_R_Z_Data[i])
            emg_R_rec.append(EMG_R_Data[i])

            i = i + 1
        else:
            Pressure_L_F_Data[:-1] = Pressure_L_F_Data[1:]
            Pressure_L_F_Data[i - 1] = Pressure_L_F_Queue.get()
            Pressure_L_B_Data[:-1] = Pressure_L_B_Data[1:]
            Pressure_L_B_Data[i - 1] = Pressure_L_B_Queue.get()

            Pressure_R_F_Data[:-1] = Pressure_R_F_Data[1:]
            Pressure_R_F_Data[i - 1] = Pressure_R_F_Queue.get()
            Pressure_R_B_Data[:-1] = Pressure_R_B_Data[1:]
            Pressure_R_B_Data[i - 1] = Pressure_R_B_Queue.get()

            EMG_L_Data[:-1] = EMG_L_Data[1:]
            EMG_L_Data[i - 1] = EMG_L_Queue.get()
            EMG_R_Data[:-1] = EMG_R_Data[1:]
            EMG_R_Data[i - 1] = EMG_R_Queue.get()

            Velocity_L_X_Data[:-1] = Velocity_L_X_Data[1:]
            Velocity_L_X_Data[i - 1] = Velocity_L_X_Queue.get()
            Velocity_L_Z_Data[:-1] = Velocity_L_Z_Data[1:]
            Velocity_L_Z_Data[i - 1] = Velocity_L_Z_Queue.get()

            Velocity_R_X_Data[:-1] = Velocity_R_X_Data[1:]
            Velocity_R_X_Data[i - 1] = Velocity_R_X_Queue.get()
            Velocity_R_Z_Data[:-1] = Velocity_R_Z_Data[1:]
            Velocity_R_Z_Data[i - 1] = Velocity_R_Z_Queue.get()

            # Data collection for data analysis
            Pressure_L_F_rec.append(Pressure_L_F_Data[-1])
            Pressure_L_B_rec.append(Pressure_L_B_Data[-1])
            deltaVx_L_rec.append(Velocity_L_X_Data[-1])
            deltaVz_L_rec.append(Velocity_L_Z_Data[-1])
            emg_L_rec.append(EMG_L_Data[-1])
            Pressure_R_F_rec.append(Pressure_R_F_Data[-1])
            Pressure_R_B_rec.append(Pressure_R_B_Data[-1])
            deltaVx_R_rec.append(Velocity_R_X_Data[-1])
            deltaVz_R_rec.append(Velocity_R_Z_Data[-1])
            emg_R_rec.append(EMG_R_Data[-1])


        self.Pressure_L_F_Curve.setData(Pressure_L_F_Data)
        self.Pressure_L_B_Curve.setData(Pressure_L_B_Data)
        self.Pressure_R_F_Curve.setData(Pressure_R_F_Data)
        self.Pressure_R_B_Curve.setData(Pressure_R_B_Data)
        self.EMG_L_Curve.setData(EMG_L_Data)
        self.EMG_R_Curve.setData(EMG_R_Data)
        self.Velocity_L_X_Curve.setData(Velocity_L_X_Data)
        self.Velocity_L_Z_Curve.setData(Velocity_L_Z_Data)
        self.Velocity_R_X_Curve.setData(Velocity_R_X_Data)
        self.Velocity_R_Z_Curve.setData(Velocity_R_Z_Data)




    def Serial(self):
        global i;
        global q;
        while (True):
            n = mSerial.inWaiting()

            if (n):
                line = str(mSerial.readline())
                dat = line.split(",")
                # print(line)
                # print(dat)
                if len(dat) == 12:
                    Pressure_L_F_Queue.put(dat[1])
                    Pressure_L_B_Queue.put(dat[2])
                    EMG_L_Queue.put(dat[3])
                    Pressure_R_F_Queue.put(dat[4])
                    Pressure_R_B_Queue.put(dat[5])
                    EMG_R_Queue.put(dat[6])
                    Velocity_L_X_Queue.put(dat[7])
                    Velocity_L_Z_Queue.put(dat[8])
                    Velocity_R_X_Queue.put(dat[9])
                    Velocity_R_Z_Queue.put(dat[10])

    def pressure_analysis(self):
        LF_len = len(Pressure_L_F_rec)
        LB_len = len(Pressure_L_B_rec)
        RF_len = len(Pressure_R_F_rec)
        RB_len = len(Pressure_R_B_rec)
        actual_len = min(LF_len, LB_len, RF_len, RB_len)
        del Pressure_L_F_rec[actual_len:]
        del Pressure_L_B_rec[actual_len:]
        del Pressure_R_F_rec[actual_len:]
        del Pressure_R_B_rec[actual_len:]

        L_seq = combine_heel_toe(Pressure_L_F_rec, Pressure_L_B_rec)
        R_seq = combine_heel_toe(Pressure_R_F_rec, Pressure_R_B_rec)

        # calculate the number of strides, and take the smaller number
        L_changepoints = find_changepoints(L_seq)
        R_changepoints = find_changepoints(R_seq)

        # calculate the average time of each stance
        Left_changepoints = dict(L_changepoints)
        Left_one_to_three = Left_changepoints["(1, 3)"]
        num_L_changepoints = len(Left_one_to_three)

        Right_changepoints = dict(R_changepoints)
        Right_one_to_three = Right_changepoints["(1, 3)"]
        num_R_changepoints = len(Right_one_to_three)

        L_stride_time = list()
        R_stride_time = list()
        for i in range(num_L_changepoints - 1):
            stride_time_L = Left_one_to_three[i+1] - Left_one_to_three[i]
            L_stride_time.append(stride_time_L)
        for i in range(num_R_changepoints - 1):
            stride_time_R = Right_one_to_three[i+1] - Right_one_to_three[i]
            R_stride_time.append(stride_time_R)
        
        L_stride_time_avg = Average(L_stride_time) * 1000 / system_freq # given in ms
        R_stride_time_avg = Average(R_stride_time) * 1000 / system_freq # given in ms

        # unit test button clicked to change data display
        # self.Label_Strd_time_l.setText("# of Left Strides:" + str(num_L_changepoints))
        #TODO display avg stride time
        self.Label_Strd_time_l.setText("Average Stride Time(Left): " + str(L_stride_time_avg))
        self.Label_Strd_time_r.setText("Average Stride Time(Right): " + str(R_stride_time_avg))

def Average(lst):
    return sum(lst) / len(lst)

def find_changepoints(arr):
    changepoints = defaultdict(list)
    current_value = arr[0]
    for (index, value) in enumerate(arr):
        if value != current_value:
            changepoints[str((current_value, value))].append(index)
            current_value = value
    return changepoints

def combine_heel_toe(front, back):
    combined = list()
    error = 4
    for i in range(len(front)):
        if front[i] == 0 and back[i] == 0:
            combined.append(1)
        elif front[i] == 0 and back[i] == 1:
            combined.append(2)
        elif front[i] == 1 and back[i] == 0:
            combined.append(3)
        elif front[i] == 1 and back[i] == 1:
            combined.append(4)
        else:
            combined.append(error)
    return combined





if __name__ == "__main__":

    Pressure_L_F_rec.clear()
    Pressure_L_B_rec.clear()
    deltaVx_L_rec.clear()
    deltaVz_L_rec.clear()
    emg_L_rec.clear()
    Pressure_R_F_rec.clear()
    Pressure_R_B_rec.clear()
    deltaVx_R_rec.clear()
    deltaVz_R_rec.clear()
    emg_R_rec.clear()

    app = QApplication(sys.argv)

    w = Win()



    bps = 9600
    # Serial is open
    mSerial = serial.Serial(portx, int(bps))
    if (mSerial.isOpen()):
        dat = 0xff;
        dat >> 2;
        print("open success")
        # Send some stuff to the serial port
        mSerial.write("hello".encode())
        mSerial.flushInput()  # Clear buffer
    else:
        print("open failed")
        serial.close()  # close serial port
    th1 = threading.Thread(target=w.Serial)
    th1.start()

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(w.plotData)  # Set timer to refresh the display
    timer.start(15)  # Called every X ms

    w.show()


    sys.exit(app.exec_())