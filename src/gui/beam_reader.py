import threading
import time
import requests

class Beam_Reader:
    def __init__(self, esp32_ip):
        self.esp32_url = f"http://{esp32_ip}"
        
        # stores the value of both beam being broken or not
        self.made_shot = False
        self.lock = threading.Lock()

    def read_sensor(self):
        try:
            response = requests.get(self.esp32_url, timeout=1)
            if response.status_code == 200:
                data = response.json()
                return data["sensor_1"]
        except requests.RequestException as e:
            print(f"error connecting to ESP32: {e}")
        return None

    # function to check if the beams were broken for a certain period of time
    def update_loop(self, duration):
        start_time = time.time()

        was_beam_broken = False
        
        while time.time() - start_time < duration:
            sensor_value = self.read_sensor()

            if sensor_value == 0:
                was_beam_broken = True
                break
            time.sleep(0.1)

        with self.lock:
            self.made_shot = was_beam_broken

        #return was_beam_broken
    

    def get_shot_status(self):
        with self.lock:
            return self.made_shot