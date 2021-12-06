"""
    GroceryModel
    This script handles the Grocery Model final project for CSS 458
    BY: Maxwell Trinh and Jacob Chesnut
"""

#Import statements

import numpy as np
import random

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
STORE_SIZE = 20
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


#Global return values
#int representing the number of steps made in the current simulation
CUSTOMER_STEPS = 0
#int representing the number of items sold in the current simulation
ITEMS_SOLD = 0
#float representing the amount of money made in the current simulation
MONEY_MADE = 0.0

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
        diff = customerCoords - shelfLoc
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
        diff = customerCoords - otherCustomerLoc
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
    
    #attempt to move vertically
    shelfVector = customerCoords - closestShelf.loc_in_env
    if(shelfVector[0] > 1 and not blockedDirections[0]):
        #move north
        customerCoords[0] = customerCoords[0] - 1
        customerToMove.loc_in_env = customerCoords
        return
    if(shelfVector[0] < -1 and not blockedDirections[2]):
        #move south
        customerCoords[0] = customerCoords[0] + 1
        customerToMove.loc_in_env = customerCoords
        return
    
    #attempt to move horizontally
    if(shelfVector[1] > 1 and not blockedDirections[3]):
        #move west
        customerCoords[1] = customerCoords[1] - 1
        customerToMove.loc_in_env = customerCoords
        return
    if(shelfVector[1] < -1 and not blockedDirections[1]):
        #move east
        customerCoords[1] = customerCoords[1] + 1
        customerToMove.loc_in_env = customerCoords
        return
    
    #otherwise move randomly
    randomDirection = GetRandDirection(blockedDirections)
    if(randomDirection == 0):
        #move north
        customerCoords[0] = customerCoords[0] - 1
        customerToMove.loc_in_env = customerCoords
        return
    if(randomDirection == 1):
        #move east
        customerCoords[1] = customerCoords[1] + 1
        customerToMove.loc_in_env = customerCoords
        return
    if(randomDirection == 2):
        #move south
        customerCoords[0] = customerCoords[0] + 1
        customerToMove.loc_in_env = customerCoords
        return
    if(randomDirection == 3):
        #move west
        customerCoords[1] = customerCoords[1] - 1
        customerToMove.loc_in_env = customerCoords
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
            for j in customerToPurchase.secondary_list:
                #item customer wants
                if(j.name == i.stock.name):
                    #remove item
                    newList = []
                    for k in customerToPurchase.secondary_list:
                        #add into the list if not being removed
                        if(not j == k):
                            newList.append(k)
                    customerToPurchase.primary_list = np.array(newList)
                    #increment counters
                    ITEMS_SOLD = ITEMS_SOLD + 1
                    MONEY_MADE = MONEY_MADE + j.price 
 
    def initItems():
        """        
        takes a numpy array of strings and a numpy array of floats, which 
        paired together represent an item. Returns a numpy array of all items 
        created from this.
        """
        #2017 prices for common grocery items. source https://www.visualcapitalist.com/decade-grocery-prices/
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
        PRIMARY_LIST.append(Item('Eggs', 1.6)) #made up price
        PRIMARY_LIST.append(Item('Water', 1.1)) #made up price
        PRIMARY_LIST.append(Item('Pet Food', 4.63)) #made up price
        
        #Secondary items. Makeing stuff up rn
        SECONDARY_LIST.append(Item('Chips', 2.50))
        SECONDARY_LIST.append(Item('Soda', 1.22))
        SECONDARY_LIST.append(Item('Gum', 0.76))
        SECONDARY_LIST.append(Item('Chocolate', 1.02))
        SECONDARY_LIST.append(Item('Ice Cream', 4.70))
        SECONDARY_LIST.append(Item('Fizzy Water', 2.50))
        SECONDARY_LIST.append(Item('Carrot', 3.22))
        SECONDARY_LIST.append(Item('Cake', 10.45))
        SECONDARY_LIST.append(Item('Cookies', 5.78))
        SECONDARY_LIST.append(Item('Beer', 4.20))
        SECONDARY_LIST.append(Item('Cooking Wine', 8.00))
        SECONDARY_LIST.append(Item('Doughnut', 1.41))
        SECONDARY_LIST.append(Item('Chicken Nuggets', 5.80))
        SECONDARY_LIST.append(Item('Fries', 3.69))
        SECONDARY_LIST.append(Item('Cheese', 1.98))
        SECONDARY_LIST.append(Item('Rice Noodles', 5.78))
        SECONDARY_LIST.append(Item('Jelly', 3.12))
        SECONDARY_LIST.append(Item('Juice', 4.90))
        SECONDARY_LIST.append(Item('Brownies', 1.94))
        SECONDARY_LIST.append(Item('Pizza', 6.66))
        
        
    def createStore():
        """
        createStore: takes a 2D numpy array of coordinates (a[0,:] = x coords. 
        A[1,:] = y coords), and returns a numpy array of shelves created in
        each coordinate, with a random item per shelf.
        """
        lol = 1
    def createCustomer():
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
        lol = 1
    def createCustomerList():
        """
        createCustomerList: takes an integer for the number of customers to 
        create, a numpy array of floats representing percentages in an item
        density for primary items (defaults to None if unused), and a numpy
        array of floats representing percentages in an item density for 
        secondary items (defaults to None if unused).  returns a numpy array 
        of that many Customers, using the densities if given.

        """
        lol = 1
        
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

