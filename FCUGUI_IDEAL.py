import os
# Show current generation, display total error and maximum error

import platform
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
import qrc_resources
import addpointdlg
from mainwindow_test import Ui_MainWindow
from GA_Algorithm_03 import *
import serial
import time


__version__ = "1.0.0"

HOST = "localhost"
PORT = 9001
WAVELENGTH = 0      # Wavelength index
AMPLITUDE = 1       # Amplitude index
FWHM = 2            # FWHM index
LED_LOCATIONS = 3   # List of LED locations on PCD board for that wavelength
COMPORT = '\\.\COM5'

# Test Constants
ON_LED = 2


class MainWindow(QMainWindow, Ui_MainWindow):

    MAGIC_NUMBER = 0x3051E #Arbitrary number to identify FCU data files
    FILE_VERSION = 100 #Version of file format  

    # LED data [wavelength, maximum amplitude, FWHM, (LED locations)]
    LED_LIST = [########### Datasheet values ##############
                [350, 2, 15, (1, 3, 5)],   # 4
                [355, 2, 15, (8, 10)],   # 2             
                [360, 3, 15, (12, 14)],   # 2
                [365, 3, 15, (15, 16)],   # 2
                [370, 3.2, 15, (17,)], # 1
                [375, 5, 15, (19,)],   # 1
                [385, 4, 15, (23,)],   # 1
                [390, 4.8, 15, (24,)], # 1
                [395, 6, 15, (28,)],   # 1
                [400, 4.8, 15, (30,)], # 1
                [405, 15, 15, (2,)],  # 1
                [410, 6.9, 15, (7,)], # 1
                [415, 13.5, 15, (21,)],# 1
                [430, 20, 25, (26,)],  # 1
                [450, 20, 25, (4,)],  # 1
                [470, 4, 30, (6, 13)],   # 2
                [490, 2.4, 30, (11, 9)], # 2
                [505, 4, 30, (18,)],   # 1
                [525, 5.6, 30, (20,)], # 1
                [545, 8, 40, (22,)],   # 1
                [565, 2.5, 40, (31, 29, 27, 25, 0)],   # 5
                #[590, 4, 15],
                #[610, 4, 15],
                #[630, 5, 20],
                #[645, 5, 20]
                ############# Measured values ###############
                #[410.5, 1.1, 12.9, (2,)],
                #[411.6, 31.8, 15, (7,)],
                #[416.2, 30.4, 17, (21,)],
                #[425.23, 38.9, 18.3, (26,)],
                #[447, 4, 19.4, (4,)],
                #[465.8, 2.2, 32, (13,)],
                #[470.3, 13.8, 30.5, (6,)],
                #[486.56, 12.7, 23.3, (9, 11)],
                #[501.72, 2.6, 29.3, (18,)],
                #[519.8, 2.1, 29.2, (20,)],
                #[545.6, 1, 51, (22,)],
                #[565, 1, 30, (0, 25, 27, 29, 31)]
                #[408, 1, 15, (2,)],
                #[411, 19.4, 15, (7,)],
                #[415, 17.7, 17, (21,)],
                #[425, 22, 18, (26,)],
                #[447, 3.2, 20, (4,)],
                #[470, 3.6, 32, (6, 13)],
                #[489, 10, 23, (9, 11)],
                #[504, 1.6, 31, (18,)],
                #[520, 1.1, 31, (20,)],
                #[541, 1, 55, (22,)],
                #[565, 1, 30, (0, 25, 27, 29, 31)]
                ]

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)
        # Draw plots initially
        self.update_plot_1(clear=True)
        self.update_plot_2(clear=True)
        self.numGenLineEdit.setText("6")
        
        self.dirty = False
        self.filename = None
        self.fname = None
        # Create socket
        self.socket = QTcpSocket()
        self.nextBlockSize = 0 #Variable that will be used to determine whether we have received sufficient response data
        self.request = None #Request object containing request data

        self.ser = serial.Serial(COMPORT)
        self.ser.close()
        self.ser.open()
        
        self.points = [] #Create an empty list to contain spectral profile data [wavelength, amplitude]

        self.led_outputs = []            # Empty list to contain calculated LED outputs
        #self.target_wl = array([])
        #self.target_sd = array([])

        status = self.statusBar() #Creates status bar
        status.showMessage("Ready", 5000) #Displays "Ready" for 5 seconds at launch
        

        #This block creates actions in the menu bar using the createAction definition
        fileNewAction = self.createAction("&New...", self.fileNew,
                QKeySequence.New, "filenew",
                "Create a new spectral profile")
        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                QKeySequence.Open, "fileopen",
                "Open an existing spectral profile")
        fileSaveAction = self.createAction("&Save", self.fileSave,
                QKeySequence.Save, "filesave", "Save the spectral profile")
        fileSaveAsAction = self.createAction("Save &As...",
                self.fileSaveAs, icon="filesaveas",
                tip="Save the spectral profile using a new name")
        fileQuitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")
        editAddAction = self.createAction("&Add...", self.addPoint,
                "Ctrl+A", "editadd", "Add a point")
        editEditAction = self.createAction("&Edit...", self.editPoint,
                "Ctrl+E", "editedit", "Edit the highlighted point")
        editRemoveAction = self.createAction("&Remove...", self.removePoint,
                "Del", "editdelete", "Remove highlighted point")

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (fileNewAction, fileOpenAction,
                                      fileSaveAction, fileSaveAsAction))
        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolBar")
        self.addActions(editToolbar, (editAddAction, editEditAction, editRemoveAction))

        #Create the file menu and then add actions to it.
        fileMenu = self.menuBar().addMenu("&File")
        self.addActions(fileMenu, (fileNewAction, fileOpenAction,
                fileSaveAction, fileSaveAsAction, None, fileQuitAction))
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (editAddAction, editEditAction, editRemoveAction))

        self.updateTable()
        self.updateLEDTable()
        self.setWindowTitle("Facility Calibration Unit - Ideal")

        #Button connections
        self.connect(self.optimizePushButton, SIGNAL("clicked()"), self.callAlgorithm)
        self.connect(self.updateTargetButton, SIGNAL("clicked()"), self.updateTarget)
        self.connect(self.onPushButton, SIGNAL("clicked()"), self.turnLEDsOn)
        self.connect(self.offPushButton, SIGNAL("clicked()"), self.turnLEDsOff)
        self.connect(self.sendPushButton, SIGNAL("clicked()"), self.sendSerial)
        self.connect(self.testPushButton, SIGNAL("clicked()"), self.runTest)
        self.connect(self.singleLEDButton, SIGNAL("clicked()"), self.singleLEDMode)
        self.connect(self.maxPowerButton, SIGNAL("clicked()"), self.test_TurnOnAllMax)

        #Socket connections
