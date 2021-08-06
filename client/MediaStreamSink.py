from qtpy.QtWidgets import QLabel
from qtpy.QtGui import QImage,QPixmap
from .VideoRenderSurface import VideoRenderSurface
from videoCodec.VideoSink import VideoRender
from threading import Lock
from av.frame import Frame

class FPVVideoRender(VideoRender):
    def __init__(self, render_surface:VideoRenderSurface):
        super(FPVVideoRender, self).__init__()
        self.surface_lock = Lock()
        self.render_surface = render_surface

    def render_frame(self,frame:Frame):
        # print('render_frame')
        self.render_surface.render(frame)

