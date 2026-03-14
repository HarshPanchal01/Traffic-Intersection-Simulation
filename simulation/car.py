import numpy as np
from scipy.integrate import ode
import pygame
import math

class Trajectory:
    def __init__(self, direction, turn):
        self.direction = direction
        self.turn = turn

        # start_pos is the center line separating the two lanes
        if direction == 'N':
            self.start_pos = (360, 0)
            self.start_angle = 180
            self.dir_vec = (0, 1)
            self.right_vec = (-1, 0)
        elif direction == 'S':
            self.start_pos = (440, 800)
            self.start_angle = 0
            self.dir_vec = (0, -1)
            self.right_vec = (1, 0)
        elif direction == 'E':
            self.start_pos = (800, 360)
            self.start_angle = 90
            self.dir_vec = (-1, 0)
            self.right_vec = (0, -1)
        elif direction == 'W':
            self.start_pos = (0, 440)
            self.start_angle = -90
            self.dir_vec = (1, 0)
            self.right_vec = (0, 1)

        self.straight_dist = 320.0
        self.arc_len = 0.0

        if turn == 'right':
            self.R = 40.0
            self.arc_len = self.R * math.pi / 2
            arc_start_pos = (self.start_pos[0] + self.dir_vec[0] * self.straight_dist,
                             self.start_pos[1] + self.dir_vec[1] * self.straight_dist)
            self.arc_center = (arc_start_pos[0] + self.right_vec[0] * self.R,
                               arc_start_pos[1] + self.right_vec[1] * self.R)
        elif turn == 'left':
            self.R = 120.0
            self.arc_len = self.R * math.pi / 2
            arc_start_pos = (self.start_pos[0] + self.dir_vec[0] * self.straight_dist,
                             self.start_pos[1] + self.dir_vec[1] * self.straight_dist)
            self.arc_center = (arc_start_pos[0] - self.right_vec[0] * self.R,
                               arc_start_pos[1] - self.right_vec[1] * self.R)

    def get_position_and_angle(self, dist):
        if dist <= self.straight_dist or self.turn == 'straight':
            x = self.start_pos[0] + self.dir_vec[0] * dist
            y = self.start_pos[1] + self.dir_vec[1] * dist
            return x, y, self.start_angle, self.right_vec[0], self.right_vec[1]

        if dist <= self.straight_dist + self.arc_len:
            arc_dist = dist - self.straight_dist
            theta = arc_dist / self.R
            cx, cy = self.arc_center

            if self.turn == 'right':
                vx, vy = -self.right_vec[0] * self.R, -self.right_vec[1] * self.R
                cos_t, sin_t = math.cos(theta), math.sin(theta)
                nx = vx * cos_t - vy * sin_t
                ny = vx * sin_t + vy * cos_t
                ang = self.start_angle - math.degrees(theta)
                rx, ry = -nx / self.R, -ny / self.R
                return cx + nx, cy + ny, ang, rx, ry

            elif self.turn == 'left':
                vx, vy = self.right_vec[0] * self.R, self.right_vec[1] * self.R
                cos_t, sin_t = math.cos(-theta), math.sin(-theta)
                nx = vx * cos_t - vy * sin_t
                ny = vx * sin_t + vy * cos_t
                ang = self.start_angle + math.degrees(theta)
                rx, ry = nx / self.R, ny / self.R
                return cx + nx, cy + ny, ang, rx, ry

        straight_2_dist = dist - self.straight_dist - self.arc_len

        if self.turn == 'right':
            end_ang = self.start_angle - 90
            new_dir = self.right_vec
            new_right = (-self.dir_vec[0], -self.dir_vec[1])
            cx, cy = self.arc_center
            vx, vy = -self.right_vec[0] * self.R, -self.right_vec[1] * self.R
            cos_t, sin_t = math.cos(math.pi/2), math.sin(math.pi/2)
            arc_end_x = cx + vx * cos_t - vy * sin_t
            arc_end_y = cy + vx * sin_t + vy * cos_t
            return arc_end_x + new_dir[0] * straight_2_dist, arc_end_y + new_dir[1] * straight_2_dist, end_ang, new_right[0], new_right[1]

        elif self.turn == 'left':
            end_ang = self.start_angle + 90
            new_dir = (-self.right_vec[0], -self.right_vec[1])
            new_right = self.dir_vec
            cx, cy = self.arc_center
            vx, vy = self.right_vec[0] * self.R, self.right_vec[1] * self.R
            cos_t, sin_t = math.cos(-math.pi/2), math.sin(-math.pi/2)
            arc_end_x = cx + vx * cos_t - vy * sin_t
            arc_end_y = cy + vx * sin_t + vy * cos_t
            return arc_end_x + new_dir[0] * straight_2_dist, arc_end_y + new_dir[1] * straight_2_dist, end_ang, new_right[0], new_right[1]