##        self.connect(self.socket, SIGNAL("connected()"),
##                     self.sendRequest) # Send request once connection is established
##        self.connect(self.socket, SIGNAL("readyRead()"),
##                     self.readResponse) # Read response when there is data to read
##        self.connect(self.socket, SIGNAL("disconnected()"),
##                     self.serverHasStopped) # If connection disconnets, let user know
##        self.connect(self.socket, SIGNAL("error(QAbstractSocket::SocketError)"),
##                     self.serverHasError) # In case of error, inform user
##        self.connect(self.sendPushButton, SIGNAL("clicked()"),
##                     self.send) # When send button is clicked, send LED data.

        

    #This method is simply a helper method for creating new actions.
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    #Helper method to add actions to a menu or toolbar.
    #Target is menu or toolbar, and actions is a list of actions of <Nones>.
    #Can also add separators unlike built-in QWidget.addActions()
    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    #Dirty = unsaved changes
    #If main window is dirty, pop up message box asking user if they want to save changes
    def okToContinue(self):
        if self.dirty:
            #Pop-up with three choices: yes, no, and cancel.
            reply = QMessageBox.question(self,
                            "FCU - Unsaved Changes",
                            "Save unsaved changes?",
                            QMessageBox.Yes|QMessageBox.No|
                            QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False #Don't save, keep current image
            elif reply == QMessageBox.Yes:
                self.fileSave() #Save and exit
            #If no, don't save and exit.
        return True

##########################################################################################
################ DRAW TABLES #############################################################
##########################################################################################

    #This method draws the table and populates it with values from points (wavelength, amplitude)
    def updateTable(self, current=None):
        self.table.clear()
        self.table.setRowCount(len(self.points))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Wavelength (nm)", "Amplitude (mW)"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Don't allow edits
        self.table.setSelectionBehavior(QTableWidget.SelectRows) # Select whole row
        self.table.setSelectionMode(QTableWidget.SingleSelection) # Select one row at a time
        selected = None
        self.points.sort()
        for row, (wavelength, amplitude) in enumerate(self.points):
            item = QTableWidgetItem("%d" % wavelength)
            item.setTextAlignment(Qt.AlignCenter)
            if current is not None and current == id(row):
                selected = item
            item.setData(Qt.UserRole, QVariant(long(id(row))))
            self.table.setItem(row, 0, item) #void setItem ( int row, int column, QTableWidgetItem * item )
            item = QTableWidgetItem("%.2f" % amplitude)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, item)
        self.table.resizeColumnsToContents()
        if selected is not None:
            selected.setSelected(True)
            self.table.setCurrentItem(selected)
            self.table.scrollToItem(selected)

