# -*- coding: utf-8 -*-
""" Item Class
    
    CSS 458
    By: Maxwell Trinh and Jacob Chesnut
    12/1/2021
"""

import numpy as np

class Item(object):
    
    def __init__(self, n_init = '', p_init = 0.0) :
        
        
        self.name = n_init
        self.price = p_init