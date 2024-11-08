# Adaptive Traffic Signal Timer
![traffic-signal](https://github.com/user-attachments/assets/7a927f31-2b37-478e-a723-bd6362991251)

### Adaptive Traffic Signal Timer

This Adaptive Traffic Signal Timer uses live images from the cameras at traffic junctions for traffic density calculation using YOLO object detection and sets the signal timers accordingly, thus reducing the traffic congestion on roads, providing faster transit to people, and reducing fuel consumption.

### Inspiration

Traffic congestion is becoming one of the critical issues with the increasing population and automobiles in cities. Traffic jams not only cause extra delay and stress for drivers but also increase fuel consumption and air pollution.

According to the TomTom Traffic Index, 3 of the top 10 cities facing the most traffic congestion are in India: Mumbai, Bengaluru, and New Delhi. People are compelled to spend hours stuck in traffic jams, wasting valuable time in daily commutes. Current traffic light controllers use fixed timers and do not adapt to real-time traffic conditions on the road.

To address this, we developed an improved traffic management system using a Computer Vision-based traffic light controller that autonomously adapts to traffic at intersections. The proposed system adjusts the green signal duration based on traffic density, giving longer green times to directions with heavier traffic and reducing wait times at busy intersections.

### Additional Features

1. Congestion Alerts: Provides real-time updates about traffic jams to previous signals , helping them choose better routes and avoid congested areas.


2. Emergency Vehicle Priority: Detects emergency vehicle sirens and changes signals to give priority to ambulances, fire trucks, or police vehicles, ensuring they have a clear path through intersections.


3. Signal Fault Detection: Monitors traffic signals for malfunctions, such as lights stuck on not functioning. It instantly alerts authorities, allowing quick repairs and minimizing disruptions.


4. Red Light Violation Detection: Identifies vehicles that run red lights, capturing violations to help enforce traffic laws and improve safety.


5. Peak Hour Optimization: if four way junction experience the heavy traffic during that time system analysis the past data that store on the server and adjust the green signal timing accordingly 



------------------------------------------
### Implementation Details

This project can be broken down into 3 modules:

1. `Vehicle Detection Module` - This module is responsible for detecting the number of vehicles in the image received as input from the camera. More specifically, it will provide as output the number of vehicles of each vehicle class such as car, bike, bus, truck, and rickshaw.

2. `Signal Switching Algorithm` - This algorithm updates the red, green, and yellow times of all signals. These timers are set bases on the count of vehicles of each class received from the vehicle detection module and several other factors such as the number of lanes, average speed of each class of vehicle, etc. 

3. `Simulation Module` - A simulation is developed from scratch using [Pygame](https://www.pygame.org/news) library to simulate traffic signals and vehicles moving across a traffic intersection.

   ------------------------------------------
### Prerequisites

1. [Python 3.7](https://www.python.org/downloads/release/python-370/)
2. [Microsoft Visual C++ build tools](http://go.microsoft.com/fwlink/?LinkId=691126&fixForIE=.exe.) (For Windows only)

------------------------------------------
### Installation

* Step I: Clone the Repository
```sh
      $ git clone https://github.com/mihir-m-gandhi/Adaptive-Traffic-Signal-Timer
```

* Step II: Download the weights file from [here](https://drive.google.com/file/d/1flTehMwmGg-PMEeQCsDS2VWRLGzV6Wdo/view?usp=sharing) and place it in the Adaptive-Traffic-Signal-Timer/Code/YOLO/darkflow/bin directory

* Step III: Install the required packages
```sh
      # On the terminal, move into Adaptive-Traffic-Signal-Timer/Code/YOLO/darkflow directory
      $ cd Adaptive-Traffic-Signal-Timer/Code/YOLO/darkflow
      $ pip install -r requirements.txt
      $ python setup.py build_ext --inplace
```

* Step IV: Run the code
```sh
      # To run vehicle detection
      $ python vehicle_detection.py
      
      # To run simulation
      $ python simulation.py
```

------------------------------------------
### Demo
Simulation Demonstration:  [Click](https://drive.google.com/drive/folders/1RO7SM88A_VNxnZvil1Jpp3BAMKBh6JB_?usp=sharing) to view the simulation of our  proposed system.

![](https://drive.google.com/file/d/17TLH60VoSxW6PFZHFpM82vaRdutnihgT/view?usp=sharing)
* `Vehicle Detection`

<p align="center">
  <img height="400px" src="https://github.com/Saravanarajan25/ai-based-traffic-management/raw/main/vehicle-detection.png" alt="Vehicle Detection">
</p>

<br> 

* `Signal Switching Algorithm and Simulation`

<p align="center">
    <img src="./Demo.gif">
</p>

