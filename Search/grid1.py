#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 18:08:18 2017

@author: bobradov
"""

import GridWorld as gw
import Astar as astar

if __name__ == '__main__':
    # Do some tests
    
    gw1 = gw.GridWorld(5, 5)
    
    gw1.add_vline(2, 0, 2, val=9)
    print(gw1.to_string())
    
    # Define start and end nodes
    start = gw1.get_node_id(0, 0)
    end   = gw1.get_node_id(4, 0)
    
    def manhattan_dist(gwn, node, goal):
        xn, yn = gwn.get_coords(node)
        xg, yg = gwn.get_coords(goal)
        return abs(xg - xn) + abs(yg - yn)
    
    search = astar.Astar(gw1, lambda node : manhattan_dist(gw1, node, end))
    
    path, explored = search.find_path(start, end)
    
    print('Path: ', path)
    
    gw1.add_path(path)
    
    print(gw1.to_string())