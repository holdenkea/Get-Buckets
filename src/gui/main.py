import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QGraphicsRectItem,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPathItem,
    QLineEdit, QLabel
)

from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer, QEvent, pyqtSignal

import pyqtgraph as pg
import numpy as np

from uwb_reader import Data_Reader_Thread
import pose_classifier as pc
import beam_reader as br
import gui_overlay as go

import threading
import queue

import time
import os

import random 

class MyApp(QMainWindow):

    # signal for gui overlay
    set_color_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("UWB Pose Tracker UI")
        self.setGeometry(100, 100, 800, 800)

        # Central widget & main horizontal layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # === Left panel with buttons ===
        self.button_panel = QWidget()
        button_layout = QVBoxLayout()
        self.button_panel.setLayout(button_layout)

        # --- Buttons ---
        self.begin_tracking_button = QPushButton("Begin Workout")
        self.stop_button = QPushButton("Stop Workout")
        self.save_button = QPushButton("Save Run")

        # Connect buttons to functions
        self.begin_tracking_button.clicked.connect(self.begin_tracking)
        self.stop_button.clicked.connect(self.stop_run)
        self.save_button.clicked.connect(self.save_run)

        # wifi label fields
        self.ip_input_label = QLabel("ESP32 IP Address:")
        self.ip_input_field = QLineEdit()
        self.ip_input_field.setPlaceholderText("xxx.xxx.x.xx")

        # buttons added here
        button_layout.addWidget(self.ip_input_label)
        button_layout.addWidget(self.ip_input_field)
        button_layout.addWidget(self.begin_tracking_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.save_button)

        # Push everything to the top
        button_layout.addStretch()

        # === Right panel with the plot ===
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')  # Optional: white background

        # Add both panels to the main layout
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setAspectLocked(True)  # Keep correct proportions
        
        # visible coordinate range in plot
        self.plot_widget.setXRange(0, 50)
        self.plot_widget.setYRange(0, 47)
        
        # test coordinate range 3x3 feet
        #self.plot_widget.setXRange(0, 10)
        #self.plot_widget.setYRange(0, 10)
        
        self.plot_widget.disableAutoRange()

        main_layout.addWidget(self.button_panel, stretch=1)
        main_layout.addWidget(self.plot_widget, stretch=4)

        # draw court lines
        self.draw_court()  

        # scatter plot item for showing one point at a time
        self.scatter_item = pg.ScatterPlotItem()
        self.plot_widget.addItem(self.scatter_item)

        # scatter plot item for shooting points
        self.scatter_item_shooting = pg.ScatterPlotItem(symbol='o', size=10, pen=pg.mkPen(color='green'), brush=pg.mkBrush(color='green'))
        self.plot_widget.addItem(self.scatter_item_shooting)

        # initialize data reader to None until the button is pressed
        self.data_reader_thread = None

        # initialize stop request
        self.stop_requested = False

        # queue to hold both position and action information
        self.position_action_queue = queue.Queue()

        # initialize last shot time
        self.last_shot_time = 0
        
        self.show()

        # OVERLAY code
        # connect signal to lambda function so that in set_gui_color,
        # the gui can be set to clear after a delay WITHOUT disrupting other threads
        # SINCE QTimer.singleShot can only be called from the main thread
        self.set_color_signal.connect(self.set_gui_color)

        # color overlay from gui_overlay
        self.overlay = go.ColorOverlay(self.centralWidget())
        self.overlay.resize(self.centralWidget().size())
        self.overlay.raise_()
        self.overlay.show()

        # tracks window resizing
        self.centralWidget().installEventFilter(self)

        self.current_color = 'CLEAR'

    def eventFilter(self, source, event):
        if event.type() == QEvent.Resize and source == self.centralWidget():
            self.overlay.resize(source.size())
        return super().eventFilter(source, event)
###########################################################################################
#                               Save Run Function(s)                                      #
###########################################################################################

    def save_run(self):
        print("Save Run button clicked!")

