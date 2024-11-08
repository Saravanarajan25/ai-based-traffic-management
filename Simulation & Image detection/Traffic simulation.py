# LAG
# NO. OF VEHICLES IN SIGNAL CLASS
# stops not used
# DISTRIBUTION
# BUS TOUCHING ON TURNS
# Distribution using python class

# *** IMAGE XY COOD IS TOP LEFT
import random
import math
import time
import threading
# from vehicle_detection import detection
import pygame
import sys
import os
from datetime import datetime
import pandas as pd
from openpyxl import Workbook, load_workbook
# options={
#    'model':'./cfg/yolo.cfg',     #specifying the path of model
#    'load':'./bin/yolov2.weights',   #weights
#    'threshold':0.3     #minimum confidence factor to create a box, greater than 0.3 good
# }

# tfnet=TFNet(options)    #READ ABOUT TFNET

# Default values of signal times
defaultRed = 150
defaultYellow = 5
defaultGreen = 10
defaultMinimum = 30
defaultMaximum = 45

signals = []
noOfSignals = 4
simTime = 300       # change this to change time of simulation
timeElapsed = 0

currentGreen = 0   # Indicates which signal is green
nextGreen = (currentGreen+1)%noOfSignals
currentYellow = 0   # Indicates whether yellow signal is on or off 

# Average times for vehicles to pass the intersection
carTime = 2
bikeTime = 1
rickshawTime = 2.25 
busTime = 2.5
truckTime = 2.5

# Count of cars at a traffic signal
noOfCars = 0
noOfBikes = 0
noOfBuses =0
noOfTrucks = 0
noOfRickshaws = 0
noOfLanes = 2

# Red signal time at which cars will be detected at a signal
detectionTime = 5

speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'rickshaw':2, 'bike':2.5 , 'ambulance' : 3}  # average speeds of vehicles

# Coordinates of start
x = {'right':[0,0,0], 'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}    
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[498,466,436], 'up':[800,800,800]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'rickshaw', 4:'bike', 5:'ambulance'}

directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}
directionToIndex = {v: k for k, v in directionNumbers.items()}
currentGreen = directionToIndex['right']


# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods = [(530,210),(810,210),(810,550),(530,550)]
vehicleCountCoods = [(480,210),(880,210),(880,550),(480,550)]
vehicleCountTexts = ["0", "0", "0", "0"]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

mid = {'right': {'x':705, 'y':445}, 'down': {'x':695, 'y':450}, 'left': {'x':695, 'y':425}, 'up': {'x':695, 'y':400}}
rotationAngle = 3

# Gap between vehicles
gap = 15    # stopping gap
gap2 = 15   # moving gap


# Define a variable to track the current green signal
currentGreen = 0  # Example: 0 for 'right', 1 for 'down', etc.

# Define the normal signal rotation (example: cycling through directions)
normalSignalRotation = [0, 1, 2, 3]  # Order of signal rotation
normalSignalIndex = 0  # Index to track current signal in the normal rotation


pygame.init()
simulation = pygame.sprite.Group()

