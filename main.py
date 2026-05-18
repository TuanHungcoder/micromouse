import time
import micropython
from machine import Timer

import config
from sensors import SensorArray
from motors import RobotDrive
from encoders import SystemEncoders
from pid import PID
from maze import MazeSolver

LOOP_S = config.LOOP_PERIOD_MS / 1000.0


def clamp_pwm(value):
    v = int(value)
    if v > 1023:
        return 1023
    if v < -1023:
        return -1023
    return v


def clamp_steer(value):
    m = config.MAX_STEER
    if value > m:
        return m
    if value < -m:
        return -m
    return value


class Micromouse:
    def __init__(self):
        micropython.alloc_emergency_exception_buf(100)

        self.sensors = SensorArray()
        self.drive = RobotDrive()
        self.encoders = SystemEncoders()
        self.maze = MazeSolver()
        self.steer_pid = PID(config.KP, config.KI, config.KD)

        self._timer = None
        self.front_blocked = False

    def _is_front_blocked(self):
        front_avg = (self.sensors.values[1] + self.sensors.values[2]) / 2
        return front_avg > config.FRONT_WALL_THRESHOLD

    def _control_loop(self, timer):
        self.sensors.read_sensors()

        if self._is_front_blocked():
            self.front_blocked = True
            self.drive.drive(0, 0)
            return

        self.front_blocked = False
        error = self.sensors.get_steering_error()
        correction = clamp_steer(self.steer_pid.compute(error, LOOP_S))

        left = clamp_pwm(config.BASE_SPEED + correction)
        right = clamp_pwm(config.BASE_SPEED - correction)
        self.drive.drive(left, right)

    def start(self):
        if self._timer is not None:
            return
        self._timer = Timer(0)
        self._timer.init(
            period=config.LOOP_PERIOD_MS,
            mode=Timer.PERIODIC,
            callback=self._control_loop,
        )

    def stop(self):
        if self._timer is not None:
            self._timer.deinit()
            self._timer = None
        self.drive.drive(0, 0)


def main():
    print("Khoi dong Micromouse...")
    bot = Micromouse()

    print("San sang! Rut tay khoi xe trong 3 giay...")
    time.sleep(3)

    bot.start()
    print("Dang chay bam tuong (Ctrl+C de dung).")

    try:
        while True:
            time.sleep(0.2)
            if bot.front_blocked:
                print("Tuong phia truoc! Dang dung...")
    except KeyboardInterrupt:
        pass
    finally:
        bot.stop()
        print("Da dung.")


if __name__ == "__main__":
    main()
