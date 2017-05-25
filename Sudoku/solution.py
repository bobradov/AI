#!/usr/bin/env python3

assignments = []


def cross(a, b):
    return [s+t for s in a for t in b]


rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

# Standard Sudoku
row_units    = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

 # Diagonals
back_slash   = [rows[index]+cs for index, cs in enumerate(cols) ]
forw_slash   = [rows[8-index]+cs for index, cs in enumerate(cols)]

# build diagonal Sudoku peers
# This is the default, as called by 'solve'
# Using 'solve_standard_sudoku' to solve without diagonals
unitlist = row_units + column_units + square_units + [back_slash] + [forw_slash]
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)



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


# Added this function for running additional tests
# In additional tests, solution is not know a priori
# but possible check to validity of answer
def is_valid_solution(grid_dict):
    """ Check a grid dictionary to see if represents a valid
    solution to Sudoku. 
    The constarainst must be valid, i.e. the peers of every box
    must contain values distinct from the said box.
    
    Applicable to both standard and diagonal sudoku.
    
    """
    
    # Check no conflicts with peers
    for cur_box in boxes:
        if grid_dict[cur_box] in peers[cur_box]:
            return False
        
    # Check no unfinished boxes
    for cur_box in boxes:
        if len(grid_dict[cur_box]) > 1:
            return False
        
    # Check each digit appears exactly 9 times
    hist = {str(digit) : 0 for digit in range(1, 10)}
    for cur_box in boxes:
        hist[grid_dict[cur_box]] += 1
    vals = hist.values()
    if max(vals) != 9 and min(vals) !=9:
        return False
        
    # All checks passed ...    
    return True

    




def eliminate(values):
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
       
        if len(values[cur_box]) == 1:
            # Loop over all peers, eliminate values[cur_box]
            elim_val = values[cur_box]
            
            for cur_peer in peers[cur_box]:
                if elim_val in values[cur_peer]:
                    assign_value(new_dict, cur_peer, new_dict[cur_peer].replace(elim_val,''))
                    
    return new_dict


# This is the version of only_choice provided after 'unlocking' it
# by providing a working version. The working version I used for this
# is 'only_choice_old'. Gives the same answer, but is less efficient.
# 
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
                assign_value(values, dplaces[0], digit)
    return values


