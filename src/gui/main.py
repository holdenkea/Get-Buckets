import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QHBoxLayout, QVBoxLayout, QWidget, QGraphicsRectItem,
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPathItem
)

import pyqtgraph as pg
import numpy as np

from data_reader import Data_Reader_Thread
import pose_classifier as pc

import threading

import queue

class MyApp(QMainWindow):
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

        # Add buttons to layout
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
        self.plot_widget.enableAutoRange(False)

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

        self.show()

    #################################### BUTTON FUNCTIONS ####################################
    def save_run(self):
        print("Save Run button clicked!")
        # TODO: Export plot data or session info to JSON, CSV, etc.

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

    def begin_tracking(self):
        self.stop_requested = False

        # Start the data reading thread
        if not self.data_reader_thread:
            self.data_reader_thread = Data_Reader_Thread('./src/uwb/python/toy.txt')
            self.data_reader_thread.new_signal.connect(self.update_position)
            self.data_reader_thread.start()

            self.pose_classifier = pc.Pose_Classifier(self, self.data_reader_thread, self.position_action_queue)

            classifier_thread = threading.Thread(target=self.pose_classifier.output_video_with_prediction)
            classifier_thread.start()

    # tracking helper function to plot position
    def update_position(self, position):
        # update the UI with the new position
        print(f"Tag position: {position}")

        if not self.position_action_queue.empty():
            action, position_at_action = self.position_action_queue.get()
            print(f"CURRENT ACTION IS {action, position_at_action}")
            if action == "shooting":
                print("Shooting detected")

                # add shooting point to scatter item
                self.scatter_item_shooting.addPoints([position_at_action[0]], [position_at_action[1]], symbol='o', size=10, pen=pg.mkPen(color='green'), brush=pg.mkBrush(color='green'))
        
        
        self.scatter_item.clear()
        self.scatter_item.addPoints([position[0]], [position[1]])



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
