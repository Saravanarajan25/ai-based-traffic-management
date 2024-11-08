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
ambulance=3.0

# Count of cars at a traffic signal
noOfCars = 0
noOfBikes = 0
noOfBuses =0
noOfTrucks = 0
noOfRickshaws = 0
ambulance=0
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
gap = 10    # stopping gap
gap2 = 10   # moving gap



# Define a variable to track the current green signal
currentGreen = 0  # Example: 0 for 'right', 1 for 'down', etc.

# Define the normal signal rotation (example: cycling through directions)
normalSignalRotation = [0, 1, 2, 3]  # Order of signal rotation
normalSignalIndex = 0  # Index to track current signal in the normal rotation

signal_name_to_index = {
    "up": 1,
    "right": 0,
    "down": 3,
    "left": 2
}
pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum , signal_position, state='red'):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0
        self.position = signal_position  # Position where the signal is located
        self.state = state  # 'red', 'green', 'yellow'
    
   


class Vehicle:
    def __init__(self, vehicleClass, crossed, x, y, stop, waiting=False):
        self.vehicleClass = vehicleClass  # Type of vehicle (car, bus, etc.)
        self.crossed = crossed            # Whether the vehicle has crossed the stop line
        self.x = x                        # Vehicle's x-coordinate
        self.y = y                        # Vehicle's y-coordinate
        self.stop = stop                  # Stop coordinates
        self.waiting = waiting            # True if the vehicle is waiting at the signal



class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn , position):
        pygame.sprite.Sprite.__init__(self)
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
            

            crossed_signals[direction][lane] = crossed_count

    return crossed_signals


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


def get_waiting_ambulance_signal():
    """
    Check all four signals and return the signal direction where an ambulance is waiting.
    
    Returns:
        str: The direction where the ambulance is waiting (e.g., 'right', 'left', 'up', 'down').
             Returns None if no ambulance is waiting at any signal.
    """
    # Directions for all signals
    directions = ['right', 'left', 'up', 'down']

    # Check each signal direction
    for direction in directions:
        # Iterate over the lanes in the current signal direction
        for lane in vehicles[direction]:
            if lane == 'crossed':  # Skip the 'crossed' key
                continue
            
            # Iterate over each vehicle in the lane
            for vehicle in vehicles[direction][lane]:
                # Check if the vehicle is an ambulance and if it is waiting
                if vehicle.vehicleClass == 'ambulance':
                    # If an ambulance is found and is waiting, return the direction
                    return direction
    
    # If no ambulance is found, return None
    return None

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
                        return vehicle_list  # Return the signal where the ambulance is waiting
    return None  # No ambulance found






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
    #saveCycleData(get_current_signal_name(),  counts['totalCrossedCars'], counts['totalCrossedBuses'], counts['totalCrossedTrucks'], counts['totalCrossedRickshaws'], counts['totalCrossedBikes'], crossed_vehicles, greenTime, rem_vechile)

    
#1st fuction call.....
def count_total_crossed_minus_stopped():
    # Fetch crossed and stopped vehicle data
    crossed_signals= count_vehicles_crossed_by_signal()  # Ensure this function returns valid data
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
    file_path = "thala1.xlsx"

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
def change_signal(new_signal):
    global currentGreen, nextGreen
    
    # Set the new current green signal
    currentGreen = new_signal
    nextGreen = (currentGreen + 1) % noOfSignals  # Update next green signal

    # Set red time for the next signal based on the current green signal's yellow and green times
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    print(f"Signal changed: Current Green = {currentGreen + 1}, Next Green = {nextGreen + 1}")


import time
import threading

# Flags and variables to track ambulance state
ambulance_waiting = False
ambulance_signal_index = None
previous_green_signal = None
override_timer_active = False

# Ambulance green time duration
ambulance_green_time = 10  # seconds

def change_signal_for_ambulance(signal_index):
    global currentGreen, nextGreen, ambulance_waiting, ambulance_signal_index, previous_green_signal, override_timer_active

    if not ambulance_waiting:  # Only change if an ambulance is detected
        ambulance_waiting = True
        ambulance_signal_index = signal_index
        previous_green_signal = currentGreen  # Store the previous green signal

        # Set ambulance signal to green and stop the regular loop temporarily
        signals[signal_index].red = 0
        signals[signal_index].green = ambulance_green_time
        signals[signal_index].yellow = defaultYellow

        # Update current green to ambulance signal and temporarily pause the regular loop
        currentGreen = signal_index
        nextGreen = (currentGreen + 1) % noOfSignals
        override_timer_active = True

        print(f"Ambulance detected! Changing signal {signal_index + 1} to green for {ambulance_green_time} seconds.")
        printStatus()

        # Start a thread to reset the signal after 10 seconds and resume normal cycle
        threading.Thread(target=restore_signal_after_ambulance).start()
        thread = threading.Thread(name="detection", target=setTime, args=())
        thread.daemon = True
        thread.start()
        time.sleep(1)

