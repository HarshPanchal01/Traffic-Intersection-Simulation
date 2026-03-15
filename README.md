# Traffic Intersection Simulation

A hybrid continuous/discrete 2D simulation of a 4-way traffic intersection built in Python with Pygame, created for the CSCI 3010U Simulation and Modeling course project.

## Features
- **Multi-Lane Physics:** Cars traverse 4 distinct lanes with smooth, mathematically accurate turning trajectories and correct visual rotations.
- **Continuous Kinematics:** Vehicles realistically accelerate, cruise, and brake using the explicit Runge-Kutta (RK4) method to solve the ODEs.
- **Dynamic Yielding & Intersection Logic:** Left-turning cars safely yield to moving oncoming traffic. Right-turning cars can turn on red after stopping if the coast is clear.
- **Traffic Light State Machine:** Fully functional configurable traffic light system that correctly handles N/S and E/W lane cycling.
- **Poisson Spawning:** Natural, burst-like traffic generation mathematically modeled using the inverse CDF of an exponential distribution.
- **Driver Profiles:** Vehicles feature randomized attributes for max speed, acceleration, and reaction times, creating realistic traffic waves and accordion effects.
- **Visual Polish:** Fully featured intersection with central dashed lines, curved turning road markings, dynamically rendered car sprites, turn signals, and glowing traffic lights.

## Requirements
- Python 3.x
- `pygame`
- `numpy`
- `scipy`
- `matplotlib`

## Usage
Run the simulation:
```bash
python3 main.py
```

### Controls
- `p`: Pause the simulation
- `r`: Resume the simulation
- `q`: Stop the simulation and quit
