#!/usr/bin/env python
import struct, string, math
import copy

#this will be the game object your player will manipulate
class SudokuBoard:

    #the constructor for the SudokuBoard
    def __init__(self, size, board):
        self.BoardSize = size #the size of the board
        self.CurrentGameboard= board #the current state of the game board
        self.UnAssignedValue = [ [ [0] for i in range(size) ] for j in range(size) ]
        self.consistency_check = 0
        self.initialize_possible(board)
        

    #This function will create a new sudoku board object with
    #with the input value placed on the GameBoard row and col are
    #both zero-indexed
    def set_value(self, row, col, value):
        self.CurrentGameboard[row][col]=value # add the value to the appropriate position on the board
        return SudokuBoard(self.BoardSize, self.CurrentGameboard) # return a new board of the same size with the value added

    # Initialize the possible values from current board.
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
        self.consistency_check += 1
        self.UnAssignedValue[row][col] = [0]
        for i in range(self.BoardSize):
            if val in self.UnAssignedValue[row][i]:
                self.UnAssignedValue[row][i].remove(val)

        for i in range(self.BoardSize):
            if val in self.UnAssignedValue[i][col]:
                self.UnAssignedValue[i][col].remove(val)

        part_size = int(math.sqrt(self.BoardSize))

        row_begin = int(row / part_size) * part_size
        col_begin = int(col / part_size) * part_size

        for i in range(row_begin, row_begin + part_size):
            for j in range(col_begin, col_begin + part_size):
                if val in self.UnAssignedValue[i][j]:
                    self.UnAssignedValue[i][j].remove(val)

    def get_next_blank(self, row, col):
        for i in range(self.BoardSize):
            for j in range(self.BoardSize):
                if (i != row or j != col) and self.CurrentGameboard[i][j] == 0:
                    return [i,j]
        return [-1, -1];

    def forward_checking(self, row, col):
        next_row = self.get_next_blank(row, col)[0]
        next_col = self.get_next_blank(row, col)[1]
        if row == -1:
            return True

        possible_board = copy.deepcopy(self.UnAssignedValue)

        if self.UnAssignedValue[row][col] != [] or self.UnAssignedValue[row][col] != [0] :
            for i in self.UnAssignedValue[row][col]:
                self.CurrentGameboard[row][col] = i
                self.update_possible_unassigned(row, col, i)
                if self.forward_checking(next_row, next_col):
                    return True
                self.UnAssignedValue = copy.deepcopy(possible_board)

        self.CurrentGameboard[row][col] = 0
        return False


# return BoardArray

# def backtracking( BoardArray ):


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

# board = init_board("16x16.sudoku")
board = init_board("9x9.sudoku")

row = board.get_next_blank(0, 0)[0]
col = board.get_next_blank(0, 0)[1]
board.forward_checking(row, col)

print board.CurrentGameboard
# print board.UnAssignedValue
print "is complete: " + iscomplete(board.CurrentGameboard)
print "consistency check: " + board.consistency_check