class Car:
    _BASE_IMAGE = None
    _DETAILS_IMAGE = None

    @classmethod
    def load_sprites(cls):
        if cls._BASE_IMAGE is None:
            cls._BASE_IMAGE = pygame.image.load('assets/car_base.png').convert_alpha()
            cls._DETAILS_IMAGE = pygame.image.load('assets/car_details.png').convert_alpha()

    def __init__(self, direction, turn, lane):
        Car.load_sprites()
        self.direction = direction # 'N', 'S', 'E', 'W'
        self.turn = turn # 'straight', 'left', 'right'
        self.current_lane = lane # 'left', 'right'
        self.target_lane = lane
        self.lateral_offset = -20.0 if lane == 'left' else 20.0

        self.trajectory = Trajectory(direction, turn)

        # State: [position_1d, velocity_1d]
        self.state = [0.0, 15.0] # start at 0 local distance, initial speed 15

        # Driver behaviors
        self.max_speed = np.random.uniform(25.0, 50.0)
        self.acceleration = np.random.uniform(10.0, 20.0)
        self.braking = np.random.uniform(20.0, 40.0)
        self.reaction_time = np.random.uniform(0.3, 1.5)
        self.current_reaction_timer = 0.0
        self.has_stopped_for_red = False

        self.t = 0.0
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_initial_value(self.state, self.t)

        self.length = 40
        self.width = 20
        self.color = (np.random.randint(50, 255), np.random.randint(50, 255), np.random.randint(50, 255))

        # Pre-generate un-rotated images
        self.img_off = self._create_base_image(False, False)
        self.img_left = self._create_base_image(True, False)
        self.img_right = self._create_base_image(False, True)

    def _create_base_image(self, blink_left, blink_right):
        img = self._BASE_IMAGE.copy()
        img.fill(self.color, special_flags=pygame.BLEND_MULT)
        img.blit(self._DETAILS_IMAGE, (0, 0))

        signal_color = (255, 165, 0, 255)
        if blink_left:
            pygame.draw.rect(img, signal_color, (2, 0, 4, 4))
            pygame.draw.rect(img, signal_color, (2, 36, 5, 4))
        if blink_right:
            pygame.draw.rect(img, signal_color, (14, 0, 4, 4))
            pygame.draw.rect(img, signal_color, (13, 36, 5, 4))

        return img

    def f(self, t, state, a):
        x, v = state
        return [v, a]

    def update(self, dt, light_state, distance_to_car_ahead, must_yield_left=False, can_right_on_red=False):
        v = self.state[1]
        dist_to_stop_line = self.trajectory.straight_dist - self.state[0]

        # Post-turn merging logic
        if self.state[0] > self.trajectory.straight_dist + self.trajectory.arc_len + 40.0:
            if self.turn == 'left' and self.current_lane == 'left':
                self.target_lane = 'right' # Merge back to right lane after left turn

        # Lateral offset smoothing
        target_offset = -20.0 if self.target_lane == 'left' else 20.0
        if self.lateral_offset < target_offset:
            self.lateral_offset = min(target_offset, self.lateral_offset + 30.0 * dt)
        elif self.lateral_offset > target_offset:
            self.lateral_offset = max(target_offset, self.lateral_offset - 30.0 * dt)

        self.current_lane = 'left' if self.lateral_offset < 0 else 'right'

        if light_state == 'GREEN':
            self.has_stopped_for_red = False

        a = 0.0
        braking_dist = (v**2) / (2 * self.braking) if v > 0 else 0.0

        stopping_for_light = False
        stopping_for_yield = False

        if light_state in ['RED', 'YELLOW'] and dist_to_stop_line > 0:
            if light_state == 'RED':
                if self.turn == 'right' and self.current_lane == 'right':
                    if dist_to_stop_line < 35.0 and v < 1.0:
                        self.has_stopped_for_red = True

                    if not self.has_stopped_for_red:
                        if dist_to_stop_line <= braking_dist + 30.0:
                            stopping_for_light = True
                    else:
                        if not can_right_on_red:
                            stopping_for_light = True
                else:
                    if dist_to_stop_line <= braking_dist + 30.0:
                        stopping_for_light = True
            elif light_state == 'YELLOW':
                if self.turn == 'left':
                    # If we are far from the intersection, we must stop for yellow.
                    if dist_to_stop_line > 80.0 and dist_to_stop_line <= braking_dist + 30.0:
                        stopping_for_light = True
                else:
                    if dist_to_stop_line <= braking_dist + 30.0:
                        stopping_for_light = True

        dist_to_yield_point = 0.0
        if self.turn == 'left' and must_yield_left:
            dist_to_yield_point = (self.trajectory.straight_dist + 30.0) - self.state[0]
            if dist_to_yield_point > 0:
                if dist_to_yield_point <= braking_dist + 15.0:
                    stopping_for_yield = True

        stopping_for_car = False
        if distance_to_car_ahead is not None:
            if distance_to_car_ahead <= braking_dist + self.length + 20.0:
                stopping_for_car = True

        need_to_stop = stopping_for_car or stopping_for_light or stopping_for_yield

        if need_to_stop:
            a = -self.braking
            if v <= 1.0:
                if (stopping_for_light and dist_to_stop_line < 35.0) or \
                   (stopping_for_car and distance_to_car_ahead < self.length + 25.0) or \
                   (stopping_for_yield and dist_to_yield_point < 20.0):
                    a = 0.0
                    self.state[1] = 0.0
            self.current_reaction_timer = 0.0
        else:
            if self.state[1] < 0.1:
                self.current_reaction_timer += dt
                if self.current_reaction_timer >= self.reaction_time:
                    a = self.acceleration
                else:
                    a = 0.0
            else:
                target_speed = self.max_speed

                clearing_intersection = False
                if self.turn == 'left' and light_state in ['YELLOW', 'RED'] and self.state[0] > self.trajectory.straight_dist - 30:
                    clearing_intersection = True
                if self.state[0] > self.trajectory.straight_dist - 50 and self.state[0] < self.trajectory.straight_dist + self.trajectory.arc_len:
                    if clearing_intersection:
                        target_speed = self.max_speed
                    else:
                        target_speed = self.max_speed * 0.5

                if v < target_speed:
                    if clearing_intersection:
                        a = self.acceleration * 2.0
                    else:
                        a = self.acceleration
                elif v > target_speed + 2.0:
                    a = -self.braking * 0.5
                else:
                    a = 0.0

        if v < 0.0 and a < 0.0:
            a = 0.0
            self.state[1] = 0.0

        self.solver.set_f_params(a)
        if self.solver.successful():
            self.solver.integrate(self.t + dt)
            self.t += dt
            self.state = self.solver.y
            if self.state[1] < 0:
                self.state[1] = 0.0

    def draw(self, screen):
        bx, by, ang, rx, ry = self.trajectory.get_position_and_angle(self.state[0])
        cx = bx + rx * self.lateral_offset
        cy = by + ry * self.lateral_offset

        blink_on = False
        if self.state[0] < self.trajectory.straight_dist + self.trajectory.arc_len:
            blink_on = (int(self.t * 2) % 2 == 0)

        # Also blink if changing lanes
        is_changing_lanes = (self.current_lane != self.target_lane) or (abs(self.lateral_offset) < 19.0)

        img_to_rotate = self.img_off

        if is_changing_lanes and (int(self.t * 2) % 2 == 0):
            if self.target_lane == 'left':
                img_to_rotate = self.img_left
            else:
                img_to_rotate = self.img_right
        else:
            if self.turn == 'left' and blink_on:
                img_to_rotate = self.img_left
            elif self.turn == 'right' and blink_on:
                img_to_rotate = self.img_right

        rotated_img = pygame.transform.rotate(img_to_rotate, ang)
        rect = rotated_img.get_rect(center=(cx, cy))
        screen.blit(rotated_img, rect)
