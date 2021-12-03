"""
    GroceryModel
    This script handles the Grocery Model final project for CSS 458
    BY: Maxwell Trinh and Jacob Chesnut
"""

#Import statements

import numpy as np

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
    for i in storeShelves:
        pass
    for i in allCustomers:
        pass
        

def CustomerPurchase(customerToPurchase, storeShelves):
    """
    CustomerPurchase
    attempts to purchase items around the customer, if they are in the
    customer's primary or secondary item lists
    """
    
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

