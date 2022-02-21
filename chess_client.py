import pygame
import json
import socket
import threading
import config

pygame.init()
ip = config.get_ip()


class ChessClient:
    def __init__(self, port, name):
        self.winner = False
        self.dimension = (512, 512)
        self.square_size = self.dimension[0] // 8
        self.screen = pygame.display.set_mode(self.dimension)
        pygame.display.set_caption('Chess')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.sock.send(json.dumps(name).encode('utf-8'))
        self.board = [['--'] * 8] * 8
        self.moves = [[0] * 8] * 8
        self.turn = False
        self.images = {}
        self.current = (-1, -1)
        self.color = ''
        self.promotion_window = False
        self.game_ongoing = True

    def load_images(self):
        for piece in ['wR', 'wN', 'wB', 'wQ', 'wK', 'wp', 'bR', 'bN', 'bB', 'bQ', 'bK', 'bp', 'dot']:
            self.images[piece] = pygame.transform.scale(
                pygame.image.load('images/' + piece + '.png'), (self.square_size, self.square_size))

    def draw_board(self):
        colors = {0: 'white', 1: 'gray'}

        for row in range(8):
            for col in range(8):
                pygame.draw.rect(self.screen, colors[(row + col) % 2],
                                 pygame.Rect(col * self.square_size, row * self.square_size, self.square_size,
                                             self.square_size))
                if self.board[row][col] != '--':
                    self.screen.blit(self.images[self.board[row][col]],
                                     (col * self.square_size, row * self.square_size))

                if self.moves[row][col] == 1:
                    self.screen.blit(self.images['dot'],
                                     (col * self.square_size, row * self.square_size))
                elif self.moves[row][col] == 2:
                    pygame.draw.rect(self.screen, pygame.Color('red'),
                                     pygame.Rect(col * self.square_size, row * self.square_size, self.square_size,
                                                 self.square_size), 3)

        pygame.draw.rect(self.screen, pygame.Color('blue'),
                         pygame.Rect(self.current[0] * self.square_size, self.current[1] * self.square_size,
                                     self.square_size, self.square_size), 3)

    def draw_promotion(self):
        self.screen.fill((159, 30, 170))
        msg = pygame.font.Font('freesansbold.ttf', 32)
        msg = msg.render('Choose one for Promotion', True, pygame.Color('black'))
        self.screen.blit(msg, (60, self.square_size))

        self.screen.blit(
            pygame.transform.scale(self.images[self.color + 'Q'], (self.square_size, self.square_size)),
            (2 * self.square_size, 3 * self.square_size))
        self.screen.blit(
            pygame.transform.scale(self.images[self.color + 'B'], (self.square_size, self.square_size)),
            (4 * self.square_size, 3 * self.square_size))
        self.screen.blit(
            pygame.transform.scale(self.images[self.color + 'R'], (self.square_size, self.square_size)),
            (2 * self.square_size, 5 * self.square_size))
        self.screen.blit(
            pygame.transform.scale(self.images[self.color + 'N'], (self.square_size, self.square_size)),
            (4 * self.square_size, 5 * self.square_size))

    def send_data(self, data):
        data = (data[0] // 64, data[1] // 64)
        if self.promotion_window:
            if data == (2, 3):
                data = self.color + 'Q'
                self.promotion_window = False
            elif data == (4, 3):
                data = self.color + 'B'
                self.promotion_window = False
            elif data == (2, 5):
                data = self.color + 'R'
                self.promotion_window = False
            elif data == (4, 5):
                data = self.color + 'N'
                self.promotion_window = False
        elif self.moves[data[1]][data[0]] != 0:
            self.moves = [[0] * 8] * 8
            self.current = (-1, -1)
        self.turn = False
        self.sock.send(json.dumps(data).encode('utf-8'))

    def receive_data(self):
        while self.game_ongoing:
            received = False
            while (not received) and self.game_ongoing:
                try:
                    board = json.loads(self.sock.recv(4096).decode('utf-8'))
                    received = True
                except json.JSONDecodeError:
                    board = 'wait'
                    break
            if board == 'turn':
                self.turn = True
            elif board[:-1] == 'promote':
                self.color = board[-1]
                self.turn = True
                self.promotion_window = True
            elif type(board) == list and board.copy().pop() == 0:
                board.pop()
                self.moves = board
            elif board[:4] == 'OVER':
                text = pygame.font.Font('fonts/MoneraCalm.otf', 80)
                msg = text.render(board.split(' ')[1] + ' Wins', True, (255, 0, 0))
                self.screen.blit(msg, (150, 200))
                self.winner = True
                break

            elif board != 'wait':
                self.board = board

    def game_play(self):
        self.load_images()
        threading.Thread(target=self.receive_data).start()

        while self.game_ongoing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sock.send(json.dumps('**||GIVEUP||**').encode('utf-8'))
                    self.game_ongoing = False
                elif event.type == pygame.MOUSEBUTTONUP and self.turn:
                    pos = pygame.mouse.get_pos()
                    self.current = (pos[0] // 64, pos[1] // 64)
                    threading.Thread(target=lambda: self.send_data(pos)).start()

            if not self.promotion_window:
                if not self.winner:
                    self.draw_board()
            else:
                self.draw_promotion()
            pygame.display.update()