def restore_signal_after_ambulance():
    global ambulance_waiting, currentGreen, nextGreen, ambulance_signal_index, previous_green_signal, override_timer_active

    # Wait for the ambulance green duration to finish
    time.sleep(ambulance_green_time)

    # Reset signal state and resume normal traffic cycle
    if ambulance_waiting:
        ambulance_waiting = False
        override_timer_active = False

        # Restore previous green and next green signals
        currentGreen = previous_green_signal
        nextGreen = (currentGreen + 1) % noOfSignals

        
        signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green



        
        print(f"Ambulance has crossed. Reverting to the previous signal cycle.")
        printStatus()
        
# Function to reset the ambulance flag after signal returns to normal
def reset_ambulance_flag():
    global ambulance_waiting
    ambulance_waiting = False
def check_if_ambulance_crossed():
    
    ambulance_position = get_ambulance_position()
    crossing_threshold_y = 100
    if ambulance_position is None or ambulance_position.y < crossing_threshold_y:
        return True
    else:
        return False
def update_yellow_and_switch_signals():
    """Handles the yellow phase and switches the green signal to the next signal in the cycle."""
    global currentGreen, currentYellow, nextGreen

    # Set yellow signal on
    currentYellow = 1
    vehicleCountTexts[currentGreen] = "0"

    # While the timer of the current yellow signal is not zero
    while signals[currentGreen].yellow > 0:
        printStatus()  # Update the display or console with current status
        updateValues()  # Perform necessary updates (e.g., decrement timers)
        time.sleep(0.5)  # Wait to simulate real-time behavior

    # Reset stop coordinates of lanes and vehicles for the current direction
    for i in range(3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]

    # Additional loop to process vehicle crossing during the yellow phase
    while signals[currentGreen].yellow > 0:
        printStatus()
        updateValues()
        crossed_counts = count_vehicles_crossed_by_signal()  # Track vehicles that crossed during yellow
        time.sleep(0.5)

    # Set yellow signal off
    currentYellow = 0

    # Reset all signal times of the current signal to default values
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    # Move to the next green signal in the cycle
    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSignals

    # Set the red time for the next-to-next signal
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green

def repeat():
    global currentGreen, currentYellow, nextGreen, ambulance_detected, ambulance_signal_index, override_timer_active
    
    while(signals[currentGreen].green > 0):  # While the timer of the current green signal is not zero
        printStatus()
        updateValues()
        time.sleep(1)
        # Check if any ambulance is waiting at a red signal
        ambulance_signal = get_waiting_ambulance_signal()  # Detect ambulance waiting at any signal
        if ambulance_signal is not None :
            # Convert signal name to index if necessary
            if isinstance(ambulance_signal, str):
                ambulance_signal = signal_name_to_index.get(ambulance_signal)
            
            # Ensure ambulance_signal is now an integer
            if isinstance(ambulance_signal, int):
                print(f"Ambulance detected! Changing red signal at {ambulance_signal + 1} to green.")
                override_timer_active = True
                # Only override if the current signal's green time is sufficient to finish
                if signals[currentGreen].green > 5:  # Adjust this threshold as needed
                    change_signal_for_ambulance(ambulance_signal)
                      # Exit the loop to handle the ambulance signal change immediately
                else:
                    # If green time is low, continue until the signal cycle finishes
                    print("Not enough time left for override, continuing current cycle.")
                    break

        # Run standard signal updates only if the override is not active
        if not override_timer_active:
            if signals[currentGreen].green > 0:
                printStatus()
                updateValues()
                time.sleep(1)
            elif signals[currentGreen].yellow > 0:
                printStatus()
                updateValues()
                time.sleep(0.5)
            else:
                # Cycle to the next signal only if no ambulance override is active
                signals[currentGreen].green = defaultGreen
                signals[currentGreen].yellow = defaultYellow
                signals[currentGreen].red = defaultRed
                currentGreen = nextGreen
                nextGreen = (currentGreen + 1) % noOfSignals
                signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
        if signals[(currentGreen + 1) % noOfSignals].red == detectionTime:  # Set time of next green signal 
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
            # setTime()
        time.sleep(1)

    update_yellow_and_switch_signals()
    repeat()  # Continue the loop for the next cycle
 

