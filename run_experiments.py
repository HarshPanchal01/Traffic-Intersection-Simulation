import pygame
import math

from simulation.traffic_light import TrafficLightSystem
from simulation.spawner import Spawner
from simulation.vehicle import Vehicle
from analytics.metrics import MetricsManager
from analytics.plotter import generate_plots

def run_headless_sim(sim_time_limit, spawn_rate, green_time, dt=1.0/60.0):
    traffic_lights = TrafficLightSystem(ns_green=green_time, ew_green=green_time)
    spawner = Spawner(rate=spawn_rate)
    vehicles = {'N': [], 'S': [], 'E': [], 'W': []}
    metrics = MetricsManager()
    
    total_sim_time = 0.0
    collision_count = 0
    collided_pairs = set()

    while total_sim_time < sim_time_limit:
        total_sim_time += dt
        
        # Update logic
        traffic_lights.update(dt)
        new_vehicles = spawner.update(dt)
        for direction, turn, lane, vehicle_type in new_vehicles:
            lane_vehicles = [c for c in vehicles[direction] if c.lane == lane]
            if not lane_vehicles or lane_vehicles[-1].state[0] > 50.0:
                vehicles[direction].append(Vehicle(direction, turn, lane, vehicle_type))

        all_vehicles = []
        for direction in ['N', 'S', 'E', 'W']:
            if direction in ['N', 'S']:
                light_state = traffic_lights.ns_state
            else:
                light_state = traffic_lights.ew_state
                
            for i, vehicle in enumerate(vehicles[direction]):
                # Find the closest vehicle ahead, including those from other directions that merged.
                min_dist_ahead = float('inf')
                
                lane_vehicles_ahead = [c for c in vehicles[direction][:i] if c.lane == vehicle.lane]
                if lane_vehicles_ahead:
                    vehicle_ahead = lane_vehicles_ahead[-1]
                    # 1D Distance = Position of car ahead - Position of current car - their half lengths
                    d = vehicle_ahead.state[0] - vehicle.state[0] - (vehicle.length / 2) - (vehicle_ahead.length / 2)
                    if d > 0 and d < min_dist_ahead:
                        min_dist_ahead = d

                pos1 = vehicle.get_world_pos()
                _, _, _, rx, ry = vehicle.trajectory.get_position_and_angle(vehicle.state[0])
                dx_dir, dy_dir = ry, -rx
                
                for other_dir in ['N', 'S', 'E', 'W']:
                    if other_dir == direction: continue
                    for ov in vehicles[other_dir]:
                        if ov.state[0] > 300: # Has started turning / merged
                            pos2 = ov.get_world_pos()
                            dx = pos2[0] - pos1[0]
                            dy = pos2[1] - pos1[1]
                            
                            _, _, _, ov_rx, ov_ry = ov.trajectory.get_position_and_angle(ov.state[0])
                            ov_dx_dir, ov_dy_dir = ov_ry, -ov_rx
                            
                            if (dx_dir * ov_dx_dir + dy_dir * ov_dy_dir) > 0.5:
                                forward_dist = dx * dx_dir + dy * dy_dir
                                if forward_dist > 0:
                                    lateral_dist = abs(dx * rx + dy * ry)
                                    if lateral_dist < 15.0:
                                        d = forward_dist - (vehicle.length / 2) - (ov.length / 2)
                                        if d > 0 and d < min_dist_ahead:
                                            min_dist_ahead = d
                                        
                dist_ahead = min_dist_ahead if min_dist_ahead != float('inf') else None
                    
                must_yield_left = False
                can_right_on_red = False
                
                if vehicle.turn == 'left':
                    opposing_dir = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                    for opp_vehicle in vehicles[opposing_dir]:
                        if opp_vehicle.turn in ['straight', 'right']:
                            if light_state in ['YELLOW', 'RED'] and opp_vehicle.state[0] < 270:
                                continue
                            if 270 <= opp_vehicle.state[0] < 450:
                                must_yield_left = True
                                break
                            elif opp_vehicle.state[0] < 270:
                                v_opp = opp_vehicle.state[1]
                                if v_opp > 0.1:
                                    time_to_intersect = (270 - opp_vehicle.state[0]) / v_opp
                                    if time_to_intersect < 5.5:
                                        must_yield_left = True
                                        break
                                
                if vehicle.turn == 'right' and light_state == 'RED':
                    cross_left_dir = {'N':'E', 'S':'W', 'E':'S', 'W':'N'}[direction]
                    opposing_dir = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                    
                    is_safe = True
                    for cross_vehicle in vehicles[cross_left_dir]:
                        if cross_vehicle.turn in ['straight', 'left']:
                            if 250 < cross_vehicle.state[0] < 500:
                                is_safe = False
                                break
                            elif cross_vehicle.state[0] <= 250 and cross_vehicle.state[1] > 0.1:
                                time_to_intersect = (270 - cross_vehicle.state[0]) / cross_vehicle.state[1]
                                if time_to_intersect < 5.0:
                                    is_safe = False
                                    break
                    if is_safe:
                        for opp_vehicle in vehicles[opposing_dir]:
                            if opp_vehicle.turn == 'left':
                                if 250 < opp_vehicle.state[0] < 500:
                                    is_safe = False
                                    break
                                elif opp_vehicle.state[0] <= 250 and opp_vehicle.state[1] > 0.1:
                                    time_to_intersect = (270 - opp_vehicle.state[0]) / opp_vehicle.state[1]
                                    if time_to_intersect < 5.0:
                                        is_safe = False
                                        break
                    can_right_on_red = is_safe
                    
                cross_traffic_blocking = False
                if vehicle.state[0] < 270:
                    cross_dirs = ['E', 'W'] if direction in ['N', 'S'] else ['N', 'S']
                    for c_dir in cross_dirs:
                        for cv in vehicles[c_dir]:
                            if 300 < cv.state[0] < 500 and cv.state[1] < 15.0:
                                cross_traffic_blocking = True
                                break
                        if cross_traffic_blocking:
                            break
                            
                vehicle.update(dt, light_state, dist_ahead, must_yield_left, can_right_on_red, cross_traffic_blocking)
                all_vehicles.append(vehicle)

        # Collision detection
        for i in range(len(all_vehicles)):
            for j in range(i + 1, len(all_vehicles)):
                car1 = all_vehicles[i]
                car2 = all_vehicles[j]
                pos1 = car1.get_world_pos()
                pos2 = car2.get_world_pos()
                
                # Distance formula: d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
                dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                
                if dist < 30.0:
                    pair_id = tuple(sorted((id(car1), id(car2))))
                    if pair_id not in collided_pairs:
                        collision_count += 1
                        collided_pairs.add(pair_id)
                        print(f"\nCollision Detected! {car1.direction}-{car1.turn} ({car1.state[0]:.1f}) vs {car2.direction}-{car2.turn} ({car2.state[0]:.1f})")

        metrics.update_max_queue(vehicles)

        for direction in ['N', 'S', 'E', 'W']:
            for vehicle in vehicles[direction]:
                if vehicle.state[0] >= 850.0:
                    collided_pairs = {p for p in collided_pairs if id(vehicle) not in p}
                    metrics.add_completed_vehicle(vehicle)
            vehicles[direction] = [vehicle for vehicle in vehicles[direction] if vehicle.state[0] < 850.0]

    return {
        'avg_wait_time': metrics.get_avg_wait_time(),
        'throughput': metrics.get_throughput(sim_time_limit),
        'max_queue_length': metrics.max_queue_length,
        'collisions': collision_count
    }