class EmergencyVehicleManager:
    def _init_(self, signals, vehicles, no_of_signals, direction_to_index, default_signal_times):
        """
        Initialize the Emergency Vehicle Manager.
        
        signals: dict -> Dictionary of all traffic signals in the simulation.
        vehicles: dict -> Dictionary containing lists of vehicles for each direction.
        no_of_signals: int -> The total number of signals in the system.
        direction_to_index: dict -> Maps direction to signal index.
        default_signal_times: dict -> Default times for red, yellow, green signals.
        """
        self.signals = signals
        self.vehicles = vehicles
        self.no_of_signals = no_of_signals
        self.direction_to_index = direction_to_index
        self.default_signal_times = default_signal_times

    def detect_ambulance(self):
        """
        Detect if an ambulance is waiting at any signal.
        
        Returns the direction where the ambulance is waiting, or None if no ambulance is waiting.
        """
        for direction, vehicle_list in self.vehicles.items():
            for vehicle in vehicle_list:
                if isinstance(vehicle, Ambulance):  # Assuming Ambulance class is defined
                    return direction
        return None
    
    def handle_ambulance(self, ambulance_signal):
        """
        Handle the ambulance by setting the appropriate signal to green and 
        all other signals to red.
        
        ambulance_signal: str -> The direction from which the ambulance is coming.
        """
        ambulance_index = self.direction_to_index[ambulance_signal]
        
        # Set the ambulance signal to green immediately if it’s not already green
        if self.signals[ambulance_signal].state != 'green':
            self.change_signal_state(ambulance_signal, 'green')

        # Set all other signals to red
        for direction in self.signals:
            if direction != ambulance_signal:
                self.change_signal_state(direction, 'red')

        print(f"Ambulance is given priority. Green signal set for {ambulance_signal}.")

        # Let the ambulance pass for 5 seconds (can be adjusted)
        time.sleep(5)
        self.reset_signals()

    def change_signal_state(self, direction, state):
        """
        Change the state of the traffic signal for a specific direction.
        
        direction: str -> Direction of the signal (e.g., 'left', 'right', 'up', 'down')
        state: str -> New state of the signal (e.g., 'green', 'red', 'yellow')
        """
        self.signals[direction].state = state
        if state == 'green':
            self.signals[direction].signalText = "GO"
        elif state == 'red':
            self.signals[direction].signalText = "STOP"
        elif state == 'yellow':
            self.signals[direction].signalText = "SLOW"
        
        print(f"Signal for {direction} is now {state.upper()}.")

    def reset_signals(self):
        """
        Reset all signals to their default state after handling the ambulance.
        """
        for direction in self.signals:
            signal = self.signals[direction]
            signal.state = 'red'
            signal.signalText = "STOP"
            signal.green = self.default_signal_times[direction]['green']
            signal.yellow = self.default_signal_times[direction]['yellow']
            signal.red = self.default_signal_times[direction]['red']
        
        # Reset to the next scheduled green signal
        self.resume_normal_operation()

    def resume_normal_operation(self):
        """
        Resume normal traffic signal operation after the ambulance has cleared the intersection.
        """
        # For simplicity, set to the next scheduled green signal (you can customize this logic)
        next_green_signal = self.get_next_green_signal()
        self.change_signal_state(next_green_signal, 'green')
        print(f"Resuming normal operation. Next green signal is for {next_green_signal}.")

    def get_next_green_signal(self):
        """
        Get the next signal that should be green based on the simulation logic.
        
        Returns the direction of the next green signal.
        """
        # Assuming there is a logic to determine which signal is green next based on timings or priority
        # For simplicity, we cycle through the signals in a round-robin fashion
        return 'left'  # You can customize this logic based on your system


class TrafficSignal:
    def _init_(self, red, yellow, green, minimum, maximum , signal_position, state='red'):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0
        self.position = signal_position  # Position where the signal is located
        self.state = state  # 'red', 'green', 'yellow'
    
   

import time

class TrafficController:
    def _init_(self):
        self.signals = {
            'left': TrafficSignal(30, 5, 45, 5, 60, 1, 'left'),
            'right': TrafficSignal(30, 5, 45, 5, 60, 2, 'right'),
            'up': TrafficSignal(30, 5, 45, 5, 60, 3, 'up'),
            'down': TrafficSignal(30, 5, 45, 5, 60, 4, 'down')
        }

    def set_green(self, direction):
        signal = self.signals[direction]
        signal.state = 'green'
        print(f"Signal {direction}: Green")

    def set_red(self, direction):
        signal = self.signals[direction]
        signal.state = 'red'
        print(f"Signal {direction}: Red")

    def set_yellow(self, direction):
        signal = self.signals[direction]
        signal.state = 'yellow'
        print(f"Signal {direction}: Yellow")

    def get_state(self, direction):
        return self.signals[direction].get_state()

    def normal_operation(self):
        repeat()

    def handle_ambulance(self, ambulance_signal):
        global currentGreen, currentYellow, signals
        
        print(f"Ambulance waiting at signal: {ambulance_signal}")

        # Find the index of the signal where the ambulance is waiting
        ambulance_index = directionToIndex[ambulance_signal]

        # Set the ambulance signal to green immediately if it’s not already green
        if currentGreen != ambulance_index:
            # Set the current green signal to red
            signals[currentGreen].green = 0
            signals[currentGreen].yellow = 0
            signals[currentGreen].red = defaultRed
            vehicleCountTexts[currentGreen] = "0"

            # Set the ambulance signal to green and override other signal settings
            currentGreen = ambulance_index
            signals[currentGreen].green = defaultGreen  # You can extend the green time if needed
            signals[currentGreen].red = 0
            signals[currentGreen].yellow = 0
            signals[currentGreen].signalText = "GO"

            # Update the red time of other signals
            for i in range(noOfSignals):
                if i != currentGreen:
                    signals[i].red = signals[currentGreen].green + signals[currentGreen].yellow

        print("Ambulance has priority. Signal set to green for ambulance direction.")
        time.sleep(3)  # Adjust based on estimated time for ambulance to clear intersection

        # Restore normal signal settings after ambulance has passed
        self.reset_signals()

    def reset_signals(self):
        global nextGreen, currentGreen
        # Resume regular signal operation
        currentGreen = nextGreen  # Go to the next scheduled green signal
        nextGreen = (currentGreen + 1) % noOfSignals
        signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
        print("Resuming normal operation.")


