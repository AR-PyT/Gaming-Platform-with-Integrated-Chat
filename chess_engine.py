import numpy


class ChessEngine:
    def __init__(self):
        # Main Game board window
        self.board = numpy.array((
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ))
        self.recent_piece = (-1, -1)

        # LL, LR, RL, RR when true can castle to that side
        self.castle = [True, True, True, True]

    def move_piece(self, new_position):
        if self.recent_piece != (-1, -1):
            if self.castle:
                if self.board[self.recent_piece[1]][self.recent_piece[0]] == 'bK':
                    if new_position == [2, 0]:
                        self.board[0][3] = 'bR'
                        self.board[0][0] = '--'
                    elif new_position == [6, 0]:
                        self.board[0][5] = 'bR'
                        self.board[0][7] = '--'
                    self.castle[0] = self.castle[1] = False
                elif self.board[self.recent_piece[1]][self.recent_piece[0]] == 'wK':
                    if new_position == [2, 7]:
                        self.board[7][3] = 'wR'
                        self.board[7][0] = '--'
                    elif new_position == [6, 7]:
                        self.board[7][5] = 'wR'
                        self.board[7][7] = '--'
                    self.castle[2] = self.castle[3] = False
                elif self.board[self.recent_piece[1]][self.recent_piece[0]][1] == 'bR':
                    if self.recent_piece[0] == 0:
                        self.castle[0] = False
                    elif self.recent_piece[0] == 7:
                        self.castle[1] = False
                elif self.board[self.recent_piece[1]][self.recent_piece[0]][1] == 'wR':
                    if self.recent_piece[0] == 0:
                        self.castle[2] = False
                    elif self.recent_piece[0] == 7:
                        self.castle[3] = False

            if self.board[self.recent_piece[1]][self.recent_piece[0]] == '':
                pass
            self.board[new_position[1]][new_position[0]] = self.board[self.recent_piece[1]][self.recent_piece[0]]
            self.board[self.recent_piece[1]][self.recent_piece[0]] = '--'
            self.recent_piece = (-1, -1)

    def possible_moves(self, position, color):
        # Possible move list 0 no move 1 possible 2 enemy location
        moves = numpy.zeros((8, 8), int)

        # Finding row and col of selected piece
        self.recent_piece = position
        col, row = position[0], position[1]

        # If the white user selects black piece or viceversa
        if self.board[row][col][0] != color:
            return moves.tolist()
        if self.board[row][col][1] == 'B':
            self.bish_moves(moves, (row, col), color)
        elif self.board[row][col][1] == 'R':
            self.rook_moves(moves, (row, col), color)
        elif self.board[row][col][1] == 'Q':
            self.queen_move(moves, (row, col), color)
        elif self.board[row][col][1] == 'N':
            self.knight_move(moves, (row, col), color)
        elif self.board[row][col][1] == 'K':
            self.king_move(moves, (row, col), color)
            self.castling(moves, color)
        elif self.board[row][col][1] == 'p':
            self.pawn_moves(moves, (row, col), color)

        self.valid_moves(moves, color)

        return moves.tolist()

    def castling(self, moves, color):
        if color == 'b':
            if self.castle[0] and self.board[0][1] == self.board[0][2] == self.board[0][3] == '--':
                moves[0][2] = 1
            if self.castle[1] and self.board[0][5] == self.board[0][6] == '--':
                moves[0][6] = 1
        else:
            if self.castle[2] and self.board[7][1] == self.board[7][2] == self.board[7][3] == '--':
                moves[7][2] = 1
            if self.castle[3] and self.board[7][5] == self.board[7][6] == '--':
                moves[7][6] = 1

    # Check diagonals from given pos and append moves to a list
    def check_diagonals(self, moves, pos, row_inc, col_inc, enemy):
        row, col = pos[0], pos[1]

        # Increment row and col so as to not select the ini position
        row += row_inc
        col += col_inc

        # Do till row or col leave the range
        while 0 <= row <= 7 and 0 <= col <= 7:
            # If empty put 1
            if self.board[row][col] == '--':
                moves[row][col] = 1
            # If enemy put 2
            elif self.board[row][col][0] == enemy:
                moves[row][col] = 2
                return
            else:
                return

            # Incrementing again
            row += row_inc
            col += col_inc

    def bish_moves(self, move_list, pos, color):
        # Finding enemy color
        enemy = 'b'
        if color == enemy: enemy = 'w'

        # Finding all diagonals from the given point
        self.check_diagonals(move_list, pos, 1, 1, enemy)
        self.check_diagonals(move_list, pos, 1, -1, enemy)
        self.check_diagonals(move_list, pos, -1, -1, enemy)
        self.check_diagonals(move_list, pos, -1, 1, enemy)

    def rook_moves(self, move_list, pos, color):
        # Finding enemy color
        enemy = 'b'
        if color == enemy: enemy = 'w'

        # Can move in straight lines so check the diagonals keeping either row or col to 0 rise

        self.check_diagonals(move_list, pos, 1, 0, enemy)
        self.check_diagonals(move_list, pos, -1, 0, enemy)
        self.check_diagonals(move_list, pos, 0, -1, enemy)
        self.check_diagonals(move_list, pos, 0, 1, enemy)

    def queen_move(self, move_list, pos, color):
        self.bish_moves(move_list, pos, color)
        self.rook_moves(move_list, pos, color)

    def knight_move(self, move_list, pos, color):
        # Finding enemy color
        enemy = 'b'
        if color == enemy: enemy = 'w'
        for row_inc in [2, -2]:
            for col_inc in [1, -1]:

                # Finding coordinates for destination
                row = pos[0] + row_inc
                col = pos[1] + col_inc

                # If new position out of board continue
                if 0 <= row < 8 and 0 <= col < 8:

                    # Check board at the final location
                    if self.board[row][col] == '--':
                        move_list[row][col] = 1
                    elif self.board[row][col][0] == enemy:
                        move_list[row][col] = 2

                # Check for reverse combo
                row = pos[0] + col_inc
                col = pos[1] + row_inc

                if 0 <= row < 8 and 0 <= col < 8:

                    if self.board[row][col] == '--':
                        move_list[row][col] = 1
                    elif self.board[row][col][0] == enemy:
                        move_list[row][col] = 2

    def king_move(self, move_list, pos, color):
        # Finding enemy color
        enemy = 'b'
        if color == enemy: enemy = 'w'

        # Check all elements around the king
        for row_inc in [0, 1, -1]:
            for col_inc in [0, 1, -1]:
                row, col = pos[0] + row_inc, pos[1] + col_inc

                if 0 <= row < 8 and 0 <= col < 8:
                    if self.board[row][col] == '--':
                        move_list[row][col] = 1
                    elif self.board[row][col][0] == enemy:
                        move_list[row][col] = 2

    def pawn_moves(self, move_list, pos, color):
        # Finding enemy color
        enemy = 'b'
        if color == enemy: enemy = 'w'

        # Adding possible moves in the straight path
        row, col = pos

        # Saving number of iterations in a variable
        places_ahead = 1

        # Performing white and black operations
        if color == 'b':
            if row == 1: places_ahead = 2
            if col != 7 and self.board[row + 1][col + 1][0] == enemy:
                move_list[row + 1][col + 1] = 2
            if col != 0 and self.board[row + 1][col - 1][0] == enemy:
                move_list[row + 1][col - 1] = 2
            for i in range(1, places_ahead + 1):
                if self.board[row + i][col] == '--':
                    move_list[row + i][col] = 1
                else:
                    return
        else:
            if row == 6: places_ahead = 2
            if col != 7 and self.board[row - 1][col + 1][0] == enemy:
                move_list[row - 1][col + 1] = 2
            if col != 0 and self.board[row - 1][col - 1][0] == enemy:
                move_list[row - 1][col - 1] = 2
            for i in range(1, places_ahead + 1):
                if self.board[row - i][col] == '--':
                    move_list[row - i][col] = 1
                else:
                    return

    def check(self, board, enemy):
        # Find kings position on board
        color = 'b'
        if color == enemy: color = 'w'
        kingPos = list(zip(numpy.where(board == color + 'K')[0], numpy.where(board == color + 'K')[1]))[0]

        move = numpy.zeros((8, 8), int)
        for row in range(8):
            for col in range(8):
                if board[row][col][0] == enemy:
                    if board[row][col][1] == 'B':
                        self.bish_moves(move, (row, col), enemy)
                    elif board[row][col][1] == 'R':
                        self.rook_moves(move, (row, col), enemy)
                    elif board[row][col][1] == 'Q':
                        self.queen_move(move, (row, col), enemy)
                    elif board[row][col][1] == 'N':
                        self.knight_move(move, (row, col), enemy)
                    elif board[row][col][1] == 'K':
                        self.king_move(move, (row, col), enemy)
                    elif board[row][col][1] == 'p':
                        self.pawn_moves(move, (row, col), enemy)
        print(move)
        if move[kingPos[0]][kingPos[1]] == 0:
            return False
        return True

    def valid_moves(self, move, color):
        # Finding enemy color
        enemy = 'b'
        if enemy == color: enemy = 'w'

        actual_board = numpy.copy(self.board)
        print(self.recent_piece)
        for row in range(8):
            for col in range(8):
                if move[row][col] != 0:
                    self.board[row][col] = self.board[self.recent_piece[1]][self.recent_piece[0]]
                    self.board[self.recent_piece[1]][self.recent_piece[0]] = '--'
                    if self.check(self.board, enemy):
                        move[row][col] = 0
                    print(self.board)
                    self.board = numpy.copy(actual_board)

    def checkWinner(self, color):
        enemy = 'b'
        if enemy == color: enemy = 'w'
        for i in ['B', 'p', 'R', 'K', 'Q', 'N']:
            positions = numpy.where(self.board == enemy + i)
            for pos in list(zip(positions[0], positions[1])):
                if numpy.array(self.possible_moves((pos[0], pos[1]), color)).any():
                    return False
        print('SENDING WINNNER CHOSEN \n\n')
        return True
