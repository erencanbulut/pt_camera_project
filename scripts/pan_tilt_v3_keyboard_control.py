# -*- coding: utf-8 -*-
"""
Pan and Tilt Control with Keyboard Arrow Keys
Use arrow keys to move pan and tilt motors by fixed 1° increments (5 steps for pan, 3 steps for tilt).
Press 'q' to exit.
"""
import sys
import termios
import tty
from gpiozero import OutputDevice
import time

# Define the pins as OutputDevice instances
# Pan motor pins
coil_A_1_pin = OutputDevice(24)  # pink
coil_A_2_pin = OutputDevice(4)   # orange
coil_B_1_pin = OutputDevice(23)  # blue
coil_B_2_pin = OutputDevice(25)  # yellow

# Tilt motor pins
coil2_A_1_pin = OutputDevice(18)  # pink
coil2_A_2_pin = OutputDevice(22)  # orange
coil2_B_1_pin = OutputDevice(17)  # blue
coil2_B_2_pin = OutputDevice(27)  # yellow

# Step sequence for 4-wire stepper
StepCount = 8
Seq = [
    [0, 1, 0, 0],
    [0, 1, 0, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 0, 1, 0],
    [0, 0, 1, 0],
    [0, 1, 1, 0]
]

# Movement parameters
PAN_STEPS = 5    # steps for ~1° pan
TILT_STEPS = 3    # steps for ~1° tilt
DELAY_PAN = 0.7 / 1000.0   # seconds
DELAY_TILT = 0.9 / 1000.0  # seconds

# Pan motor control functions
def setStepPan(w1, w2, w3, w4):
    coil_A_1_pin.value = w1
    coil_A_2_pin.value = w2
    coil_B_1_pin.value = w3
    coil_B_2_pin.value = w4


def forwardPan(delay, steps):
    for _ in range(steps):
        for j in range(StepCount):
            setStepPan(*Seq[j])
            time.sleep(delay)


def backwardPan(delay, steps):
    for _ in range(steps):
        for j in reversed(range(StepCount)):
            setStepPan(*Seq[j])
            time.sleep(delay)

# Tilt motor control functions
def setStepTilt(w1, w2, w3, w4):
    coil2_A_1_pin.value = w1
    coil2_A_2_pin.value = w2
    coil2_B_1_pin.value = w3
    coil2_B_2_pin.value = w4


def upwardTilt(delay, steps):
    for _ in range(steps):
        for j in reversed(range(StepCount)):
            setStepTilt(*Seq[j])
            time.sleep(delay)


def downwardTilt(delay, steps):
    for _ in range(steps):
        for j in range(StepCount):
            setStepTilt(*Seq[j])
            time.sleep(delay)

# Get a single character (including arrow keys) from stdin

def getKey():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == '\x1b':  # ANSI escape sequence
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Main control loop
if __name__ == '__main__':
    print("Use arrow keys to pan/tilt (1° per press). Press 'q' to quit.")
    try:
        while True:
            key = getKey()
            if key == 'q':
                print("Exiting.")
                break
            elif key == '\x1b[C':  # Right arrow
                print("Pan right 1°")
                forwardPan(DELAY_PAN, PAN_STEPS)
            elif key == '\x1b[D':  # Left arrow
                print("Pan left 1°")
                backwardPan(DELAY_PAN, PAN_STEPS)
            elif key == '\x1b[A':  # Up arrow
                print("Tilt up 1°")
                upwardTilt(DELAY_TILT, TILT_STEPS)
            elif key == '\x1b[B':  # Down arrow
                print("Tilt down 1°")
                downwardTilt(DELAY_TILT, TILT_STEPS)
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting.")
    finally:
        # Reset all coils off
        setStepPan(0,0,0,0)
        setStepTilt(0,0,0,0)
