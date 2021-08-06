from videoCodec import SerializableData
from abc import ABCMeta, abstractmethod
from threading import Thread, Lock
from queue import Queue
import time
import traceback

class CtrlSinkInterface(metaclass=ABCMeta):
    @abstractmethod
    def sink(self,status_dict:dict):
        pass

class MockCtrlSinkInterface(CtrlSinkInterface):
    def sink(self,status_dict:dict):
        print(status_dict)

class CtrlSink():
    def __init__(self,serializableData:SerializableData,
                 ctrl_sink_queue:Queue,time_gap = 0.01):
        self._running = True
        self._ctrl_sink_queue = ctrl_sink_queue
        self.serializableData = serializableData
        self.time_gap = time_gap
        self._ctrl_sink_interface = None
        self._sink_interface_lock = Lock()

    def start(self):
        self.sink_thread = Thread(target=self._status_sink_worker,
                                  args=[])
        self.sink_thread.start()

    def stop(self):
        self._running = False

    def _status_sink_worker(self):
        while self._running:
            try:
                ctrl_packet = self._ctrl_sink_queue.get_nowait()
                ctrl_packet = ctrl_packet.data()
                ctrl_dict = self.serializableData.deserialize(ctrl_packet)
                with self._sink_interface_lock:
                    if self._ctrl_sink_interface:
                        self._ctrl_sink_interface.sink(ctrl_dict)
            except:
                # print(traceback.print_exc())
                time.sleep(self.time_gap)

    def set_sink_interface(self,sink_interface:CtrlSinkInterface):
        with self._sink_interface_lock:
            self._ctrl_sink_interface = sink_interface
