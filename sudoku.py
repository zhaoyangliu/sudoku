#!/usr/bin/env python
import struct, string, math
import copy
from operator import itemgetter

#this will be the game object your player will manipulate
class SudokuBoard:

    #the constructor for the SudokuBoard
    def __init__(self, size, board):
        self.BoardSize = size #the size of the board
        self.CurrentGameboard= board #the current state of the game board
        self.UnAssignedValue = [ [ [0] for i in range(size) ] for j in range(size) ]
        self.all_pair = [ [ i, j] for i in range(size) for j in range(size)]
        self.consistency_check = 0
        self.initialize_possible(board)
        self.fill_seq = [[]]

    #This function will create a new sudoku board object with
    #with the input value placed on the GameBoard row and col are
    #both zero-indexed
    def set_value(self, row, col, value):
        self.CurrentGameboard[row][col]=value # add the value to the appropriate position on the board
        return SudokuBoard(self.BoardSize, self.CurrentGameboard) # return a new board of the same size with the value added

    # Initialize all the possible values from current board.
    def initialize_possible(self, board):
        size = self.BoardSize
        number_list = [ i+1 for i in range(self.BoardSize)]
        self.UnAssignedValue = [ [ copy.deepcopy(number_list) for i in range(size) ] for j in range(size) ]

        for i in range(self.BoardSize):
            for j in range(self.BoardSize):
                if self.CurrentGameboard[i][j] != 0:
                    self.update_possible_unassigned(i, j, self.CurrentGameboard[i][j])

    # Update the possible values based on a given "row, col, value"
    def update_possible_unassigned(self, row, col, val):
        self.UnAssignedValue[row][col] = []

        # update row values
        for i in range(self.BoardSize):
            if val in self.UnAssignedValue[row][i]:
                self.UnAssignedValue[row][i].remove(val)

        # update column values
        for i in range(self.BoardSize):
            if val in self.UnAssignedValue[i][col]:
                self.UnAssignedValue[i][col].remove(val)

        # update subgrid values
        part_size = int(math.sqrt(self.BoardSize))
        row_begin = int(row / part_size) * part_size
        col_begin = int(col / part_size) * part_size
        for i in range(row_begin, row_begin + part_size):
            for j in range(col_begin, col_begin + part_size):
                if val in self.UnAssignedValue[i][j]:
                    self.UnAssignedValue[i][j].remove(val)

    # generates frequency counter for a value 
    def get_constrain_value_num(self, row, col, val):
        count = 0

        # loop thru row values
        for i in range(self.BoardSize):
            if val in self.UnAssignedValue[row][i]:
                count += 1

        # loop thru column values
        for i in range(self.BoardSize):
            if val in self.UnAssignedValue[i][col]:
                count += 1

        # loop thru subgrid values
        part_size = int(math.sqrt(self.BoardSize))
        row_begin = int(row / part_size) * part_size
        col_begin = int(col / part_size) * part_size
        for i in range(row_begin, row_begin + part_size):
            for j in range(col_begin, col_begin + part_size):
                if val in self.UnAssignedValue[i][j]:
                    count += 1
        return count

    # determines where to start solving from
    def get_first_zero(self, row, val):
        for i in range(self.BoardSize):
            for j in range(self.BoardSize):
                if self.CurrentGameboard[i][j] == 0:
                    return [i,j]
        return [-1, -1]

    # determines number of constraint variables for a given (row, column)
    def get_constrain_num(self, row, col):
        count = []

        # loop thru rows
        for i in range(self.BoardSize):
            if self.CurrentGameboard[row][i] == 0 and [row,i] not in count:
                count.append([row,i])

        # loop thru columns
        for i in range(self.BoardSize):
            if self.CurrentGameboard[i][col] == 0 and [i, col] not in count:
                count.append([i,col])

        # loop thru subgrid
        part_size = int(math.sqrt(self.BoardSize))
        row_begin = int(row / part_size) * part_size
        col_begin = int(col / part_size) * part_size
        for i in range(row_begin, row_begin + part_size):
            for j in range(col_begin, col_begin + part_size):
                if self.CurrentGameboard[i][j] == 0 and [i, j] not in count:
                    count.append([i,j])
        return len(count)

    # Get the next none-zero blank cell
    def get_next_blank(self, row, col):
        for i in range(self.BoardSize):
            for j in range(self.BoardSize):
                if (i != row or j != col) and self.CurrentGameboard[i][j] == 0:
                    return [i, j, self.UnAssignedValue[row][col]]
        return [-1, -1, self.UnAssignedValue[row][col]];

    # return a set of (row, column) pairs of the minimum remaining variables
    def get_MRV_blank(self, row, col, board):
        # initializes the minimum to some arbitrary large number
        min = self.BoardSize + 1
        MRV_set = []

        # loops thru all the cells on the game board and returns all (row, column) pairs that have the smallest number of remaining variables
        for pair in board:
            i = pair[0]
            j = pair[1]
            if (i != row or j != col) and self.CurrentGameboard[i][j] == 0 :
                if ( len(self.UnAssignedValue[i][j]) <= min ) :
                    # finds new minimum for remaining variables
                    min = len(self.UnAssignedValue[i][j])

                    if len(MRV_set) != 0:
                        tmp = MRV_set.pop()
                        # removes all (row, column) pairs with remaining variables greater than new minimum
                        while len(self.UnAssignedValue[tmp[0]][tmp[1]]) > min and len(MRV_set) > 0:
                            tmp = MRV_set.pop()
                        # adds (row, column) pair if it meets the new minimum
                        if len(self.UnAssignedValue[tmp[0]][tmp[1]]) == min:
                            MRV_set.append(tmp)
                    MRV_set.append([i,j])
        return MRV_set

    # return a set of (row, column) pairs of the most constrained variables
    def get_MCV_blank(self, row, col, board):
        # initializes max to some arbitrarily small number
        max = -1
        MCV_set = []

        # loops thru all the cells on the game board and returns all (row, column) pairs that have the largest number of constrained variables
        for pair in board:
            i = pair[0]
            j = pair[1]
            if (i != row or j != col) and self.CurrentGameboard[i][j] == 0 :
                constrain_num = self.get_constrain_num(i, j)

                if ( constrain_num >= max ):
                    # finds new maximum for constrained variables
                    max = constrain_num

                    if len(MCV_set) != 0:
                        tmp = MCV_set.pop()
                        # removes all (row, column) pairs of constrined variables less than new maximum
                        while (self.get_constrain_num(tmp[0],tmp[1]) < max and len(MCV_set) > 0):
                            tmp = MCV_set.pop()
                        # adds (row, column) pair if it meets the new maximum
                        if self.get_constrain_num(tmp[0],tmp[1]) == max:
                            MCV_set.append(tmp)
                    MCV_set.append([i,j])
        return MCV_set

    # least constraining value
    def get_LCV_value(self, row, col):
        LCV_set = []

        # find the number of constraining values for unassigned cells
        for value in self.UnAssignedValue[row][col]:
            constrain_value_num = self.get_constrain_value_num(row, col, value)
            LCV_set.append([ value, constrain_value_num])

        # sort the set to find the one that rules out fewest values in the remaining variables
        LCV_set = sorted(LCV_set, key = itemgetter(1))
        return [i[0] for i in LCV_set]

    # choose contraint heuristics
    # 0: pick next blank cell
    # 1: MRV
    # 2: MCV
    # 3: MRV + MCV
    # 4: MCV + MRV
    # 5: MRV + MCV + LCV
    def get_choice_blank(self, row, col, kind):
        result = []
        if kind ==0:
            return self.get_next_blank(row, col)

        if kind == 1 or kind == 3 or kind == 5:
            result = self.get_MRV_blank(row, col, self.all_pair)

        if kind == 2 or kind == 4:
            result = self.get_MCV_blank(row, col, self.all_pair)

        if kind == 3 or kind == 5:
            result = self.get_MCV_blank(row, col, result)

        if kind == 4:
            result = self.get_MRV_blank(row, col, result)

        if result == []:
            return [-1, -1, self.UnAssignedValue[row][col]]

        if kind == 5:
            return [result[0][0], result[0][1], self.get_LCV_value(row, col)]

        return [result[0][0], result[0][1], self.UnAssignedValue[row][col]]

    # Foward Checking
    def forward_checking(self, row, col, kind = 0):
        # finished traversing entire board
        if row == -1 :
            return True

        # maintain a copy of current game board for recovery later on
        possible_board = copy.deepcopy(self.UnAssignedValue)

        # for a cell that hasn't been assigned a value
        if self.UnAssignedValue[row][col] != [] :
            # for the next blank cell recursively run thru potential values and update the game board
            # return game board to original state if answer isn't found
            row_col_val = self.get_choice_blank(row, col, kind)
            for i in row_col_val[2]:
                self.consistency_check += 1
                self.CurrentGameboard[row][col] = i
                self.update_possible_unassigned(row, col, i)
                if self.forward_checking(row_col_val[0], row_col_val[1], kind):
                    self.fill_seq.insert(0, [row, col])
                    return True
                self.UnAssignedValue = copy.deepcopy(possible_board)

        # variable has no legal values
        self.CurrentGameboard[row][col] = 0
        return False

    # Back Tracking 
    def back_tracking(self, row, col):
        # determines if found a correct solution after it finishes traversing the entire board
        if row == -1:
            return True if iscomplete(self.CurrentGameboard) else False
        if self.consistency_check > 500000:
            return False

        # loops through all the potential values of the next empty cell using a depth first search
        # recursively determines if selected value is correct
        row_col_val = self.get_next_blank(row, col)
        for i in row_col_val[2]:
            self.consistency_check += 1
            self.CurrentGameboard[row][col] = i 
            if self.back_tracking(row_col_val[0], row_col_val[1]):
                return True;

        self.CurrentGameboard[row][col] = 0
        return False;

