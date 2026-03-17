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
            self.start_pos = (350, 0)
            self.start_angle = 180
            self.dir_vec = (0, 1)
            self.right_vec = (-1, 0)
        elif direction == 'S':
            self.start_pos = (450, 800)
            self.start_angle = 0
            self.dir_vec = (0, -1)
            self.right_vec = (1, 0)
        elif direction == 'E':
            self.start_pos = (800, 350)
            self.start_angle = 90
            self.dir_vec = (-1, 0)
            self.right_vec = (0, -1)
        elif direction == 'W':
            self.start_pos = (0, 450)
            self.start_angle = -90
            self.dir_vec = (1, 0)
            self.right_vec = (0, 1)

        self.straight_dist = 300.0
        self.arc_len = 0.0

        if turn == 'right':
            self.R = 50.0
            self.arc_len = self.R * math.pi / 2
            arc_start_pos = (self.start_pos[0] + self.dir_vec[0] * self.straight_dist,
                             self.start_pos[1] + self.dir_vec[1] * self.straight_dist)
            self.arc_center = (arc_start_pos[0] + self.right_vec[0] * self.R,
                               arc_start_pos[1] + self.right_vec[1] * self.R)
        elif turn == 'left':
            self.R = 150.0
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

class Vehicle:
    _SPRITES = {}

    @classmethod
    def load_sprites(cls):
        if not cls._SPRITES:
            for v_type in ['car', 'small_car', 'bus', 'truck']:
                asset_name = 'car' if v_type in ['car', 'small_car'] else v_type
                
                base_img = pygame.image.load(f'assets/{asset_name}_base.png').convert_alpha()
                details_img = pygame.image.load(f'assets/{asset_name}_details.png').convert_alpha()
                
                if v_type == 'small_car':
                    # Scale down the car sprites for small vehicle
                    new_size = (int(base_img.get_width() * 0.8), int(base_img.get_height() * 0.8))
                    base_img = pygame.transform.smoothscale(base_img, new_size)
                    details_img = pygame.transform.smoothscale(details_img, new_size)

                cls._SPRITES[v_type] = {
                    'base': base_img,
                    'details': details_img
                }

    def __init__(self, direction, turn, lane, vehicle_type='car'):
        Vehicle.load_sprites()
        self.direction = direction # 'N', 'S', 'E', 'W'
        self.turn = turn # 'straight', 'left', 'right'
        self.lane = lane # 'left', 'right'
        self.vehicle_type = vehicle_type
        self.lateral_offset = -25.0 if lane == 'left' else 25.0

        self.trajectory = Trajectory(direction, turn)

        # State: [position_1d, velocity_1d]
        self.state = [-80.0, 15.0] # start off-screen, initial speed 15

        # Driver behaviors and dimensions based on vehicle type
        if vehicle_type == 'car':
            self.max_speed = np.random.uniform(25.0, 50.0)
            self.acceleration = np.random.uniform(10.0, 20.0)
            self.braking = np.random.uniform(20.0, 40.0)
            self.length = 40
            self.width = 20
        elif vehicle_type == 'small_car':
            self.max_speed = np.random.uniform(30.0, 55.0)
            self.acceleration = np.random.uniform(12.0, 25.0)
            self.braking = np.random.uniform(25.0, 45.0)
            self.length = 32
            self.width = 16
        elif vehicle_type == 'bus':
            self.max_speed = np.random.uniform(20.0, 40.0)
            self.acceleration = np.random.uniform(5.0, 12.0)
            self.braking = np.random.uniform(15.0, 30.0)
            self.length = 80
            self.width = 24
        elif vehicle_type == 'truck':
            self.max_speed = np.random.uniform(18.0, 35.0)
            self.acceleration = np.random.uniform(4.0, 10.0)
            self.braking = np.random.uniform(10.0, 25.0)
            self.length = 100
            self.width = 24

        self.reaction_time = np.random.uniform(0.3, 1.5)
        self.current_reaction_timer = 0.0
        self.has_stopped_for_red = False

        self.t = 0.0

        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_initial_value(self.state, self.t)

        self.color = (np.random.randint(50, 255), np.random.randint(50, 255), np.random.randint(50, 255))

        # Metrics
        self.wait_time = 0.0
        self.has_exited = False

        # Pre-generate un-rotated images
        self.img_off = self._create_base_image(False, False)
        self.img_left = self._create_base_image(True, False)
        self.img_right = self._create_base_image(False, True)

    def _create_base_image(self, blink_left, blink_right):
        base = self._SPRITES[self.vehicle_type]['base']
        details = self._SPRITES[self.vehicle_type]['details']
        
        img = base.copy()
        img.fill(self.color, special_flags=pygame.BLEND_MULT)
        img.blit(details, (0, 0))

        signal_color = (255, 165, 0, 255)
        # Adjust signal positions based on vehicle length (approximate front and back)
        w, l = self.width, self.length
        # The sprites are oriented facing "up" (or "right" usually, let's assume "right" for length along x-axis based on previous code)
        # Previous signal coordinates: 
        # blink_left: (2, 0, 4, 4), (2, 36, 5, 4) -> x near 0 and y near 0, x near 0 and y near 36
        # This implies length is along Y axis? Let's check: length=40, width=20. x is 0..20, y is 0..40.
        # So it's facing along Y-axis or X-axis? The original had y=36, so length is along Y axis, facing up or down.
        # blink_left: top-left (2, 0), bottom-left (2, 36).
        # blink_right: top-right (14, 0), bottom-right (13, 36). width was 20.
        
        # Let's adjust based on l and w:
        if blink_left:
            pygame.draw.rect(img, signal_color, (2, 0, 4, 4))
            pygame.draw.rect(img, signal_color, (2, l - 4, 5, 4))
        if blink_right:
            pygame.draw.rect(img, signal_color, (w - 6, 0, 4, 4))
            pygame.draw.rect(img, signal_color, (w - 7, l - 4, 5, 4))

        return img

    def f(self, t, state, a):
        x, v = state
        return [v, a]

    def update(self, dt, light_state, distance_to_vehicle_ahead, must_yield_left=False, can_right_on_red=False):
        v = self.state[1]
        dist_to_stop_line = self.trajectory.straight_dist - self.state[0]
        
        if light_state == 'GREEN':
            self.has_stopped_for_red = False
        
        a = 0.0
        braking_dist = (v**2) / (2 * self.braking) if v > 0 else 0.0
        
        stopping_for_light = False
        stopping_for_yield = False
        
        if light_state in ['RED', 'YELLOW'] and dist_to_stop_line > 0:
            if light_state == 'RED':
                if self.turn == 'right' and self.lane == 'right':
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
        if distance_to_vehicle_ahead is not None:
            if distance_to_vehicle_ahead <= braking_dist + 20.0:
                stopping_for_car = True

        need_to_stop = stopping_for_car or stopping_for_light or stopping_for_yield

        if need_to_stop:
            a = -self.braking
            if v <= 1.0:
                if (stopping_for_light and dist_to_stop_line < 35.0) or \
                   (stopping_for_car and distance_to_vehicle_ahead < 25.0) or \
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
                # If past or very close to the stop line and light is YELLOW/RED, speed up to clear
                if light_state in ['YELLOW', 'RED'] and self.state[0] > self.trajectory.straight_dist - 15:
                    clearing_intersection = True

                # Reduce speed for turns
                if self.turn != 'straight' and self.state[0] > self.trajectory.straight_dist - 50 and self.state[0] < self.trajectory.straight_dist + self.trajectory.arc_len:
                    if clearing_intersection:
                        target_speed = self.max_speed * 1.2 # Go faster than normal to clear intersection
                    else:
                        target_speed = self.max_speed * 0.5
                elif clearing_intersection:
                    target_speed = self.max_speed * 1.2

                if v < target_speed:
                    if clearing_intersection:
                        a = self.acceleration * 3.0 # punch it!
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

        # Update wait time if stationary
        if self.state[1] < 0.1:
            self.wait_time += dt

        # Mark as exited once it clears the intersection
        if not self.has_exited and self.state[0] > self.trajectory.straight_dist + self.trajectory.arc_len:
            self.has_exited = True

    def get_world_pos(self):
        bx, by, ang, rx, ry = self.trajectory.get_position_and_angle(self.state[0])
        cx = bx + rx * self.lateral_offset
        cy = by + ry * self.lateral_offset
        return cx, cy

    def draw(self, screen):
        cx, cy = self.get_world_pos()
        _, _, ang, _, _ = self.trajectory.get_position_and_angle(self.state[0])

        blink_on = False
        if self.state[0] < self.trajectory.straight_dist + self.trajectory.arc_len:
            blink_on = (int(self.t * 2) % 2 == 0)

        img_to_rotate = self.img_off

        if self.turn == 'left' and blink_on:
            img_to_rotate = self.img_left
        elif self.turn == 'right' and blink_on:
            img_to_rotate = self.img_right

        rotated_img = pygame.transform.rotate(img_to_rotate, ang)
        rect = rotated_img.get_rect(center=(cx, cy))
        screen.blit(rotated_img, rect)
