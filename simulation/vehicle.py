import numpy as np
from scipy.integrate import ode
import pygame
import math

class Trajectory:
    """
    Defines the mathematical path a vehicle follows through the intersection.
    The path is represented parametrically as a function of distance traveled (dist).
    It consists of a straight segment, an optional circular arc for turning, and 
    another straight segment exiting the intersection.
    """
    def __init__(self, direction, turn):
        self.direction = direction
        self.turn = turn

        # start_pos is the center line separating the two lanes.
        # dir_vec is the unit vector pointing in the direction of initial travel.
        # right_vec is the orthogonal unit vector pointing to the right of dir_vec.
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

        # Distance from spawn to the start of the intersection box.
        self.straight_dist = 300.0
        self.arc_len = 0.0

        # Calculate the center of rotation (arc_center) and arc length for turns.
        if turn == 'right':
            self.R = 50.0
            self.arc_len = self.R * math.pi / 2
            # The start of the arc is at the end of the straight line segment
            arc_start_pos = (self.start_pos[0] + self.dir_vec[0] * self.straight_dist,
                             self.start_pos[1] + self.dir_vec[1] * self.straight_dist)
            # The center of the turning circle is R distance to the right of the arc start
            self.arc_center = (arc_start_pos[0] + self.right_vec[0] * self.R,
                               arc_start_pos[1] + self.right_vec[1] * self.R)
        elif turn == 'left':
            self.straight_dist = 300.0
            self.R = 150.0
            self.arc_len = self.R * math.pi / 2
            arc_start_pos = (self.start_pos[0] + self.dir_vec[0] * self.straight_dist,
                             self.start_pos[1] + self.dir_vec[1] * self.straight_dist)
            # The center of the turning circle is R distance to the left (negative right_vec)
            self.arc_center = (arc_start_pos[0] - self.right_vec[0] * self.R,
                               arc_start_pos[1] - self.right_vec[1] * self.R)

    def get_position_and_angle(self, dist):
        """
        Calculates the 2D world coordinates and orientation of the vehicle given its 
        1D distance traveled along the path.
        
        Returns:
            x (float): World X coordinate
            y (float): World Y coordinate
            angle (float): Orientation in degrees
            rx (float): Right-pointing unit vector X (used for lane offset)
            ry (float): Right-pointing unit vector Y
        """
        # Phase 1: Approaching the intersection (Straight line)
        if dist <= self.straight_dist or self.turn == 'straight':
            x = self.start_pos[0] + self.dir_vec[0] * dist
            y = self.start_pos[1] + self.dir_vec[1] * dist
            return x, y, self.start_angle, self.right_vec[0], self.right_vec[1]

        # Phase 2: Inside the intersection (Curved arc)
        if dist <= self.straight_dist + self.arc_len:
            arc_dist = dist - self.straight_dist
            theta = arc_dist / self.R # Angle swept along the arc in radians
            cx, cy = self.arc_center

            if self.turn == 'right':
                # Vector from arc center to the start of the arc
                vx, vy = -self.right_vec[0] * self.R, -self.right_vec[1] * self.R
                # Apply 2D rotation matrix to find current position on arc
                cos_t, sin_t = math.cos(theta), math.sin(theta)
                nx = vx * cos_t - vy * sin_t
                ny = vx * sin_t + vy * cos_t
                
                ang = self.start_angle - math.degrees(theta)
                # Calculate new right-pointing vector (normal to tangent)
                rx, ry = -nx / self.R, -ny / self.R
                return cx + nx, cy + ny, ang, rx, ry

            elif self.turn == 'left':
                # Vector from arc center to the start of the arc
                vx, vy = self.right_vec[0] * self.R, self.right_vec[1] * self.R
                # Apply 2D rotation matrix (negative theta because turning left)
                cos_t, sin_t = math.cos(-theta), math.sin(-theta)
                nx = vx * cos_t - vy * sin_t
                ny = vx * sin_t + vy * cos_t
                
                ang = self.start_angle + math.degrees(theta)
                # Calculate new right-pointing vector (normal to tangent)
                rx, ry = nx / self.R, ny / self.R
                return cx + nx, cy + ny, ang, rx, ry

        # Phase 3: Exiting the intersection (Straight line)
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

        # Initialize the ODE solver for continuous kinematics
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
        # Use actual sprite dimensions for blinker positions
        img_w, img_h = img.get_size()
        
        if blink_left:
            pygame.draw.rect(img, signal_color, (2, 0, 4, 4)) # Front left
            pygame.draw.rect(img, signal_color, (2, img_h - 4, 4, 4)) # Back left
        if blink_right:
            pygame.draw.rect(img, signal_color, (img_w - 6, 0, 4, 4)) # Front right
            pygame.draw.rect(img, signal_color, (img_w - 6, img_h - 4, 4, 4)) # Back right

        return img

    def f(self, t, state, a):
        """
        The system of first-order ordinary differential equations (ODEs).
        
        We have:
            dx/dt = v (velocity)
            dv/dt = a (acceleration)
            
        Args:
            t (float): Current simulation time
            state (list): [position, velocity]
            a (float): Current acceleration command applied by the driver
            
        Returns:
            list: [dx/dt, dv/dt]
        """
        x, v = state
        return [v, a]

    def update(self, dt, light_state, distance_to_vehicle_ahead, must_yield_left=False, can_right_on_red=False, cross_traffic_blocking=False):
        v = self.state[1]
        dist_to_stop_line = (self.trajectory.straight_dist - 30.0) - self.state[0]
        
        if light_state == 'GREEN':
            self.has_stopped_for_red = False
        
        a = 0.0
        
        # Calculate minimum safe braking distance based on current velocity.
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

        if cross_traffic_blocking and dist_to_stop_line > 0:
            if dist_to_stop_line <= braking_dist + 30.0:
                stopping_for_yield = True
                dist_to_yield_point = dist_to_stop_line

        stopping_for_car = False
        if distance_to_vehicle_ahead is not None:
            if distance_to_vehicle_ahead <= braking_dist + 40.0:
                stopping_for_car = True

        need_to_stop = stopping_for_car or stopping_for_light or stopping_for_yield

        if need_to_stop:
            a = -self.braking
            if v <= 1.0:
                if (stopping_for_light and dist_to_stop_line < 35.0) or \
                   (stopping_for_car and distance_to_vehicle_ahead < 35.0) or \
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
                if light_state in ['YELLOW', 'RED'] and self.state[0] > 255.0:
                    clearing_intersection = True

                # Reduce speed for turns
                if self.turn != 'straight' and self.state[0] > self.trajectory.straight_dist - 50 and self.state[0] < self.trajectory.straight_dist + self.trajectory.arc_len:
                    if clearing_intersection:
                        target_speed = max(self.max_speed * 1.5, 30.0) # Go faster than normal to clear intersection
                    else:
                        if self.turn == 'right':
                            target_speed = max(self.max_speed * 0.7, 20.0)
                        else:
                            target_speed = max(self.max_speed * 0.9, 24.0)
                elif clearing_intersection:
                    target_speed = max(self.max_speed * 2.0, 25.0)

                if v < target_speed:
                    if clearing_intersection:
                        a = self.acceleration * 4.0 # punch it!
                    else:
                        a = self.acceleration
                elif v > target_speed + 2.0:
                    a = -self.braking * 0.5
                else:
                    a = 0.0
        if v < 0.0 and a < 0.0:
            a = 0.0
            self.state[1] = 0.0

        # Feed the acceleration command to the ODE solver
        self.solver.set_f_params(a)
        
        # Perform explicit Runge-Kutta 4 (RK4) integration step
        if self.solver.successful():
            self.solver.integrate(self.t + dt)
            self.t += dt
            self.state = self.solver.y
            
            # Prevent moving backwards
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
            # Sync blinkers globally across all vehicles
            blink_on = ((pygame.time.get_ticks() // 500) % 2 == 0)

        img_to_rotate = self.img_off

        if self.turn == 'left' and blink_on:
            img_to_rotate = self.img_left
        elif self.turn == 'right' and blink_on:
            img_to_rotate = self.img_right

        rotated_img = pygame.transform.rotate(img_to_rotate, ang)
        rect = rotated_img.get_rect(center=(cx, cy))
        screen.blit(rotated_img, rect)
