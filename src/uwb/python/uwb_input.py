import serial
import serial.tools.list_ports

import trilateration as tl

# this function reads data line by line from either toy data or UWB input
def read_data():
    try:
        line = ser.readline().decode('utf-8', errors='ignore')

    except Exception as e:
        print(f"Error reading/parsing data from UWB stream: {e}")
        return None, None

    #line = ser.readline().decode('utf-8', errors='ignore')
    print(f"Raw data: {line}")

    if line.startswith("RANGE:"):
        _, values = line.split(":")
        d0, d1, d2 = map(float, values.split(","))

        # call trilateration function here
        xt, yt = tl.perform_trilateration(d0, d1, d2, anchor_coordinates)
        print(f"Estimated position: ({xt}, {yt})")
        return xt, yt
  
def read_toy_data(file):
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
                xt, yt = tl.perform_trilateration(d0, d1, d2, anchor_coordinates_cm)
                print(f"Estimated position: ({xt}, {yt})")
                return xt, yt
            except Exception as e:
                print(f"Failed to parse line: {e}")
                return None, None
            

# function to get the correct COM port
def get_first_com():
    port_list = serial.tools.list_ports.comports()

    if len(port_list) <= 0:
        print("No COM")
        return ""
    else:
        print("First COM")
        for com in port_list:
            print(com)
            return list(com)[0]

def freedom_units_to_other_units(coords_feet):
    return [(x * 30.48, y * 30.48) for x, y in coords_feet]

##################################################################
#                      Main Code Block                           #
#                                                                #
##################################################################

anchor_coordinates_ft = [
    (0,0),
    (50,0),
    (25,47)
]

anchor_coordinates_cm = freedom_units_to_other_units(anchor_coordinates_ft)

# HOLDEN KEEP THESE TWO INPUTS SEPERATE UNTIL YOU VERIFY BOTH WORK INDEPENDENTLY

input_selection = input("Type 1 to test pygame on toy data, type 2 to use UWB input \n")
input_selection = int(input_selection)

if input_selection == 1:
    # initialize toy data 
    with open('./src/uwb/python/toy.txt', 'r') as file:
        print("Toy data selected for input \n")

        try:        
            tag_position = None

            while True:
                
                new_position = read_toy_data(file)
                if new_position == (None, None):
                    break

                tag_position = new_position

        except Exception as e:
            print(f"Error {e}")

        finally:
            print("End of csv file")

elif input_selection == 2:
    # initialize serial input
    ser = serial.Serial(get_first_com(), 115200, timeout=1)
    ser.reset_input_buffer()
    print(f"UWB modules selected for input with port {ser} \n")
    try:
            # initialize pygame
            pygame.init()
            screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
            pygame.display.set_caption("UWB Tag Position Tracker")
            clock = pygame.time.Clock()

            #runtime = time.time()
            tag_position = None

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt

                new_position = read_data()
                if new_position != (None, None):
                    tag_position = new_position

                # update display
                draw_frame(screen, tag_position)

                # limit refresh rate
                clock.tick(30)

                # flush input buffer
                if time.time() - runtime > 0.5:
                    runtime = time.time()
                    ser.reset_input_buffer()
    except Exception as e:
            print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")
        pygame.quit()
        sys.exit()

else:
    print("Incorrect input, please type 1 or 2 \n")

