from machine import Pin, PWM
import config

class Motor:
    def __init__(self, pin_in1, pin_in2, pin_pwm):
        self.in1 = Pin(pin_in1, Pin.OUT)
        self.in2 = Pin(pin_in2, Pin.OUT)
        self.pwm = PWM(Pin(pin_pwm))
        self.pwm.freq(20000) # Tần số 20kHz để motor không kêu o o

    def set_speed(self, speed):
        # Giới hạn tốc độ trong khoảng -1023 đến 1023
        speed = max(min(speed, 1023), -1023)
        
        if speed > 0:    # Tiến
            self.in1.value(1)
            self.in2.value(0)
        elif speed < 0:  # Lùi
            self.in1.value(0)
            self.in2.value(1)
        else:            # Dừng
            self.in1.value(0)
            self.in2.value(0)

        self.pwm.duty(int(abs(speed)))

class RobotDrive:
    def __init__(self):
        self.motor_l = Motor(config.M_L_IN1, config.M_L_IN2, config.M_L_PWM)
        self.motor_r = Motor(config.M_R_IN1, config.M_R_IN2, config.M_R_PWM)

    def drive(self, left_speed, right_speed):
        self.motor_l.set_speed(left_speed)
        self.motor_r.set_speed(right_speed)
