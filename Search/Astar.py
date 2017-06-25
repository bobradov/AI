import search
import sys
import queue as Q

class Astar(object):
    ''' Class for performing Uniform Cost Search on a Graph
    '''
    
    def __init__(self, graph, heuristic):
        self.graph = graph
        self.heuristic = heuristic
        
    def find_path(self, start_node, end_node):
        ''' Perform UCS search
        '''
        
        # Start the frontier with the original node
        # The cost of the start node is 0
        frontier = Q.PriorityQueue()
        start_cost = self.heuristic(start_node)
        
        # Frontier: (tot_cost, path_cost, node)
        
        frontier.put((start_cost, 0, start_node))
        explored = set()
        path_cost = {}
        path_cost[start_node] = 0
        best_cost = {}
        best_cost[start_node] = start_cost
        
        
        # Store paths as a dictionary
        # The key is the name of a node, the value is 
        # the name of the node that led to the key
        paths = {}
        
        while not frontier.empty():
            # Get the next node in priority order 
            # from the frontier
            tot_cur_cost, cur_cost, cur_explored = frontier.get()
            explored.add(cur_explored)
            print('cur_cost: ', cur_cost, 
                  ' tot_cur_cost: ', tot_cur_cost,
                  ' cur_explored: ', cur_explored)
            
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
                    
                    # Compute cost
                    # Based on past cost, added path cost to neighbor,
                    # and a heuristic applied to the neighbor
                    new_cost = cur_cost + neigh_cost
                    tot_cost = new_cost + self.heuristic(neighbor)
                    print('Neighbor: ', neighbor, ' cur_cost=', cur_cost,
                          ' neigh_cost=', neigh_cost,
                          ' heuristic=', self.heuristic(neighbor))
                                      
                    
                    # Do we add it to the frontier? Only if we haven't
                    # already added it at lower cost (using a different
                    # path)
                    if neighbor not in best_cost.keys() or tot_cost < best_cost[neighbor]:
                        best_cost[neighbor] = tot_cost
                        path_cost[neighbor] = new_cost
                        frontier.put((tot_cost, new_cost, neighbor))
                        paths[neighbor] = cur_explored
                       
                   
                    
                    
                
                
        # If we got this far, there are no nodes in the frontier
        # but we haven't found our goal node
        # Declare failure.
        print('Failed to find node ', end_node)
        return []
        
        
if __name__ == "__main__":
    # Do some tests
    
    if len(sys.argv) == 1:
        print('usage: Astar start')
        exit()
        
        
    # Distances to Bucharest
    buch_dist = { 'Arad' : 366,
                  'Bucharest' : 0,
                  'Craiova' : 160,
                  'Drobeta' : 242,
                  'Eforie'  : 161,
                  'Fagaras' : 176,
                  'Giurgiu' : 77,
                  'Hirsova' : 151,
                  'Iasi'    : 226,
                  'Lugoj'   : 244,
                  'Mehadia' : 241,
                  'Neamt'   : 234,
                  'Oradea'  : 380,
                  'Pitesti' : 100,
                  'Rimnicu' : 193,
                  'Sibiu'   : 253,
                  'Timisoara' : 329,
                  'Urziceni' : 80,
                  'Vaslui'  : 199,
                  'Zerind'  : 394 }    
        
    start = sys.argv[1]
    
    map = search.DEG('cities.txt')  
    
    # Apply Astar search to travel from Bucharest
    # Since the heuristic applies only to distances to Bucharest,
    # the destination must always be Bucharest
    astar = Astar(map, lambda x : buch_dist[x])
    path, explored = astar.find_path (start, 'Bucharest')  

    print('Solution path: ', path) 
    print('Explored: ', len(explored))      
    
        
