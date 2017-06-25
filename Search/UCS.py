import search
import sys
import queue as Q

class UCS(object):
    ''' Class for performing Uniform Cost Search on a Graph
    '''
    
    def __init__(self, graph):
        self.graph = graph
        
    def find_path(self, start_node, end_node):
        ''' Perform UCS search
        '''
        
        # Start the frontier with the original node
        # The cost of the start node is 0
        frontier = Q.PriorityQueue()
        frontier.put((0, start_node))
        explored = set()
        best_cost = {}
        best_cost[start_node] = 0
        
        
        # Store paths as a dictionary
        # The key is the name of a node, the value is 
        # the name of the node that led to the key
        paths = {}
        
        while not frontier.empty():
            # Get the next node in priority order 
            # from the frontier
            cur_cost, cur_explored = frontier.get()
            explored.add(cur_explored)
            print('cur_cost: ', cur_cost, ' cur_explored: ', cur_explored)
            
            if cur_explored == end_node:
                    #print('Found ', end_node)
                    # Now retrace steps
                    sol_path = [end_node]
                    cur_node = end_node
                    while cur_node != start_node:
                        cur_node = paths[cur_node]
                        sol_path.append(cur_node)
                        
                    return (list(reversed(sol_path)), explored)
            
            # Explore its neightbors
            # Track the cost associated with neighbors
            for neighbor, neigh_cost in self.graph.adj(cur_explored):
                
                if neighbor not in explored: 
                    # Add to frontier
                    # Cost of new node is added to the total
                    # cost asscoaited with the path so far
                    # Add to observed nodes, don't return to them
                    # Leave breadcrumbs to retrace our path
                    new_cost = cur_cost + neigh_cost
                    if neighbor not in best_cost.keys() or new_cost < best_cost[neighbor]:
                        best_cost[neighbor] = new_cost
                        frontier.put((cur_cost + neigh_cost, neighbor))
                        paths[neighbor] = cur_explored
                        #print('Added to frontier:', neighbor, ' with cost=', 
                        #              cur_cost + neigh_cost,
                        #              ' acc cost=', cur_cost, ' neigh_cost=', neigh_cost)
                   
                    
                    
                
                
        # If we got this far, there are no nodes in the frontier
        # but we haven't found our goal node
        # Declare failure.
        print('Failed to find node ', end_node)
        return []
        
        
if __name__ == "__main__":
    # Do some tests
    
    if len(sys.argv) == 1:
        print('usage: ucs start end')
        exit()
        
    start = sys.argv[1]
    end   = sys.argv[2]
    
    map = search.DEG('cities.txt')  
    ucs = UCS(map)
    path, explored = ucs.find_path (start, end)  

    print('Solution path: ', path) 
    print('Explored: ', len(explored))      
    
        
