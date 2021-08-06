from .FPVController import *
from qtpy.QtWidgets import QPushButton
class ControlPad():
    def __init__(self):
        self.x_motion = FPVController.MOTION_STAND_BY
        self.y_motion = FPVController.MOTION_STAND_BY
        self.is_brake = False
        self.servo_degree = 90
        self.yaw_min_degree = 0
        self.yaw_max_degree = 180
        self.speed = 0.3

    def change_servo_degree(self,delta_degree)->int:
        print("change servo degree delta {}".format(delta_degree))
        self.servo_degree = max(self.yaw_min_degree,min(self.servo_degree+delta_degree,self.yaw_max_degree))
        FPVController.instance().set_servo(self.servo_degree)


    def change_servo_degree_to(self,degree):
        print("change_servo_degree to {}".format(degree))
        self.servo_degree = degree
        FPVController.instance().set_servo(degree)

    def set_x_motion(self,motion):
        self.x_motion = motion
        self.update_motion()

    def set_y_motion(self,motion):
        self.y_motion = motion
        self.update_motion()

    def update_motion(self):
        controller = FPVController.instance()
        if self.is_brake:
            controller.set_motion(FPVController.MOTION_BRAKE)
            return

        if self.y_motion==FPVController.MOTION_FORWARD:
            if self.x_motion == FPVController.MOTION_SPIN_LEFT:
                controller.set_motion(FPVController.MOTION_TURN_LEFT)
                return
            if self.x_motion == FPVController.MOTION_SPIN_RIGHT:
                controller.set_motion(FPVController.MOTION_TURN_RIGHT)
                return
            if self.x_motion == FPVController.MOTION_STAND_BY:
                controller.set_motion(self.y_motion)
                return

        if self.y_motion==FPVController.MOTION_BACKWARD:
            if self.x_motion == FPVController.MOTION_SPIN_LEFT:
                controller.set_motion(FPVController.MOTION_BACK_LEFT)
                return
            if self.x_motion == FPVController.MOTION_SPIN_RIGHT:
                controller.set_motion(FPVController.MOTION_BACK_RIGHT)
                return

            if self.x_motion == FPVController.MOTION_STAND_BY:
                controller.set_motion(self.y_motion)
                return

        if self.y_motion == FPVController.MOTION_STAND_BY:
            controller.set_motion(self.x_motion)
            return


    def on_activate_forward(self):
        self.y_motion = FPVController.MOTION_FORWARD
        self.update_motion()

    def on_deactivate_forward(self):
        if self.y_motion == FPVController.MOTION_FORWARD:
            self.y_motion = FPVController.MOTION_STAND_BY
        self.update_motion()

    def on_activate_backward(self):
        self.y_motion = FPVController.MOTION_BACKWARD
        self.update_motion()

    def on_deactivate_backward(self):
        if self.y_motion == FPVController.MOTION_BACKWARD:
            self.y_motion = FPVController.MOTION_STAND_BY
        self.update_motion()

    def on_activate_left(self):
        self.x_motion = FPVController.MOTION_SPIN_LEFT
        self.update_motion()

    def on_deactivate_left(self):
        if self.x_motion == FPVController.MOTION_SPIN_LEFT:
            self.x_motion = FPVController.MOTION_STAND_BY
        self.update_motion()

    def on_activate_right(self):
        self.x_motion = FPVController.MOTION_SPIN_RIGHT
        self.update_motion()

    def on_deactivate_right(self):
        if self.x_motion == FPVController.MOTION_SPIN_RIGHT:
            self.x_motion = FPVController.MOTION_STAND_BY
        self.update_motion()

    def change_speed(self,speed):
        speed = min(1.0,max(0.0,speed))
        print("change_speed to {}".format(speed))
        self.speed = speed
        FPVController.instance().set_speed(speed)