class Vehicle(pygame.sprite.Sprite):
    def _init_(self, lane, vehicleClass, direction_number, direction, will_turn , position):
        pygame.sprite.Sprite._init_(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        self.position = position
        vehicles[direction][lane].append(self)
        # self.stop = stops[direction][lane]
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)
        self.waiting = False  # Initialize waiting attribute as False
        self.crossed = False
        
    
        if(direction=='right'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):    # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().width - gap         # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
            else:
                self.stop = defaultStop[direction]
            # Set new starting and stopping coordinate
            temp = self.currentImage.get_rect().width + gap    
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction=='left'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif(direction=='down'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction=='up'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        if(self.direction=='right'):
            if(self.crossed==0 and self.x+self.currentImage.get_rect().width>stopLines[self.direction]):   # if the image has crossed stop line now
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.x+self.currentImage.get_rect().width<mid[self.direction]['x']):
                    if((self.x+self.currentImage.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x+self.currentImage.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - gap2) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x += self.speed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 2
                        self.y += 1.8
                        if(self.rotateAngle==90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.image = pygame.image.load(path)
                    else:
                        if(self.index==0 or self.y+self.currentImage.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - gap2) or self.x+self.currentImage.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - gap2)):
                            self.y += self.speed
            else: 
                if((self.x+self.currentImage.get_rect().width<=self.stop or self.crossed == 1 or (currentGreen==0 and currentYellow==0)) and (self.index==0 or self.x+self.currentImage.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - gap2) or (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x += self.speed  # move the vehicle



        elif(self.direction=='down'):
            if(self.crossed==0 and self.y+self.currentImage.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.y+self.currentImage.get_rect().height<mid[self.direction]['y']):
                    if((self.y+self.currentImage.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.y+self.currentImage.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - gap2) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.y += self.speed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 2.5
                        self.y += 2
                        if(self.rotateAngle==90):
                            self.turned = 1
                    else:
                        if(self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or self.y<(vehicles[self.direction][self.lane][self.index-1].y - gap2)):
                            self.x -= self.speed
            else: 
                if((self.y+self.currentImage.get_rect().height<=self.stop or self.crossed == 1 or (currentGreen==1 and currentYellow==0)) and (self.index==0 or self.y+self.currentImage.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - gap2) or (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.y += self.speed
            
        elif(self.direction=='left'):
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.x>mid[self.direction]['x']):
                    if((self.x>=self.stop or (currentGreen==2 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x -= self.speed
                else: 
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 1.8
                        self.y -= 2.5
                        if(self.rotateAngle==90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.currentImage = pygame.image.load(path)
                    else:
                        if(self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height +  gap2) or self.x>(vehicles[self.direction][self.lane][self.index-1].x + gap2)):
                            self.y -= self.speed
            else: 
                if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first vehicle in that lane or it is has enough gap to the next vehicle in that lane)
                    self.x -= self.speed  # move the vehicle    
            # if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2))):                
            #     self.x -= self.speed
        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.y>mid[self.direction]['y']):
                    if((self.y>=self.stop or (currentGreen==3 and currentYellow==0) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height +  gap2) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                        self.y -= self.speed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 1
                        self.y -= 1
                        if(self.rotateAngle==90):
                            self.turned = 1
                    else:
                        if(self.index==0 or self.x<(vehicles[self.direction][self.lane][self.index-1].x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width - gap2) or self.y>(vehicles[self.direction][self.lane][self.index-1].y + gap2)):
                            self.x += self.speed
            else: 
                if((self.y>=self.stop or self.crossed == 1 or (currentGreen==3 and currentYellow==0)) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.y -= self.speed
def count_vehicle_types_at_signal(signal_direction):
    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0, 0, 0, 0, 0
    
    # Iterate over each lane in the given signal direction
    for lane in vehicles[signal_direction]:
        if lane == 'crossed':  # Skip the 'crossed' key
            continue
        for vehicle in vehicles[signal_direction][lane]:
            if vehicle.crossed == 0:  # Only count vehicles that haven't crossed
                vclass = vehicle.vehicleClass
                # Count the vehicles based on their class
                if vclass == 'car':
                    noOfCars += 1
                elif vclass == 'bus':
                    noOfBuses += 1
                elif vclass == 'truck':
                    noOfTrucks += 1
                elif vclass == 'rickshaw':
                    noOfRickshaws += 1
                elif vclass == 'bike':
                    noOfBikes += 1

    return {
        'cars': noOfCars,
        'buses': noOfBuses,
        'trucks': noOfTrucks,
        'rickshaws': noOfRickshaws,
        'bikes': noOfBikes
    }


#2nd function cal...........
def count_vehicles_crossed_by_signal():
    crossed_signals = {}
    directions = ['right', 'left', 'up', 'down']
    waiting_ambulance_signal = None  # Track the signal direction of waiting ambulance

    for direction in directions:
        crossed_signals[direction] = {}
        for lane in vehicles[direction]:
            if lane == 'crossed':  # Skip the 'crossed' key
                continue
            
            crossed_count = 0
            for vehicle in vehicles[direction][lane]:
                if vehicle.crossed == 1:  # If the vehicle has crossed the stop line
                    crossed_count += 1
                
                # Check if the vehicle is an ambulance and is waiting
                if vehicle.vehicleClass == 'ambulance' and vehicle.waiting:
                    waiting_ambulance_signal = direction  # Store the direction of waiting ambulance

            crossed_signals[direction][lane] = crossed_count

    return crossed_signals, waiting_ambulance_signal


#3rd function................
def count_vehicles_stopped_at_red_signal():
    stopped_signals = {}
    directions = ['right', 'left', 'up', 'down']

    for direction in directions:
        stopped_signals[direction] = {}
        for lane in vehicles[direction]:
            if lane == 'crossed':  # Skip the 'crossed' key
                continue
            stopped_count = 0
            for vehicle in vehicles[direction][lane]:
                # Check if the vehicle hasn't crossed and is stopped at its stop coordinate
                if vehicle.crossed == 0 and vehicle.x == vehicle.stop or vehicle.y == vehicle.stop:
                    stopped_count += 1
            stopped_signals[direction][lane] = stopped_count

    return stopped_signals

#5th function ...................
def count_crossed_vehicle_types_at_signal(signal_direction):
    crossedCars, crossedBuses, crossedTrucks, crossedRickshaws, crossedBikes = 0, 0, 0, 0, 0
    
    # Iterate over each lane in the given signal direction
    for lane in vehicles[signal_direction]:
        if lane == 'crossed':  # Skip the 'crossed' key
            continue
        for vehicle in vehicles[signal_direction][lane]:
            if vehicle.crossed == 1:  # Count vehicles that have crossed the stop line
                vclass = vehicle.vehicleClass
                # Count based on vehicle class
                if vclass == 'car':
                    crossedCars += 1
                elif vclass == 'bus':
                    crossedBuses += 1
                elif vclass == 'truck':
                    crossedTrucks += 1
                elif vclass == 'rickshaw':
                    crossedRickshaws += 1
                elif vclass == 'bike':
                    crossedBikes += 1

    return {
        'crossedCars': crossedCars,
        'crossedBuses': crossedBuses,
        'crossedTrucks': crossedTrucks,
        'crossedRickshaws': crossedRickshaws,
        'crossedBikes': crossedBikes
    }

def count_crossed_vehicles_at_all_signals():
    directions = ['right', 'left', 'up', 'down']
    
    # Initialize variables to store total counts of crossed vehicles by type across all signals
    total_crossed_cars = 0
    total_crossed_buses = 0
    total_crossed_trucks = 0
    total_crossed_rickshaws = 0
    total_crossed_bikes = 0
    
    # Iterate over each direction
    for direction in directions:
        counts = count_crossed_vehicle_types_at_signal(direction)
        total_crossed_cars += counts['crossedCars']
        total_crossed_buses += counts['crossedBuses']
        total_crossed_trucks += counts['crossedTrucks']
        total_crossed_rickshaws += counts['crossedRickshaws']
        total_crossed_bikes += counts['crossedBikes']
    
    return {
        'totalCrossedCars': total_crossed_cars,
        'totalCrossedBuses': total_crossed_buses,
        'totalCrossedTrucks': total_crossed_trucks,
        'totalCrossedRickshaws': total_crossed_rickshaws,
        'totalCrossedBikes': total_crossed_bikes
    }



def get_current_signal_name():
    # Assuming signals is a list of  objects
    # and currentGreen holds the index of the active signal
    signal_direction = directionNumbers[currentGreen]
    return signal_direction

def count_remaining_vehicles_at_current_signal():
    # Get the current signal direction
    current_signal_direction = get_current_signal_name()

    # Initialize vehicle counts
    remainingCars = 0
    remainingBuses = 0
    remainingTrucks = 0
    remainingRickshaws = 0
    remainingBikes = 0
    
    # Get the vehicle list for the current signal direction
    if current_signal_direction in vehicles:
        for lane in vehicles[current_signal_direction]:
            if lane == 'crossed':  # Skip the 'crossed' key
                continue
            for vehicle in vehicles[current_signal_direction][lane]:
                if vehicle.crossed == 0:  # Count only vehicles that haven't crossed
                    vclass = vehicle.vehicleClass
                    # Count based on vehicle class
                    if vclass == 'car':
                        remainingCars += 1
                    elif vclass == 'bus':
                        remainingBuses += 1
                    elif vclass == 'truck':
                        remainingTrucks += 1
                    elif vclass == 'rickshaw':
                        remainingRickshaws += 1
                    elif vclass == 'bike':
                        remainingBikes += 1

    return {
        'remainingCars': remainingCars,
        'remainingBuses': remainingBuses,
        'remainingTrucks': remainingTrucks,
        'remainingRickshaws': remainingRickshaws,
        'remainingBikes': remainingBikes
    }

def update_vehicle_status(self):
    # Check if the vehicle is waiting at the red signal
    current_signal = signals[self.direction_number]
    
    if current_signal.red > 0 and not self.crossed:
        self.waiting = True  # Vehicle is waiting at red
    else:
        self.waiting = False  # Vehicle is moving or has crossed
def count_vehicles_crossed_by_signal():
    for direction, lanes in vehicles.items():
        for lane, vehicle_list in lanes.items():
            if isinstance(vehicle_list, list):  # Check if vehicle_list is a list
                for vehicle in vehicle_list:
                    if vehicle.vehicleClass == 'ambulance' and vehicle.waiting:
                        return vehicle_list, direction  # Return the signal where the ambulance is waiting
    return None, None  # No ambulance found



def changeSignalToGreen(direction):
    """
    Change the traffic signal to green for the specified direction.
    
    Args:
        direction (str): The direction for which the signal should be changed to green.
    """
    global currentGreen
    if direction in directionToIndex:
        currentGreen = directionToIndex[direction]
        print(f"Traffic signal updated: Green for {direction}")
    else:
        print(f"Error: Invalid direction '{direction}'")


def restoreNormalSignal():
    """
    Restore the normal traffic signal rotation.
    """
    global normalSignalIndex, currentGreen
    
    # Move to the next signal in the rotation
    normalSignalIndex = (normalSignalIndex + 1) % len(normalSignalRotation)
    currentGreen = normalSignalRotation[normalSignalIndex]
    
    print(f"Traffic signal restored to normal: Green for {directionNumbers[currentGreen]}")


        
def reset_signals():
    global currentGreen, currentYellow
    # Implement logic to reset signals to their normal states
    currentGreen = defaultGreen  # Set this to the default direction index
    currentYellow = defaultYellow
    print("Signals reverted to normal routine.")

def changeSignalToGreen(direction):
    """
    Change the traffic signal to green for the specified direction.
    
    Args:
        direction (str): The direction for which the signal should be changed to green.
    """
    global currentGreen
    currentGreen = directionToIndex[direction]
    print(f"Traffic signal updated: Green for {direction}")



# Initialization of signals with default values
def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum ,signal_position=50 )
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum , signal_position=50)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum , signal_position=50)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum , signal_position=50)
    signals.append(ts4)
    repeat()

# Set time according to formula
def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws, noOfLanes
    global carTime, busTime, truckTime, rickshawTime, bikeTime
    os.system("say detecting vehicles, "+directionNumbers[(currentGreen+1)%noOfSignals])
#    detection_result=detection(currentGreen,tfnet)
#    greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (noOfBuses*busTime) + (noOfBikes*bikeTime))/(noOfLanes+1))
#    if(greenTime<defaultMinimum):
#       greenTime = defaultMinimum
#    elif(greenTime>defaultMaximum):
#       greenTime = defaultMaximum
    # greenTime = len(vehicles[currentGreen][0])+len(vehicles[currentGreen][1])+len(vehicles[currentGreen][2])
    # noOfVehicles = len(vehicles[directionNumbers[nextGreen]][1])+len(vehicles[directionNumbers[nextGreen]][2])-vehicles[directionNumbers[nextGreen]]['crossed']
    # print("no. of vehicles = ",noOfVehicles)
    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0,0,0,0,0
    for j in range(len(vehicles[directionNumbers[nextGreen]][0])):
        vehicle = vehicles[directionNumbers[nextGreen]][0][j]
        if(vehicle.crossed==0):
            vclass = vehicle.vehicleClass
            # print(vclass)
            noOfBikes += 1
    for i in range(1,3):
        for j in range(len(vehicles[directionNumbers[nextGreen]][i])):
            vehicle = vehicles[directionNumbers[nextGreen]][i][j]
            if(vehicle.crossed==0):
                vclass = vehicle.vehicleClass
                # print(vclass)
                if(vclass=='car'):
                    noOfCars += 1
                elif(vclass=='bus'):
                    noOfBuses += 1
                elif(vclass=='truck'):
                    noOfTrucks += 1
                elif(vclass=='rickshaw'):
                    noOfRickshaws += 1
    
    



    greenTime = math.ceil(((noOfCars*2) + (noOfRickshaws*2) + (noOfBuses*3) + (noOfTrucks*3)+ (noOfBikes*1))/(noOfLanes+1))
    def calculate_time(distance_meters, speed_kmph):
        distance_kilometers = distance_meters / 1000
        time_hours = distance_kilometers / speed_kmph
        time_seconds = time_hours * 3600
        return time_seconds
    
    distance = greenTime  # distance in meters
    speed = 3
    time_seconds = calculate_time(distance, speed)
    print('Green Time: ',time_seconds)
    if time_seconds <= 20:
        greenTime = defaultGreen
    elif 20 < time_seconds <= 40:
        greenTime = defaultMinimum
    elif 40 < time_seconds:
        greenTime = defaultMaximum
    signals[(currentGreen+1)%(noOfSignals)].green = greenTime
    crossed_vehicles , direc= count_total_crossed_minus_stopped()
    print("No of vechile crossed :",crossed_vehicles)
    counts = count_crossed_vehicles_at_all_signals()
    counts = count_crossed_vehicles_at_all_signals()
    # Call the function to get counts of remaining vehicles
    remaining_vehicles = count_remaining_vehicles_at_current_signal()
    rem_vechile = remaining_vehicles['remainingCars'] + remaining_vehicles['remainingBuses'] + remaining_vehicles['remainingTrucks'] + remaining_vehicles['remainingRickshaws']+remaining_vehicles['remainingBikes']


    # Print the total number of crossed cars
    print(f"Total crossed cars: {counts['totalCrossedCars']}")
    
    # Similarly, print other vehicle types if needed
    print(f"Total crossed buses: {counts['totalCrossedBuses']}")
    print(f"Total crossed trucks: {counts['totalCrossedTrucks']}")
    print(f"Total crossed rickshaws: {counts['totalCrossedRickshaws']}")
    print(f"Total crossed bikes: {counts['totalCrossedBikes']}")
    a = counts['totalCrossedBikes']
    print(a)
    print(get_current_signal_name())
    saveCycleData(get_current_signal_name(),  counts['totalCrossedCars'], counts['totalCrossedBuses'], counts['totalCrossedTrucks'], counts['totalCrossedRickshaws'], counts['totalCrossedBikes'], crossed_vehicles, greenTime, rem_vechile)

    
#1st fuction call.....
def count_total_crossed_minus_stopped():
    # Fetch crossed and stopped vehicle data
    crossed_signals, a = count_vehicles_crossed_by_signal()  # Ensure this function returns valid data
    stopped_signals = count_vehicles_stopped_at_red_signal()  # Ensure this function returns valid data

    # If either of these is None or invalid, handle gracefully
    if crossed_signals is None or stopped_signals is None:
        print("Error: crossed_signals or stopped_signals is None!")
        return 0, None  # Return a default value or appropriate error value

    total_difference = 0
    directions = ['right', 'left', 'up', 'down']

    for direction in directions:
        # Ensure crossed_signals[direction] is not None and is iterable
        if direction not in crossed_signals or crossed_signals[direction] is None:
            print(f"Error: No crossed signals data for direction '{direction}'")
            continue  # Skip to the next direction if the data is invalid

        for lane in crossed_signals[direction]:
            crossed_count = crossed_signals[direction].get(lane, 0)  # Default to 0 if lane not found
            stopped_count = stopped_signals.get(direction, {}).get(lane, 0)  # Default to 0 if lane not stopped
            total_difference += crossed_count - stopped_count

    # Return the calculated total difference and the last direction processed
    return total_difference, direction



def saveCycleData( signalname , noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes, 
                  total_vehicles_crossed, green_signal_time, remaining_vehicles):
    """
    Save traffic cycle data to an Excel file, including vehicle counts, signal info, and timings.
    
    Parameters:
    - signal_name: Name of the signal (e.g., 'right', 'left', 'up', 'down')
    - noOfCars: Number of cars that crossed during the green light
    - noOfBuses: Number of buses that crossed during the green light
    - noOfTrucks: Number of trucks that crossed during the green light
    - noOfRickshaws: Number of rickshaws that crossed during the green light
    - noOfBikes: Number of bikes that crossed during the green light
    - total_vehicles_crossed: Total number of vehicles that crossed during the green light
    - green_signal_time: Time the signal remained green (in seconds)
    - remaining_vehicles: Number of vehicles remaining after the light turned red
    """

    # Create a DataFrame with vehicle counts for the current cycle
    data = {
        'Cycle': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],  # Timestamp for cycle
        'signal name' : [signalname],                                       # Name of the signal
        'crossedCars': [noOfCars],                                        # Number of cars
        'crossedBuses': [noOfBuses],                                      # Number of buses
        'crossedTrucks': [noOfTrucks],                                    # Number of trucks
        'crossedRickshaws': [noOfRickshaws],                              # Number of rickshaws
        'crossedBikes': [noOfBikes],                                      # Number of bikes
        'TotalCrossed': [total_vehicles_crossed],                  # Total vehicles crossed
        'GreenSignalTime': [green_signal_time],                    # Time taken for green signal (seconds)
        'RemainingVehicles': [remaining_vehicles]                  # Remaining vehicles after red light
    }

    # Convert data to a pandas DataFrame
    df = pd.DataFrame(data)

    # Specify the path to save the Excel file
    file_path = "aaadata.xlsx"

    if os.path.exists(file_path):
        # Load existing data
        existing_df = pd.read_excel(file_path, engine='openpyxl')
        # Append new data to the existing data
        updated_df = pd.concat([existing_df, df], ignore_index=True)
    else:
        # If file does not exist, create a new DataFrame with the current data
        updated_df = df

    # Save the updated DataFrame to the Excel file
    updated_df.to_excel(file_path, index=False, engine='openpyxl')
    print(f"Data saved to {file_path} successfully!")

# Example usage:
# You can call this function and pass the required values to store data.
# Example:
# saveCycleData("right", 5, 2, 1, 3, 10, 21, 45, 7)

def repeat():
    global currentGreen, currentYellow, nextGreen

    while signals[currentGreen].green > 0:  # while the timer of current green signal is not zero
        printStatus()
        updateValues()

        if signals[(currentGreen + 1) % noOfSignals].red == detectionTime:  # set time of next green signal
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()

        time.sleep(1)

    currentYellow = 1  # set yellow signal on
    vehicleCountTexts[currentGreen] = "0"
    
    # reset stop coordinates of lanes and vehicles
    for i in range(0, 3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]

    while signals[currentGreen].yellow > 0:  # while the timer of current yellow signal is not zero
        printStatus()
        updateValues()
        
        # Check if an ambulance is waiting at the signal
        crossed_counts, is_ambulance_waiting = count_vehicles_crossed_by_signal()
        if is_ambulance_waiting is not None:  # If an ambulance is waiting, prioritize it
            print("An ambulance is waiting at a signal.", is_ambulance_waiting)
            amb = TrafficController()
            amb.handle_ambulance(is_ambulance_waiting)  # Handle ambulance
            return  # Return to avoid further processing of this cycle
        
        time.sleep(0.5)

    currentYellow = 0  # set yellow signal off

    # Reset all signal times of current signal to default times
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    currentGreen = nextGreen  # set next signal as green signal
    nextGreen = (currentGreen + 1) % noOfSignals  # set next green signal
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green  # set red time for next signal
    repeat()  # Continue the cycle

    

# Print the signal timers on cmd
def printStatus():                                                                                           
	for i in range(0, noOfSignals):
		if(i==currentGreen):
			if(currentYellow==0):
				print(" GREEN TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
			else:
				print("YELLOW TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
		else:
			print("   RED TS",i+1,"-> r:",signals[i].red," y:",signals[i].yellow," g:",signals[i].green)
	print()

# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
                signals[i].totalGreenTime+=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1




def generateVehicles():
    while True:
        # Define weights for vehicle types; ambulance has a lower probability
        vehicle_type = random.choices(
            population=[0, 1, 2, 3, 4],  # Indices for each vehicle type (0 to 4 are regular vehicles, 5 is ambulance)
            weights=[20, 20, 20, 20, 20],  # Lower weight for ambulance to make it rarer
            k=1
        )[0]

        # Determine lane based on vehicle type (bikes in lane 0, others in lane 1)
        if vehicle_type == 4:  # 4 could represent a bike in this setup
            lane_number = 0
        else:
            lane_number = 1

        # Decide if the vehicle will turn, for those in lane 1
        will_turn = 1 if (lane_number == 1 and random.randint(0, 4) <= 2) else 0

        # Assign a direction number based on weighted random values
        temp = random.randint(0, 999)
        direction_number = 0
        thresholds = [400, 800, 900, 1000]
        if temp < thresholds[0]:
            direction_number = 0
        elif temp < thresholds[1]:
            direction_number = 1
        elif temp < thresholds[2]:
            direction_number = 2
        elif temp < thresholds[3]:
            direction_number = 3

        # Instantiate the vehicle object (assuming Vehicle class is defined)
        vehicle = Vehicle(
            lane_number, 
            vehicleTypes[vehicle_type], 
            direction_number, 
            directionNumbers[direction_number], 
            will_turn, 
            position=10
        )

        # Check if the generated vehicle is an ambulance
        if vehicle_type == 5:  # Assuming 5 represents an ambulance
            print("Ambulance generated!")

        time.sleep(0.8)





# Assuming necessary classes like TrafficSignal, Vehicle, etc., are already defined

# Simulation Time Thread Function
def simulationTime():
    global timeElapsed, simTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed == simTime):
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')
            for i in range(noOfSignals):
                print('Lane', i+1, ':', vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
            print('Total vehicles passed: ', totalVehicles)
            print('Total time passed: ', timeElapsed)
            print('No. of vehicles passed per unit time: ', (float(totalVehicles) / float(timeElapsed)))
            os._exit(1)

# Main Class
class Main:
    def _init_(self):
        # Start the simulation time thread
        thread4 = threading.Thread(name="simulationTime", target=simulationTime, args=())
        thread4.daemon = True
        thread4.start()

        # Initialization thread
        thread2 = threading.Thread(name="initialization", target=initialize, args=())
        thread2.daemon = True
        thread2.start()

        # Colours 
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)

        # Screensize 
        self.screenWidth = 1400
        self.screenHeight = 800
        self.screenSize = (self.screenWidth, self.screenHeight)

        # Setting background image i.e. image of intersection
        self.background = pygame.image.load('images/mod_int.png')

        # Initialize pygame screen
        self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("SIMULATION")

        # Loading signal images and font
        self.redSignal = pygame.image.load('images/signals/red.png')
        self.yellowSignal = pygame.image.load('images/signals/yellow.png')
        self.greenSignal = pygame.image.load('images/signals/green.png')
        self.font = pygame.font.Font(None, 30)

        # Vehicle generation thread
        thread3 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
        thread3.daemon = True
        thread3.start()

        # Run the simulation
        self.run_simulation()

    def run_simulation(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.screen.blit(self.background, (0, 0))  # Display background in simulation

            # Check for waiting ambulances and adjust signals
            crossed_counts, waiting_ambulance_signal = count_vehicles_crossed_by_signal()
            

            if waiting_ambulance_signal:
                self.handle_ambulance(waiting_ambulance_signal)  # Handle the ambulance

            # Update signal states and display
            for i in range(noOfSignals):
                if i == currentGreen:
                    if currentYellow == 1:
                        if signals[i].yellow == 0:
                            signals[i].signalText = "STOP"
                        else:
                            signals[i].signalText = signals[i].yellow
                        self.screen.blit(self.yellowSignal, signalCoods[i])
                    else:
                        if signals[i].green == 0:
                            signals[i].signalText = "SLOW"
                        else:
                            signals[i].signalText = signals[i].green
                        self.screen.blit(self.greenSignal, signalCoods[i])
                else:
                    if signals[i].red <= 10:
                        if signals[i].red == 0:
                            signals[i].signalText = "GO"
                        else:
                            signals[i].signalText = signals[i].red
                    else:
                        signals[i].signalText = "---"
                    self.screen.blit(self.redSignal, signalCoods[i])

            # Render the signal texts for display
            signalTexts = ["", "", "", ""]
            for i in range(noOfSignals):
                signalTexts[i] = self.font.render(str(signals[i].signalText), True, self.white, self.black)
                self.screen.blit(signalTexts[i], signalTimerCoods[i])
                displayText = vehicles[directionNumbers[i]]['crossed']
                vehicleCountTexts[i] = self.font.render(str(displayText), True, self.black, self.white)
                self.screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

            # Time elapsed text display
            timeElapsedText = self.font.render("Time Elapsed: " + str(timeElapsed), True, self.black, self.white)
            self.screen.blit(timeElapsedText, (1100, 50))

            # Display the vehicles
            for vehicle in simulation:
                self.screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
                vehicle.move()

            pygame.display.flip()  # Update the display

    

# Run the simulation
Main()
