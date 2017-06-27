#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 16:59:05 2017

@author: bobradov
"""

class GridWorld(object):
    ''' A grid in which the squares are occupied with various
    obstacles.
    Provides a playground for testing path-finding algorithms.
    '''
    
    def __init__(self, rows, cols):
        self.rows = int(rows)
        self.cols = int(cols)
        self.grid = [0]*self.rows*self.cols
        
    def to_string(self):
        ret_str = ''
        for cur_row in range(0, self.rows):
            for cur_col in range(0, self.cols):
                val = self.get_value(cur_col, cur_row)
                if val != 0:
                    ret_str += str(val)
                else:
                    ret_str += '-'
            ret_str += '\n'
                    
        return ret_str
    
    
    def add_path(self, path):
        for cur_step in path:
            self.grid[cur_step] = 'x'
    
    def add_vline(self, x, ymin, ymax, val=1):
        for cur_y in range(ymin, ymax + 1):
            node_id = self.get_node_id(x, cur_y)
            self.grid[node_id] = val
        print(self.grid)
        
    def get_value(self, x, y):
        if x >= 0 and x < self.cols and y >= 0 and y < self.rows:
            #print('Got ', self.grid[x+self.cols*y], ' with x=', x, ' y=', y)
            #print(type(x))
            #print(type(y))
            #print(type(self.cols))
            return self.grid[x + self.cols*y]
        else:
            #print('Got None with x=', x, ' y=', y)
            return None
        
    def get_node_id(self, x, y):
        return x + self.cols*y
        
    def get_coords(self, id):
        x = id % self.cols
        y = int((id - x) / self.cols)
        return (x, y)
    
    def adj(self, node_id):
        ''' Find all adjacencies of node named node_id
        
        Return: list of tuples
                [(node_id1, cost), (node_id2, cost), ...]
        '''
        
        x, y = self.get_coords(node_id)
        
        #print('neighbors of node: ', node_id, ' at coords: x=', x, ' y=', y)
        
        retlist = []
        
        # Attempt to get horizontal moves
        val_right = self.get_value(x + 1, y)
        if val_right != None:
            retlist.append((self.get_node_id(x + 1, y), val_right))
            
        val_left  = self.get_value(x - 1, y)
        if val_left != None:
            retlist.append((self.get_node_id(x - 1, y), val_left))
            
        # Attempt vertical moves
        val_up = self.get_value(x, y - 1)
        if val_up != None:
            retlist.append((self.get_node_id(x, y - 1), val_up))
            
        val_down  = self.get_value(x, y + 1)
        if val_down != None:
            retlist.append((self.get_node_id(x, y + 1), val_down))
        
        #print('Full retlist for node: ', retlist)
        return retlist
    
if __name__ == '__main__':
    # Do some tests
    
    gw = GridWorld(5, 5)
    
    gw.add_vline(2, 0, 2, val=9)
    print(gw.to_string())
    
    node_ids = [gw.get_node_id(x, y) for y in range(0, 5) for x in range(0, 5)]
    print('node_id: ', node_ids)
    
    