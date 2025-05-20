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

def backwardsPan(delay, steps):
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStepPan(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)

def forwardPanWithAcceleration(initial_delay, final_delay, steps):
    """Move the pan motor forward with acceleration."""
    delay = initial_delay
    step_decrement = (initial_delay - final_delay) / steps
    for i in range(steps):
        for j in range(StepCount):
            setStepPan(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
        delay = max(final_delay, delay - step_decrement)

def backwardPanWithAcceleration(initial_delay, final_delay, steps):
    """Move the pan motor backward with acceleration."""
    delay = initial_delay
    step_decrement = (initial_delay - final_delay) / steps
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStepPan(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
        delay = max(final_delay, delay - step_decrement)

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

def downwardTiltWithAcceleration(initial_delay, final_delay, steps):
    """Move the tilt motor downward with acceleration."""
    delay = initial_delay
    step_decrement = (initial_delay - final_delay) / steps
    for i in range(steps):
        for j in range(StepCount):
            setStepTilt(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
        delay = max(final_delay, delay - step_decrement)

def upwardTiltWithAcceleration(initial_delay, final_delay, steps):
    """Move the tilt motor upward with acceleration."""
    delay = initial_delay
    step_decrement = (initial_delay - final_delay) / steps
    for i in range(steps):
        for j in reversed(range(StepCount)):
            setStepTilt(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
        delay = max(final_delay, delay - step_decrement)

# Minimum delay (for max speed): 0.7ms.
# Pan Test
delay = 0.7
steps = 300
forwardPan(delay / 1000.0, steps)
backwardsPan(delay / 1000.0, steps)

# Pan Test with Acceleration
initial_delay = 0.8
final_delay = 0.7
forwardPanWithAcceleration(initial_delay  / 1000.0, final_delay/ 1000.0, steps)
backwardPanWithAcceleration(initial_delay  / 1000.0, final_delay / 1000.0, steps)

# Minimum delay (for max speed): 0.9ms.
# Tilt Test
delay = 0.9
steps = 200
downwardTilt(delay / 1000.0, steps)
upwardTilt(delay / 1000.0, steps)

# Tilt Test with Acceleration
initial_delay = 1.0
final_delay = 0.7
downwardTiltWithAcceleration(initial_delay / 1000.0, final_delay / 1000.0, steps)
upwardTiltWithAcceleration(initial_delay / 1000.0, final_delay / 1000.0, steps)
