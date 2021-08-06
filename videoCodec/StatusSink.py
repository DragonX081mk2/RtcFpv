from abc import ABCMeta,abstractmethod
from av.frame import Frame
from queue import Queue
from threading import Thread
import traceback
import time

class StatusRender(metaclass=ABCMeta):
    def __init__(self):
        self._render_buffer = Queue()
        self._running = True

    def onStatus(self,status:dict):
        # print("on frame")
        self._render_buffer.put(status)

    def start(self):
        self._thread = Thread(target = self.render_worker_target,
                              args={})
        self._thread.start()

    def render_worker_target(self):
        while self._running:
            try:
                status = self._render_buffer.get_nowait()
            except:
                time.sleep(0.0001)
                continue

            try:
                self.render_status(status)
            except:
                print(traceback.print_exc())

    @abstractmethod
    def render_status(self,status:dict):
        pass


class StatusBlackHole(StatusRender):
    def render_status(self,status:dict):
        pass