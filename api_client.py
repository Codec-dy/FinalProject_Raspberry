


import re
import time

import requests
import obd_reader
from datetime import datetime


class APIClient:
    def __init__(self):
        # self.base_url = "http://127.0.0.1:8000" 
        self.base_url = "https://finalproject-backend-3r92.onrender.com"
        self.Reader = obd_reader.OBDReader()
        self.vehicle_id = "9015fe12-f55c-4ca4-b6d9-afd0fb1988a3"  # Replace with the actual vehicle ID
        # self.vehicle_id = "7e80c87a-1c23-4cf4-8d7e-be6ea989f5f4"  # Replace with the actual vehicle ID
        self.current_driving_session_id = None
        if self.check_connection():
            try:
                self.send_offline_data()
            except Exception as e:
                print(f"Error occurred while sending offline data: {e}")
        else:
            print("No connection to the server. Data will be stored locally.")
    
    def store_data_in_file(self,key, value):
        # Store the data in a file if offline
        with open("data.txt", "a") as f:
            f.write(f"{key}: {value}\n")
        

    def clear_data_file(self):
        # Clear the data file after sending the data to the server
        with open("data.txt", "w") as f:
            f.write("")
    
    def send_offline_data(self):
        # Read the data from the file and send it to the server
        lst = []
        ## put data into a dictionary
        data_dict = {}
        with open("data.txt", "r") as f:
            data = f.readlines()
            
        for line in data:
            key, value =  line.strip().split(": ", 1)
            if key == "End Driving Session":
                lst.append(data_dict)
                data_dict = {}  # Reset the dictionary for the next session
                continue
            else:
                data_dict[key] = value

        if lst:
            print("Sending offline data to the server...")
            try:
                for session in lst:
                    start_time = datetime.fromtimestamp(float(session.get("start_time")))
                    end_time = datetime.fromtimestamp(float(session.get("end_time")))
                    telemetry = eval(session.get("telemetry"))  # Convert string representation of list back to list
                    self.send_start_time(start_time)
                    for telemetry_data in telemetry:
                        telemetry_data["driving_session_id"] = self.current_driving_session_id
                        telemetry_data["timestamp"] = datetime.fromtimestamp(
                            float(telemetry_data["timestamp"])
                        ).isoformat()
                    self.send_telemetry_data(telemetry)
                    self.end_driving_session(self.current_driving_session_id, end_time)
                self.clear_data_file()
            except Exception as e:
                print(f"Error occurred while sending offline data: {e}")
        else:
            print("No offline data to send.")

    def check_connection(self):
        try:
            response = requests.get(f"{self.base_url}/api/raspberrypitest", timeout=5)
            if response.status_code == 200:
                print("Connection to the server is successful.")
                return True
            else:
                print(f"Connection to the server failed with status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Connection to the server failed: {e}")
            return False
    
    def post(self, endpoint, data):
        response = requests.post(f"{self.base_url}{endpoint}", json=data)
        return response.json()

    def post_query(self, endpoint, params):
        response = requests.post(f"{self.base_url}{endpoint}", params=params)
        return response.json()

    def put_query(self,endpoint,params):
        response = requests.put(f"{self.base_url}{endpoint}", params=params)
        return response.json()

    def get(self,endpoint):
        response = requests.get(f"{self.base_url}{endpoint}")
        return response.json()

    def start_driving_session(self):
        response = None
        lst = []
        engine_status = 0
        while True:
            
            engine_status = self.Reader.get_engine_on()
            print("engine_status ", engine_status)
            if engine_status == 1:

                print("Engine is ON. Starting driving session...")
                self.store_data_in_file("start_time", time.time())
                self.store_data_in_file("vehicle_id", self.vehicle_id)
                break
                
            else:
                print("Engine is OFF. Waiting for the engine to start...")
                time.sleep(5)  # Wait for 5 seconds before checking again   
        
        while True:
            if engine_status == 0:
                print("Engine is OFF. Ending driving session...")
                driving_session_id = "None"
                self.store_data_in_file("end_time", time.time())
                self.store_data_in_file("telemetry", lst)
                self.store_data_in_file("End Driving Session", "-------------------")
                try:
                    self.send_offline_data()
                except Exception as e:
                    print(f"Error occurred while sending offline data: {e}")
                break
            engine_status = self.Reader.get_engine_on()
            print("Engine is ON. Continuing driving session...")
            self.Reader.driving_session(lst, vehicle_id=self.vehicle_id, driving_session_id=self.current_driving_session_id)
            time.sleep(2)  # Wait for 5 seconds before checking again
           

    def end_driving_session(self, driving_session_id, end_time=None):
        endpoint = f"/api/driving_sessions/end"
        response = self.put_query(
            endpoint,
            {"driving_session_id": driving_session_id, "end_time": end_time},
        )
        print(response)

    def send_start_time(self, start_time):
        endpoint = "/api/driving_sessions/start"
        response = self.post_query(
            endpoint,
            {"vehicle_id": self.vehicle_id, "start_time": start_time},
        )
        print(response)
        self.current_driving_session_id = response.get("driving_session_id")

    def send_telemetry_data(self, telemetry):
        endpoint = "/api/telemetry"
        response = self.post(endpoint, telemetry)
        print(response)

    def send_diagnostics_info(self, info):
        endpoint = "/api/diagnostics"
        print(info)
        data = {
            "title": info["title"],
            "vehicle_id": info["vehicle_id"],
            "code": info["code"],
            "description": info["description"],
            "severity": info["severity"],
            "causes": info["causes"],
            "recommended": info["recommended"],
            "cost_to_repair": info["cost_to_repair"]
        }
        return self.post(endpoint, data)

client = APIClient()
client.start_driving_session()
# client.send_offline_data()


