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

portx = 'COM20'# Check device manager for COM port number

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

historyLength = 1200

Pressure_L_F_Data = np.zeros(historyLength).__array__('d')  # fix the array size
Pressure_L_B_Data = np.zeros(historyLength).__array__('d')
EMG_L_Data = np.zeros(historyLength).__array__('d')
Velocity_L_X_Data = np.zeros(historyLength).__array__('d')
Velocity_L_X_Data = np.zeros(historyLength).__array__('d')

Pressure_R_F_Data = np.zeros(historyLength).__array__('d')  # fix the array size
Pressure_R_B_Data = np.zeros(historyLength).__array__('d')
EMG_R_Data = np.zeros(historyLength).__array__('d')
Velocity_R_X_Data = np.zeros(historyLength).__array__('d')
Velocity_R_X_Data = np.zeros(historyLength).__array__('d')

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
        self.setWindowTitle("Sketch1115")
        self.resize(1920,1080)

        #Left
        self.Pressure_L_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Pressure_L_pw.resize(400,225)
        self.Pressure_L_pw.move(30,30)
        self.Pressure_L_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Pressure_L_pw.setRange(xRange=[0, historyLength], yRange=[300, 850], padding=0)
        self.Pressure_L_F_Curve = self.Pressure_L_pw.plot(Pressure_L_F_Data, pen='r')  # plot in the widget
        self.Pressure_L_B_Curve = self.Pressure_L_pw.plot(Pressure_L_B_Data, pen='r')  # plot in the widget

        self.EMG_L_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.EMG_L_pw.resize(400,225)
        self.EMG_L_pw.move(30, 270)
        self.EMG_L_pw.showGrid(x=True, y=True)  # Turn on grid
        self.EMG_L_pw.setRange(xRange=[0, historyLength], yRange=[300, 850], padding=0)
        self.EMG_L_Curve = self.EMG_L_pw.plot(EMG_L_Data, pen='r')  # plot in the widget

        self.Velocity_L_X_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Velocity_L_X_pw.resize(400, 225)
        self.Velocity_L_X_pw.move(30, 510)
        self.Velocity_L_X_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Velocity_L_X_pw.setRange(xRange=[0, historyLength], yRange=[300, 850], padding=0)
        self.Velocity_L_X_Curve = self.Velocity_L_X_pw.plot(Velocity_L_X_Data, pen='r')  # plot in the widget

        self.Velocity_L_Z_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Velocity_L_Z_pw.resize(400, 225)
        self.Velocity_L_Z_pw.move(30, 760)
        self.Velocity_L_Z_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Velocity_L_Z_pw.setRange(xRange=[0, historyLength], yRange=[300, 850], padding=0)
        self.Velocity_L_Z_Curve = self.Velocity_L_Z_pw.plot(Velocity_L_Z_Data, pen='r')  # plot in the widget

        #Right
        self.Pressure_R_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Pressure_R_pw.resize(400, 225)
        self.Pressure_R_pw.move(500, 30)
        self.Pressure_R_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Pressure_R_pw.setRange(xRange=[0, historyLength], yRange=[300, 850], padding=0)
        self.Pressure_R_F_Curve = self.Pressure_R_pw.plot(Pressure_R_F_Data, pen='r')  # plot in the widget
        self.Pressure_R_B_Curve = self.Pressure_R_pw.plot(Pressure_R_B_Data, pen='r')  # plot in the widget

        self.EMG_R_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.EMG_R_pw.resize(400, 225)
        self.EMG_R_pw.move(500, 270)
        self.EMG_R_pw.showGrid(x=True, y=True)  # Turn on grid
        self.EMG_R_pw.setRange(xRange=[0, historyLength], yRange=[300, 850], padding=0)
        self.EMG_R_Curve = self.EMG_R_pw.plot(EMG_R_Data, pen='r')  # plot in the widget

        self.Velocity_R_X_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Velocity_R_X_pw.resize(400, 225)
        self.Velocity_R_X_pw.move(500, 510)
        self.Velocity_R_X_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Velocity_R_X_pw.setRange(xRange=[0, historyLength], yRange=[300, 850], padding=0)
        self.Velocity_R_X_Curve = self.Velocity_R_X_pw.plot(Velocity_R_X_Data, pen='r')  # plot in the widget

        self.Velocity_R_Z_pw = pg.PlotWidget(self)  # Create a PlotWidget
        self.Velocity_R_Z_pw.resize(400, 225)
        self.Velocity_R_Z_pw.move(500, 760)
        self.Velocity_R_Z_pw.showGrid(x=True, y=True)  # Turn on grid
        self.Velocity_R_Z_pw.setRange(xRange=[0, historyLength], yRange=[300, 850], padding=0)
        self.Velocity_R_Z_Curve = self.Velocity_R_Z_pw.plot(Velocity_R_Z_Data, pen='r')  # plot in the widget

        # self.L_BPM1 = QLabel(self)
        # self.L_BPM1.setText("BPM")
        # self.L_BPM1.resize(400, 50)
        # self.L_BPM1.move(1000, 10)
        # self.L_BPM1.setStyleSheet("QLabel{color:rgb(255,22,22,255);font-size:50px;font-weight:normal;font-family:Arial;}")


    def plotData(self):
        global i;
        if i < historyLength:
            Pressure_L_F_Data[i] = Pressure_L_F_Queue.get()
            Pressure_L_B_Data[i] = Pressure_L_B_Queue.get()
            i = i + 1
        else:
            Pressure_L_F_Data[:-1] = Pressure_L_F_Data[1:]
            Pressure_L_F_Data[i - 1] = Pressure_L_F_Queue.get()
            Pressure_L_B_Data[:-1] = Pressure_L_B_Data[1:]
            Pressure_L_B_Data[i - 1] = Pressure_L_B_Queue.get()

        self.Pressure_L_F_Curve.setData(Pressure_L_F_Data)
        self.Pressure_L_B_Curve.setData(Pressure_L_B_Data)

    def Serial(self):
        global i;
        global q;
        while (True):
            n = mSerial.inWaiting()

            if (n):
                dat = mSerial.readline()
                # print(dat)
                Pressure_L_F_Queue.put(dat)
                Pressure_L_B_Queue.put(dat)
    
    def data_collection(self):
        # the list is initialized each time this method is called
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

        cntr = 0
        recording_len = 20 # length of data kept (in seconds)
        num_data = recording_len*1000/rate #

        for cntr in range(num_data):
            Pressure_L_F_rec.append(Pressure_L_F_Queue.get())
            Pressure_L_B_rec.append(Pressure_L_F_Queue.get())
            deltaVx_L_rec.append(Pressure_L_F_Queue.get())
            deltaVz_L_rec.append(Pressure_L_F_Queue.get())
            emg_L_rec.append(Pressure_L_F_Queue.get())

            Pressure_R_F_rec.append(Pressure_L_F_Queue.get())
            Pressure_R_B_rec.append(Pressure_L_F_Queue.get())
            deltaVx_R_rec.append(Pressure_L_F_Queue.get())
            deltaVz_R_rec.append(Pressure_L_F_Queue.get())
            emg_R_rec.append(Pressure_L_F_Queue.get())

            i = i + 1

