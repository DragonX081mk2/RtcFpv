from abc import ABCMeta,abstractmethod
from videoCodec.SerializableData import FPVStatusData
from videoCodec.FPVCTRLSink import CtrlSinkInterface
from .qtwebviewDemo import Ui_MainWindow
from threading import Thread
import time


class StatusDisplay(CtrlSinkInterface):
    def sink(self,status_dict:dict):
        pass

class FPVStatusDisplay(StatusDisplay):
    def __init__(self,win:Ui_MainWindow,render_time_gap = 0.3):
        self._win = win
        self._lat = 91
        self._lon = 181
        self._spd = 0
        self._dir = 0
        self._running = True
        self.render_time_gap = render_time_gap
        self.start()

    def sink(self,status_dict:dict):
        lat = status_dict[FPVStatusData.KEY_LATITUDE]
        lon = status_dict[FPVStatusData.KEY_LONGITUDE]
        # if self._lat >= 181:
        #     self._lat = lat
        #
        direction = int(status_dict[FPVStatusData.KEY_DIRECTION])
        speed = status_dict[FPVStatusData.KEY_SPEED]
        self._lat = lat
        self._lon = lon
        self._dir = direction
        self._spd = speed

    def show_lnglat(self,lat:float,lon:float):
        print("show_lnglat ",lat," ",lon)
        self._win.webEngineView.page().runJavaScript("setLocation({:.7f},{:.7f})".format(lat,lon))

    def show_direction(self,angle:int):
        self._win.webEngineView.page().runJavaScript("setAngle({})".format(angle))

    def on_gps_not_valid(self):
        print('gps data not valid')

    def show_speed(self,speed):
        print("speed is {}".format(speed))


    def status_render_worker(self):
        while self._running:
            if self._lon <= 180 and self._lon >= -180 and self._lat <= 90 and self._lat >= -90:
                self.show_lnglat(self._lon, self._lat)
                self.show_direction(self._dir)
            else:
                print("render lon ",self._lon,',lat ',self._lat)
                self.on_gps_not_valid()

            time.sleep(self.render_time_gap)

    def stop(self):
        self._running = False

    def start(self):
        self._render_thread = Thread(target=self.status_render_worker,
                                     args = [])
        self._render_thread.start()