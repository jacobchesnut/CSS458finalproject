"""
    GroceryModel
    This script handles the Grocery Model final project for CSS 458
    BY: Maxwell Trinh and Jacob Chesnut
"""

#Import statements

import numpy as np
import random

import matplotlib.pyplot as plt
import matplotlib.cm as cm

#Constants

#numpy array of items representing the pool of primary items customers can have
#numpy array of items representing the pool of secondary items customers can have
#numpy array of items representing the pool of all items customers can have
#int representing the distance in any direction a customer can purchase items from
VIEW_RANGE = 1
#int representing the number of steps between customers entering the store
DELTA_CUSTOMER = 5
#int representing the total number of customers which can enter the store
TOTAL_CUSTOMERS = 30
#int representing the size of the array which will represent the store
STORE_SIZE = 10
#int representing the number of steps which can pass before forcibly ending the simulation
MAX_TIME = 500
#int representing the number of items a customer will have in their primary list
NUMBER_PRIMARY_LIST = 3
#int representing the number of itmes a customer will have in their secondary list
NUMBER_SECONDARY_LIST = 7
#array of item that will be used in generating the primary list
PRIMARY_LIST = []
#array of item that will be used in generating the secondary list
SECONDARY_LIST = []
#array of x and y value for spawner location
SPAWNER = [9,8]

#Global return values
#int representing the number of steps made in the current simulation
CUSTOMER_STEPS = 0
#int representing the number of items sold in the current simulation
ITEMS_SOLD = 0
#float representing the amount of money made in the current simulation
MONEY_MADE = 0.0
#stores each item and its purchased amount 
ITEMS_COUNTER = []

