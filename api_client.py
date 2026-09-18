


import requests


class APIClient:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"  

    def post(self, endpoint, data):
        response = requests.post(f"{self.base_url}{endpoint}", json=data)
        return response.json()

    def send_diagnostics_info(self, info):
        endpoint = "/api/diagnostics"
        print(info)
        data = {
            "title": info["title"],
            "vehicle_id": "7e80c87a-1c23-4cf4-8d7e-be6ea989f5f4",
            "code": info["code"],
            "description": info["description"],
            "severity": info["severity"],
            "causes": info["causes"],
            "recommended": info["recommended"],
            "cost_to_repair": info["cost_to_repair"]
        }
        return self.post(endpoint, data)

client = APIClient()
client.send_diagnostics_info(
    {
  "vehicle_id": "12345",
  "title": "Engine Misfire Detected",
  "code": "P0301",
  "description": "Cylinder 1 is misfiring.",
  "severity": "high",
  "causes": [
    "Faulty spark plug",
    "Defective ignition coil",
    "Fuel injector problem"
  ],
  "recommended": "Inspect and replace the spark plug or ignition coil for cylinder 1.",
  "cost_to_repair": "$150-$400"
})