def main():
    # Setup hidden pygame window for sprites to load
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    sim_time = 300 # 5 minutes per run
    
    # Experiment 1: Vary Green Light Time (fixed arrival rate)
    fixed_rate = 0.5
    green_times = [5, 10, 15, 20, 30, 40, 60]
    exp1_results = []
    
    print(f"Running Experiment 1: Varying Green Light Time (rate = {fixed_rate} vehicles/second)")
    for g in green_times:
        print(f"Simulating Green Time = {g:02d}s... ", end='', flush=True)
        res = run_headless_sim(sim_time, fixed_rate, g)
        exp1_results.append((g, res))
        print(f"Done. Avg Wait: {res['avg_wait_time']:5.1f}s, Throughput: {res['throughput']:5.1f} veh/min, Collisions: {res['collisions']}")
        
    # Experiment 2: Vary Arrival Rate (fixed green time)
    fixed_green = 20.0
    arrival_rates = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25]
    exp2_results = []
    
    print(f"\nRunning Experiment 2: Varying Arrival Rate (Green Time = {fixed_green} seconds)")
    for r in arrival_rates:
        print(f"Simulating Arrival Rate = {r:.2f} veh/sec... ", end='', flush=True)
        res = run_headless_sim(sim_time, r, fixed_green)
        exp2_results.append((r, res))
        print(f"Done. Avg Wait: {res['avg_wait_time']:5.1f}s, Throughput: {res['throughput']:5.1f} veh/min, Collisions: {res['collisions']}")
        
    print("\nGenerating Plots...")
    generate_plots(exp1_results, exp2_results)
    print("Plots saved in analytics/plots/ folder.")

if __name__ == "__main__":
    main()
