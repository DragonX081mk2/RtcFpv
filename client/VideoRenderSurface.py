from abc import ABCMeta,abstractmethod
from av.frame import Frame
from threading import Lock
from qtpy import QtWidgets
from qtpy.QtGui import QPixmap,QImage

class VideoRenderSurface(metaclass=ABCMeta):
    @abstractmethod
    def render(self,frame:Frame):
        pass

class ControllerVideoRenderSurface(VideoRenderSurface):
    def __init__(self,surface:QtWidgets.QLabel):
        self.render_surface = surface

    def render(self,frame:Frame):
        if self.render_surface is not None:
            # print("fpv render in surface")
            img = frame.to_ndarray(format="rgb24")
            #
            # pixelMap = QPixmap.fromImage(QImage(img, img.shape[0], img.shape[1], QImage.Format_RGB888))
            # self.render_surface.setPixmap(pixelMap)
            #
            height, width, bytesPerComponent = img.shape
            bytesPerLine = bytesPerComponent * width
            q_image = QImage(img.data, width, height, bytesPerLine,
                             QImage.Format_RGB888).scaled(self.render_surface.width(), self.render_surface.height())
            self.render_surface.setPixmap(QPixmap.fromImage(q_image))

