# Traffic Intersection Simulation

A hybrid continuous/discrete 2D simulation of a 4-way traffic intersection built in Python with Pygame, created for the CSCI 3010U Simulation and Modeling course project.

## Features
- **Multi-Lane Physics:** Vehicles traverse 4 distinct lanes with smooth, mathematically accurate turning trajectories and correct visual rotations.
- **Continuous Kinematics:** Vehicles realistically accelerate, cruise, and brake using the explicit Runge-Kutta (RK4) method to solve the ODEs.
- **Collision Detection & Logging:** Pairwise distance-based collision detection with real-time HUD counters and timestamped terminal logging.
- **Real-Time Analytics HUD:** Live monitoring of simulation metrics including active vehicle counts, global average wait times, throughput (vehicles/min), and maximum queue lengths.
- **Dynamic Yielding & Intersection Logic:** Optimized left-turn yielding (proceeding once oncoming traffic passes the midpoint) and safe right-turn-on-red behavior.
- **Automatic Video Capturing:** The simulation automatically records every run from the moment it starts and saves it as an `.mp4` file upon quitting.
- **Poisson Spawning:** Natural, burst-like traffic generation mathematically modeled using the inverse CDF of an exponential distribution.
- **Driver Profiles:** Vehicles feature randomized attributes for max speed, acceleration, and reaction times, creating realistic traffic waves and accordion effects.
- **Visual Polish:** Fully featured intersection with central dashed lines, curved turning road markings, dynamically rendered vehicle sprites, turn signals, and glowing traffic lights.

## Requirements
- Python 3.x
- `pygame-ce`
- `numpy`
- `scipy`
- `opencv-python`
- `matplotlib`

## Usage
Run the simulation:
```bash
python3 main.py
```

### Controls
- `p`: pause the simulation
- `r`: resume the simulation
- `s`: take a snapshot (.png)
- `q`: quit and save the recording (.mp4)

## Project Structure
- `main.py`: Entry point and Pygame visualization loop.
- `simulation/`: Core logic including kinematics, traffic lights, and spawner.
- `analytics/`: Metrics management and data collection.
- `assets/`: Image sprites for vehicles and traffic lights.
- `report/`: LaTeX source for the final project documentation.
