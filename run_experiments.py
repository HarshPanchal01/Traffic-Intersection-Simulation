import pygame
import numpy as np
import math
import sys
import os

# Setup hidden pygame window for sprites to load
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

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
            if not lane_vehicles or lane_vehicles[-1].state[0] > 10.0:
                vehicles[direction].append(Vehicle(direction, turn, lane, vehicle_type))

        all_vehicles = []
        for direction in ['N', 'S', 'E', 'W']:
            if direction in ['N', 'S']:
                light_state = traffic_lights.ns_state
            else:
                light_state = traffic_lights.ew_state
                
            for i, vehicle in enumerate(vehicles[direction]):
                dist_ahead = None
                lane_vehicles_ahead = [c for c in vehicles[direction][:i] if c.lane == vehicle.lane]
                if lane_vehicles_ahead:
                    vehicle_ahead = lane_vehicles_ahead[-1]
                    pos1 = vehicle.get_world_pos()
                    pos2 = vehicle_ahead.get_world_pos()
                    center_dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                    dist_ahead = center_dist - (vehicle.length / 2) - (vehicle_ahead.length / 2)
                    
                must_yield_left = False
                can_right_on_red = False
                
                if vehicle.turn == 'left':
                    opposing_dir = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                    for opp_vehicle in vehicles[opposing_dir]:
                        if opp_vehicle.turn in ['straight', 'right']:
                            if light_state in ['YELLOW', 'RED'] and opp_vehicle.state[0] < 320:
                                continue
                            if 320 <= opp_vehicle.state[0] < 400:
                                must_yield_left = True
                                break
                            elif opp_vehicle.state[0] < 320:
                                v_opp = opp_vehicle.state[1]
                                if v_opp > 0.1:
                                    time_to_intersect = (320 - opp_vehicle.state[0]) / v_opp
                                    if time_to_intersect < 3.5:
                                        must_yield_left = True
                                        break
                                
                if vehicle.turn == 'right' and light_state == 'RED':
                    cross_left_dir = {'N':'E', 'S':'W', 'E':'S', 'W':'N'}[direction]
                    opposing_dir = {'N':'S', 'S':'N', 'E':'W', 'W':'E'}[direction]
                    
                    is_safe = True
                    for cross_vehicle in vehicles[cross_left_dir]:
                        if cross_vehicle.turn in ['straight', 'left']:
                            if 320 < cross_vehicle.state[0] < 480:
                                is_safe = False
                                break
                            elif 150 < cross_vehicle.state[0] <= 320 and cross_vehicle.state[1] > 2.0:
                                is_safe = False
                                break
                    if is_safe:
                        for opp_vehicle in vehicles[opposing_dir]:
                            if opp_vehicle.turn == 'left':
                                if 320 < opp_vehicle.state[0] < 450:
                                    is_safe = False
                                    break
                                elif 200 < opp_vehicle.state[0] <= 320 and opp_vehicle.state[1] > 2.0:
                                    is_safe = False
                                    break
                    can_right_on_red = is_safe
                    
                vehicle.update(dt, light_state, dist_ahead, must_yield_left, can_right_on_red)
                all_vehicles.append(vehicle)

        for i in range(len(all_vehicles)):
            for j in range(i + 1, len(all_vehicles)):
                car1 = all_vehicles[i]
                car2 = all_vehicles[j]
                pos1 = car1.get_world_pos()
                pos2 = car2.get_world_pos()
                dist = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                if dist < 30.0:
                    pair_id = tuple(sorted((id(car1), id(car2))))
                    if pair_id not in collided_pairs:
                        collision_count += 1
                        collided_pairs.add(pair_id)

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
    sim_time = 300 # 5 minutes per run
    
    # Experiment 1: Vary Green Light Time (fixed arrival rate)
    fixed_rate = 0.5
    green_times = [5, 10, 15, 20, 30, 40, 60]
    exp1_results = []
    
    print(f"Running Experiment 1: Varying Green Light Time (rate={fixed_rate} v/s)")
    for g in green_times:
        print(f"  Simulating Green Time = {g:02d}s... ", end='', flush=True)
        res = run_headless_sim(sim_time, fixed_rate, g)
        exp1_results.append((g, res))
        print(f"Done. Avg Wait: {res['avg_wait_time']:5.1f}s, Throughput: {res['throughput']:5.1f} v/m, Collisions: {res['collisions']}")
        
    # Experiment 2: Vary Arrival Rate (fixed green time)
    fixed_green = 20.0
    arrival_rates = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25]
    exp2_results = []
    
    print(f"\nRunning Experiment 2: Varying Arrival Rate (green_time={fixed_green}s)")
    for r in arrival_rates:
        print(f"  Simulating Arrival Rate = {r:.2f} v/s... ", end='', flush=True)
        res = run_headless_sim(sim_time, r, fixed_green)
        exp2_results.append((r, res))
        print(f"Done. Avg Wait: {res['avg_wait_time']:5.1f}s, Throughput: {res['throughput']:5.1f} v/m, Collisions: {res['collisions']}")
        
    print("\nGenerating Plots...")
    generate_plots(exp1_results, exp2_results)
    print("Plots saved in analytics/plots/ folder.")

if __name__ == "__main__":
    main()