def only_choice_old(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    
    new_values = values.copy()
    
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
                        #new_values[cur_block_in_unit] = str(val)
                        assign_value(new_values, cur_block_in_unit, str(val))
                    
            
        
    return new_values      



def reduce_puzzle(in_values):
    """Repeated application of the heuristics to reduce the board. 
    Continues until no more simplification possible.
    """
    # Defensive copy first
    values = in_values.copy()
    stalled = False
    
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Apply all heuristics
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        
        stalled = solved_values_before == solved_values_after
        
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
        
        
    # No more progress   
    return values






def search(in_values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."   
    # Are we already done?
    # If so, there are no more unfinished boxes, and we can return
    num_unfinished_boxes = len([box for box in in_values.keys() 
                                            if len(in_values[box]) > 1])
    
    if num_unfinished_boxes == 0:
        return in_values
    
    # OK, not done. 
    
    # Reduce the board as much as possible
    # If a bad board results, return to the previous
    # point in the recursion
    values = reduce_puzzle(in_values)
    if values == False:
        return False
    
    # Find the box with the smallest number of possibilities (but greater>1)
    # Recurse through the possibilities of this box
    len_list = [ (box, len(values[box])) for box in values.keys() 
                                         if len(values[box]) > 1 ]
    
    # It's possible the reduction has actually solved the puzzle.
    # In that case, len_list is empty and we are done
    if len(len_list) < 1:
        return values
    
    # Non-empty list of candidates to expand
    # Choose the one with the smallest number of digits
    min_element = min(len_list, key=lambda x : x[1])
    min_box = min_element[0]
    
    # Recurse through possible values of this box
    for guess_value in values[min_box]:
        guess_board = values.copy()
        guess_board[min_box] = guess_value
        
        res = search(guess_board)
        if not res:
            continue

        num_unfinished_boxes = len([box for box in res.keys() 
                                            if len(res[box]) > 1])
        if num_unfinished_boxes == 0:
            return res
    






def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(in_values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Defensive copy
    values = in_values.copy()
    
    
    # Reduce the number of searches in naked_twins double loop by
    # focusing only on entries with two values
    pair_values = [cur_box for cur_box in boxes if len(values[cur_box]) == 2]
    
    
    # NB: The double loop will create "double" the number twins with 
    # transposed entries; but not a big problem
    # naked_twins_tuple = (first_twin, second_twin, digits)
    naked_twins = [(cur_box1, cur_box2, values[cur_box1]) 
                        for cur_box1 in pair_values 
                        for cur_box2 in peers[cur_box1] 
                        if values[cur_box1] == values[cur_box2] ]
    
   
        
    # Process pairs of naked twins
    for cur_twin in naked_twins:
        cur_box1   = cur_twin[0]
        cur_box2   = cur_twin[1]
        digits     = cur_twin[2]
     
        # Find all peers which can be replaced, i.e. not single
        # values or twins
        # To be replaceable, it must be a peer of both cur_box1 and cur_box2
        # Also, no replacing of single-digit values (the twins should
        # have been eliminated if they have a single-digit peer, but
        # that may not be the sequence of operations)
        targets = [ cur_peer for cur_peer in peers[cur_box1] 
                                          if cur_peer in peers[cur_box2]
                                          if len(values[cur_peer]) > 1]
        
        
        for peer_box in targets:
            for digit in digits:
                if digit in values[peer_box]:
                    values = assign_value(values, 
                                          peer_box, 
                                          values[peer_box].replace(digit,''))   
                    
    return values
    

def solve_standard_sudoku(grid):
    """
    Find the solution to a standard Sudoku grid, i.e. one without diagonal constraints.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    
    # build standard Sudoku peers
    # Override globals to use only standard Sudoku peers.
    global unitlist 
    unitlist = row_units + column_units + square_units
    global units 
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    global peers 
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    
    return search(grid_values(grid))
     

    

def solve(grid):
    """
    Find the solution to a diagonal Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Apply the recursive solution method
    # Since no overrides to peers, it solves the diagonal Sudoku.
    return search(grid_values(grid))



if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    
    # basic test-cases
    print('\n\nstandard sudoku:\n\n')
    display(solve_standard_sudoku(diag_sudoku_grid))
    
    print('\n\ndiagonal sudoku:\n\n')
    display(solve(diag_sudoku_grid))
    
    
    # Test naked twin with input from auto-grader
    # Previous versions of the algorithm were failing on this testcase
    # because they were not eliminating digits from two-digit entries

    
    nt_board = {"G7": "2345678", "G6": "1236789",  "G5": "23456789", "G4": "345678", 
                "G3": "1234569", "G2": "12345678", "G1": "23456789", "G9": "24578", "G8": "345678", 
                "C9": "124578",  "C8": "3456789",  "C3": "1234569",  "C2": "1234568", 
                "C1": "2345689", "C7": "2345678",  "C6": "236789",  "C5": "23456789", "C4": "345678", 
                "E5": "678",     "E4": "2",        "F1": "1", "F2": "24", "F3": "24", "F4": "9", 
                "F5": "37",      "F6": "37", "F7": "58", "F8": "58", 
                "F9": "6", "B4": "345678", "B5": "23456789", 
                "B6": "236789", "B7": "2345678", "B1": "2345689", 
                "B2": "1234568", "B3": "1234569", "B8": "3456789", 
                "B9": "124578", "I9": "9", "I8": "345678", 
                "I1": "2345678", "I3": "23456", "I2": "2345678", 
                "I5": "2345678", "I4": "345678", "I7": "1", 
                "I6": "23678", "A1": "2345689", "A3": "7", 
                "A2": "234568", "E9": "3", "A4": "34568", 
                "A7": "234568", "A6": "23689", "A9": "2458", 
                "A8": "345689", "E7": "9", "E6": "4", "E1": 
                "567", "E3": "56", "E2": "567", "E8": "1", "A5": "1", 
                "H8": "345678", "H9": "24578", "H2": "12345678", "H3": "1234569", 
                "H1": "23456789", "H6": "1236789", "H7": "2345678", "H4": "345678", 
                "H5": "23456789", "D8": "2", "D9": "47", "D6": "5", "D7": "47", 
                "D4": "1", "D5": "36", "D2": "9", "D3": "8", "D1": "36"}
    
    print('before naked twins:')
    display(nt_board)
    print('\n\nafter naked twins:')
    new_vals = naked_twins(nt_board)
    display(new_vals)
    
    # pygame not working on my setup, commenting out for now
   
'''
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
'''