import search
import sys
from collections import deque

class BFS(object):
    ''' Class for performing Breadth-First Search on a Graph
    '''
    
    def __init__(self, graph):
        self.graph = graph
        
    def find_path(self, start_node, end_node):
        ''' Perform BFS search
        '''
        
        # Start the frontier with the original node
        frontier = deque([start_node])
        observed = set(start_node)
        
        # Store paths as a dictionary
        # The key is the name of a node, the value is 
        # the name of the node that led to the key
        paths = {}
        
        while len(frontier) > 0:
            cur_explored = frontier.popleft()
            # Store the explored set, so as to not visit again
            
            for neighbor, _ in self.graph.adj(cur_explored):
                # Did we find the goal?
                # If not, add the new neighbor to the frontier
                if neighbor not in observed: 
                    # Add to frontier
                    # Add to observed nodes, don't return to them
                    # Leave breadcrumbs to retrace our parth
                    frontier.append(neighbor)
                    observed.add(neighbor)
                    paths[neighbor] = cur_explored
                    
                if neighbor == end_node:
                    print('Found ', end_node)
                    # Now retrace steps
                    sol_path = [end_node]
                    cur_node = end_node
                    while cur_node != start_node:
                        cur_node = paths[cur_node]
                        sol_path.append(cur_node)
                        
                    return list(reversed(sol_path))
                
        # If we got this far, there are no nodes in the frontier
        # but we haven't found our goal node
        # Declare failure.
        print('Failed to find node ', end_node)
        return []
        
        
if __name__ == "__main__":
    # Do some tests
    
    if len(sys.argv) == 1:
        print('usage: bfs start end')
        exit()
        
    start = sys.argv[1]
    end   = sys.argv[2]
    
    map = search.DEG('cities.txt')  
    bfs = BFS(map)
    path = bfs.find_path (start, end)  

    print('Solution path: ', path)       
    
        
