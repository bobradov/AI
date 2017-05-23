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
    
    new_dict = { key : values[key] for key in values  }
    
    for cur_box in boxes:
       
        if len(values[cur_box]) == 1:
            #print('Unique value in:', cur_box, ' with value=', values[cur_box])
            
            # Loop over all peers, eliminate values[cur_box]
            elim_val = new_dict[cur_box]
            
            for cur_peer in peers[cur_box]:
                if elim_val in new_dict[cur_peer]:
                    #print('Must eliminate ', elim_val, ' from ', cur_peer)
                    split_str = new_dict[cur_peer].split(elim_val)
                    new_val = split_str[0] + split_str[1]
                    #print('Old val: ', values[cur_peer], ' new val:', new_val)
                    new_dict[cur_peer] = new_val
                    
    return new_dict

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    # TODO: Implement only choice strategy here
    
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


def reduce_puzzle(in_values):
    # Defensive copy first
    values = in_values.copy()
    stalled = False
    print('At start:')
    display(values)
    
    
    while not stalled:
        #print(' >>>>>>> Iteration: ', iter, ' <<<<<<<<<<<')
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        #print('Solved values at start of iteration: ', solved_values_before)
        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)
        #print('After elimination:')
        display(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)
        #print('After only choice:')
        display(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        #print('Solved values at end of iteration: ', solved_values_after)
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
        
        
    # No more progress
    # Is it because we are done?
    # If so, no box has a value longer than 1
    num_unfinished_boxes = len([box for box in values.keys() if len(values[box]) > 1])
    #print('Number of unfinished boxes: ', num_unfinished_boxes)
     
        
    return values

  
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
    '''
    
    grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    values = grid_values(grid2)
    print('Initial harder sudoku:')
    #display(values)
    harder_sudoku = reduce_puzzle(values)
    print('After attempting to reduce:')
    display(harder_sudoku)
    
    #eliminate