##########################################################################################
################ GUI ACTIONS #############################################################
##########################################################################################

    def updateLEDTable(self, current=None):
        self.LEDtable.clear()
        self.LEDtable.setRowCount(len(self.LED_LIST))
        self.LEDtable.setColumnCount(3)
        self.LEDtable.setHorizontalHeaderLabels(["Wavelength (nm)", "Amplitude (mW)", "   Duty Cycle   "])
        self.LEDtable.setEditTriggers(QTableWidget.NoEditTriggers) # Don't allow edits
        self.LEDtable.setSelectionBehavior(QTableWidget.SelectRows) # Select whole row
        self.LEDtable.setSelectionMode(QTableWidget.SingleSelection) # Select one row at a time
        selected = None
        self.points.sort()
        for row, (wavelength, amplitude, dummy1, dummy2) in enumerate(self.LED_LIST):
            item = QTableWidgetItem("%d" % wavelength)
            item.setTextAlignment(Qt.AlignCenter)
            if current is not None and current == id(row):
                selected = item
            item.setData(Qt.UserRole, QVariant(long(id(row))))
            self.LEDtable.setItem(row, 0, item) #void setItem ( int row, int column, QTableWidgetItem * item )
            if row < len(self.led_outputs):
                item = QTableWidgetItem("%.2f" % self.led_outputs[row])
                item.setTextAlignment(Qt.AlignCenter)
                self.LEDtable.setItem(row, 1, item)
                item = QTableWidgetItem("%.3f" % (self.led_outputs[row]/amplitude))
                item.setTextAlignment(Qt.AlignCenter)
                self.LEDtable.setItem(row, 2, item)
        self.LEDtable.resizeColumnsToContents()
        if selected is not None:
            selected.setSelected(True)
            self.LEDtable.setCurrentItem(selected)
            self.LEDtable.scrollToItem(selected)

    #Clears the data points and redraws the empty table
    def fileNew(self):
        if not self.okToContinue():
            return
        self.points = []
        self.led_outputs = []
        self.statusBar().clearMessage()
        self.updateTable()
        self.updateLEDTable()
        # Clear plot 1
        self.update_plot_1(clear=True)
        # Clear plot 2
        self.update_plot_2(clear=True)

    #Opens an existing file
    def fileOpen(self):
        if not self.okToContinue():
            return
        dir = os.path.dirname(self.filename) \
                if self.filename is not None else "."
        fname = unicode(QFileDialog.getOpenFileName(self,
                    "FCU - Load Spectral Profile", dir,
                    "Spectral Profile data files (*.mqb)"))
        if fname:
            self.filename = fname
            if self.loadQDataStream():
                self.updateStatus("Opened file %s" % self.filename)
                self.updateTable()
                self.updateLEDTable()
                self.updateTarget()
                self.updateCalculated()
            else:
                self.updateStatus("Failed to open %s" % self.filename)
                

    #Saves the current file
    def fileSave(self):
        if not self.points:
            return
        if self.filename is None:
            self.fileSaveAs()
        else:
            if self.saveQDataStream():
                self.updateStatus("Saved as %s" % self.filename)
                self.dirty = False
            else:
                self.updateStatus("Failed to save %s" % self.filename)

    #Save as new name
    def fileSaveAs(self):
        if not self.points:
            return
        fname = self.filename if self.filename is not None else "."
        fname = unicode(QFileDialog.getSaveFileName(self,
                    "FCU - Save Spectral Profile", fname,
                    "Spectral Profile data files (*.mqb)"))
        if fname:
            if "." not in fname:
                fname += ".mqb"
            self.filename = fname
            self.fileSave()


    def saveQDataStream(self):
        openfile = open(self.filename, 'w')
        openfile.write(repr((self.points, self.led_outputs)))
        openfile.close()
        return True

    def loadQDataStream(self):
        openfile = open(self.filename, 'r')
        self.points, self.led_outputs = eval(openfile.read())
        openfile.close()
        return True
            

    #Saves the data in binary format
##    def saveQDataStream(self):
##        error = None
##        fh = None
##        print "before try"
##        try:
##            print "before Qfile"
##            fh = QFile(self.filename)
##            openfile = open('pathtofile', 'w')
##            if not fh.open(QIODevice.WriteOnly):
##                raise IOError, unicode(fh.errorString())
##            stream = QDataStream(fh)
##            #stream.writeInt32(self.MAGIC_NUMBER)
##            #stream.writeInt32(self.FILE_VERSION)
##            #stream.setVersion(QDataStream.Qt_4_2)
##            #openfile.write('Debug file')
##            print self.points
##            print self.led_outputs
##            stream.writeQString(repr((self.points, self.led_outputs)))
##            openfile.write(repr((self.points, self.led_outputs)))
####            for wavelength, amplitude in self.points:
####                stream.writeInt16(repr(wavelength))
####                stream.writeDouble(repr(amplitude))
####                #openfile.write(str(wavelength))
####                #openfile.write(str(amplitude))
####                print [wavelength, amplitude]
##            #stream.writeInt32(int(600))
##            #print int(600)
##            #for amplitude in self.led_outputs:
##                #stream.writeDouble(amplitude)
##                #print amplitude
##        except (IOError, OSError), e:
##            error = "Failed to save: %s" % e
##            print error
##        finally:
##            print "before openfile.close"
##            openfile.close()
##            if fh is not None:
##                fh.close()
##            if error is not None:
##                return False, error
##            self.dirty = False
##            return True

    #Loads data from a binary file
