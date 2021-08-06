from multiprocessing import Process,Array
import time
import Adafruit_PCA9685



class Servo():
    def __init__(self,servo_freq = 150,min_angle=0,max_angle=180,channel=4,Adafruit_PCA9685:Adafruit_PCA9685.PCA9685=None): # arr give delta angle
        self.angle_speed = 60 / 0.15
        self.min_angle=min_angle
        self.max_angle=max_angle
        self.channel = channel
        
        self.pwm_cycle = 1000 / servo_freq
        self.dc_interval = 2.9 / self.pwm_cycle
        self.mindc = 0.5 / self.pwm_cycle + self.dc_interval * (self.min_angle / 180)
        self.maxdc = 3.4 / self.pwm_cycle - self.dc_interval * ((180-self.max_angle) / 180)
        self.dc = (self.mindc+self.maxdc) / 2 / self.pwm_cycle
        if Adafruit_PCA9685 is None:
            Adafruit_PCA9685 = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
        self.p = Adafruit_PCA9685
        self.change_dc(self.dc)


        
    def _cal_delta_dutycycle(self, delta_angle):
        delta_dc = delta_angle / 180 * self.dc_interval
        dc = self.dc + delta_dc
        if dc < self.mindc:
            return self.mindc
        elif dc> self.maxdc:
            return self.maxdc
        else:
            return dc

    def _cal_dutycycle(self,angle):
        dc = (angle-self.min_angle) / 180 * self.dc_interval + self.mindc
        return max(self.mindc,min(dc,self.maxdc))

    def change_dc(self,dc):
        self.dc = dc
        dc_data = int(4096*self.dc)
        self.p.set_pwm(self.channel,0,dc_data)

    def change_delta_angle(self,delta_angle):
        dc = self._cal_delta_dutycycle(delta_angle)
        self.change_dc(dc)

    def change_angle_to(self,angle):
        dc = self._cal_dutycycle(angle)
        self.change_dc(dc)

if __name__ == '__main__':
    p = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
    servo = Servo(Adafruit_PCA9685=p)
    for i in range(5):
        angle = 180/5 * i
        servo.change_angle_to(angle)
        time.sleep(0.5)
    servo.change_dc(0)
