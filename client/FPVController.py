from videoCodec.SerializableData import SerializableData,FPVSerializeControlData,FPVStatusData
from threading import Thread,Lock
import time
from queue import Queue
from videoCodec.VideoTransporter import CTRLPacket,VideoTransporter



class FPVController():

    MOTION_FORWARD = FPVSerializeControlData.VALUE_FORWARD
    MOTION_BACKWARD = FPVSerializeControlData.VALUE_BACKWARD
    MOTION_TURN_LEFT = FPVSerializeControlData.VALUE_TURN_LEFT
    MOTION_TURN_RIGHT = FPVSerializeControlData.VALUE_TURN_RIGHT
    MOTION_BACK_LEFT = FPVSerializeControlData.VALUE_BACK_LEFT
    MOTION_BACK_RIGHT = FPVSerializeControlData.VALUE_BACK_RIGHT
    MOTION_SPIN_LEFT = FPVSerializeControlData.VALUE_SPIN_LEFT
    MOTION_SPIN_RIGHT = FPVSerializeControlData.VALUE_SPIN_RIGHT
    MOTION_BRAKE = FPVSerializeControlData.VALUE_BRAKE
    MOTION_STAND_BY = FPVSerializeControlData.VALUE_STANDBY

    _instance_lock = Lock()


    def __init__(self):
        self.motion = FPVSerializeControlData.VALUE_STANDBY
        self.servo_degree = 90
        self._running = True
        self.speed = 0.3

    @classmethod
    def instance(cls, *args, **kwargs):
        with cls._instance_lock:
            if not hasattr(FPVController, "_instance"):
                FPVController._instance = FPVController(*args, **kwargs)
        return FPVController._instance

    def start(self):
        self.send_thread = Thread(target=self.msg_send_thread_worker,
                                  args = [])
        self.send_thread.start()

    def stop(self):
        self._running = False

    def msg_send_thread_worker(self):
        while self._running:
            ctrl_data_dict = self.get_control_data()
            msg_send = FPVSerializeControlData.serialize(ctrl_data_dict)
            VideoTransporter.instance().send(CTRLPacket(msg_send))
            time.sleep(0.05)


    def get_control_data(self)->dict:
        ctrl_dict = dict()
        ctrl_dict[FPVSerializeControlData.KEY_MOTION] = self.motion
        ctrl_dict[FPVSerializeControlData.KEY_YAW] = int(self.servo_degree)
        ctrl_dict[FPVSerializeControlData.KEY_SPEED] = self.speed
        return ctrl_dict

    def set_motion(self,motion):
        print(motion)
        self.motion = motion

    def set_servo(self,degree):
        self.servo_degree = degree

    def set_speed(self,speed):
        self.speed = speed