##    def loadQDataStream(self):
##        error = None
##        fh = None
##        try:
##            fh = QFile(self.filename)
##            if not fh.open(QIODevice.ReadOnly):
##                raise IOError, unicode(fh.errorString())
##            stream = QDataStream(fh)
##            magic = stream.readInt32()
##            if magic != self.MAGIC_NUMBER:
##                raise IOError, "unrecognized file type"
##            version = stream.readInt32()
##            if version < self.FILE_VERSION:
##                raise IOError, "old and unreadable file format"
##            elif version > self.FILE_VERSION:
##                raise IOError, "new and unreadable file format"
##            stream.setVersion(QDataStream.Qt_4_2)
##            self.points = []
##            while not stream.atEnd():
##                wavelength = stream.readInt32()
##                if wavelength == 600:
##                    print "breakbreakbreakbreakbreakbreakbreakbreakbreakbreak"
##                    break
##                amplitude = stream.readDouble()
##                print [wavelength, amplitude]
##                self.points.append([wavelength,amplitude])
##            self.led_outputs = []
##            while not stream.atEnd():
##                self.led_outputs.append(stream.readDouble())
##        except (IOError, OSError), e:
##            error = "Failed to load: %s" % e
##        finally:
##            if fh is not None:
##                fh.close()
##            if error is not None:
##                return False, error
##            self.__dirty = False
##            return True

    #Updates the status to reflect actions or give information about actions
    #Updates the window title to relfect status of current work (file name and whether there are unsaved changes)
    def updateStatus(self, message):
        self.statusBar().showMessage(message, 5000)
        if self.filename is not None:
            self.setWindowTitle("FCU - %s[*]" % \
                                os.path.basename(self.filename))
        elif self.points:
            self.setWindowTitle("FCU - Unnamed[*]")
        else:
            self.setWindowTitle("FCU[*]")
        self.setWindowModified(self.dirty)

##########################################################################################
################ INPUT FUNCTIONS #########################################################
##########################################################################################

    def addPoint(self):
        form = addpointdlg.AddPointDlg(self.points, None, self)
        if form.exec_():
            self.points = form.points
            self.updateTable()

    def removePoint(self):
        point = self.currentPoint()
        if point is not None:
            wavelength = " %d" % point[WAVELENGTH]
            amplitude = " %d" % point[AMPLITUDE]
            if QMessageBox.question(self,
                        "FCU - Delete Point",
                        "Delete Point (%s, %s)" % (wavelength, amplitude),
                        QMessageBox.Yes|QMessageBox.No) == \
                    QMessageBox.Yes:
                self.points.remove(point)
                self.updateTable()

    def editPoint(self):
        point = self.currentPoint()
        if point is not None:
            form = addpointdlg.AddPointDlg(self.points, point, self)
            if form.exec_():
                self.points = form.points
                self.updateTable()

    def currentPoint(self):
        row = self.table.currentRow()
        if row > -1:
            wavelength = int(self.table.item(row, 0).text())
            amplitude = float(self.table.item(row,1).text())     
            return [wavelength, amplitude]
        return None

##########################################################################################
################ NETWORK FUNCTIONS SECTION ###############################################
##########################################################################################

    def send(self):
        for i, amplitude in enumerate(self.led_outputs):
            duty_cycle = int(round(amplitude / self.LED_LIST[i][AMPLITUDE] * 4096))
            self.request = QByteArray() #Create a request QByteArray()
            stream = QDataStream(self.request, QIODevice.WriteOnly) #Create a data stream
            stream.setVersion(QDataStream.Qt_4_2) #Set version
            #stream.writeUInt16(0) #Write number of bytes occupied by request, 0 = don't know
            #stream << action << LED #Write data to stream
            stream << duty_cycle
            if self.socket.isOpen():
                self.socket.close()
            self.socket.connectToHost(HOST, PORT)

    def sendRequest(self):
        self.nextBlockSize = 0 #Sets the next block size to be 0 for response
        self.socket.write(self.request) #Writes request byte array to socket
        self.request = None #Once data is written, request is set to None

    def readResponse(self):
        pass

    def serverHasStopped(self):
        self.socket.close()
        self.updateStatus("Server has stopped.")

    def serverHasError(self, error):
        self.socket.close()
        self.updateStatus("Sever has error.")


