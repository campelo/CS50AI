"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    validateBoard(board)
    xCount = 0
    oCount = 0
    for row in board:
        for item in row:
            if item == X:
                xCount += 1
            elif item == O:
                oCount += 1
    if xCount == oCount:
        return X
    return O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    validateBoard(board)
    result = []
    for rowIdx, row in enumerate(board):
        for colIdx, col in enumerate(row):
            if col == EMPTY:
                result.append((rowIdx,colIdx))
    return result

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    validateBoard(board)
    if board[action[0]][action[1]] != EMPTY:
        raise AttributeError("Action not allowed")
    response = []
    for rowIdx, row in enumerate(board):
        response.append([])
        for col in row:
            response[rowIdx].append(col)
    response[action[0]][action[1]] = player(board)
    return response

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    validateBoard(board)
    for row in board:
        if hasWinner(row):
            return row[0]
    for i in range(3):
        if (hasWinner([board[0][i],board[1][i],board[2][i]])):
            return board[0][i]
    if (hasWinner([board[0][0],board[1][1],board[2][2]])):
        return board[1][1]
    if (hasWinner([board[0][2],board[1][1],board[2][0]])):
        return board[1][1]
    return None
    
def hasWinner(threeValues):
    if EMPTY in threeValues:
        return False
    return all(value is threeValues[0] for value in threeValues)

def hasValidCells(board):
    for row in board:
        for i in range(3):
            if (row[i] not in [X, O, EMPTY]):
                return False
    return True
    
def validateBoard(board):
    if not board is None and len(board) == 3 and all(len(row) == 3 for row in board) and hasValidCells(board):
        return    
    raise ValueError("board has invalid values")

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    validateBoard(board)
    return winner(board) is not None or not hasEmptyCell(board)
    
def hasEmptyCell(board):
    validateBoard(board)
    for row in board:
        if EMPTY in row:
            return True
    return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    validateBoard(board)
    if terminal(board):
        if winner(board) == X:
            return 1
        if winner(board) == O:
            return -1
    return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    validateBoard(board)
    if (terminal(board)):
        return None
    if player(board) is X:
        return maxvalue(board)[1]
    return minvalue(board)[1]

def maxvalue(board, ignoreValuesGreatherThan = 999):
    if terminal(board):
        return (utility(board), None)
    response = (-999, None)
    for action in actions(board):        
        temp = minvalue(result(board, action), max(response[0], -999))
        if (temp[0] > response[0]):
            response = (temp[0], action)
        if response[0] >= ignoreValuesGreatherThan :
            return response
    return response

def minvalue(board, ignoreValuesLessThan = -999):
    if terminal(board):
        return (utility(board), None)
    response = (999, None)
    for action in actions(board):        
        temp = maxvalue(result(board, action), min(response[0], 999))
        if temp[0] < response[0]:
            response = (temp[0], action)
        if response[0] <= ignoreValuesLessThan :
            return response
    return response

'''
board = [[EMPTY, O, EMPTY],
            [X, O, X],
            [X, EMPTY, O]]

# minimax
print(minimax(board))

# validateBoard
print(validateBoard(board))

# utility
print(utility(board))

# terminal 
print(terminal(board))

# winner  
print (winner(board))

# result 
r = result(board, (0,2))
print(r)

# actions
for (i,j) in actions(board):
    print(f"action: {i}, {j}")

# player    
print(f"player: {player(board)}")
'''