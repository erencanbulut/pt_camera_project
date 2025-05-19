# -*- coding: utf-8 -*-
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

# Pan motor control
def setStepPan(w1, w2, w3, w4):
    coil_A_1_pin.value = w1
    coil_A_2_pin.value = w2
    coil_B_1_pin.value = w3
    coil_B_2_pin.value = w4

def forwardPan(delay, steps):
    for i in range(steps):
        for j in range(StepCount):
            setStepPan(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)

def backwardPan(delay, steps):
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStepPan(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)

# Tilt motor control
def setStepTilt(w1, w2, w3, w4):
    coil2_A_1_pin.value = w1
    coil2_A_2_pin.value = w2
    coil2_B_1_pin.value = w3
    coil2_B_2_pin.value = w4

def downwardTilt(delay, steps):
    for i in range(steps):
        for j in range(StepCount):
            setStepTilt(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)

def upwardTilt(delay, steps):
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStepTilt(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)

# Pan Test
delay = 0.7
#steps = 170  # For each 15°
#steps = 256  # For each 45°
#steps = 341  # For each 60°
#steps = 512  # For each 90°
#steps = 1024  # For each 180°
#forwardPan(delay / 1000.0, steps)
#backwardPan(delay / 1000.0, steps)


# Tilt Test
delay = 0.9
steps = 171 # For each 60°
#steps = 341 # For each 120°
#downwardTilt(delay / 1000.0, steps)
#upwardTilt(delay / 1000.0, steps)

