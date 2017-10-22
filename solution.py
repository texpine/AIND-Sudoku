assignments = []


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

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for box, value in values.items():  
        if len(value) == 1:
            continue

        for unit in units[box]:            
            # counting the amount of copies of each value in the box
            # we put the count in a dictionary that uses the value as keyu
            value_dict = {}
            for box_unit in unit:
                if values[box_unit] in value_dict.keys():
                    value_dict[values[box_unit]] += 1
                else:
                    value_dict[values[box_unit]] = 1
                        
            # from the counting dictionary, we loop to find the ones
            # which the count is equal to the amount of digits, which
            # constitutes a twin
            for key, value in value_dict.items():
                if len(key) == value and value > 1:                    
                    # naked twins found, loops other boxes to remove this content
                    for number in key:                        
                        for box_unit in unit:                            
                            if values[box_unit] != key and number in values[box_unit]:
                                values[box_unit] = values[box_unit].replace(number, '')
        
    return values
                                
            
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    values_proc = values.copy()
    solved_values = [box for box in values_proc.keys() if len(values_proc[box]) == 1]
    for box in solved_values:
        digit = values_proc[box]
        for peer in peers[box]:
            values_proc[peer] = values_proc[peer].replace(digit,'')
    return values_proc

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    values_proc = values.copy()
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values_proc[box]]
            if len(dplaces) == 1:
                values_proc[dplaces[0]] = digit
    return values_proc

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    values_proc = values.copy()
    solved_values = [box for box in values_proc.keys() if len(values_proc[box]) == 1]    
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values_proc.keys() if len(values_proc[box]) == 1])
        values_proc = eliminate(values_proc)
        values_proc = only_choice(values_proc)
        solved_values_after = len([box for box in values_proc.keys() if len(values_proc[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values_proc.keys() if len(values_proc[box]) == 0]):
            return False
    return values_proc

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values_reduced = reduce_puzzle(values)
    if values_reduced is False:
        return False ## Failed earlier
    if all(len(values_reduced[s]) == 1 for s in boxes): 
        return values_reduced ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values_reduced[s]), s) for s in boxes if len(values_reduced[s]) > 1)    
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values_reduced[s]:
        new_sudoku = values_reduced.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    result = search(values) #naked_twins(search(values))
    for box, value in result.items():
        assign_value(values, box, value)
    return result

#global vars
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# adding diagonal Sudoku
diagonal_units = [
    [rows[i] + cols[i] for i in range(0, len(rows))], 
    [rows[i] + cols[len(rows)-1-i] for i in range(0, len(rows))]
]
# just added diagonals as a new unit possibility
unitlist = row_units + column_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'    
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
