# -*- coding: utf-8 -*-
""" Customer Class
    
    CSS 458
    By: Maxwell Trinh and Jacob Chesnut
    12/1/2021
"""

import numpy as np

class Customer(object):
    
    def __init__(self, x_init=0, y_init=0, pl_init = [], sl_init = []) :
        
        self.loc_in_env = np.array([x_init, y_init])
        
        self.primary_list = pl_init
        self.secondary_list = sl_init