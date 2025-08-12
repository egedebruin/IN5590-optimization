import math
import numpy as np
import pybullet as p
import pybullet_data
import time

def run(actions, render=False):
    # Connect and store the client ID
    if render:
        client = p.connect(p.GUI)
    else:
        client = p.connect(p.DIRECT)

    p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=client)
    p.setGravity(0, 0, -9.8, physicsClientId=client)

    p.loadURDF("plane.urdf", physicsClientId=client)
    robot = p.loadURDF("files/generated_quadruped.urdf", [0, 0, 1], physicsClientId=client)

    start_pos, _ = p.getBasePositionAndOrientation(robot, physicsClientId=client)

    amplitude_multiplier = 1.0
    frequency_multiplier = 0.02
    phase_multiplier = np.pi * 2

    for t in range(2000):
        for j in range(p.getNumJoints(robot, physicsClientId=client)):
            angle = actions[j * 3] * amplitude_multiplier * np.sin(actions[j * 3 + 1] * frequency_multiplier * t + actions[j * 3 + 2] * phase_multiplier)
            p.setJointMotorControl2(robot, j, p.POSITION_CONTROL, targetPosition=angle, physicsClientId=client)
        p.stepSimulation(physicsClientId=client)
        if render:
            time.sleep(1. / 240.)

    end_pos, _ = p.getBasePositionAndOrientation(robot, physicsClientId=client)

    displacement = math.sqrt(sum((end - start) ** 2 for start, end in zip(start_pos, end_pos)))

    p.disconnect(physicsClientId=client)
    return displacement
