from multiprocessing import connection
import time

import obd


class OBDReader:
    def __init__(self):
        self.connection = None
        self.cmd = None  # Placeholder for OBD command, can be set later
        self._connect() 

   #Connect to the OBD-II adapter
    def _connect(self):
        self.connection = obd.OBD()  # Auto-connect to the OBD-II adapter
        # self.connection = obd.OBD("COM4")  # Auto-connect to the OBD-II adapter
        self.cmd = obd.commands
        

    #Helper method to get the value of a specific OBD-II command
    def _get_value(self, command):
            if self.connection and self.connection.is_connected():
    
                response = self.connection.query(command)
    
                if response.value is not None:
                    return response.value.magnitude
    
            return None

    #Get the RPM value from the vehicle
    
    def get_rpm(self):
        return self._get_value(self.cmd.RPM)

    #Get the vehicle speed from the OBD-II adapter
    def get_speed(self):
        try:
            return self._get_value(self.cmd.SPEED) * 0.621371  # Convert from km/h to mph
        except:
            return None

    #Get the throttle position from the OBD-II adapter
    #This Throttle Position sensor measures the position of the throttle valve, which controls the amount of air entering the engine.
    #Without accurate throttle position readings, the engine may not operate optimally, leading to increased fuel consumption and potential engine damage.
    def get_throttle_position(self):
        return self._get_value(self.cmd.THROTTLE_POS)
        
    #Get the engine load from the OBD-II adapter
    #This Engine Load sensor measures the current load on the engine, which is important for monitoring engine performance and efficiency.
    #Without accurate engine load readings, the engine may not operate optimally, leading to increased fuel consumption and potential engine damage.
    def get_engine_load(self):
        return self._get_value(self.cmd.ENGINE_LOAD)


    #Get the fuel level from the OBD-II adapter
    #This Fuel Level sensor measures the amount of fuel remaining in the vehicle's fuel tank, which is important for monitoring fuel consumption and planning refueling stops.
    def get_fuel_level(self):
        return self._get_value(self.cmd.FUEL_LEVEL)
    
    #Get the coolant temperature from the OBD-II adapter
    #This Coolant Temperature sensor measures the temperature of the engine coolant, which is important for monitoring engine health and preventing overheating.
    #Without accurate coolant temperature readings, the engine may overheat, leading to potential engine damage.
    def get_coolant_temp(self):
        return self._get_value(self.cmd.COOLANT_TEMP)

    #Get the intake air temperature from the OBD-II adapter
    #This Intake Air Temperature sensor measures the temperature of the air entering the engine, which is important for determining the correct air-fuel mixture for combustion.
    #Without accurate intake air temperature readings, the engine may run too rich or too lean,
    def get_intake_air_temp(self):
        return self._get_value(self.cmd.INTAKE_TEMP)
    
    #Get the mass air flow from the OBD-II adapter
    #This MAF sensor measures the amount of air entering the engine, which is crucial for determining the correct fuel-to-air ratio for combustion.
    #Without accurate MAF readings, the engine may run too rich or too lean, leading to poor performance, increased emissions, and potential engine damage.
    def get_mass_air_flow(self):
        return self._get_value(self.cmd.MAF)
        
    #Get the fuel pressure from the OBD-II adapter
    #This Fuel Pressure sensor measures the pressure of the fuel in the fuel system, which is important for ensuring proper fuel delivery to the engine.
    #Without the correct fuel pressure, the engine may not run efficiently or may not run at all.
    def get_fuel_pressure(self):
        return self._get_value(self.cmd.FUEL_PRESSURE)

    #Get the timing advance from the OBD-II adapter
    #This Timing Advance sensor measures the timing of the spark plug firing in relation to the position of the piston in the cylinder.
    #Proper timing is crucial for efficient combustion and engine performance. Incorrect timing can lead to knocking, poor fuel economy, and increased emissions.
    def get_timing_advance(self):
        return self._get_value(self.cmd.TIMING_ADVANCE)
        
    
    #Get the control module voltage from the OBD-II adapter
    #This Control Module Voltage sensor measures the voltage supplied to the vehicle's control modules, which is important for ensuring proper operation of the vehicle's electronic systems.
    #Without the correct voltage, the control modules may not function properly, leading to various electrical issues and potential vehicle malfunctions.
    def get_control_module_voltage(self):
        return self._get_value(self.cmd.CONTROL_MODULE_VOLTAGE)

    #Get the short term fuel trim from the OBD-II adapter
    #This Short Term Fuel Trim sensor measures the immediate adjustments made by the engine control unit (ECU) to the fuel injection system in order to maintain the optimal air-fuel ratio for combustion.
    #Short term fuel trim is important for monitoring engine performance and efficiency. Abnormal short term
    def get_short_term_fuel_trim(self):
        return self._get_value(self.cmd.SHORT_FUEL_TRIM_1)


    #Get the transmission fluid temperature from the OBD-II adapter
    #This Transmission Fluid Temperature sensor measures the temperature of the transmission fluid, which is important for
    def get_transmission_fluid_temp(self):
        return self._get_value(self.cmd.TRANS_TEMP)

    #Get hybrid battery voltage from the OBD-II adapter
    #This Hybrid Battery Voltage sensor measures the voltage of the hybrid battery pack, which is important
    def get_hybrid_battery_life(self):
        return self._get_value(self.cmd.HYBRID_BATTERY_REMAINING)


    #Get engine on
    #This Engine On sensor checks if the engine is currently running, which is important for determining the vehicle's operational status.
    def get_engine_on(self):
        read = self.read_data(None,None)
        
        if any(v for v in read.values()):
            return 1
        return 0
    
    #Calculate the overall engine health score based on various OBD-II parameters
    #The engine health score is calculated based on several key parameters, including engine load, coolant temperature, MAP pressure, RPM, throttle position, MAF, and short term fuel trim. Each parameter is scored individually based on predefined thresholds, and the overall health score is a weighted average of these individual scores.
    def engine_health(self):

        # Get the six PIDs we are using
        engine_load = self.get_engine_load()
        coolant_temp = self.get_coolant_temp()
        map_pressure = self._get_value(self.cmd.INTAKE_PRESSURE)
        rpm = self.get_rpm()
        throttle = self.get_throttle_position()
        maf = self.get_mass_air_flow()
        speed = self.get_speed()
        fuel_trim = self.get_short_term_fuel_trim()

        # -----------------------------------------------------
        # Make sure the required data exists
        # -----------------------------------------------------

        readings = [
            engine_load,
            coolant_temp,
            map_pressure,
            rpm,
            throttle,
            maf,
            fuel_trim
        ]

        if any(value is None for value in readings):
            return {
                "health_score": None,
                "status": "Insufficient data",
                "message": "Not enough OBD-II data to calculate engine health."
            }

        # -----------------------------------------------------
        # HYBRID ENGINE CHECK
        # -----------------------------------------------------
        # Your Ford C-Max is a hybrid.
        # When RPM is 0, the gasoline engine may simply be OFF.

        if rpm <= 0 and speed <= 0:
            return {
                "health_score": None,
                "status": "Engine Off",
                "message": "Gasoline engine is currently not running."
            }

        # =====================================================
        # INDIVIDUAL HEALTH SCORES
        # =====================================================

        # -----------------------------------------------------
        # -----------------------------------------------------
        # 1. ENGINE LOAD SCORE - PID 04
        # -----------------------------------------------------
        # Match the speed-based engine load table shown in the reference image.
        # Excellent / Good / Warning / Very High thresholds vary by speed band.
        if (0 <= speed <= 30 and engine_load <= 25) or (30 < speed <= 60 and engine_load <= 10) or (60 < speed <= 90 and engine_load <= 15) or (speed > 90 and engine_load <= 20):
            load_score = 100

        elif (0 <= speed <= 30 and 25 < engine_load <= 45) or (30 < speed <= 60 and 10 < engine_load <= 30) or (60 < speed <= 90 and 15 < engine_load <= 35) or (speed > 90 and 20 < engine_load <= 40):
            load_score = 85

        elif (0 <= speed <= 30 and 45 < engine_load <= 70) or (30 < speed <= 60 and 30 < engine_load <= 50) or (60 < speed <= 90 and 35 < engine_load <= 55) or (speed > 90 and 40 < engine_load <= 60):
            load_score = 65

        elif (0 <= speed <= 30 and engine_load > 70) or (30 < speed <= 60 and engine_load > 50) or (60 < speed <= 90 and engine_load > 55) or (speed > 90 and engine_load > 60):
            load_score = 45

        else:
            load_score = 20

        # -----------------------------------------------------
        # 2. COOLANT TEMPERATURE SCORE - PID 05
        # -----------------------------------------------------
        # python-OBD normally returns coolant temperature in °C.
        
        if coolant_temp > 125:
            coolant_score = 20
        elif coolant_temp > 115:
            coolant_score = 35
        elif coolant_temp > 105:
            coolant_score = 50
        elif coolant_temp > 95:
            coolant_score = 65
        elif coolant_temp > 85:
            coolant_score = 85
        elif coolant_temp > 70:
            coolant_score = 100
        else:
            coolant_score = 85

        # -----------------------------------------------------
        # 3. MAP SCORE - PID 0B
        # -----------------------------------------------------
        # Score based on engine load range and its expected MAP range.
        # This mirrors the reference chart: engine load drives the expected MAP,
        # and the actual MAP value is then judged against that target range.
        if engine_load <= 20:
            if 20 <= map_pressure <= 40:
                map_score = 100
            else:
                map_score = 20

        elif engine_load <= 40:
            if 30 <= map_pressure <= 50:
                map_score = 85
            else:
                map_score = 20

        elif engine_load <= 60:
            if 40 <= map_pressure <= 65:
                map_score = 70
            else:
                map_score = 20

        elif engine_load <= 80:
            if 55 <= map_pressure <= 80:
                map_score = 50
            else:
                map_score = 20

        elif engine_load <= 100:
            if 70 <= map_pressure <= 100:
                map_score = 30
            else:
                map_score = 20

        else:
            map_score = 20

        # -----------------------------------------------------
        # 4. RPM SCORE - PID 0C
        # -----------------------------------------------------

        if (0 <= rpm <= 800 and speed==0) or (0 < speed <= 30 and 0 < rpm <= 1800) or (30 < speed <= 60 and 900 < rpm <= 1800) or (60 < speed <= 90 and 1200 < rpm <= 2200) or (speed>90 and 1500 < rpm <= 2500):
            # This is a normal idle range for many vehicles when the car is stopped, a normal range for low-speed driving, and a normal range for highway driving.
            rpm_score = 100

        elif (800 <= rpm <= 1000 and speed==0) or (0 < speed <= 30 and 1800 < rpm <= 2500) or (30 < speed <= 60 and  1800 < rpm <= 2500) or (60 < speed <= 90 and 2200 < rpm <= 3000) or (speed>90 and 2500 < rpm <= 3500):
            rpm_score = 85

        elif (1000 <= rpm <= 1300 and speed==0) or (0 < speed <= 30 and 2500 < rpm <= 3500) or (30 < speed <= 60 and  2500 < rpm <= 3500) or (60 < speed <= 90 and 3000 < rpm <= 3500) or (speed>90 and 3500 < rpm <= 4500):
            rpm_score = 65

        elif (rpm>1300 and speed==0) or (0 < speed <= 30 and rpm>3500) or (30 < speed <= 60 and  rpm>3500) or (60 < speed <= 90 and rpm >3500) or (speed>90 and rpm > 4500):
            rpm_score = 45

        else:
            rpm_score = 20

        # -----------------------------------------------------
        # 5. THROTTLE POSITION SCORE - PID 11
        # -----------------------------------------------------
        # Throttle by itself isn't necessarily bad when high.
        # We mainly check that it is within a valid range.
        if (0 <= speed <= 30 and 5 < throttle <= 15) or (30 < speed <= 60 and 5 < throttle <= 15) or (60 < speed <= 90 and 5 < throttle <= 20) or (speed>90 and 10 < throttle <= 25):
            # This is a normal idle range for many vehicles when the car is stopped, a normal range for low-speed driving, and a normal range for highway driving.
            throttle_score = 100
        elif (0 <= speed <= 30 and 15 < throttle <= 30) or (30 < speed <= 60 and  15 < throttle <= 25) or (60 < speed <= 90 and 20 < throttle <= 25) or (speed>90 and 25 < throttle <= 40):
            throttle_score = 85

        elif (0 <= speed <= 30 and 30 < throttle <= 50) or (30 < speed <= 60 and  25 < throttle <= 35) or (60 < speed <= 90 and 25 < throttle <= 35) or (speed>90 and 40 < throttle <= 50):
            throttle_score = 65

        elif (0 <= speed <= 30 and throttle>30) or (30 < speed <= 60 and  35 < throttle <= 50) or (60 < speed <= 90 and 35 < throttle <= 55) or (speed>90 and 50 < throttle <= 60):
            throttle_score = 45

        else:
            throttle_score = 20
        
        # -----------------------------------------------------
        # 6. MAF SCORE - PID 10
        # -----------------------------------------------------
        # MAF depends heavily on RPM and engine load.
        # Here we check for obviously abnormal readings.

        if rpm <= 1000:
            if 1 <= maf <= 5:
                maf_score = 100
            else:
                maf_score = 20

        elif rpm <= 2000:
            if 2 <= maf <= 10:
                maf_score = 85
            else:
                maf_score = 20

        elif rpm <= 3000:
            if 5 <= maf <= 20:
                maf_score = 70
            else:
                maf_score = 20

        elif rpm <= 4000:
            if 10 <= maf <= 30:
                maf_score = 50
            else:
                maf_score = 20

        elif rpm > 4000:
            if 20 <= maf <= 40:
                maf_score = 30
            else:
                maf_score = 20

        else:
            maf_score = 20

        #=====================================================
        #Short Term Fuel Trim Score - PID 06
        #=====================================================
        if -5 <= fuel_trim <= 5:
            fuel_trim_score = 100

        elif -10 <= fuel_trim <= 10:
            fuel_trim_score = 85

        elif -15 <= fuel_trim <= 15:
            fuel_trim_score = 70

        elif -25 <= fuel_trim <= 25:
            fuel_trim_score = 50

        else:
            fuel_trim_score = 20

        # =====================================================
        # WEIGHTED ENGINE HEALTH SCORE
        # =====================================================

        # health_score = (
        #     (load_score * 0.15) +
        #     (coolant_score * 0.20) +
        #     (map_score * 0.15) +
        #     (rpm_score * 0.15) +
        #     (throttle_score * 0.10) +
        #     (maf_score * 0.25)
        # )

        health_score = (
            (load_score * 0.15) +
            (coolant_score * 0.20) +
            (map_score * 0.15) +
            (rpm_score * 0.10) +
            (fuel_trim_score * 0.20) +
            (maf_score * 0.20)
        )

        # Round to whole number
        health_score = round(health_score)

        # =====================================================
        # HEALTH STATUS
        # =====================================================

        if health_score >= 90:
            status = "Excellent"

        elif health_score >= 75:
            status = "Good"

        elif health_score >= 60:
            status = "Fair"

        elif health_score >= 40:
            status = "Poor"

        else:
            status = "Critical"

        # =====================================================
        # RETURN RESULTS
        # =====================================================

        return {
            "health_score": health_score,
            "status": status,

            "pids": {
                "engine_load": engine_load,
                "coolant_temperature": coolant_temp,
                "map": map_pressure,
                "rpm": rpm,
                "throttle_position": throttle,
                "maf": maf,
                "fuel_trim": fuel_trim
            },

            "component_scores": {
                "engine_load": load_score,
                "coolant_temperature": coolant_score,
                "map": map_score,
                "rpm": rpm_score,
                "throttle_position": throttle_score,
                "maf": maf_score,
                "fuel_trim": fuel_trim_score
            }
        }
    
    #Read all available OBD-II data from the vehicle
    def read_data(self, vehicle_id=None, driving_session_id=None):
        if self.connection and self.connection.is_connected():
            # Read various OBD-II parameters
            return {
                "vehicle_id": vehicle_id,
                "driving_session_id": driving_session_id,
                "rpm": self.get_rpm(),
                "speed": self.get_speed(),
                "throttle_position": self.get_throttle_position(),
                "engine_load": self.get_engine_load(),
                "fuel_level": self.get_fuel_level(),
                "coolant_temperature": self.get_coolant_temp(),
                "intake_air_temperature": self.get_intake_air_temp(),
                "map_pressure": self._get_value(self.cmd.INTAKE_PRESSURE),
                "mass_air_flow": self.get_mass_air_flow(),
                "fuel_pressure": self.get_fuel_pressure(),
                "timing_advance": self.get_timing_advance(),
                "control_module_voltage": self.get_control_module_voltage(),
                "short_trim": self.get_short_term_fuel_trim(),
                "hybrid_battery_life": self.get_hybrid_battery_life()
            }
        else:
            return None

    #Get the Diagnostic Trouble Codes (DTCs) from the vehicle
    #DTCs are codes generated by the vehicle's onboard diagnostic system to indicate specific issues
    def get_dtc(self):
        if self.connection and self.connection.is_connected():
            response = self.connection.query(self.cmd.GET_DTC)
            return response.value if response.value is not None else None
        else:
            return None
    

    def driving_session(self,lst, vehicle_id=None, driving_session_id=None):
        try:
            data = self.read_data(vehicle_id=vehicle_id, driving_session_id=driving_session_id)
            if data:
                print(data)
                lst.append(data)
                
            else:
                print("No OBD-II connection.")
            time.sleep(1)  # Wait for 1 second before the next reading
        except:
            print("an error occurred while reading data.")
        
    # def driving_session(self):
    #     lst = []
    #     hlth_list = []
        
    #     while True:
    #         try:
    #             data = self.read_data()
    #             data_2 = self.engine_health()
    #             if data:
    #                 print(data)
    #                 lst.append(data)
    #                 hlth_list.append(data_2)
    #             else:
    #                 print("No OBD-II connection.")
    #             time.sleep(1)  # Wait for 1 second before the next reading
    #         except KeyboardInterrupt:
    #             print("Driving session ended by user.")
    #             #write data to a file
    #             # timestamp 
    #             timestamp = time.strptime
    #             with open(f"driving_session_data{timestamp}.txt", "w") as f:
    #                 for item in lst:
    #                     f.write("%s\n" % item)
    #             with open("driving_session_health_data.txt", "w") as f:
    #                 for item in hlth_list:
    #                     f.write("%s\n" % item)
    #             break
                

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
        else:
            print("No OBD connection to disconnect.")

    

# Reader = OBDReader()
# # # print(Reader.read_data())
# print(Reader.get_engine_on())