def find_changepoints(arr):
    changepoints = defaultdict(list)
    current_value = arr[0]
    for (index, value) in enumerate(arr):
        if value != current_value:
            changepoints[ (current_value, value) ].append(index)
            current_value = value
    
    return changepoints

def combine_heel_toe(front, back):
    combined = list()
    error = 4
    for i in range(len(front)):
        if front[i] == 0 and back[i] == 0:
            combined.append(0)
        elif front[i] == 0 and back[i] == 1:
            combined.append(1)
        elif front[i] == 1 and back[i] == 0:
            combined.append(2)
        elif front[i] == 1 and back[i] == 1:
            combined.append(3)
        else:
            combined.append(error)
            

def pressure_analysis(LF, LB, RF, RB):
    LF_len = len(LF)
    LB_len = len(LB)
    RF_len = len(RF)
    RB_len = len(RB)
    min_len = min[LF_len, LB_len, RF_len, RB_len]
    del LF[]

    for i in range(actual_len):
        if LF[i] == 0 and LB[i] == 0:
            
    LF_seq = find_changepoints(LF)
    LB_seq = find_changepoints(LB)
    RF_seq = find_changepoints(RF)
    RB_seq = find_changepoints(RB)
    
    # calculate the number of strides, and take the smaller number

    # calculate the average time of each stance 



if __name__ == "__main__":

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
    timer.start(1)  # Called every X ms

    w.show()

    # ---------grace's code starts here ----------
    # to simplify things always use right foot forward
    w.datacollection()
    pressure_analysis(Pressure_L_F_rec, Pressure_L_B_rec, Pressure_R_F_rec, Pressure_R_B_rec)
    # ---------grace's code stops here -----------

    sys.exit(app.exec_())