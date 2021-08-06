from .FPVSensor import FPVSensor
from videoCodec.SerializableData import FPVStatusData
from serial import Serial
import pynmea2
import traceback

RMC = "RMC"
VTG = "VTG"

class GpsSensor(FPVSensor):
    def __init__(self,port:str='/dev/ttyTHS1',baudrate:int = 9600):
        super(GpsSensor,self).__init__(time_gap=0)
        self.port = port
        self.baudrate = baudrate
        self.ser = Serial(port=self.port,baudrate=self.baudrate)

    def get_sensor_data(self) ->dict:
        data = dict()
        try:
            line = self.ser.readline().decode()
            print(line)
        except:
            print(traceback.print_exc())
        if line[3:].startswith(RMC):
            nmea_res = pynmea2.parse(line)
            if nmea_res.is_valid:
                data[FPVStatusData.KEY_LONGITUDE] = nmea_res.longitude
                data[FPVStatusData.KEY_LATITUDE] = nmea_res.latitude
                data[FPVStatusData.KEY_SPEED] = float(nmea_res.data[6])*1.852
                data[FPVStatusData.KEY_DIRECTION] = float(nmea_res.data[7])
            else:
                data[FPVStatusData.KEY_LONGITUDE] = nmea_res.longitude
                data[FPVStatusData.KEY_LATITUDE] = nmea_res.latitude
                data[FPVStatusData.KEY_SPEED] = float(nmea_res.data[6]) * 1.852
                data[FPVStatusData.KEY_DIRECTION] = float(nmea_res.data[7])
        return data


class MockGpsSensor(FPVSensor):
    def __init__(self, file_dir = './simu_datas/gps_record.txt'):
        super(MockGpsSensor, self).__init__(time_gap=0)
        with open(file_dir,'r') as gps_file:
            self.lines = gps_file.readlines()
        self.record_idx = 0
        self.record_num = len(self.lines)

    def get_sensor_data(self) -> dict:
        data = dict()
        line = self.lines[self.record_idx]
        self.record_idx = (self.record_idx+1) % self.record_num
        if line[3:].startswith(RMC):
            nmea_res = pynmea2.parse(line)
            if nmea_res.is_valid:
                data[FPVStatusData.KEY_LONGITUDE] = nmea_res.longitude
                data[FPVStatusData.KEY_LATITUDE] = nmea_res.latitude
                data[FPVStatusData.KEY_SPEED] = float(nmea_res.data[6]) * 1.852
                data[FPVStatusData.KEY_DIRECTION] = float(nmea_res.data[7])
            else:
                data[FPVStatusData.KEY_LONGITUDE] = nmea_res.longitude
                data[FPVStatusData.KEY_LATITUDE] = nmea_res.latitude
                data[FPVStatusData.KEY_SPEED] = float(nmea_res.data[6]) * 1.852
                data[FPVStatusData.KEY_DIRECTION] = float(nmea_res.data[7])
        return data


