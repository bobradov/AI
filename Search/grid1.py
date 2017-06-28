#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 18:08:18 2017

@author: bobradov
"""

import GridWorld as gw
import Astar as astar
import math

if __name__ == '__main__':
    # Do some tests
    
    n_grid = 50
    
    gw1 = gw.GridWorld(n_grid, n_grid)
    
    gw1.add_vline(int(n_grid/3)-1, int(0.25*n_grid), n_grid-1, val=9)
    gw1.add_vline(int(2*n_grid/3), 0, int(0.65*n_grid), val=9)
    #print(gw1.to_string())
    
    # Define start and end nodes
    start = gw1.get_node_id(0, 0)
    end   = gw1.get_node_id(n_grid-1, 0)
    
    def manhattan_dist(gwn, node, goal):
        xn, yn = gwn.get_coords(node)
        xg, yg = gwn.get_coords(goal)
        return abs(xg - xn) + abs(yg - yn)
    
    def euclidean_dist(gwn, node, goal):
        xn, yn = gwn.get_coords(node)
        xg, yg = gwn.get_coords(goal)
        return math.sqrt((xg - xn)*(xg - xn) + 
                         (yg - yn)*(yg - yn))
        
    #search = astar.Astar(gw1, lambda node : manhattan_dist(gw1, node, end))
    
    search = astar.Astar(gw1, lambda node : euclidean_dist(gw1, node, end))
    
    path, explored = search.find_path(start, end)
    
    #print('Path: ', path)
    
    gw1.add_path(path)
    
    print(gw1.to_string())