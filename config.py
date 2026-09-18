# App Configuration
class Config:
    API_URL = "http://192.168.1.100:7000"
    OBD_PORT = None          # Auto detect the port it is connected to
    READ_INTERVAL = 3        # seconds to wait between each OBD read
    DEVICE_NAME = "DriveSensePi"    #   Pi name to be displayed in the backend