# Print the signal timers on cmd
def printStatus():                                                                                           
	for i in range(0, noOfSignals):

		if(i==currentGreen):
			if(currentYellow==0  ):
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
        # Adjusted range to make ambulance appear less frequently
        vehicle_type = random.choices(
            population=[0, 1, 2, 3, 4, 5],  # Indices for each vehicle type
            weights=[20, 20, 20, 20, 20, 3],  # Lower weight for ambulance
            k=1
        )[0]

        # Define lanes based on vehicle type
        if vehicle_type == 4:  # If vehicle type is 'bike'
            lane_number = 0  # Bikes go in lane 0
        else:
            lane_number = 1  # Other vehicles go in lane 1

        will_turn = 0
        if lane_number == 1:
            temp = random.randint(0, 4)
            if temp <= 2:
                will_turn = 1
            else:
                will_turn = 0

        temp = random.randint(0, 999)
        direction_number = 0
        a = [400, 800, 900, 1000]
        if temp < a[0]:
            direction_number = 0
        elif temp < a[1]:
            direction_number = 1
        elif temp < a[2]:
            direction_number = 2
        elif temp < a[3]:
            direction_number = 3

        # Create the vehicle, including the new 'ambulance' type
        vehicle = Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn, position=10)

        # Check if an ambulance is generated
        if vehicle_type == 5:
            print("\nAmbulance generated!\n")
            
            

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
    def __init__(self):

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


    def handle_ambulance_and_cycle(self, i):
        """Handles signal cycle updates with ambulance priority logic for the specified signal index."""
        global currentGreen, currentYellow, ambulance_detected, ambulance_signal_index, ambulance_crossed, ambulance_timer

        # Check if an ambulance is detected and waiting at the current signal
        if ambulance_detected and i == ambulance_signal_index:
            # Prioritize green light for the ambulance
            if not ambulance_crossed:
                signals[i].signalText = ambulance_timer
                self.screen.blit(self.greenSignal, signalCoods[i])

                # Decrement the timer specifically for the ambulance and check if it has crossed
                if ambulance_timer > 0:
                    ambulance_timer -= 1
                ambulance_crossed = check_if_ambulance_crossed()  # This function should detect if the ambulance has crossed

            # After the ambulance crosses, reset to normal signal operation
            if ambulance_crossed:
                ambulance_detected = False
                ambulance_timer = 10  # Reset timer for the next ambulance event
                print("Ambulance has crossed. Reverting to normal cycle.")    
    def update_signal_cycle(self, i):
        """Update and display the signal based on its current cycle state."""
        global currentGreen, currentYellow

        # Check if current signal is green
        if i == currentGreen:
            if currentYellow == 1:  # Check if it's in the yellow phase
                if signals[i].yellow == 0:
                    signals[i].signalText = "STOP"
                else:
                    signals[i].signalText = signals[i].yellow
                self.screen.blit(self.yellowSignal, signalCoods[i])
            else:  # If not yellow, show green
                if signals[i].green == 0:
                    signals[i].signalText = "SLOW"
                else:
                    signals[i].signalText = signals[i].green
                self.screen.blit(self.greenSignal, signalCoods[i])
        else:
            # Handle red signal for all other signals
            if signals[i].red <= 10:
                if signals[i].red == 0:
                    signals[i].signalText = "GO"
                else:
                    signals[i].signalText = signals[i].red
            else:
                signals[i].signalText = "---"
            self.screen.blit(self.redSignal, signalCoods[i])

    def run_simulation(self):
        """Run the main simulation loop."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.screen.blit(self.background, (0, 0))  # Display background in simulation

            # New variables for tracking ambulance detection
            ambulance_detected = False
            ambulance_crossed = False
            ambulance_signal_index = None  # Index of the signal where the ambulance is waiting
            ambulance_timer = 10  # Time to keep the signal green for the ambulance (in seconds)

            for i in range(noOfSignals):
                if ambulance_detected and i == ambulance_signal_index:
                    self.handle_ambulance_and_cycle(i)
                    self.update_signal_cycle(i)
                else:
                    # Call the update_signal_cycle method using self
                    self.update_signal_cycle(i)

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
