#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 16:43:25 2017

@author: bobradov
"""

class Node(object):
    def __init__(self, name):
        self.name = name
        self.edge_list = []
        
class DirectedEdge(object):
    def __init__(self, prop_dict, points_to):
        self.prop_dict = prop_dict
        self.points_to = points_to


class DEG(object):
    ''' Class for Directed Edge Graphs
    '''
    
    def __init__(self, fname):
        self.nodes = {}
        if not self.load(fname):
            raise OSError
            
            
    def adj(self, node_name):
        ''' Find all adjacencies of node named node_name
        
        Return: list of tuples
                [(node_name, cost), (node_name, cost), ...]
        '''
        cur_node = self.nodes[node_name]
        edges = cur_node.edge_list
        
        ret_list = [(cur_edge.points_to.name, cur_edge.prop_dict['dist'])
                    for cur_edge in edges]
        return ret_list
        
        
    
    def to_string(self):
        str_build = ''
        for cur_node in self.nodes:
            str_build += 'Node: ' + cur_node + ' '
            '''
            for cur_edge in self.nodes[cur_node].edge_list:
                str_build += cur_edge.prop_dict['dist'] + 'km to: '
                str_build += cur_edge.points_to.name + ' '
            '''
            for neighbor, dist in self.adj(cur_node):
                str_build += str(dist) + 'km to: '
                str_build += neighbor + ' '
            str_build += '\n'
        return str_build
    
    
            
    def load(self, fname):
        fp = open(fname, 'r')
        all_text = fp.read()
        
        # Build graph in two passes
        # 1. Scan for node names
        # 2. Scan for directed edges
        
        lines = all_text.split('\n')
        
        # Node building
        for cur_line in lines:
            if len(cur_line) > 0:
                words = cur_line.split()
                #print('words: ', words)
                
                cur_node_name = words[0]
                self.nodes[cur_node_name] = Node(cur_node_name)
             
        # Now that nodes are built, loop again and build edges
        for cur_line in lines:
             if len(cur_line) > 0:
                words = cur_line.split()
                cur_node_name = words.pop(0)
                
                # Now read all the edge connections
                while len(words) > 0:
                    goal_node = words.pop(0)
                    goal_dist = int(words.pop(0))
                    
                    # Create a new edge
                    new_edge = DirectedEdge({'dist' : goal_dist}, 
                                              self.nodes[goal_node])
                    
                    self.nodes[cur_node_name].edge_list.append(new_edge)
                    
                    
                    
                
        
        #print(lines)
        return True
        
        
        
if __name__ == '__main__':
    map = DEG('cities.txt')
    
    print(map.to_string())
    
        
    