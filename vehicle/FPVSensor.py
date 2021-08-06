from abc import ABCMeta,abstractmethod
from threading import Thread,Lock
from videoCodec.SerializableData import FPVStatusData
from videoCodec.VideoTransporter import VideoTransporter,CTRLPacket
import time
import traceback


class FPVSensor(metaclass=ABCMeta):
    def __init__(self,time_gap = 0.01,error_print=False):
        self._data_lock = Lock()
        self._data_dict = dict()
        self._running_lock = Lock()
        self._running = False
        self._time_gap = time_gap
        self._error_print = error_print

    '''
    func: get_data
    dscp: this method is called by sensor manager for get sensor data async
    '''
    def get_data(self)->dict:
        with self._data_lock:
            return self._data_dict

    def _on_get_data_from_sensor(self,key,value):
        self._data_dict[key] = value

    @abstractmethod
    def get_sensor_data(self)->dict:
        pass

    def on_start(self):
        pass

    def _sensor_thread_worker(self):
        while self._running:
            with self._running_lock:
                try:
                    data = self.get_sensor_data()
                except:
                    if self._error_print:
                        print(traceback.print_exc())
                    continue

                with self._data_lock:
                    for key,value in data.items():
                        self._on_get_data_from_sensor(key,value)

    def start(self):
        self.on_start()
        with self._running_lock:
            if not self._running:
                self._running = True

                self._thread = Thread(target=self._sensor_thread_worker,
                                  args=[])
                self._thread.start()

    def stop(self):
        self._running = False

    def restart(self):
        self.stop()
        self.start()

class FPVSensorsManager():
    _instance_lock = Lock()

    @classmethod
    def instance(cls,*args,**kwargs):
        with cls._instance_lock:
            if not hasattr(cls,"_instance"):
                cls._instance = FPVSensorsManager(*args,**kwargs)
        return cls._instance

    def __init__(self,query_time_gap = 0.01,report_time_gap=0.3):
        self._sensors_lock = Lock()
        self._sensor_nodes = []
        self._status_dict = dict()
        self._running = True
        self.query_time_gap = query_time_gap
        self.report_time_gap = report_time_gap


    def update_status_dict(self,status_dict:dict):
        for key,value in status_dict.items():
            self._status_dict[key] = value

    def sensors_query_worker(self):
        while self._running:
            with self._sensors_lock:
                for sensor in self._sensor_nodes:
                    _sensor_data = sensor.get_data()
                    self.update_status_dict(_sensor_data)
            time.sleep(self.query_time_gap)

    def status_send_worker(self):
        while self._running:
            status_bytes = FPVStatusData.serialize(self._status_dict)
            VideoTransporter.instance().send(CTRLPacket(status_bytes))
            time.sleep(self.report_time_gap)

    def register_sensor(self,sensor:FPVSensor):
        sensor.start()
        with self._sensors_lock:
            self._sensor_nodes.append(sensor)

    def start(self):
        self._query_thread = Thread(target=self.sensors_query_worker,
                                    args=[])

        self._send_thread = Thread(target=self.status_send_worker,
                                   args=[])

        self._query_thread.start()
        self._send_thread.start()


    def stop(self):
        self._running = False

