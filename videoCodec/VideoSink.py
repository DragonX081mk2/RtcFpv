from abc import ABCMeta,abstractmethod
from av.frame import Frame
from queue import Queue
from threading import Thread
import time

class VideoRender(metaclass=ABCMeta):
    def __init__(self):
        self._render_buffer = Queue()
        self._running = True

    def onFrame(self,frame:Frame):
        # print("on frame")
        self._render_buffer.put(frame)

    def start(self):
        self._thread = Thread(target = self.render_worker_target,
                              args={})
        self._thread.start()

    def stop(self):
        self._running = False

    def render_worker_target(self):
        while self._running:
            try:
                frame = self._render_buffer.get_nowait()
                self.render_frame(frame)
            except:
                time.sleep(0.0001)
                continue

    @abstractmethod
    def render_frame(self,frame:Frame):
        pass


class VideoBlackHole(VideoRender):
    def render_frame(self,frame:Frame):
        pass