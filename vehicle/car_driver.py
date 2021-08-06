import Adafruit_PCA9685
import time
from multiprocessing import Process,Array
from videoCodec.FPVCTRLSink import CtrlSinkInterface
from videoCodec.SerializableData import FPVSerializeControlData
from vehicle.i2c_camera_servo import Servo


IN1 = 0 # L B
IN2 = 1 # L F
IN3 = 3 # R B
IN4 = 2 # R F

p = Adafruit_PCA9685.PCA9685(address = 0x40,busnum=1)
speed_ratio=0.3
pwm_freq = 150

def motor_init():
    p.set_pwm_freq(pwm_freq)
    p.set_pwm(IN1,0,0)
    p.set_pwm(IN2,0,0)
    p.set_pwm(IN2,0,0)
    p.set_pwm(IN2,0,0)

    
def backward(delaytime = 1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,int(speed_ratio*4096))
    p.set_pwm(IN2,0,0)
    p.set_pwm(IN3,0,int(speed_ratio*4096))
    p.set_pwm(IN4,0,0)
    # time.sleep(delaytime)

def forward(delaytime = 1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,0)
    p.set_pwm(IN2,0,int(speed_ratio*4096))
    p.set_pwm(IN3,0,0)
    p.set_pwm(IN4,0,int(speed_ratio*4096))
    # time.sleep(delaytime)
	
def brake(delaytime = 1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,4096)
    p.set_pwm(IN2,0,4096)
    p.set_pwm(IN3,0,4096)
    p.set_pwm(IN4,0,4096)
    # time.sleep(delaytime)

def back_left(delaytime = 1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,0)
    p.set_pwm(IN2,0,0)
    p.set_pwm(IN3,0,int(speed_ratio*4096))
    p.set_pwm(IN4,0,0)
    # time.sleep(delaytime)


    
def back_right(delaytime = 1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,int(speed_ratio*4096))
    p.set_pwm(IN2,0,0)
    p.set_pwm(IN3,0, 0)
    p.set_pwm(IN4,0,0)
    # time.sleep(delaytime)

def spin_right(delaytime = 1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,0)
    p.set_pwm(IN2,0,int(speed_ratio*4096))
    p.set_pwm(IN3,0,int(speed_ratio*4096))
    p.set_pwm(IN4,0,0)
    # time.sleep(delaytime)

def spin_left(delaytime = 1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,int(speed_ratio*4096))
    p.set_pwm(IN2,0,0)
    p.set_pwm(IN3,0,0)
    p.set_pwm(IN4,0,int(speed_ratio*4096))
    # time.sleep(delaytime)

def turn_right(delaytime = 1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,0)
    p.set_pwm(IN2,0,int(speed_ratio*4096))
    p.set_pwm(IN3,0,0)
    p.set_pwm(IN4,0,0)
    # time.sleep(delaytime)

def turn_left(delaytime =1,speed_ratio = 0.3):
    p.set_pwm(IN1,0,0)
    p.set_pwm(IN2,0,0)
    p.set_pwm(IN3,0,0)
    p.set_pwm(IN4,0,int(speed_ratio*4096))
    # time.sleep(delaytime)




class CarCTRLSinkInterface(CtrlSinkInterface):
    def __init__(self):
        super(CarCTRLSinkInterface, self).__init__()
        self.servo = Servo(Adafruit_PCA9685=p)

    def sink(self,status_dict:dict):
        print("ctrl sink {}".format(status_dict))
        motion = status_dict[FPVSerializeControlData.KEY_MOTION]
        servo_yaw_degree = status_dict[FPVSerializeControlData.KEY_YAW]
        speed = status_dict[FPVSerializeControlData.KEY_SPEED]
        self.servo.change_angle_to(angle=servo_yaw_degree)
        if motion == FPVSerializeControlData.VALUE_FORWARD:
            forward(speed_ratio=speed)
            return
        if motion == FPVSerializeControlData.VALUE_BACKWARD:
            backward(speed_ratio=speed)
            return
        if motion == FPVSerializeControlData.VALUE_SPIN_LEFT:
            spin_left(speed_ratio=speed)
            return
        if motion == FPVSerializeControlData.VALUE_SPIN_RIGHT:
            spin_right(speed_ratio=speed)
            return
        if motion == FPVSerializeControlData.VALUE_TURN_LEFT:
            turn_left(speed_ratio=speed)
            return
        if motion == FPVSerializeControlData.VALUE_TURN_RIGHT:
            turn_right(speed_ratio=speed)
            return
        if motion == FPVSerializeControlData.VALUE_BACK_LEFT:
            back_left(speed_ratio=speed)
            return
        if motion == FPVSerializeControlData.VALUE_BACK_RIGHT:
            back_right(speed_ratio=speed)
            return
        if motion == FPVSerializeControlData.VALUE_STANDBY:
            brake()
            return
        if motion == FPVSerializeControlData.VALUE_BRAKE:
            brake()
            return



class Car_Driver(Process):
    def __init__(self, msg_arr=None, servo_freq=150,min_speed_ratio = 0.3,max_speed_ratio = 0.8):  # arr give delta angle
        super(Car_Driver, self).__init__()
        self.move_arr = msg_arr
        self.move_actions = [brake,forward,backward,spin_left,spin_right,turn_left,turn_right,back_left,back_right]
        motor_init()
        self.speed_ratio = min_speed_ratio
        self.min_speed_ratio = min_speed_ratio
        self.max_speed_ratio = max_speed_ratio

    def change_speed(self,delta_speed):
        goal_speed = self.speed_ratio+delta_speed
        print('goal speed',goal_speed)
        if goal_speed >= self.min_speed_ratio and goal_speed <= self.max_speed_ratio:
            self.speed_ratio += delta_speed
        print('speed change to',self.speed_ratio)

    def run(self):
        while True:
            move = self.move_arr[0]
            delta_speed = self.move_arr[1]-128
            if delta_speed != 0:
                print('change_speed')
                self.change_speed(delta_speed*0.1)
            if move == 0xFFFFFFF:  # ending signal
                print('{} end'.format('car driver'))
                break
            else:
                move_action = self.move_actions[move]
                move_action(0.05,self.speed_ratio)


if __name__ == '__main__':
    #p.set_pwm_freq(2000)
    motor_init()
    print("test forward...")
    forward()
    print("test back ...")
    backward()
    print("test turn left ...")
    turn_left()
    print("test turn right ..")
    turn_right()
    print("test spin left ...")
    spin_left()
    print("test spin right ...")
    spin_right()
    print("test brake")
    brake()
    # GPIO.cleanup()
    #msg_arr = Array('i',[0,128])
    #controller = Car_Driver(msg_arr=msg_arr)
    #controller.start()
    #msg_arr[1] = 129
    #print(controller.speed_ratio)
    #time.sleep(1)
    #msg_arr[1] = 128
