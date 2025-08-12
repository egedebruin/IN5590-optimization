import math

from gymnasium import Env, spaces
import numpy as np
import pygame
from Box2D import b2World, b2PolygonShape, b2FixtureDef, b2RevoluteJointDef, \
    b2Vec2


class MyBipedalWalker(Env):
    metadata = {"render_modes": ["human"], "render_fps": 50}

    def __init__(self, render_mode=None):
        super().__init__()

        self.action_space = spaces.Box(low=-1, high=1, shape=(6,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32)

        self.world = b2World(gravity=(0, -9.8), doSleep=True)

        self.ground_body = self.world.CreateStaticBody(
            position=(-250, 0),
            shapes=b2PolygonShape(box=(500, 1)),
        )

        self.rail = self.world.CreateStaticBody(position=(0, 0))

        # --------------------------
        # ---- Adjustable params ----
        torso_height = 1.7
        torso_height_variability = 0.25
        torso_length = 0.2
        torso_width = 0.5
        upper_leg_length = 1
        lower_leg_length = 0.5
        upper_leg_width = 0.1
        lower_leg_width = 0.1
        upper_leg_angle_deg = 20  # deg
        # --------------------------

        # Torso
        self.torso = self.world.CreateDynamicBody(
            position=(0, torso_height - (torso_length / 2) + 1),
            fixtures=b2FixtureDef(
                shape=b2PolygonShape(box=(torso_width / 2, torso_length / 2)),
                density=1.0,
                friction=0.3
            )
        )
        self.torso.fixedRotation = True

        # Carrier body to separate X and Y constraints
        self.carrier = self.world.CreateDynamicBody(
            position=self.torso.position,
            fixedRotation=True
        )

        # X motion: rail <-> carrier
        self.prismatic_joint_x = self.world.CreatePrismaticJoint(
            bodyA=self.rail,
            bodyB=self.carrier,
            anchor=self.carrier.position,
            axis=(1, 0),
            lowerTranslation=-100,
            upperTranslation=100,
            enableLimit=True,
        )

        # Y motion: carrier <-> torso
        self.prismatic_joint_y = self.world.CreatePrismaticJoint(
            bodyA=self.carrier,
            bodyB=self.torso,
            anchor=self.torso.position,
            axis=(0, 1),
            lowerTranslation=-torso_height_variability,
            upperTranslation=torso_height_variability,
            enableLimit=True,
        )

        # Where the upper legs attach (bottom of torso)
        local_offset = b2Vec2(0, -torso_length / 2)
        hip_anchor_world = self.torso.GetWorldPoint(local_offset)

        # ---- Upper legs ----
        self.upper_leg1 = self._create_leg(hip_anchor_world, upper_leg_length, upper_leg_width)
        self.upper_leg2 = self._create_leg(hip_anchor_world, upper_leg_length, upper_leg_width)

        # Rotate upper legs first!
        self.upper_leg1.angle = math.radians(upper_leg_angle_deg)
        self.upper_leg2.angle = math.radians(upper_leg_angle_deg)

        # Compute knee anchor at bottom end of each upper leg
        local_knee_offset = b2Vec2(0, -upper_leg_length)
        knee1_world = self.upper_leg1.GetWorldPoint(local_knee_offset)
        knee2_world = self.upper_leg2.GetWorldPoint(local_knee_offset)

        # ---- Lower legs ----
        self.lower_leg1 = self._create_leg(knee1_world, lower_leg_length, lower_leg_width)
        self.lower_leg2 = self._create_leg(knee2_world, lower_leg_length, lower_leg_width)

        # ---- Joints ----
        self.hip1 = self.world.CreateWeldJoint(
            bodyA=self.torso,
            bodyB=self.upper_leg1,
            anchor=hip_anchor_world
        )
        self.hip2 = self.world.CreateWeldJoint(
            bodyA=self.torso,
            bodyB=self.upper_leg2,
            anchor=hip_anchor_world
        )

        self.knee1 = self._create_joint(self.upper_leg1, self.lower_leg1, anchor=knee1_world)
        self.knee2 = self._create_joint(self.upper_leg2, self.lower_leg2, anchor=knee2_world)

        self.time = 0.0
        self.render_mode = render_mode
        self.screen = None
        self.clock = None
        self.PPM = 100

    def _create_leg(self, pos, length, width):
        # Create lower leg: box is offset so top end aligns with origin
        fixture = b2FixtureDef(
            shape=b2PolygonShape(box=(width / 2, length / 2, (0, -length / 2), 0)),
            density=1.0,
            friction=0.3
        )
        fixture.filter.categoryBits = 0x0002
        fixture.filter.maskBits = 0x0001  # only collide with ground

        return self.world.CreateDynamicBody(
            position=pos,
            fixtures=fixture
        )

    def _create_joint(self, bodyA, bodyB, anchor, motor=True):
        joint_def = b2RevoluteJointDef(
            bodyA=bodyA,
            bodyB=bodyB,
            localAnchorA=bodyA.GetLocalPoint(anchor),
            localAnchorB=bodyB.GetLocalPoint(anchor),
            enableMotor=motor,
            maxMotorTorque=1000,
            motorSpeed=0
        )
        joint_def.enableLimit = True
        joint_def.lowerAngle = math.radians(-60)
        joint_def.upperAngle = math.radians(60)  # e.g., 1.0  (about 57.3 degrees)
        return self.world.CreateJoint(joint_def)

    def step(self, action):
        amp1, freq1, phase1, amp2, freq2, phase2 = action
        frequency_multiplier = 8
        amplitude_multiplier = math.radians(60)
        phase_multiplier = 2 * np.pi

        knee1_target_angle = amp1 * amplitude_multiplier * np.sin(freq1 * frequency_multiplier * self.time + phase1 * phase_multiplier)
        knee2_target_angle = amp2 * amplitude_multiplier * np.sin(freq2 * frequency_multiplier * self.time + phase2 * phase_multiplier)

        # Apply sine wave motor speeds
        self.knee1.motorSpeed = (knee1_target_angle - self.knee1.angle) * 5
        self.knee2.motorSpeed = (knee2_target_angle - self.knee2.angle) * 5

        # Step physics
        self.world.Step(1.0 / 50, 6, 2)
        self.time += 1.0 / 50

        # Observations (very simple example)
        obs = np.array([
            self.torso.position.x, self.torso.position.y,
            self.upper_leg1.angle, self.lower_leg1.angle,
            self.upper_leg2.angle, self.lower_leg2.angle,
            self.knee1.motorSpeed, self.knee2.motorSpeed,
        ], dtype=np.float32)

        reward = self.torso.position.x  # encourage forward movement

        terminated = False
        truncated = False

        return obs, reward, terminated, truncated, {}

    def reset(self, seed=None, options=None):
        # For simplicity, recreate world
        self.__init__()
        obs = np.zeros(8, dtype=np.float32)
        info = {}
        return obs, info

    def render(self):
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((800, 600))
            self.clock = pygame.time.Clock()

        self.screen.fill((255, 255, 255))

        # Camera offset so torso is horizontally centered, vertically fixed near bottom
        torso_pos = self.torso.position
        camera_x = torso_pos.x * self.PPM - 400  # 400 is half screen width

        def world_to_screen(world_point):
            # Convert Box2D coordinates to screen pixels and apply camera offset
            x = (world_point[0] * self.PPM) - camera_x
            y = 600 - (world_point[1] * self.PPM)  # flip Y axis
            return (int(x), int(y))

        # Draw ground as a large rectangle spanning wide area
        ground_y = 1  # ground height in meters
        ground_rect = pygame.Rect(
            -camera_x, 600 - (ground_y * self.PPM),
                       200 * self.PPM, 10
        )
        pygame.draw.rect(self.screen, (0, 0, 0), ground_rect)

        # Draw all bodies
        for body in [self.torso, self.upper_leg1, self.lower_leg1, self.upper_leg2, self.lower_leg2]:
            for fixture in body.fixtures:
                shape = fixture.shape
                vertices = [world_to_screen(body.transform * v) for v in shape.vertices]
                pygame.draw.polygon(self.screen, (0, 0, 255), vertices)

        # for fixture in self.ground_body.fixtures:
        #     shape = fixture.shape
        #     vertices = [world_to_screen(self.ground_body.transform * v) for v in shape.vertices]
        #     pygame.draw.polygon(self.screen, (0, 0, 0), vertices)

        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.screen:
            pygame.quit()