###########################################################################################
#                              Stop Run Function(s)                                       #
###########################################################################################

    # stops the data reader and the cv2
    def stop_run(self):
        print("Stop button clicked!")

        self.stop_requested = True

        if self.data_reader_thread:
            self.data_reader_thread.stop()
            self.data_reader_thread = None

        # re enable buttons after stopping
        #self.save_button.setEnabled(True)
        self.begin_tracking_button.setEnabled(True)

###########################################################################################
#                               Tracking Function(s)                                      #
###########################################################################################
    def begin_tracking(self):        
        # create folder to store workout information
        self.current_workout_txt = self.create_workout_folder()

        self.stop_requested = False

        # Start the data reading thread
        if not self.data_reader_thread:

            # ip address from input field in UI
            esp_32_ip = self.ip_input_field.text().strip()
            print(f"STRIPPED IP IS {esp_32_ip}")
            
            if not esp_32_ip:
                print("Please enter a valid ESP32 IP address.")
                return

            self.br = br.Beam_Reader(esp_32_ip)

            # opens a uwb reader thread which consistently updates position in gui
            self.data_reader_thread = Data_Reader_Thread('./src/uwb/python/toy.txt', use_serial=False)
            # self.data_reader_thread = Data_Reader_Thread(file_path=None, use_serial=True)
            self.data_reader_thread.new_signal.connect(self.update_position)
            self.data_reader_thread.start()

            # opens a pose classifier thread to open webcam as input and outputs the video
            self.pose_classifier = pc.Pose_Classifier(self, self.data_reader_thread, self.position_action_queue)
            classifier_thread = threading.Thread(target=self.pose_classifier.output_video_with_prediction)
            classifier_thread.start()


    # tracking helper function to plot position
    def update_position(self, position):

        # duration of shooting window (seconds)
        shot_duration = 4

        # update the UI with the new position
        print(f"Tag position: {position}")

        if not self.position_action_queue.empty():

            # get current action from queue
            action, position_at_action = self.position_action_queue.get()
            print(f"CURRENT ACTION IS {action, position_at_action}")
            
            current_time = time.time()
            if action == "shooting":
                
                # set gui to yellow
                self.set_gui_color('YELLOW')

                # tune the shot delay here if needed in case shots tracked across multiple windows
                if current_time - self.last_shot_time > shot_duration:
                    print("Shooting detected")

                    # call helper function to check shot status in the background, keeping update position running
                    threading.Thread(target=self.shot_check_background, args=(position_at_action, shot_duration), daemon=True).start()

                    self.last_shot_time = current_time

                else: 
                    print("ignored duplicate shooting action")

            
        self.scatter_item.clear()
        self.scatter_item.addPoints([position[0]], [position[1]])

    def shot_check_background(self, position_at_action, shot_duration):

        # run update loop in the background, will set class variable to true if beam was broken
        # stays at false if entire duration is exhausted
        self.br.update_loop(shot_duration)

        # call function to check if shot is made (class variable initialize to true)
        shot_made = self.br.get_shot_status()

        if shot_made:
            print("SHOT MADE")

            # set gui to green
            self.set_color_signal.emit('GREEN')

            self.scatter_item_shooting.addPoints([position_at_action[0]], [position_at_action[1]], 
                                                 symbol='o', size=10, pen=pg.mkPen(color='green'), brush=pg.mkBrush(color='green'))
        else:
            print("SHOT MISSED")

            # set gui to red
            self.set_color_signal.emit('RED')

            self.scatter_item_shooting.addPoints([position_at_action[0]], [position_at_action[1]], 
                                                 symbol='x', size=10, pen=pg.mkPen(color='red'), brush=pg.mkBrush(color='red'))
        # add point and make or miss to text file
        with open(self.current_workout_txt, "a") as f:
            print(f"ADDING shot made: {shot_made}, TO FILE")
            f.write(f"Position: ({[position_at_action[0]], [position_at_action[1]]}), Make: {shot_made}\n")

        #return shot_made 
    
    def create_workout_folder(self):

        # if /src/gui/workouts doesn't exist, create folder called workouts
        workouts_path = os.path.join("src", "gui", "workouts")

        if not os.path.exists(workouts_path):
            os.makedirs(workouts_path)
            print("creating workouts folder")

        # count number of existing workout folders (filtering only directories starting with "workout_")
        existing_folders = [f for f in os.listdir(workouts_path) 
                            if os.path.isdir(os.path.join(workouts_path, f)) and f.startswith("workout_")]
        num_workouts = len(existing_folders)
 
        # create folder called workout_{size + 1}
        workout_name = f"workout_{num_workouts + 1}"
        current_workout_path = os.path.join(workouts_path, workout_name)
        os.makedirs(current_workout_path)

        # create text file for current workout
        current_workout_txt = os.path.join(current_workout_path, f"{workout_name}.txt")
        with open(current_workout_txt, "w") as f:
            f.write("")  # Create empty file

        print(f"Created {current_workout_txt}")
        
        # return path to workout text file
        return current_workout_txt

    def set_gui_color(self, selected_color):
        if selected_color == 'RED':
            self.overlay.set_overlay_color(QColor(255, 0, 0, 100))
            self.current_color = 'RED'

            print("SETTING OVERLAY TO CLEAR")
            QTimer.singleShot(500, lambda: self.set_color_signal.emit('CLEAR'))
            print("OVERLAY SET TO CLEAR")
            
        elif selected_color == 'GREEN':
            self.overlay.set_overlay_color(QColor(0, 255, 0, 100)) 
            self.current_color = 'GREEN'

            print("SETTING OVERLAY TO CLEAR")
            QTimer.singleShot(500, lambda: self.set_color_signal.emit('CLEAR'))
            print("OVERLAY SET TO CLEAR")

        elif selected_color == 'YELLOW':
            self.overlay.set_overlay_color(QColor(255, 255, 0, 100)) 
            self.current_color = 'YELLOW'

        elif selected_color == 'CLEAR':
            self.overlay.set_overlay_color(QColor(0, 0, 0, 0))
            self.current_color = 'CLEAR'
        
