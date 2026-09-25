


import re
import time

import requests
import obd_reader



class APIClient:
    def __init__(self):
        # self.base_url = "http://127.0.0.1:8000" 
        self.base_url = "https://finalproject-backend-3r92.onrender.com"
        self.Reader = obd_reader.OBDReader()
        self.vehicle_id = "9015fe12-f55c-4ca4-b6d9-afd0fb1988a3"  # Replace with the actual vehicle ID
        self.current_driving_session_id = None
        self.get("/api/raspberrypitest")

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
                endpoint = "/api/driving_sessions/start"
                print("Engine is ON. Starting driving session...")
                response = self.post_query(
                    endpoint,
                    {"vehicle_id": self.vehicle_id},
                )
                print(response)
                self.current_driving_session_id = response.get("driving_session_id")
                break
                
            else:
                print("Engine is OFF. Waiting for the engine to start...")
                time.sleep(5)  # Wait for 5 seconds before checking again   
        
        while True:
            if engine_status == 0:
                print("Engine is OFF. Ending driving session...")
                driving_session_id = response.get("driving_session_id")
                self.end_driving_session(driving_session_id)
                self.send_telemetry_data(lst)
                break
            engine_status = self.Reader.get_engine_on()
            print("Engine is ON. Continuing driving session...")
            self.Reader.driving_session(lst, vehicle_id=self.vehicle_id, driving_session_id=self.current_driving_session_id)
            time.sleep(2)  # Wait for 5 seconds before checking again
           

    def end_driving_session(self, driving_session_id):
        endpoint = f"/api/driving_sessions/end"
        response = self.put_query(
            endpoint,
            {"driving_session_id": driving_session_id},
        )
        print(response)

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