##########################################################################################
################ SERIAL FUNCTIONS SECTION ################################################
##########################################################################################
# Commands
# 0 = 0x00 = Turn LEDs off (1 byte)
# 1 = 0x20 = Turn LEDs on - do this third (1 byte)
# 2 = 0x40 = Sending pulse width modulation data - do this first (3 bytes)
# 3 = 0x60 = Send data to LEDs - do this second (1 byte)
# Baud rate = 

    def sendSerial(self):
        try:
            self.sendPWMData()
            self.loadPWMData()
        except (IOError, OSError), e:
            self.updateStatus("Failed to send: %s" % e)

    def sendPWMData(self):
        if self.led_outputs is not None:
            for i, (wavelength, max_amp, FWHM, led_locations) in enumerate(self.LED_LIST):
                if wavelength == 565:
                    duty_cycle = 1.0
                else:
                    duty_cycle = (float(self.led_outputs[i])/max_amp)/len(led_locations)
                PWM_value = int(round(duty_cycle * 4095))
                for location in led_locations:
                    #print PWM_value
                    #print duty_cycle
                    command = 0x40 # Set command to send PWM data
                    command = command | location # Set LED number
                    self.ser.write(chr(command))
                    self.ser.write(chr(PWM_value / 256))
                    self.ser.write(chr(PWM_value % 256))


##        # Make left LED bright
##        self.ser.write(chr(0x5E))
##        self.ser.write(chr(0x0D))
##        self.ser.write(chr(0x7D))
##
##        # Make right LED dim
##        self.ser.write(chr(0x5F))
##        self.ser.write(chr(0x00))
##        self.ser.write(chr(0x00))


    def loadPWMData(self):
        #command = int(0x60) # Set command to load data into LEDs
        #print "Command: %X" % (command)
        command = chr(0x60)
        self.ser.write(command)

    def turnLEDsOn(self):
        try:
            #command = int(0x20) # Set command to turn LEDs on
            #print "Command: %X" % (command)
            command = chr(0x20)
            self.ser.write(command)
        except (IOError, OSError), e:
            self.updateStatus("Failed to turn LEDs on: %s" % e)

    def turnLEDsOff(self):
        try:
            #command = int8(0x00) # Set command to turn LEDs off
            #print "Command: %X" % (command)
            command = chr(0x00)
            self.ser.write(command)
        except (IOError, OSError), e:
            self.updateStatus("Failed to turn LEDs off: %s" % e)

    def runTest(self):
        try:
            command = chr(0x80)
            self.ser.write(command)
        except (IOError, OSError), e:
            self.updateStatus("Failed to run test: %s" % e)

    def test_TurnOnAllMax(self):
        for i, (wavelength, amplitude, FWHM, led_locations) in enumerate(self.LED_LIST):
            PWM_value = 4095
            for location in led_locations:
                #print location
                command = 0x40
                command = command | location
                self.ser.write(chr(command))
                self.ser.write(chr(PWM_value / 256))
                self.ser.write(chr(PWM_value % 256))
        self.loadPWMData()
        self.turnLEDsOn()

    def test_TurnOneOn(self):
        for i, (wavelength, amplitude, FWHM, led_locations) in enumerate(self.LED_LIST):
            if i == ON_LED:
                PWM_value = 4095
            else:
                PWM_value = 0
            for location in led_locations:
                command = 0x40
                command = command | location
                self.ser.write(chr(command))
                self.ser.write(chr(PWM_value / 256))
                self.ser.write(chr(PWM_value % 256))
        self.loadPWMData()
        self.turnLEDsOn()

    def test_TurnInCircle(self):
        for i in range(0,5):
            j = 0
            while j < 32:
                for (wavelength, amplitude, FWHM, led_locations) in self.LED_LIST:
                    for location in led_locations:
                        if location == j:
                            PWM_value = 4095
                        else:
                            PWM_value = 0
                        #print location
                        command = 0x40
                        command = command | location
                        self.ser.write(chr(command))
                        self.ser.write(chr(PWM_value / 256))
                        self.ser.write(chr(PWM_value % 256))
                self.loadPWMData()
                self.turnLEDsOn()
                j = j + 1
                time.sleep(.1)

    def singleLEDMode(self):        
        for (wavelength, amplitude, FWHM, led_locations) in self.LED_LIST:
            for location in led_locations:
                if location == self.ledNumSpinBox.value():
                    PWM_value = int(round((self.dutyCycleSpinBox.value() / 100.0) * 4095))
                elif location == self.led2SpinBox.value():
                    PWM_value = int(round((self.dutyCycle2SpinBox.value() / 100.0) * 4095))
                else:
                    PWM_value = 0
                command = 0x40
                command = command | location
                self.ser.write(chr(command))
                self.ser.write(chr(PWM_value / 256))
                self.ser.write(chr(PWM_value % 256))
        self.loadPWMData()
        self.turnLEDsOn()
            
                

