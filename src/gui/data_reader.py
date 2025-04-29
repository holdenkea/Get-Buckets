from PyQt5.QtCore import QThread, pyqtSignal
import time
import numpy as np

class Data_Reader_Thread(QThread):

    anchor_coordinates_cm = [
        (0,0),
        (1524, 0),
        (762, 1432.56)
    ]

    # tuple to return coordinates
    new_signal = pyqtSignal(tuple)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.running = True
        self.current_position = (None, None)


    def run(self):
        # read toy data from the file
        with open(self.file_path, 'r') as file:
            print("Toy data selected for input \n")
            try:
                tag_position = None
                while self.running:
                    new_position = self.read_toy_data(file)
                    if new_position == (None, None):  
                        break

                    tag_position = new_position

                    # send data to the UI
                    self.current_position = new_position
                    self.new_signal.emit(tag_position)  

                    time.sleep(0.2)  

            except Exception as e:
                print(f"Error {e}")
            finally:
                print("End of CSV file")

    def get_current_position(self):
        print(f"GETTING CURRENT POSITION IN DATAREADER {self.current_position}")
        return self.current_position

    def stop(self):
        self.running = False
        self.wait()

    def read_toy_data(self, file):
        line = file.readline()
        if not line:
            return None, None
        
        line = line.strip()
        print(f"Raw data: {line}")

        if line.startswith("AT+RANGE="):
            if "range:(" in line:
                try:
                    # line.split turns the array to ["AT+RANGE=...", "d0,d1,d2,0,0...)"]
                    # [1] extracts the right size, or 1 index
                    # .split makes it ["d0,d1,d2", ""] and [0] returns the distances                
                    range_values = line.split("range:(")[1].split(")")[0]
                    print(range_values)

                    # this splits each value at a comma and slices the array to get first 3 items and converts to floats
                    d0, d1, d2 = map(float, range_values.split(",")[:3])
                    xt, yt = self.perform_trilateration(d0, d1, d2, self.anchor_coordinates_cm)
                    print(f"Estimated position: ({xt}, {yt})")
                    return xt, yt
                except Exception as e:
                    print(f"Failed to parse line: {e}")
                    return None, None

    def perform_trilateration(self, d0, d1, d2, anchor_coords):
        # for a complete breakdown of this algorithm and visuals see the readme on my github
        print("Performing Trilateration")
        # get coordinates
        point_a0 = anchor_coords[0]
        point_a1 = anchor_coords[1]
        point_a2 = anchor_coords[2]

        # unpack tuples to extract x and y values and
        x_a0, y_a0 = point_a0
        x_a1, y_a1 = point_a1
        x_a2, y_a2 = point_a2

        # perform matrix multiplication to generate the three equations
        # A * [xt yt] = B

        # left hand side of equation's coefficients (Matrix A)
        A = np.array([
            [x_a0 - x_a1, y_a0 - y_a1],
            [x_a1 - x_a2, y_a1 - y_a2],
            [x_a0 - x_a2, y_a0 - y_a2]
        ])

        # right hand side of equation's constants
        # square the distances
        d0_sq = d0**2
        d1_sq = d1**2
        d2_sq = d2**2

        # square the anchor coordinates
        x_a0_sq, y_a0_sq = x_a0**2, y_a0**2 
        x_a1_sq, y_a1_sq = x_a1**2, y_a1**2
        x_a2_sq, y_a2_sq = x_a2**2, y_a2**2

        rhs_0_minus_1 = -0.5 * (d0_sq - d1_sq - (x_a0_sq + y_a0_sq - x_a1_sq - y_a1_sq))
        rhs_1_minus_2 = -0.5 * (d1_sq - d2_sq - (x_a1_sq + y_a1_sq - x_a2_sq - y_a2_sq))
        rhs_0_minus_2 = -0.5 * (d0_sq - d2_sq - (x_a0_sq + y_a0_sq - x_a2_sq - y_a2_sq))

        # right hand side of equation's constants (Matrix B)
        B = np.array([
            rhs_0_minus_1, 
            rhs_1_minus_2, 
            rhs_0_minus_2
        ])

        # the system we want to solve is now A * [xt yt] = B
        # we will use np.linalg.lstsq to get the best fitting xt and yt as possible for the system, 
        xt_cm, yt_cm = np.linalg.lstsq(A, B, rcond=None)[0]

        # convert cm to feet
        xt_ft, yt_ft = self.cm_to_ft(xt_cm, yt_cm)

        return xt_ft, yt_ft
    
    def cm_to_ft(self, xt_cm, yt_cm):
        xt_ft = xt_cm * 0.0328084
        yt_ft = yt_cm * 0.0328084

        return xt_ft, yt_ft
