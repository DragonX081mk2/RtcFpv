from abc import ABCMeta,abstractmethod
from threading import Thread,Lock
import time

class LogStatisticBase(metaclass=ABCMeta):
    def __init__(self,report_time_s = 1):
        self._running = True
        self._report_time = report_time_s
        self._thread = Thread(target=self.log_report_target,args=[])


    def _start(self):
        self._thread.run()

    def stop(self):
        self._running = False

    def log_report_target(self):
        while self._running:
            self.log_report()
            time.sleep(self._report_time)

    @abstractmethod
    def log_report(self):
        pass