##########################################################################################
################ ALGORITHM FUNCTIONS #####################################################
##########################################################################################

    def callAlgorithm(self):
        # Clear plot 2
        self.update_plot_2(clear=True)
        # Update status
        self.statusLabel.setText("Current status... running optimization")
        self.updateStatus("Optimization begun!")
        led_list_temp = []
        for (wavelength, dummy1, fwhm, dummy2) in self.LED_LIST:
            led_list_temp.append([wavelength, fwhm])

        led_array = array(led_list_temp, float) # Create an LED array to pass to algorithm

        wl_min = float(self.points[0][WAVELENGTH])     # Determine minimum wavelength from input points
        wl_incr = 2.0                             # Set wavelength increment for distributions
        wl_max = float(self.points[len(self.points) - 1][WAVELENGTH] + wl_incr)  # Determine maximum wavelength from input points

        amp_max = 0
        for (wavelength, amplitude) in self.points:
            if amplitude > amp_max:
                amp_max = amplitude
        
        # Determine mode
        # 1-linear flat, 2-linear sloped, 3-not linear
        addpoint = False
        if len(self.points) < 2:
            return
        if len(self.points) == 2:
            if self.points[0][AMPLITUDE] == self.points[1][AMPLITUDE]:
                mode = 1
            else:
                mode = 2
        elif len(self.points) == 3:
            addpoint = True
            mode = 3
        else:
            mode = 3

        wl = arange(wl_min, wl_max, wl_incr)    # Array of all wavelengths to be plotted
        sd_target = zeros_like(wl)              # Initialize target brightness distribution
        sd = zeros_like(wl)                 # Initialize theoretical optimized distribution

        # Calculate target distribution
        index = 0
        while index < len(sd_target):
            if mode == 1:
                sd_target[index] = self.points[0][AMPLITUDE]
            elif mode == 2:
                endpoint_1 = self.points[0][AMPLITUDE]
                endpoint_2 = self.points[1][AMPLITUDE]
                m = (endpoint_1 - endpoint_2) / (wl_min - wl_max)
                b = endpoint_1 - m * wl_min
                sd_target[index] = m * wl[index] + b
            elif mode == 3:
                x_pts_temp = []
                y_pts_temp = []
                points = list(self.points)
                # Spline requires 4 points, so if only 3, then add fourth and fifth point by averaging first and last two points.
                if addpoint:
                    wavelength = (self.points[0][WAVELENGTH] + self.points[1][WAVELENGTH]) / 2
                    amplitude = (self.points[0][AMPLITUDE] + self.points[1][AMPLITUDE]) / 2
                    points.append([wavelength, amplitude])
                    length = len(self.points)
                    wavelength = (self.points[length - 2][WAVELENGTH] + self.points[length - 1][WAVELENGTH]) / 2
                    amplitude = (self.points[length - 2][AMPLITUDE] + self.points[length - 1][AMPLITUDE]) / 2
                    points.append([wavelength, amplitude])
                    points.sort()
                for (wavelength, amplitude) in points:
                    x_pts_temp.append(wavelength)
                    y_pts_temp.append(amplitude)
                x_points = array(x_pts_temp, float)
                y_points = array(y_pts_temp, float)
                spl_rep = spl.splrep(x_points, y_points, s=0)
                sd_target = spl.splev(wl, spl_rep, der=0)
                break
            index = index + 1

        self.target_wl = wl
        self.target_sd = sd_target

##        # Apply scaling factor for GA
##        sd_target_GA = zeros_like(sd_target)
##        for i in range(0, len(sd_target) - 1):
##            sd_target_GA[i] = sd_target[i] / amp_max

        sd, self.led_outputs = self.fn_ga_algorithm(led_array, sd_target, wl_min, wl_incr, wl_max)