#User-modifiable constants
#2D array which holds the positions of all shelves in the store, 33 in total
shelfPositions = np.array([[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[0,8], \
                           [2,1],[2,2],[2,3],[2,4],[2,5],[2,6],[2,7],[2,8], \
                           [4,1],[4,2],[4,3],[4,4],[4,5],[4,6],[4,7],[4,8], \
                           [6,1],[6,2],[6,3],[6,4],[6,5],[6,6],[6,7],[6,8], \
                           [8,1]])
#array which holds the percentages for primary items when using item density
#arbitrarily decided on
primaryDensity = np.array([0.02, 0.1, 0.05, 0.03, 0.1, 0.05, 0.05, 0.1,     \
                           0.07, 0.2, 0.15, 0.03, 0.05])
#array which holds the percentages for secondary items when using item density
#arbitrarily decided on
secondaryDensity = np.array([0.1, 0.05, 0.03, 0.05, 0.03, 0.05, 0.02, 0.1, \
                             0.05, 0.05, 0.02, 0.1, 0.05, 0.05, 0.04, 0.03,\
                             0.01, 0.02, 0.05, 0.1])
#Methods

def MoveCustomer(customerToMove, storeShelves, allCustomers):
    """
    MoveCustomer
    attempts to move a customer towards their next primary item
    the way customer movement works is as follows:
    the first action is to compare the customer position against all other
    customer positions, shelf positions, and shop boundaries to figure out
    which directions are available to move in.
    
    The next action is to find the coordinates of the closest primary item
    
    after these coordinates are found, the Y-axis position of the item and
    customer are compared. if the difference between positions is 1, then
    moving in the Y-direction will be ignored. otherwise the customer will
    attempt to move in the Y-direction if possible.
    
    if the customer does not move in the Y-axis, they will instead to move
    in the X direction. If Y-axis movement was ignored before this, that is
    to say, that the customer is aligned in the Y-axis to purchase the item,
    then the customer will attempt to move in the direction of the item.
    If the customer is not Y-axis aligned, it will instead choose to move in
    the direction of the closest shop boundary, if possible.
    
    if all attempted movement options have been prevented by this point,
    then the customer will attempt to move in any direction, chosen at random
    
    If the customer is blocked in all directions, it will stay still
    
    
    this movement pattern assumes that the shop is created with horizontal
    (parallel to X-axis) shelves, and that none of the shelves create corners
    with each other.
    """
    global CUSTOMER_STEPS
    customerCoords = customerToMove.loc_in_env
    #determine blocked directions
    blockedDirections = np.zeros(4, dtype=bool) #0123 = NESW
    #boundaries
    if(customerCoords[0] == 0):
        blockedDirections[0] = True
    if(customerCoords[0] == STORE_SIZE - 1):
        blockedDirections[2] = True
    if(customerCoords[1] == 0):
        blockedDirections[3] = True
    if(customerCoords[1] == STORE_SIZE - 1):
        blockedDirections[1] = True
    #store shelves
    for i in storeShelves:
        shelfLoc = i.loc_in_env
        diff = shelfLoc - customerCoords
        if(diff[0] == -1 and diff[1] == 0):
            blockedDirections[0] = True
        if(diff[0] == 1 and diff[1] == 0):
            blockedDirections[2] = True
        if(diff[0] == 0 and diff[1] == -1):
            blockedDirections[3] = True
        if(diff[0] == 0 and diff[1] == 1):
            blockedDirections[1] = True
    #customers
    for i in allCustomers:
        otherCustomerLoc = i.loc_in_env
        diff = otherCustomerLoc - customerCoords
        if(diff[0] == -1 and diff[1] == 0):
            blockedDirections[0] = True
        if(diff[0] == 1 and diff[1] == 0):
            blockedDirections[2] = True
        if(diff[0] == 0 and diff[1] == -1):
            blockedDirections[3] = True
        if(diff[0] == 0 and diff[1] == 1):
            blockedDirections[1] = True
    #do nothing if we cannot move
    if(blockedDirections[0] and blockedDirections[1] and blockedDirections[2] and blockedDirections[3]):
        return
    
    #find the closest primary item
    closestShelf = None
    closestDistance = np.array([STORE_SIZE, STORE_SIZE])
    for i in storeShelves:
        notPrimaryItem = True
        for j in customerToMove.primary_list:
            if(j.name == i.stock.name):
                notPrimaryItem = False
        if(notPrimaryItem):
            continue
        else:
            shelfCoords = i.loc_in_env
            shelfDist = np.abs(customerCoords - shelfCoords)
            newC = (shelfDist[0] * shelfDist[0]) + (shelfDist[1] * shelfDist[1])
            oldC = (closestDistance[0] * closestDistance[0]) + (closestDistance[1] * closestDistance[1])
            #if this shelf is closer
            if(oldC > newC):
                closestShelf = i
                closestDistance = shelfDist
    #avoid movement of customers finished shopping
    if(closestShelf is None):
        #print("closestShelf is none!")
        #print(customerToMove.primary_list)
        return
    
    #attempt to move vertically
    shelfVector = customerCoords - closestShelf.loc_in_env
    if(shelfVector[0] > 1 and not blockedDirections[0]):
        #move north
        customerCoords[0] = customerCoords[0] - 1
        customerToMove.loc_in_env = customerCoords
        CUSTOMER_STEPS = CUSTOMER_STEPS + 1
        return
    if(shelfVector[0] < -1 and not blockedDirections[2]):
        #move south
        customerCoords[0] = customerCoords[0] + 1
        customerToMove.loc_in_env = customerCoords
        CUSTOMER_STEPS = CUSTOMER_STEPS + 1
        return
    
    #attempt to move horizontally
    #if we need to find a way out of this row
    if(shelfVector[0] > 1 or shelfVector[0] < -1):
        if(customerCoords[1] < STORE_SIZE/2 and not blockedDirections[3]):
            #move west
            customerCoords[1] = customerCoords[1] - 1
            customerToMove.loc_in_env = customerCoords
            CUSTOMER_STEPS = CUSTOMER_STEPS + 1
            return
        if(customerCoords[1] >= STORE_SIZE/2 and not blockedDirections[1]):
            #move east
            customerCoords[1] = customerCoords[1] + 1
            customerToMove.loc_in_env = customerCoords
            CUSTOMER_STEPS = CUSTOMER_STEPS + 1
            return
    #if we otherwise need to move towards the item
    else:
        if(shelfVector[1] > 1 and not blockedDirections[3]):
            #move west
            customerCoords[1] = customerCoords[1] - 1
            customerToMove.loc_in_env = customerCoords
            CUSTOMER_STEPS = CUSTOMER_STEPS + 1
            return
        if(shelfVector[1] < -1 and not blockedDirections[1]):
            #move east
            customerCoords[1] = customerCoords[1] + 1
            customerToMove.loc_in_env = customerCoords
            CUSTOMER_STEPS = CUSTOMER_STEPS + 1
            return
    
    #otherwise move randomly
    randomDirection = GetRandDirection(blockedDirections)
    if(randomDirection == 0):
        #move north
        customerCoords[0] = customerCoords[0] - 1
        customerToMove.loc_in_env = customerCoords
        CUSTOMER_STEPS = CUSTOMER_STEPS + 1
        return
    if(randomDirection == 1):
        #move east
        customerCoords[1] = customerCoords[1] + 1
        customerToMove.loc_in_env = customerCoords
        CUSTOMER_STEPS = CUSTOMER_STEPS + 1
        return
    if(randomDirection == 2):
        #move south
        customerCoords[0] = customerCoords[0] + 1
        customerToMove.loc_in_env = customerCoords
        CUSTOMER_STEPS = CUSTOMER_STEPS + 1
        return
    if(randomDirection == 3):
        #move west
        customerCoords[1] = customerCoords[1] - 1
        customerToMove.loc_in_env = customerCoords
        CUSTOMER_STEPS = CUSTOMER_STEPS + 1
        return

def GetRandDirection(blockedDirections):
    """
    GetRandDirection
    this function will take a numpy array of blocked directions, and return
    a direction chosen randomly from those allowed.
    the directions correspond by an integer 0,1,2,3 to a cardinal direction
    north,east,south,west, respectively
    
    blockedDirections is assumed to be a 1D numpy array with four booleans
    
    this function returns an integer direction
    """
    randomDirection = random.randint(0,3)
    if(blockedDirections[randomDirection]):
        return GetRandDirection(blockedDirections)
    else:
        return randomDirection

def CustomerPurchase(customerToPurchase, storeShelves):
    """
    CustomerPurchase
    attempts to purchase items around the customer, if they are in the
    customer's primary or secondary item lists.
    The customer can only pull from shelves which are VIEW_RANGE or closer
    steps away (including diagonal steps)
    if an item is purchased, then ITEMS_SOLD will increment by one, and
    MONEY_MADE will increment by the cost of the item.
    
    customerToPurchase should be a customer object to search for
    storeShelves should be a numpy array of all shelves in the store
    """
    global ITEMS_SOLD
    global MONEY_MADE
    global ITEMS_COUNTER
    
    for i in storeShelves:
        distance = np.abs(customerToPurchase.loc_in_env - i.loc_in_env)
        #shelf in range
        if(distance[0] <= VIEW_RANGE and distance[1] <= VIEW_RANGE):
            for j in customerToPurchase.primary_list:
                #item customer wants
                if(j.name == i.stock.name):
                    #remove item
                    newList = []
                    for k in customerToPurchase.primary_list:
                        #add into the list if not being removed
                        if(not j == k):
                            newList.append(k)
                    customerToPurchase.primary_list = np.array(newList)
                    #increment counters
                    ITEMS_SOLD = ITEMS_SOLD + 1
                    MONEY_MADE = MONEY_MADE + j.price
                    ItemCounterIncrement(i.stock.name)
            for j in customerToPurchase.secondary_list:
                #item customer wants
                if(j.name == i.stock.name):
                    #remove item
                    newList = []
                    for k in customerToPurchase.secondary_list:
                        #add into the list if not being removed
                        if(not j == k):
                            newList.append(k)
                    customerToPurchase.secondary_list = np.array(newList)
                    #increment counters
                    ITEMS_SOLD = ITEMS_SOLD + 1
                    MONEY_MADE = MONEY_MADE + j.price
                    ItemCounterIncrement(i.stock.name)

def ItemCounterIncrement(inName = ''):
    for i in ITEMS_COUNTER:
        if i[0].name == inName:
            i[1] += 1

def RemoveCustomers(allCustomers):
    """
    RemoveCustomers
    removes all customers from the customer list which do not have primary
    items to search for anymore.
    
    allCustomers should be a numpy array of all customers in the simulation,
    returns a numpy array of all remaining customers which still have primary
    items to search for
    """
    returnArray = allCustomers
    for i in allCustomers:
        newList = []
        if(len(i.primary_list) == 0):
            for j in allCustomers:
                if(not i == j):
                    newList.append(j)
            returnArray = np.array(newList)
    return returnArray

def RunOneSimulation(shelves):
    """
    RunOneSimulation
    takes a numpy array of shelves representing a store, and runs a single
    simulation by creating a list of shoppers (without a probability density),
    looping through moving the customers and purchasing items, with customers
    being placed into the store every set amount of steps.
    
    shelves should be a numpy array of shelves representing the store to
    simulate.
    The results are kept in the global result variables.
    """
    #initialize items possibly
    customerList = createCustomerList(TOTAL_CUSTOMERS, None, None)
    activeCustomerList = None
    customerCounter = 0 #current customer to pull from customer list
    counter = 0 #step number in store
    global CUSTOMER_STEPS
    global ITEMS_SOLD
    global MONEY_MADE
    CUSTOMER_STEPS = 0
    ITEMS_SOLD = 0
    MONEY_MADE = 0.0
    #main simulation loop
    while(counter < MAX_TIME):
        #time to add a new customer
        if((counter % DELTA_CUSTOMER) == 0 and customerCounter < TOTAL_CUSTOMERS - 1):
            if(activeCustomerList is None):
                activeCustomerList = np.array([customerList[customerCounter]])
                customerCounter = customerCounter + 1
            else:
                newList = []
                for i in activeCustomerList:
                    newList.append(i)
                newList.append(customerList[customerCounter])
                customerCounter = customerCounter + 1
                activeCustomerList = np.array(newList)
        #loop through all customers
        for i in activeCustomerList:
            MoveCustomer(i, shelves, activeCustomerList)
            CustomerPurchase(i, shelves)
        activeCustomerList = RemoveCustomers(activeCustomerList)
        #check if it's time to exit the sim
        if(len(activeCustomerList) <= 0 and customerCounter >= TOTAL_CUSTOMERS - 1):
            return
        counter = counter + 1

def RunOneHundredSimulations(shelves):
    """
    RunOneHundredSimulations
    takes a numpy array of shelves representing a store and runs one hundred
    single simulations, averaging and returning the results as floats in a
    numpy array where a[0] = average items sold, a[1] = average money earned,
    and a[2] = average distance walked.
    """
    averageItemsSold = 0
    averageMoneyEarned = 0.0
    averageDistanceWalked = 0
    for i in range(100):
        #print("running simulation #" + str(i))
        RunOneSimulation(shelves)
        averageItemsSold = averageItemsSold + ITEMS_SOLD
        averageMoneyEarned = averageMoneyEarned + MONEY_MADE
        averageDistanceWalked = averageDistanceWalked + CUSTOMER_STEPS
        
    averageItemsSold = averageItemsSold/100
    averageMoneyEarned = averageMoneyEarned/100
    averageDistanceWalked = averageDistanceWalked/100
    return np.array([averageItemsSold, averageMoneyEarned, averageDistanceWalked])

def RunRandomizedSimulations():
    """
    RunRandomizedSimulations
    runs five sets of one hundred simulations with a different item layout for
    each set of simulations, outputting the results of each, paired with the
    item layout of the store.
    """
    for i in range(5):
        #create shelves for the store here
        shelves = createStore(shelfPositions)
        averages = RunOneHundredSimulations(shelves)
        print("For simulation " + str(i) + ":")
        print("the shelf layout was...")
        for i in shelves:
            print(i.stock.name)
        print("The average items sold was " + str(averages[0]) + ".")
        print("The average money earned was " + str(averages[1]) + ".")
        print("The average distance walked was " + str(averages[2]) + ".")

def RunOneSimulationDensity(shelves):
    """
    RunOneSimulationDensity
    takes a numpy array of shelves representing a store, and runs a single
    simulation by creating a list of shoppers (with a probability density),
    looping through moving the customers and purchasing items, with customers
    being placed into the store every set amount of steps.
    
    shelves should be a numpy array of shelves representing the store to
    simulate.
    The results are kept in the global result variables.
    """
    #initialize items possibly
    customerList = createCustomerList(TOTAL_CUSTOMERS, primaryDensity, secondaryDensity)
    activeCustomerList = None
    customerCounter = 0 #current customer to pull from customer list
    counter = 0 #step number in store
    global CUSTOMER_STEPS
    global ITEMS_SOLD
    global MONEY_MADE
    CUSTOMER_STEPS = 0
    ITEMS_SOLD = 0
    MONEY_MADE = 0.0
    #main simulation loop
    while(counter < MAX_TIME):
        #time to add a new customer
        if((counter % DELTA_CUSTOMER) == 0 and customerCounter < TOTAL_CUSTOMERS - 1):
            if(activeCustomerList is None):
                activeCustomerList = np.array([customerList[customerCounter]])
                customerCounter = customerCounter + 1
            else:
                newList = []
                for i in activeCustomerList:
                    newList.append(i)
                newList.append(customerList[customerCounter])
                customerCounter = customerCounter + 1
                activeCustomerList = np.array(newList)
        #loop through all customers
        for i in activeCustomerList:
            MoveCustomer(i, shelves, activeCustomerList)
            CustomerPurchase(i, shelves)
        activeCustomerList = RemoveCustomers(activeCustomerList)
        #check if it's time to exit the sim
        if(len(activeCustomerList) <= 0 and customerCounter >= TOTAL_CUSTOMERS - 1):
            return
        counter = counter + 1

def RunOneHundredDensitySimulations(shelves):
    """
    RunOneHundredSimulations
    takes a numpy array of shelves representing a store and runs one hundred
    single simulations, averaging and returning the results as floats in a
    numpy array where a[0] = average items sold, a[1] = average money earned,
    and a[2] = average distance walked.
    """
    averageItemsSold = 0
    averageMoneyEarned = 0.0
    averageDistanceWalked = 0
    for i in range(100):
        #print("running simulation #" + str(i))
        RunOneSimulationDensity(shelves)
        averageItemsSold = averageItemsSold + ITEMS_SOLD
        averageMoneyEarned = averageMoneyEarned + MONEY_MADE
        averageDistanceWalked = averageDistanceWalked + CUSTOMER_STEPS
    averageItemsSold = averageItemsSold/100
    averageMoneyEarned = averageMoneyEarned/100
    averageDistanceWalked = averageDistanceWalked/100
    return np.array([averageItemsSold, averageMoneyEarned, averageDistanceWalked])
        
    
 
def initItems():
    """        
    takes a numpy array of strings and a numpy array of floats, which 
    paired together represent an item. Returns a numpy array of all items 
    created from this.
    """
    #2017 prices for common grocery items. source https://www.visualcapitalist.com/decade-grocery-prices/
    global PRIMARY_LIST
    PRIMARY_LIST = []
    PRIMARY_LIST.append(Item('Bacon', 5.79)) 
    PRIMARY_LIST.append(Item('Pasta', 1.28)) 
    PRIMARY_LIST.append(Item('Beans', 1.36))         
    PRIMARY_LIST.append(Item('Ground Beef', 4.12)) 
    PRIMARY_LIST.append(Item('Flour', 0.52)) 
    PRIMARY_LIST.append(Item('Peanut Butter', 2.56)) 
    PRIMARY_LIST.append(Item('Potatoes', 0.72)) 
    PRIMARY_LIST.append(Item('Rice', 0.72)) 
    PRIMARY_LIST.append(Item('Sugar', 0.65)) 
    PRIMARY_LIST.append(Item('Milk', 3.24)) 
    PRIMARY_LIST.append(Item('Eggs', 1.43))
    PRIMARY_LIST.append(Item('Butter', 3.38))
    PRIMARY_LIST.append(Item('Bread', 1.34))
    PRIMARY_LIST = np.array(PRIMARY_LIST)
     
    #Secondary items. Makeing stuff up rn
    global SECONDARY_LIST
    SECONDARY_LIST = []
    SECONDARY_LIST.append(Item('Chips', 2.50))
    SECONDARY_LIST.append(Item('Soda', 1.22))
    SECONDARY_LIST.append(Item('Gum', 0.76))
    SECONDARY_LIST.append(Item('Chocolate', 1.02))
    SECONDARY_LIST.append(Item('Ice Cream', 4.70))
    SECONDARY_LIST.append(Item('Water', 2.50))
    SECONDARY_LIST.append(Item('Carrot', 3.22))
    SECONDARY_LIST.append(Item('Cake', 10.45))
    SECONDARY_LIST.append(Item('Cookies', 5.78))
    SECONDARY_LIST.append(Item('Beer', 4.20))
    SECONDARY_LIST.append(Item('Cooking Wine', 8.00))
    SECONDARY_LIST.append(Item('Doughnut', 1.41))
    SECONDARY_LIST.append(Item('Chicken Nuggets', 5.80))
    SECONDARY_LIST.append(Item('Soy Sauce', 3.69))
    SECONDARY_LIST.append(Item('Cheese', 1.98))
    SECONDARY_LIST.append(Item('Rice Noodles', 5.78))
    SECONDARY_LIST.append(Item('Jelly', 3.12))
    SECONDARY_LIST.append(Item('Juice', 4.90))
    SECONDARY_LIST.append(Item('Brownies', 1.94))
    SECONDARY_LIST.append(Item('Pizza', 6.66))  
    SECONDARY_LIST = np.array(SECONDARY_LIST)
    
    global ITEMS_COUNTER
    for i in PRIMARY_LIST:
        ITEMS_COUNTER.append([i, 0])
    for i in SECONDARY_LIST:
        ITEMS_COUNTER.append([i, 0])
        
def createStore(loc = []):
    """
    takes a 2D numpy array of coordinates (a[0,:] = x coords. 
    A[1,:] = y coords), and returns a numpy array of shelves created in
    each coordinate, with a random item per shelf.
    
    this function assumes that there are exactly as many items as shelves in
    the store
    """
    shelves = []
    
    #all items into a single list
    allItems = np.concatenate((PRIMARY_LIST, SECONDARY_LIST))
    
    #randomly assign an item to each shelf and remove the item from the list
    for i in range(len(allItems)):
        val = np.random.randint(0, len(allItems))
        shelves.append(Shelf(allItems[val], loc[i][0], loc[i][1]))
        newList = []
        for j in allItems:
            if(not j == allItems[val]):
                newList.append(j)
        allItems = np.array(newList)
        
    return shelves
            
def createCustomer(prim = [], sec = [], percPrim = None, percSec = None):
    """
    takes a numpy array of primary items, a numpy array of secondary items,
    a numpy array of floats representing percentages in an item density 
    for primary items (defaults to None if unused), and a numpy array of 
    floats representing percentages in an item density for secondary items
    (defaults to None if unused). Returns a single Customer created from 
    this information, with primary and secondary items chosen based off of
    random selection (with the probability density if provided) up to the
    number specified in the constants. 
    """
    custPrimList = []
    custSecList = []
    #random generation with no percent distribution
    #currently can generate duplicates
    #createCustomer(PRIMARY_LIST, SECONDARY_LIST, primaryDensity, secondaryDensity)
    

    
    for i in range(NUMBER_PRIMARY_LIST):
        val = np.random.uniform(0,1)
        newIndex = createCustomerHelper(val, percPrim, custPrimList, prim)
        custPrimList.append(prim[newIndex])

    for i in range(NUMBER_SECONDARY_LIST):
        val = np.random.uniform(0,1)
        newIndex = createCustomerHelper(val, percSec, custSecList, sec)
        custSecList.append(sec[newIndex]) 
 
    return Customer(SPAWNER[0], SPAWNER[1], custPrimList, custSecList)

def createCustomerHelper(value, probs, custList, itemList):
    """
    takes a value (between 0 and 1) and a probability array that adds up to 1
    and 
    """
    index = 0
    if probs is None:
        index = np.random.randint(0, len(itemList))
        if not custList:
            return index
        elif itemList[index] in custList:
             return createCustomerHelper(value, probs,custList, itemList)
        else:
             return index

    
    rangeLowerBound = 0
    rangeUpperBound = 0
    probs = probs
    #print (probs)
    
    
    for i in range(len(probs)):
        #print (rangeLowerBound)
        rangeUpperBound = rangeLowerBound + probs[i]
        #print (probs[i])
        #print(rangeUpperBound, rangeLowerBound, value)
        if value <= rangeUpperBound:
            index = i
            break
        else:
            rangeLowerBound += probs[i]
            
    if not custList:
        return index
    elif itemList[index] in custList:
        val = np.random.uniform(0,1)
        return createCustomerHelper(val, probs,custList, itemList)
    else:
        return index

def createCustomerList(custAmount, percPrim = None, percSec = None):
    """
    createCustomerList: takes an integer for the number of customers to 
    create, a numpy array of floats representing percentages in an item
    density for primary items (defaults to None if unused), and a numpy
    array of floats representing percentages in an item density for 
    secondary items (defaults to None if unused).  returns a numpy array 
    of that many Customers, using the densities if given.
    """
    custList = []
    for i in range(custAmount):
        custList.append(createCustomer(PRIMARY_LIST, SECONDARY_LIST,
                                       percPrim, percSec))
        
    return custList

def RunOneAnimatedSimulation(shelves):
    """
    RunOneAnimatedSimulation
    takes a numpy array of shelves representing a store, and runs a single
    simulation by creating a list of shoppers (without a probability density),
    looping through moving the customers and purchasing items, with customers
    being placed into the store every set amount of steps.
    
    the simulation will be animated
    The results are kept in the global result variables.
    """
    #initialize items possibly
    customerList = createCustomerList(TOTAL_CUSTOMERS, None, None)
    activeCustomerList = None
    customerCounter = 0 #current customer to pull from customer list
    counter = 0 #step number in store
    global CUSTOMER_STEPS
    global ITEMS_SOLD
    global MONEY_MADE
    CUSTOMER_STEPS = 0
    ITEMS_SOLD = 0
    MONEY_MADE = 0.0
    #main simulation loop
    while(counter < MAX_TIME):
        #time to add a new customer
        if((counter % DELTA_CUSTOMER) == 0 and customerCounter < TOTAL_CUSTOMERS - 1):
            if(activeCustomerList is None):
                activeCustomerList = np.array([customerList[customerCounter]])
                customerCounter = customerCounter + 1
            else:
                newList = []
                for i in activeCustomerList:
                    newList.append(i)
                newList.append(customerList[customerCounter])
                customerCounter = customerCounter + 1
                activeCustomerList = np.array(newList)
        #loop through all customers
        for i in activeCustomerList:
            MoveCustomer(i, shelves, activeCustomerList)
            CustomerPurchase(i, shelves)
        activeCustomerList = RemoveCustomers(activeCustomerList)
        runAnimatedSimulation(activeCustomerList, None)
        #check if it's time to exit the sim
        if(len(activeCustomerList) <= 0 and customerCounter >= TOTAL_CUSTOMERS - 1):
            return
        counter = counter + 1

def runAnimatedSimulation(data1, data3):
    """plot Method

    Method Arguments:
    * data1 = customers
    * data3 = undefined overlay
    
    Function:
    * plots the 3 arrays
     

    Output:
    * nice animated chart

    """
    
    #store layout
    store = np.zeros(shape=(STORE_SIZE,STORE_SIZE))
    for i in range(len(shelfPositions)):
        cords = shelfPositions[i]
        store[cords[0], cords[1]] = 1
                    
    customers = np.zeros(shape=(STORE_SIZE,STORE_SIZE))
    for i in range(len(data1)):
        cords = data1[i].loc_in_env
        customers[cords[0], cords[1]] = 1
    cMask = np.ma.masked_where(customers == 0, customers)
    
    plt.imshow(store, cmap='Blues', interpolation='nearest')
    plt.imshow(cMask, cmap='summer', interpolation='nearest')
    #plt.imshow(data3, cmap='autumn', interpolation='nearest')
    plt.show()
    plt.pause(0.01)


#Classes

class Item(object):
    """
    Item
    class containing a string of which item it is, and a float price for said item.
    """
    def __init__(self, n_init = '', p_init = 0.0) :
        
        
        self.name = n_init
        self.price = p_init

class Customer(object):
    """
    Customer
    class containing a two element numpy array representing the position within
    the store, a numpy array of items which represents the primary item list, 
    and a numpy array of items which represents the secondary item list.
    """
    def __init__(self, x_init=0, y_init=0, pl_init = [], sl_init = []) :
        
        self.loc_in_env = np.array([x_init, y_init])
        
        self.primary_list = pl_init
        self.secondary_list = sl_init

class Shelf(object):
    """
    Shelf
    class containing a reference to the item which is represented
    and a pair of integers representing the position in the store of the item.
    """
    def __init__(self, stockedItem, x_init=0, y_init=0):
        self.loc_in_env = np.array([x_init, y_init])
        self.stock = stockedItem

#TestingSuite

def TestAll():
    """
    TestAll
    this function will test all code currently testable
    this is performed by calling all relevant test functions individually
    """
    TestAllNonSim()
    TestAllSims()

def TestAllNonSim():
    """
    TestAllNonSim
    this function will test all code which is not a simulation running function
    this is performed by calling all relevant test functions individually
    """
    TestMoveCustomer()
    TestCustomerPurchase()
    TestRemoveCustomers()
    TestCreateStore()
    TestCreateCustomer()
    TestCreateCustomerList()

def TestAllSims():
    """
    TestAllSims
    this function will test all code which is a simulation running function
    this is preformed by calling all relevant test functions individually
    """
    TestOneSimulation()
    TestOneHundredSimulations()
    TestOneDensitySimulation()
    TestOneHundredDensitySimulations()

def TestMoveCustomer():
    """
    TestMoveCustomer
    this function will test the MoveCustomer function. this is done by
    generating a set of shelves, and testing the customer movement in
    different situations.
    
    the following situations are tested:
    -the customer is aligned with an item, and should move towards it
    -the customer is not aligned and should move towards the edge of the store
    """
    customer = createCustomer(PRIMARY_LIST, SECONDARY_LIST)
    customer.primary_list = np.array([PRIMARY_LIST[0]])
    customer.loc_in_env = np.array([0,1])
    shelves = np.array([Shelf(PRIMARY_LIST[0], 2, 0)])
    global CUSTOMER_STEPS
    CUSTOMER_STEPS = 0
    MoveCustomer(customer, shelves, np.array([customer]))
    if(not customer.loc_in_env[1] == 1):
        print("TestMoveCustomer Test #1 failed:")
        print("customer y position is " + str(customer.loc_in_env[1]) + " expected 1")
    if(not customer.loc_in_env[0] == 1):
        print("TestMoveCustomer Test #2 failed:")
        print("customer x position is " + str(customer.loc_in_env[0]) + " expected 1")
    if(not CUSTOMER_STEPS == 1):
        print("TestMoveCustomer Test #3 failed:")
        print("customer steps is at " + str(CUSTOMER_STEPS) + " expected 1")
    
    customer = createCustomer(PRIMARY_LIST, SECONDARY_LIST)
    customer.primary_list = np.array([PRIMARY_LIST[0]])
    customer.loc_in_env = np.array([2,3])
    shelves = np.array([Shelf(PRIMARY_LIST[0], 2, 0), Shelf(PRIMARY_LIST[0], 2, 2)])
    CUSTOMER_STEPS = 0
    MoveCustomer(customer, shelves, np.array([customer]))
    if(not customer.loc_in_env[1] == 3):
        print("TestMoveCustomer Test #4 failed:")
        print("customer y position is " + str(customer.loc_in_env[1]) + " expected 3")
    if(not customer.loc_in_env[0] == 1):
        print("TestMoveCustomer Test #5 failed:")
        print("customer x position is " + str(customer.loc_in_env[0]) + " expected 1")
    if(not CUSTOMER_STEPS == 1):
        print("TestMoveCustomer Test #6 failed:")
        print("customer steps is at " + str(CUSTOMER_STEPS) + " expected 1")

def TestCustomerPurchase():
    """
    TestCustomerPurchase
    this function will test the CustomerPurchase function. this is done by
    generating a set of shelves, and testing the customer purchasing from
    nearby shelves
    
    the following situations are tested:
    -the customer is near a shelf with an item they want, and they purchase it
    -the customer is near a shelf with a secondary item they want, and they
     purchase it
    -the customer is near a shelf without a primary or secondary item they
     want, and they do not purchase it
    """
    customer = createCustomer(PRIMARY_LIST, SECONDARY_LIST)
    customer.primary_list = np.array([PRIMARY_LIST[0]])
    customer.loc_in_env = np.array([0,1])
    shelves = np.array([Shelf(PRIMARY_LIST[0], 1, 0)])
    global ITEMS_SOLD
    global MONEY_MADE
    ITEMS_SOLD = 0
    MONEY_MADE = 0.0
    CustomerPurchase(customer, shelves)
    if(not len(customer.primary_list) == 0):
        print("TestCustomerPurchase Test #1 failed:")
        print("customer primary list is not empty, currently " + str(customer.primary_list))
    if(not ITEMS_SOLD == 1):
        print("TestCustomerPurchase Test #2 failed:")
        print("items sold is at " + str(ITEMS_SOLD) + " expected 1")
    if(not MONEY_MADE == PRIMARY_LIST[0].price):
        print("TestCustomerPurchase Test #3 failed:")
        print("money made is at " + str(MONEY_MADE) + " expected " + str(PRIMARY_LIST[0].price))
    
    customer = createCustomer(PRIMARY_LIST, SECONDARY_LIST)
    customer.secondary_list = np.array([SECONDARY_LIST[0]])
    customer.loc_in_env = np.array([0,1])
    shelves = np.array([Shelf(SECONDARY_LIST[0], 1, 0)])
    ITEMS_SOLD = 0
    MONEY_MADE = 0.0
    CustomerPurchase(customer, shelves)
    if(not len(customer.secondary_list) == 0):
        print("TestCustomerPurchase Test #4 failed:")
        print("customer primary list is not empty, currently " + str(customer.primary_list))
    if(not ITEMS_SOLD == 1):
        print("TestCustomerPurchase Test #5 failed:")
        print("items sold is at " + str(ITEMS_SOLD) + " expected 1")
    if(not MONEY_MADE == SECONDARY_LIST[0].price):
        print("TestCustomerPurchase Test #6 failed:")
        print("money made is at " + str(MONEY_MADE) + " expected " + str(PRIMARY_LIST[0].price))
    
    customer = createCustomer(PRIMARY_LIST, SECONDARY_LIST)
    customer.primary_list = np.array([PRIMARY_LIST[0]])
    customer.loc_in_env = np.array([0,1])
    shelves = np.array([Shelf(PRIMARY_LIST[1], 1, 0)])
    ITEMS_SOLD = 0
    MONEY_MADE = 0.0
    CustomerPurchase(customer, shelves)
    if(not len(customer.primary_list) == 1):
        print("TestCustomerPurchase Test #7 failed:")
        print("customer primary list is currently " + str(customer.primary_list) + "expected one item")
    if(not ITEMS_SOLD == 0):
        print("TestCustomerPurchase Test #8 failed:")
        print("items sold is at " + str(ITEMS_SOLD) + " expected 0")
    if(not MONEY_MADE == 0.0):
        print("TestCustomerPurchase Test #9 failed:")
        print("money made is at " + str(MONEY_MADE) + " expected 0")

def TestRemoveCustomers():
    """
    TestRemoveCustomers
    this function will test the RemoveCustomers function. this is done by
    generating a set of customers, and testing the customer removal for
    customers without primary items
    
    the following situations are tested:
    -one customer is left and has no more primary items
    -one customer exists but still has primary items
    """
    customer = createCustomer(PRIMARY_LIST, SECONDARY_LIST)
    customer.primary_list = np.array([])
    output = RemoveCustomers(np.array([customer]))
    if(not len(output) == 0):
        print("TestRemoveCustomers Test #1 failed:")
        print("customer list is not empty, currently " + str(output))
    
    customer = createCustomer(PRIMARY_LIST, SECONDARY_LIST)
    output = RemoveCustomers(np.array([customer]))
    if(not len(output) == 1):
        print("TestRemoveCustomers Test #1 failed:")
        print("customer list is not filled, currently " + str(output))

def TestOneSimulation():
    """
    TestOneSimulation
    this function will test the RunOneSimulation function. It will compare
    The outputs of the function to ensure they make sense
    
    the following situations are tested:
    -one simulation is run
    """
    RunOneSimulation(createStore(shelfPositions))
    if(not ITEMS_SOLD <= 300):
        print("TestOneSimulation Test #1 failed:")
        print("items sold is " + str(ITEMS_SOLD) + " expected less than 300")
    if(not CUSTOMER_STEPS <= 15000):
        print("TestOneSimulation Test #2 failed:")
        print("customer steps is " + str(CUSTOMER_STEPS) + " expected less than 15000")

def TestOneDensitySimulation():
    """
    TestOneDensitySimulation
    this function will test the RunOneDensity Simulation function. It will
    compare the outputs of the function to ensure they make sense
    
    the following situations are tested:
    -one simulation is run with density
    """
    RunOneSimulationDensity(createStore(shelfPositions))
    if(not ITEMS_SOLD <= 300):
        print("TestOneDensitySimulation Test #1 failed:")
        print("items sold is " + str(ITEMS_SOLD) + " expected less than 300")
    if(not CUSTOMER_STEPS <= 15000):
        print("TestOneDensitySimulation Test #2 failed:")
        print("customer steps is " + str(CUSTOMER_STEPS) + " expected less than 15000")

def TestOneHundredSimulations():
    """
    TestOneHundredSimulations
    this function will test the RunOneHundredSimulations function. It will compare
    The outputs of the function to ensure they make sense
    
    the following situations are tested:
    -one hundred simulations are run
    """
    output = RunOneHundredSimulations(createStore(shelfPositions))
    if(not output[0] <= 300):
        print("TestOneSimulation Test #1 failed:")
        print("average items sold is " + str(output[0]) + " expected less than 300")
    if(not output[2] <= 15000):
        print("TestOneSimulation Test #2 failed:")
        print("average customer steps is " + str(output[2]) + " expected less than 15000")

def TestOneHundredDensitySimulations():
    """
    TestOneHundredDensitySimulations
    this function will test the RunOneHundredDensitySimulations function. It will compare
    The outputs of the function to ensure they make sense
    
    the following situations are tested:
    -one hundred simulations are run with density
    """
    output = RunOneHundredDensitySimulations(createStore(shelfPositions))
    if(not output[0] <= 300):
        print("TestOneSimulation Test #1 failed:")
        print("average items sold is " + str(output[0]) + " expected less than 300")
    if(not output[2] <= 15000):
        print("TestOneSimulation Test #2 failed:")
        print("average customer steps is " + str(output[2]) + " expected less than 15000")

def TestCreateStore():
    """
    TestCreateStore
    this function will test the TestCreateStore function. it will compare the
    created shelf list to what is expected.
    
    the following situations are tested:
    -creating the store with the default layout
    """
    output = createStore(shelfPositions)
    for i in output:
        if(i.loc_in_env[0] == 0 and i.loc_in_env[1] == 0):
            print("TestCreateStore Test #1:")
            print("shelf found in 0,0 the store may not have been created correctly")

def TestCreateCustomer():
    """
    TestCreateCustomer
    this function will test the createCustomer function. it will compare the
    created customer to what is expected.
    
    the following situations are tested:
    -a single customer is created without density
    """
    customer = createCustomer(PRIMARY_LIST, SECONDARY_LIST, None, None)
    if(not len(customer.primary_list) == NUMBER_PRIMARY_LIST):
        print("TestCreateCustomer Test #1 failed:")
        print("customer primary list is " + str(customer.primary_list) + \
              " expected " + str(NUMBER_PRIMARY_LIST) + " items")
    if(not len(customer.secondary_list) == NUMBER_SECONDARY_LIST):
        print("TestCreateCustomer Test #2 failed:")
        print("customer secondary list is " + str(customer.secondary_list) + \
              " expected " + str(NUMBER_SECONDARY_LIST) + " items")

def TestCreateCustomerList():
    """
    TestCreateCustomerList
    this function will test the createCustomerList function. it will compare the
    created customer to what is expected.
    
    the following situations are tested:
    -a single customer list is created without density
    """
    customerList = createCustomerList(TOTAL_CUSTOMERS, None, None)
    if(not len(customerList) == TOTAL_CUSTOMERS):
        print("TestCreateCustomerList Test #1 failed:")
        print("customer list is " + str(customerList) + \
              " expected " + str(TOTAL_CUSTOMERS) + " customers")

def TestCustomerRangeDifference():
    """
    TestCustomerRangeDifference
    this function will get the average results from simulations run one 
    hundred times where the customer view range is changed.
    the results are printed
    the shelves are the same between simulations
    """
    global VIEW_RANGE
    shelves = createStore(shelfPositions)
    VIEW_RANGE = 0
    print("the shelf layout is...")
    for i in shelves:
        print(i.stock.name)
    for i in range(5):
        VIEW_RANGE = VIEW_RANGE + 1
        averages = RunOneHundredSimulations(shelves)
        print("For simulation with view range " + str(i + 1) + ":")
        print("The average items sold was " + str(averages[0]) + ".")
        print("The average money earned was " + str(averages[1]) + ".")
        print("The average distance walked was " + str(averages[2]) + ".")
    VIEW_RANGE = 1

def TestCustomerFlowDifference():
    """
    TestCustomerFlowDifference
    this function will get the average results from simulations run one 
    hundred times where the customer entrance rate is changed.
    the results are printed
    the shelves are the same between simulations
    """
    global DELTA_CUSTOMER
    shelves = createStore(shelfPositions)
    DELTA_CUSTOMER = 0
    print("the shelf layout is...")
    for i in shelves:
        print(i.stock.name)
    for i in range(10):
        DELTA_CUSTOMER = DELTA_CUSTOMER + 1
        averages = RunOneHundredSimulations(shelves)
        print("For simulation with steps between customers " + str(i + 1) + ":")
        print("The average items sold was " + str(averages[0]) + ".")
        print("The average money earned was " + str(averages[1]) + ".")
        print("The average distance walked was " + str(averages[2]) + ".")
    DELTA_CUSTOMER = 5

def TestCustomerTotalDifference():
    """
    TestCustomerTotalDifference
    this function will get the average results from simulations run one 
    hundred times where the number of total customers is changed.
    the results are printed
    the shelves are the same between simulations
    """
    global TOTAL_CUSTOMERS
    shelves = createStore(shelfPositions)
    TOTAL_CUSTOMERS = 0
    print("the shelf layout is...")
    for i in shelves:
        print(i.stock.name)
    for i in range(10):
        TOTAL_CUSTOMERS = TOTAL_CUSTOMERS + 10
        averages = RunOneHundredSimulations(shelves)
        print("For simulation with total customers " + str((i + 1) * 10) + ":")
        print("The average items sold was " + str(averages[0]) + ".")
        print("The average money earned was " + str(averages[1]) + ".")
        print("The average distance walked was " + str(averages[2]) + ".")
    TOTAL_CUSTOMERS = 30

def TestCustomerItemDifference():
    """
    TestCustomerTotalDifference
    this function will get the average results from simulations run one 
    hundred times where the number of items chosen per customer is changed.
    the results are printed
    the shelves are the same between simulations
    """
    global NUMBER_PRIMARY_LIST
    global NUMBER_SECONDARY_LIST
    shelves = createStore(shelfPositions)
    NUMBER_PRIMARY_LIST = 0
    NUMBER_SECONDARY_LIST = 0
    print("the shelf layout is...")
    for i in shelves:
        print(i.stock.name)
    for i in range(10):
        NUMBER_PRIMARY_LIST = NUMBER_PRIMARY_LIST + 1
        NUMBER_SECONDARY_LIST = NUMBER_SECONDARY_LIST + 1
        averages = RunOneHundredSimulations(shelves)
        print("For simulation with total items " + str((i + 1) * 2) + ":")
        print("The average items sold was " + str(averages[0]) + ".")
        print("The average money earned was " + str(averages[1]) + ".")
        print("The average distance walked was " + str(averages[2]) + ".")
    NUMBER_PRIMARY_LIST = 3
    NUMBER_SECONDARY_LIST = 7
    
#analysis
def plotStoreOutput(runs):
    
    
    global ITEMS_COUNTER
    sold = []
    rev = []
    dist = []
    
    
    display = []
    quantity = 0
    
    for i in range(runs):
        shelves = createStore(shelfPositions)
        output = RunOneHundredSimulations(shelves)
        print(output)
        
        #print out shelves
        for i in shelves:
            for j in ITEMS_COUNTER:
                if j[0].name == i.stock.name:
                    
                   if j[1] == 0:
                       quantity = j[1]
                   else:
                       quantity = j[1] / 100
            print(str([i.loc_in_env[0], i.loc_in_env[1]]) + " " + i.stock.name + " " + str(quantity))
        #resets display
        display = []
        #print out how often items were bought 
        """
        for i in ITEMS_COUNTER:
            print(i[0].name)
            if i[1] == 0:
                print(i[1])
            else:
                print(i[1] / 100)
                
                
            if past == i.loc_in_env[0]:
                
                #determine the quantity for the named item
                for j in ITEMS_COUNTER:
                    if j[0].name == i.stock.name:
                        if j[1] == 0:
                            quantity = j[1]
                        else:
                            quantity = j[1] / 100
                
                display.append(str([i.loc_in_env[0], i.loc_in_env[1]]) + " " + i.stock.name + " " + str(quantity))
                
            else:
                past += 1
                print(display)
                #print(pos)
                display = []
                
                for j in ITEMS_COUNTER:
                    if j[0].name == i.stock.name:
                        if j[1] == 0:
                            quantity = j[1]
                        else:
                            quantity = j[1] / 100
                
                display.append(str([i.loc_in_env[0], i.loc_in_env[1]]) + " " + i.stock.name + " " + str(quantity))
        
                
        """  
        
        sold.append(output[0])
        rev.append(output[1])
        dist.append(output[2])
        
    #combo = [sold,rev, dist]
    #hard coded limit might need to change
    #plt.ylim(500,600)
    plt.plot(range(runs), sold, 'ro')
    plt.plot(range(runs), rev, 'bo')
    plt.plot(range(runs), dist, 'go')
    
def customerStoreOutput(runs, custCount):
    
    global TOTAL_CUSTOMERS
    stored = TOTAL_CUSTOMERS 
    TOTAL_CUSTOMERS = custCount
    
    plotStoreOutput(runs)
    
    #restore default
    TOTAL_CUSTOMERS = stored

def plotStoreOutputDensity(runs):
    
    
    global ITEMS_COUNTER
    sold = []
    rev = []
    dist = []
    
    
    display = []
    pos = []
    past = 0
    quantity = 0
    
    for i in range(runs):
        shelves = createStore(shelfPositions)
        output = RunOneHundredDensitySimulations(shelves)
        print(output)
        
        #print out shelves
        for i in shelves:
            if past == i.loc_in_env[0]:
                
                #determine the quantity for the named item
                for j in ITEMS_COUNTER:
                    if j[0].name == i.stock.name:
                        if j[1] == 0:
                            quantity = j[1]
                        else:
                            quantity = j[1] / 100
                
                display.append(str([i.loc_in_env[0], i.loc_in_env[1]]) + i.stock.name + str(quantity))
                #pos.append()
            else:
                past += 1
                print(display)
                #print(pos)
                display = []
                pos = []
        
        #print out how often items were bought 
        """
        for i in ITEMS_COUNTER:
            print(i[0].name)
            if i[1] == 0:
                print(i[1])
            else:
                print(i[1] / 100)
        """
        #Reset
        ITEMS_COUNTER = []
        
         
        
        sold.append(output[0])
        rev.append(output[1])
        dist.append(output[2])
        
    #combo = [sold,rev, dist]
    #hard coded limit might need to change
    #plt.ylim(500,600)
    plt.plot(range(runs), sold, 'ro')
    plt.plot(range(runs), rev, 'bo')
    plt.plot(range(runs), dist, 'go')



initItems()