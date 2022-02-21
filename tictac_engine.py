# Using numpy array for main grid inside game
import numpy as np


class TicTacToe:

    def __init__(self):
        # Board size used to represent game
        # 0 represent untaken 1 for player 1 and 2 for player 2
        self.game_size = (3, 3)
        self.game_grid = np.zeros(self.game_size, int)

    def add_player_1(self, pos):
        self.game_grid[pos[0]][pos[1]] = 1

    def add_player_2(self, pos):
        self.game_grid[pos[0]][pos[1]] = 2

    @staticmethod
    def check_row(game_grid, win):
        for row in range(3):
            if np.array_equal(game_grid[row], win):
                return 'R' + str(row)
        return False

    @staticmethod
    def check_col(game_grid, win):
        for col in range(3):
            if np.array_equal(game_grid[col], win):
                return 'C' + str(col)
        return False

    @staticmethod
    def check_diagonal(game_grid, win):
        if np.all(game_grid.diagonal() == win):
            return 'DL'
        return False

    @staticmethod
    def check_diagonal_flip(game_grid, win):
        if np.all(np.fliplr(game_grid).diagonal() == win):
            return 'DR'
        return False

    def check_winner(self, player):
        # player is either 1 or 2
        win_condition = np.full((1, 3), player, dtype=int)[0]

        val = self.check_row(self.game_grid, win_condition)
        if val:
            return val
        else:
            val = self.check_col(self.game_grid.copy().transpose(), win_condition)
            if val:
                return val
            else:
                val = self.check_diagonal(self.game_grid, win_condition)
                if val:
                    return val
                else:
                    val = self.check_diagonal_flip(self.game_grid, win_condition)
                    if val:
                        return val
        return False