##        # Undo scaling factor
##        for i in range(0, len(sd) - 1):
##            sd[i] = sd[i] * amp_max
##        for i in range(0, len(self.led_outputs) - 1):
##            self.led_outputs[i] = self.led_outputs[i] * amp_max
            
        self.update_plot_1(wl_min, wl_max - wl_incr, 0, amp_max + 1, wl, sd, clear=False)
        self.updateLEDTable()

    def fn_ga_algorithm(self, led_list, sd_target, wl_min, wl_incr, wl_max):           
        amp_max = 0
        for (wavelength, amplitude) in self.points:
            if amplitude > amp_max:
                amp_max = amplitude
        pop_size = 100		# Population size, must be a multiple of 4
        num_gen = int(self.numGenLineEdit.text())	# Number of generations
        mut_rate = 0.2		# Mutation probability
        mut_max_init = 0.3		# Initial maximum allowable mutation
        led_qty = len(led_list)	# Number of genes in each chromosome
        
        # Data arrays
        wl = arange(wl_min, wl_max, wl_incr)		  # Incremental wavelength values
        sd = zeros_like(wl)                                   # Computed brightness distribution
        current_gen = zeros((pop_size, led_qty), dtype=float)
        next_gen = zeros((pop_size, led_qty), dtype=float)
        fitness = zeros(pop_size, dtype=float)

        gen_numbers = []
        costs = []

        
        # Create an initial population with chromosomes containing a random brightness
        # value in the range [0.0,2.5] for each LED.
        for j in range(0, pop_size):
            for k in range(0, led_qty):
                current_gen[j,k] = rnd.random()
        
        for n in range(num_gen):
            self.dataTextBrowser.append("Generation %d:" % n)
            self.repaint()
            # Step through the chromosomes in a population, calculate the spectral
            # distribution and fitness and add a plot of the distribution to an
            # existing figure.
            j = 0
            for chromosome in current_gen:
                    # Compute the spectral distribution for the chromosome
                    sd = fn_distribution(chromosome, wl, led_list)
                    # Use the result and a target distribution to compute a fitness
                    # parameter for the jth chromosome
                    fitness[j] = fn_fitness(sd, sd_target)
                    sd = zeros_like(wl)             # Re-initialize the distribution
                    j = j + 1

            # Sort the current population by descending fitness value (increasing
            # cost).
            sorted = fn_sort_by_fitness(current_gen, fitness, pop_size, led_qty)
            current_gen = sorted['pop']
            fitness = sorted['fit']

            gen_numbers.append(n)
            costs.append(fitness[0])
            self.update_plot_2(0, num_gen - 1, 0, costs[0], gen_numbers, costs, clear=False)
            self.dataTextBrowser.append("Cost: %f" % fitness[0])
            self.repaint()

            # Select the mating pairs from the surviving chromosomes
            mating_pairs = fn_pair_selection(fitness, pop_size, current_gen, sd, wl)

            # Generate offspring from mating pairs using one of the crossover schemes.
            offspring = zeros((pop_size, led_qty), dtype=float)
            offspring = fn_crossover_1(current_gen, mating_pairs, pop_size, led_qty)

            # Replace nonsurviving chromosomes with the new offspring to create a next
            # generation population.
            for j in range(pop_size/2):
                    next_gen[j] = current_gen[j]
                    next_gen[pop_size/2 + j] = offspring[j]

            # Introduce mutations into the next generation population reducing the
            # maximum allowable mutation size in later generations as the results
            # begin to converge.
            num_mut = int(round(pop_size * led_qty * mut_rate))
            mut_coord_list = fn_mut_selection(num_mut, pop_size, led_qty)
            mut_max = fn_mut_adj( n )
            for coord in mut_coord_list:
                mut_dir = int(round(rnd.random()))
                if mut_dir == 0:
                    mut_dir = -1
                else:
                    mut_dir = 1
                value = next_gen[coord[0], coord[1]]
                
                mut_value = value + mut_dir * mut_max * rnd.random()
                if mut_value < 0.0:
                    mut_value = 0.0
                elif mut_value > 1.0:
                    mut_value = 1.0
                next_gen[coord[0], coord[1]] = mut_value

            # Print current generation
            self.update_plot_1(wl_min, wl_max - wl_incr, 0, amp_max + 1, wl, sd_target, clear=True)
            self.update_plot_1(wl_min, wl_max - wl_incr, 0, amp_max + 1, wl, fn_distribution(current_gen[0], wl, led_list), clear=False)

            # Prepare for the next iteration
            current_gen = next_gen

            # Update Status
            self.updateStatus("Finished generation %d!" % n)
        
        self.statusLabel.setText("Current status... optimization complete")
        self.updateStatus("Optimization complete!")
        return fn_distribution(current_gen[0], wl, led_list), current_gen[0]


