import sys
from PyQt5.QtWidgets import  QApplication,QMainWindow,QPushButton
from PyQt5.QtCore import QUrl
import PyQt5.QtCore as Qt
from client.qtwebviewDemo import *
# from qt_ctrl_term_demo.amapHtml import AmapHTML
from videoCodec.VideoManager import VideoManager,CONNECTION_MODE_FPV,CONNECTION_MODE_CONTROLLER
from client.MediaStreamSink import FPVVideoRender
from client.VideoRenderSurface import ControllerVideoRenderSurface
from client.StatusRenderSurface import StatusDisplay,FPVStatusDisplay
from qtpy.QtGui import QPixmap,QImage
from client.ControlPad import ControlPad
from client.FPVController import FPVController
import time
import cv2

class MyMainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self,parent = None):
        super(MyMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.controlpad = ControlPad()
        self.bind_controlpad()
        self.webEngineView.page().runJavaScript("") # wtf in this version we need this to not die in render gps... don't know why..

    def bind_controlpad(self):
        self.forwardButton.pressed.connect(lambda:self.controlpad.on_activate_forward())
        self.backButton.pressed.connect(lambda: self.controlpad.on_activate_backward())
        self.leftButton.pressed.connect(lambda: self.controlpad.on_activate_left())
        self.rightButton.pressed.connect(lambda: self.controlpad.on_activate_right())
        self.forwardButton.released.connect(lambda: self.controlpad.on_deactivate_forward())
        self.backButton.released.connect(lambda: self.controlpad.on_deactivate_backward())
        self.leftButton.released.connect(lambda: self.controlpad.on_deactivate_left())
        self.rightButton.released.connect(lambda: self.controlpad.on_deactivate_right())
        self.yawSlider.valueChanged.connect(self.controlpad.change_servo_degree_to)
        self.speedSlider.valueChanged.connect(lambda x:self.controlpad.change_speed(x/10))
        # self.testButton.clicked.connect(lambda: self.webEngineView.page().runJavaScript("setLocation({:.7f},{:.7f})".format(120.03902621,29.33294251234)))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        if key == ord('W'):
            self.controlpad.on_activate_forward()

        elif key == ord('S'):
            self.controlpad.on_activate_backward()

        elif key == ord('A'):
            self.controlpad.on_activate_left()

        elif key == ord('D'):
            self.controlpad.on_activate_right()

        elif key == ord('Q'):
            # self.controlpad.change_servo_degree(1)
            self.yawSlider.setValue(self.yawSlider.value()+1)

        elif key == ord('E'):
            # self.controlpad.change_servo_degree(-1)
            self.yawSlider.setValue(self.yawSlider.value()-1)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        if key == ord('W'):
            self.controlpad.on_deactivate_forward()

        elif key == ord('S'):
            self.controlpad.on_deactivate_backward()

        elif key == ord('A'):
            self.controlpad.on_deactivate_left()

        elif key == ord('D'):
            self.controlpad.on_deactivate_right()

        # elif key == ord('Q'):
        #     # self.controlpad.change_servo_degree(1)
        #     self.yawSlider.setValue(self.yawSlider.value() + 1)
        #
        # elif key == ord('E'):
        #     # self.controlpad.change_servo_degree(-1)
        #     self.yawSlider.setValue(self.yawSlider.value() - 1)

    # def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
    #
    #
    # def keyReleaseEvent(self, a0: QtGui.QKeyEvent) -> None:





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MyMainWindow()
    # win.webEngineView.setHtml(AmapHTML)
    win.webEngineView.setUrl(QUrl("file:///client/amap.html"))
    render = FPVVideoRender(ControllerVideoRenderSurface(win.render_label))
    render.start()
    status_render = FPVStatusDisplay(win)
    videoManager = VideoManager.instance(CONNECTION_MODE_CONTROLLER)
    videoManager.init_all_resources(render,status_render)
    FPVController.instance().start()

    win.show()
    _exec_res = app.exec_()
    videoManager.instance().stop_all()
    FPVController.instance().stop()
    render.stop()
    status_render.stop()
    sys.exit(_exec_res)