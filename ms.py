import argparse
import curses
import time
import random

class Board:
    STATE_INIT = 0    
    STATE_MARKED = 1
    STATE_SWEPT = 2

    def __init__(self, n):
        self.n = n
        self.board = [[0] * n for _ in range(n)]
        self.state = [[Board.STATE_INIT] * n for _ in range(n)]
        self.y = 0
        self.x = 0

        self.over = False
        self.win = False
        self.mines = 0
        self.minesmarked = 0
        self.minesswept = 0

    def add_mine(self, r, c):
        if self.board[r][c] != -1:
            self.board[r][c] = -1
            self.mines += 1
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                yy = r + dy
                xx = c + dx
                if 0 <= yy and yy < self.n and 0 <= xx and xx < self.n and self.board[yy][xx] >= 0:
                    self.board[yy][xx] += 1

    def set_position(self, y, x):
        self.offset_y = y
        self.offset_x = x

    def size(self):
        return self.n

    def get_shown_ch(self, y, x):
        if self.state[y][x] == Board.STATE_INIT:
            return '*'
        if self.state[y][x] == Board.STATE_MARKED:
            return '?'
        if self.board[y][x] < 0:
            return 'x'
        return str(self.board[y][x])

    def draw(self, scr):
        if self.over:
            text = 'win' if self.win else 'lose'
            scr.addstr(self.offset_y - 2, self.offset_x, f'You {text}! Press q to exit.')
        else:
            scr.addstr(self.offset_y - 2, self.offset_x, f'Mines: {self.mines - self.minesmarked}')
        for y in range(0, self.n):
            for x in range(0, self.n):
                ch = self.get_shown_ch(y, x)
                scr.addstr(self.offset_y + y, self.offset_x + x, ch)
        scr.move(self.offset_y + self.y, self.offset_x + self.x)

    def move(self, dy, dx):
        if self.y + dy >= 0 and self.y + dy < self.n:
            self.y += dy
        if self.x + dx >= 0 and self.x + dx < self.n:
            self.x += dx

    def mark(self):
        if self.state[self.y][self.x] == Board.STATE_INIT:
            self.state[self.y][self.x] = Board.STATE_MARKED
            self.minesmarked += 1
            if self.board[self.y][self.x] < 0:
                self.minesswept += 1
        elif self.state[self.y][self.x] == Board.STATE_MARKED:
            self.state[self.y][self.x] = Board.STATE_INIT
            self.minesmarked -= 1
            if self.board[self.y][self.x] < 0:
                self.minesswept -= 1

        if self.minesswept == self.mines:
            self.check_all_swept()

    def sweep(self):
        if self.state[self.y][self.x] == Board.STATE_MARKED:
            return
        self.state[self.y][self.x] = Board.STATE_SWEPT
        if self.board[self.y][self.x] == 0:
            self.flood_fill(self.y, self.x)

        if self.board[self.y][self.x] < 0:
            self.over = True
            self.win = False            
        elif self.minesswept == self.mines:
            self.check_all_swept()

    def flood_fill(self, y, x):
        self.state[y][x] = Board.STATE_SWEPT
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                xx = x + dx
                yy = y + dy
                if xx >= 0 and xx < self.n and yy >= 0 and yy < self.n and self.state[yy][xx] == Board.STATE_INIT:
                    self.state[yy][xx] = Board.STATE_SWEPT
                    if self.board[yy][xx] == 0:
                        self.flood_fill(yy, xx)

    def check_all_swept(self):
        for y in range(self.n):
            for x in range(self.n):
                if self.state[y][x] == Board.STATE_INIT:
                    return
                if self.state[y][x] == Board.STATE_MARKED:
                    if self.board[y][x] >= 0:
                        return
        self.over = True
        self.win = True

    def game_over(self):
        return self.over

    @staticmethod
    def random_generate(n, m):
        board = Board(n)
        random.seed(int(time.time()))
        for _ in range(m):
            r = random.randint(0, n-1)
            c = random.randint(0, n-1)
            board.add_mine(r, c)
        return board

class Game:
    def __init__(self, scr):
        self.scr = scr

    def set_board(self, board):
        self.board = board
        dimy, dimx = self.scr.getmaxyx()
        sx = dimx // 2 - self.board.size() // 2
        sy = dimy // 2 - self.board.size() // 2
        self.board.set_position(sy, sx)

    def run(self):
        self.board.draw(self.scr)
        self.scr.refresh()
        while not self.board.game_over():
            ch = self.scr.getch()
            if ch == ord('q'):
                return
            if ch == curses.KEY_UP:
                self.board.move(-1, 0)
            if ch == curses.KEY_DOWN:
                self.board.move(1, 0)
            if ch == curses.KEY_LEFT:
                self.board.move(0, -1)
            if ch == curses.KEY_RIGHT:
                self.board.move(0, 1)                
            
            if ch == ord('x'):
                self.board.sweep()
            if ch == ord('a'):
                self.board.mark()

            self.board.draw(self.scr)
            self.scr.refresh()

        while True:
            ch = self.scr.getch()
            if ch == ord('q'):
                return

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('size', help='size of the the game board', type=int)
    parser.add_argument('nmines', help='number of mines', type=int)
    return parser.parse_args()

def main(scr, args):
    scr.clear()
    n = args.size
    m = args.nmines
    board = Board.random_generate(n, m)
    game = Game(scr)
    game.set_board(board)
    game.run()

if __name__ == '__main__':
    args = parse_args()
    curses.wrapper(main, args)
