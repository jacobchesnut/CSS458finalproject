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