# parse_file
#this function will parse a sudoku text file (like those posted on the website)
#into a BoardSize, and a 2d array [row,col] which holds the value of each cell.
# array elements witha value of 0 are considered to be empty

def parse_file(filename):
    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    #initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val
    
    return board
    
#takes in an array representing a sudoku board and tests to
#see if it has been filled in correctly
def iscomplete( BoardArray ):
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    #check each cell on the board for a 0, or if the value of the cell
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):

            if BoardArray[row][col]==0:
                return False
            for i in range(size):
                if ((BoardArray[row][i] == BoardArray[row][col]) and i != col):
                    return False
                if ((BoardArray[i][col] == BoardArray[row][col]) and i != row):
                    return False
            #determine which square the cell is in
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if((BoardArray[SquareRow*subsquare + i][SquareCol*subsquare + j] == BoardArray[row][col])
                       and (SquareRow*subsquare + i != row) and (SquareCol*subsquare + j != col)):
                        return False
    return True

# creates a SudokuBoard object initialized with values from a text file like those found on the course website
def init_board( file_name ):
    board = parse_file(file_name)
    return SudokuBoard(len(board), board)

# test function to run thru all the different heuristics. change the filename to switch test problems
def nine_nine_test():
    for i in range(1, 21):
        file_name = "9x9/9x9." + str(i) + ".sudoku"
        print file_name
        board = init_board(file_name)

        row = board.get_first_zero(0, 0)[0]
        col = board.get_first_zero(0, 0)[1]

        board.forward_checking(row, col, 0)
        print "consistency check: " + str(board.consistency_check)
        print "is complete: " + str(iscomplete(board.CurrentGameboard))

        board = init_board(file_name)
        board.forward_checking(row, col, 1)
        print "consistency check: " + str(board.consistency_check)
        print "is complete: " + str(iscomplete(board.CurrentGameboard))

        board = init_board(file_name)
        board.forward_checking(row, col, 3)
        print "consistency check: " + str(board.consistency_check)
        print "is complete: " + str(iscomplete(board.CurrentGameboard))

        board = init_board(file_name)
        board.forward_checking(row, col, 5)
        print "consistency check: " + str(board.consistency_check)
        print "is complete: " + str(iscomplete(board.CurrentGameboard))

# nine_nine_test()

# test one heuristic at a time. change the filename to switch test problems.
file_name = "16x16.sudoku"
board = init_board(file_name)
row = board.get_first_zero(0, 0)[0]
col = board.get_first_zero(0, 0)[1]
board.forward_checking(row, col, 3)
# board.back_tracking(row, col)

print board.CurrentGameboard
print "is complete: " + str(iscomplete(board.CurrentGameboard))
print "consistency check: " + str(board.consistency_check)
print board.fill_seq