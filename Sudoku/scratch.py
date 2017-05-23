#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 17:14:10 2017

@author: bobradov
"""



def cross(a, b):
    return [s+t for s in a for t in b]





def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


# WARNING! We've modified this function to return '123456789' instead of '.' for boxes with no value.
# Look at the explanation above in the text.
def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values



def eliminate_old(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    
    new_dict = values.copy()
    
    for cur_box in boxes:
       
        if len(new_dict[cur_box]) == 1:
            #print('Unique value in:', cur_box, ' with value=', new_dict[cur_box])
            
            # Loop over all peers, eliminate values[cur_box]
            elim_val = new_dict[cur_box]
            
            for cur_peer in peers[cur_box]:
                if elim_val in new_dict[cur_peer]:
                    #print('Must eliminate ', elim_val, ' from ', 
                    #      cur_peer)
                    #print('Eliminating ', elim_val, ' from ', new_dict[cur_peer])
                    if len(new_dict[cur_peer]) > 1:
                        new_dict[cur_peer] = new_dict[cur_peer].replace(elim_val, '')
                    #print('After elimination, got: ', new_dict[cur_peer])
                                       
    return new_dict

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def only_choice_old(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    
    new_values = { key : values[key] for key in values  }
    
    for cur_block in units:
        for cur_unit in units[cur_block]:
            # Build histogram of values
            hist = { str(i) : 0 for i in range(1, 10) }
            
            for cur_block_in_unit in cur_unit:
                vals = new_values[cur_block_in_unit]
                for cur_val in vals:
                    hist[cur_val] += 1
         
            
            # Now find if there are any digits in this unit with a 
            # single occurrence
            unique_vals = [ i for i in range(1, 10) if hist[str(i)]==1 ]
          
            
            # Now find out where each unique value belongs
            # Update dictionary
            for val in unique_vals:
                for cur_block_in_unit in cur_unit:
                    if str(val) in new_values[cur_block_in_unit]:
                        new_values[cur_block_in_unit] = str(val)
                    
            
        
    return new_values      

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            #print('Bad reduction')
            #display(values)
            return False
    return values


def reduce_puzzle_old(in_values):
    # Defensive copy first
    values = in_values.copy()
    stalled = False
    #ßprint('At start:')
    #display(values)
    
    
    while not stalled:
        #print(' >>>>>>> Iteration: ', iter, ' <<<<<<<<<<<')
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        #print('Solved values at start of iteration: ', solved_values_before)
        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)
        #print('After elimination:')
        #display(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)
        #print('After only choice:')
        #display(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        #print('Solved values at end of iteration: ', solved_values_after)
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            print('Bad reduction')
            display(values)
            return False
        
        
    # No more progress   
    return values



def search_new(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt



def search(in_values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function    
    # Choose one of the unfilled squares with the fewest possibilities    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!

   
    # Are we done?
    # If so, there are no more unfinished boxes, and we can return
    
    num_unfinished_boxes = len([box for box in in_values.keys() 
                                            if len(in_values[box]) > 1])
    print('Number of unfinished boxes:', num_unfinished_boxes)
    if num_unfinished_boxes == 0:
        print('Puzzle solved.')
        return in_values
    
    # OK, not done. Do recursion
    
    # Reduce the board as much as possible
    values = reduce_puzzle(in_values)
    if values == False:
        # Bad reduction, inconsistent board
        return False
    
    # Find the box with the smallest number of possibilities (but greater>1)
    len_list = [ (box, len(values[box])) for box in values.keys() 
                                         if len(values[box]) > 1 ]
    
    if len(len_list) < 1:
        print('Puzzle solved after final reduction.')
        return values
    
    min_element = min(len_list, key=lambda x : x[1])
    #print(len_list)
    #print('min_element: ', min_element)
    min_box = min_element[0]
    
    for guess_value in values[min_box]:
        #print('>>>> Guessing ', min_box, ' contains ', guess_value)
        guess_board = values.copy()
        guess_board[min_box] = guess_value
        
        res = search(guess_board)
        if not res:
            continue
        #print('res: ', res)
        num_unfinished_boxes = len([box for box in res.keys() 
                                            if len(res[box]) > 1])
        if num_unfinished_boxes == 0:
            #print('Returning from function ...')
            return res
    
    # Shouldn't need to return from here, implies search failed.    
    #print('returning from end ...')    
    #return guess_board


  
if __name__ == '__main__':
    
    
    
    rows = 'ABCDEFGHI'
    cols = '123456789'
    
    boxes = cross(rows, cols)

    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
    unitlist = row_units + column_units + square_units
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    
    '''
    grid_string = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
    
    display(grid_values(grid_string))
    
    print('After elimination:')
    
    new_values = eliminate(grid_values(grid_string))
    display(new_values)
    #print(new_values)
    
    # Now do only choice
    print('After only choice:')
    only_choice_dict = only_choice(new_values)
    #print(only_choice_dict)
    display(only_choice_dict)
    
    
    # Now test reduce puzzle
    # Start with initial description of board
    final_board = reduce_puzzle(grid_values(grid_string))
    display(final_board)
   
    
    
    '''
    grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    values = grid_values(grid2)
    print('Initial harder sudoku:')
    display(values)
    harder_sudoku = reduce_puzzle(values)
    print('After attempting to reduce:')
    display(harder_sudoku)
    
    # Start search with original values
    final = search(values)
    print('Final board:')
    display(final)
    
    #eliminate