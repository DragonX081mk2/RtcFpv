from qtpy.QtWidgets import QLabel
from qtpy.QtGui import QImage,QPixmap
from .StatusRenderSurface import StatusDisplay
from videoCodec.StatusSink import StatusRender
from threading import Lock

class FPVStatusRender(StatusRender):
    def __init__(self, status_display:StatusDisplay):
        super(FPVStatusRender, self).__init__()
        self.surface_lock = Lock()
        self.status_display = status_display

    def render_status(self,status:dict):
        # print('render_frame')
        self.status_display.sink(status)