###########################################################################################
#                             Court Drawing Function(s)                                   #
###########################################################################################
 
    def draw_court(self):
        # half court, (x, y, width, height)
        boundary = QGraphicsRectItem(0, 0, 50, 47)
        boundary.setPen(pg.mkPen('black', width=2))
        self.plot_widget.addItem(boundary)

        # sidelines that extend past half court, (x1, y1, x2, y2)
        left_sideline = QGraphicsLineItem(0, 47 , 0, 53)
        left_sideline.setPen(pg.mkPen('black', width=2))
        right_sideline = QGraphicsLineItem(50, 47, 50, 53)
        right_sideline.setPen(pg.mkPen('black', width=2))

        self.plot_widget.addItem(left_sideline)
        self.plot_widget.addItem(right_sideline)

        # center circle, x,y (bottom left corner of bounding box),width, height
        center_circle = QGraphicsEllipseItem(19, 41, 12, 12)
        center_circle.setPen(pg.mkPen('black', width=2))
        self.plot_widget.addItem(center_circle)

        # free throw circle
        # circle bounding box ((x,y of bottom left point), width, height)
        bb_free_throw_circle = pg.QtCore.QRectF(19, 13, 12, 12)

        # bottom half (solid)
        bottom_half = pg.QtGui.QPainterPath()
        bottom_half.arcMoveTo(bb_free_throw_circle, 0)
        bottom_half.arcTo(bb_free_throw_circle, 0, 180)  
        bottom_item  = QGraphicsPathItem(bottom_half)
        bottom_item .setPen(pg.mkPen('black', width=2, style=pg.QtCore.Qt.DotLine))
        self.plot_widget.addItem(bottom_item)

        # top half (dotted)
        top_half = pg.QtGui.QPainterPath()
        top_half.arcMoveTo(bb_free_throw_circle, 180)
        top_half.arcTo(bb_free_throw_circle, 180, 180) 
        top_item  = QGraphicsPathItem(top_half)
        top_item .setPen(pg.mkPen('black', width=2))
        self.plot_widget.addItem(top_item)

        # free throw vertical lines
        left_freethrow = QGraphicsLineItem(19, 0 , 19, 19)
        left_freethrow.setPen(pg.mkPen('black', width=2))
        right_freethrow = QGraphicsLineItem(31, 0, 31, 19)
        right_freethrow.setPen(pg.mkPen('black', width=2))

        self.plot_widget.addItem(left_freethrow)
        self.plot_widget.addItem(right_freethrow)

        # free throw line
        freethrow_line = QGraphicsLineItem(19, 19, 31, 19)
        freethrow_line.setPen(pg.mkPen('black', width=2))
        self.plot_widget.addItem(freethrow_line)

        # outer free throw lines
        outer_left_freethrow = QGraphicsLineItem(17, 0 , 17, 19)
        outer_left_freethrow.setPen(pg.mkPen('black', width=2))
        outer_right_freethrow = QGraphicsLineItem(33, 0, 33, 19)
        outer_right_freethrow.setPen(pg.mkPen('black', width=2))

        self.plot_widget.addItem(outer_left_freethrow)
        self.plot_widget.addItem(outer_right_freethrow)

        left_freethrow_extended = QGraphicsLineItem(17, 19 , 19, 19)
        left_freethrow_extended.setPen(pg.mkPen('black', width=2))
        right_freethrow_extended = QGraphicsLineItem(31, 19, 33, 19)
        right_freethrow_extended.setPen(pg.mkPen('black', width=2))

        self.plot_widget.addItem(left_freethrow_extended)
        self.plot_widget.addItem(right_freethrow_extended)

        # backboard and hoop components
        # backboard
        backboard = QGraphicsLineItem(22, 4, 28, 4)
        backboard.setPen(pg.mkPen('black', width=2))
        self.plot_widget.addItem(backboard)

        # hoop
        hoop = QGraphicsEllipseItem(24.25, 4, 1.5, 1.5)
        hoop.setPen(pg.mkPen('black', width=2))
        self.plot_widget.addItem(hoop)

        # three-point components 
        # left and right three point lines
        left_threepoint = QGraphicsLineItem(3, 0 , 3, 14)
        left_threepoint.setPen(pg.mkPen('black', width=2))
        right_threepoint = QGraphicsLineItem(47, 0, 47, 14)
        right_threepoint.setPen(pg.mkPen('black', width=2))

        self.plot_widget.addItem(left_threepoint)
        self.plot_widget.addItem(right_threepoint)

        # three-point arc (relative to center of hoop)
        radius = 23.75
        hoop_center_x = 25
        hoop_center_y = 4.75

        # convert arc x-positions to angles using inverse cosine
        angle1 = np.degrees(np.arccos((3 - hoop_center_x) / radius))  # right side (larger angle)
        angle2 = np.degrees(np.arccos((47 - hoop_center_x) / radius))  # left side (smaller angle)

        # bounding box for arc
        bb_three = pg.QtCore.QRectF(hoop_center_x - radius, hoop_center_y - radius, 2*radius, 2*radius)
    
        # draw only top half of arc
        arc = pg.QtGui.QPainterPath()
        arc.arcMoveTo(bb_three, angle2 + 180)
        arc.arcTo(bb_three, angle2 + 180, angle1 - angle2)

        arc_item = QGraphicsPathItem(arc)
        arc_item.setPen(pg.mkPen('black', width=2))
        self.plot_widget.addItem(arc_item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    sys.exit(app.exec_())



