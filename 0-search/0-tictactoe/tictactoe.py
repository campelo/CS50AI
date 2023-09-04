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
    for row in board:
        if hasWinner(row):
            return row[0]
    for i in range(2):
        if (hasWinner([board[0][i],board[1][i],board[2][i]])):
            return board[0][i]
    if (hasWinner([board[0][0],board[1][1],board[2][2]])):
        return board[0][0]
    if (hasWinner([board[2][2],board[1][1],board[0][0]])):
        return board[2][2]
    return None
    
    
def hasWinner(threeValues):
    if EMPTY in threeValues:
        return False
    return all(value is threeValues[0] for value in threeValues)


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