##########################################################################################
################ PLOTTING FUNCTIONS ######################################################
##########################################################################################
       

    # Updates plots one. Pass in the set of x-y points and limits to plot
    # and whether or not to clear the plot before displaying them.
    def update_plot_1(self, x_min=350, x_max=550, y_min=0, y_max=4, x_points=None, y_points=None, clear=False):
        if clear:
            self.plot_1.canvas.ax.clear()
            self.plot_1.canvas.ax.set_xlabel('Wavelength (nm)')#, size='x-large')
            self.plot_1.canvas.ax.set_ylabel('Amplitude (mW)')#, size='x-large')
            self.plot_1.canvas.ax.set_title('Target and Calculated Profiles')#, size='x-large')
            self.plot_1.canvas.ax.xaxis.grid(True, which='major')
            self.plot_1.canvas.ax.yaxis.grid(True, which='major')
            self.plot_1.canvas.draw()

        if x_points is not None and y_points is not None:
            self.plot_1.canvas.ax.plot(x_points, y_points)
            self.plot_1.canvas.ax.set_xlim([x_min, x_max])
            self.plot_1.canvas.ax.set_ylim([y_min, y_max])
            self.plot_1.canvas.draw()
            self.repaint()


    # Updates plots two. Pass in the set of x-y points and limits to plot
    # and whether or not to clear the plot before displaying them.
    def update_plot_2(self, x_min=350, x_max=550, y_min=0, y_max=4, x_points=None, y_points=None, clear=False):
        if clear:
            self.plot_2.canvas.ax.clear()
            self.plot_2.canvas.ax.set_xlabel('Generation')#, size='x-large')
            self.plot_2.canvas.ax.set_ylabel('Squared Error')#, size='x-large')
            self.plot_2.canvas.ax.set_title('Cost Function')#, size='x-large')
            self.plot_2.canvas.ax.xaxis.grid(True, which='major')
            self.plot_2.canvas.ax.yaxis.grid(True, which='major')
            self.plot_2.canvas.draw()

        if x_points is not None and y_points is not None:
            self.plot_2.canvas.ax.plot(x_points, y_points)
            self.plot_2.canvas.ax.set_xlim([x_min, x_max])
            self.plot_2.canvas.ax.set_ylim([y_min, y_max])
            self.plot_2.canvas.draw()
            self.repaint()
            
        
    def updateTarget(self):
        wl_min = float(self.points[0][WAVELENGTH])     # Determine minimum wavelength from input points
        wl_incr = 2.0                             # Set wavelength increment for distributions
        wl_max = float(self.points[len(self.points) - 1][WAVELENGTH] + wl_incr)  # Determine maximum wavelength from input points

        amp_max = 0
        for (wavelength, amplitude) in self.points:
            if amplitude > amp_max:
                amp_max = amplitude
        
        # Determine mode
        # 1-linear flat, 2-linear sloped, 3-not linear
        addpoint = False
        if len(self.points) < 2:
            return
        if len(self.points) == 2:
            if self.points[0][AMPLITUDE] == self.points[1][AMPLITUDE]:
                mode = 1
            else:
                mode = 2
        elif len(self.points) == 3:
            addpoint = True
            mode = 3
        else:
            mode = 3

        wl = arange(wl_min, wl_max, wl_incr)    # Array of all wavelengths to be plotted
        sd_target = zeros_like(wl)              # Initialize target brightness distribution
        sd = zeros_like(wl)                 # Initialize theoretical optimized distribution

        # Calculate target distribution
        index = 0
        while index < len(sd_target):
            if mode == 1:
                sd_target[index] = self.points[0][AMPLITUDE]
            elif mode == 2:
                endpoint_1 = self.points[0][AMPLITUDE]
                endpoint_2 = self.points[1][AMPLITUDE]
                m = (endpoint_1 - endpoint_2) / (wl_min - wl_max)
                b = endpoint_1 - m * wl_min
                sd_target[index] = m * wl[index] + b
            elif mode == 3:
                x_pts_temp = []
                y_pts_temp = []
                points = list(self.points)
                # Spline requires 4 points, so if only 3, then add fourth and fifth point by averaging first and last two points.
                if addpoint:
                    wavelength = (self.points[0][WAVELENGTH] + self.points[1][WAVELENGTH]) / 2
                    amplitude = (self.points[0][AMPLITUDE] + self.points[1][AMPLITUDE]) / 2
                    points.append([wavelength, amplitude])
                    length = len(self.points)
                    wavelength = (self.points[length - 2][WAVELENGTH] + self.points[length - 1][WAVELENGTH]) / 2
                    amplitude = (self.points[length - 2][AMPLITUDE] + self.points[length - 1][AMPLITUDE]) / 2
                    points.append([wavelength, amplitude])
                    points.sort()
                for (wavelength, amplitude) in points:
                    x_pts_temp.append(wavelength)
                    y_pts_temp.append(amplitude)
                x_points = array(x_pts_temp, float)
                y_points = array(y_pts_temp, float)
                spl_rep = spl.splrep(x_points, y_points, s=0)
                sd_target = spl.splev(wl, spl_rep, der=0)
                break
            index = index + 1
        
        self.update_plot_1(wl_min, wl_max - wl_incr, 0, amp_max + 1, wl, sd_target, clear=True)
        
    def updateCalculated(self):
        wl_min = float(self.points[0][WAVELENGTH])     # Determine minimum wavelength from input points
        wl_incr = 2.0                             # Set wavelength increment for distributions
        wl_max = float(self.points[len(self.points) - 1][WAVELENGTH] + wl_incr)  # Determine maximum wavelength from input points
        wl = arange(wl_min, wl_max, wl_incr)    # Array of all wavelengths to be plotted

        amp_max = 0
        for (wavelength, amplitude) in self.points:
            if amplitude > amp_max:
                amp_max = amplitude

        led_list_temp = []
        for (wavelength, dummy1, fwhm, dummy2) in self.LED_LIST:
            led_list_temp.append([wavelength, fwhm])

        led_list = array(led_list_temp, float) # Create an LED array to pass to algorithm

        self.update_plot_1(wl_min, wl_max - wl_incr, 0, amp_max + 1, wl, fn_distribution(self.led_outputs, wl, led_list), clear=False)
        


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("HETDEX")
    app.setOrganizationDomain("hetdex.org")
    app.setApplicationName("Facility Calibration Unit")
    app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()


main()
