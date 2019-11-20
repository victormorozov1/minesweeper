import pygame
from random import randrange


class Cell:
    def __init__(self, x, y, val):
        self.x = x
        self.y = y
        self.val = val
        self.open = False
        self.flag = False
        self.pict = not_oppened_cell_pict

    def __str__(self):
        ret = 'coords: ' + str((self.x, self.y)) + ' value = '
        if self.val == -1:
            ret += 'mine '
        else:
            ret += str(self.val) + ' '
        if self.open:
            ret += 'cell is open '
        if self.flag:
            ret += 'cell is under flag'
        return ret

    def is_mine(self):
        return self.val == -1

    def inverse_flag(self):
        if self.flag:
            self.flag = False
            self.pict = not_oppened_cell_pict
        else:
            self.flag = True
            self.pict = flag_cell_pict

    def check_mine(self):
        self.open = True
        if self.is_mine():
            self.pict = mine_cell_pict
            return True
        self.pict = numbers[self.val]


class Field:
    def __init__(self, n, num_mines):
        self.a = []
        self.num_mines = num_mines
        self.n = n
        self.cells_to_open = self.n ** 2 - self.num_mines

        for i in range(n):
            self.a.append([])
            for j in range(n):
                if num_mines and randrange(((n - i - 1) * n + n - j) // num_mines) == 0:
                    self.a[-1].append(Cell(i, j, -1))
                    num_mines -= 1
                else:
                    self.a[-1].append(Cell(i, j, 0))
        for i in range(n):
            for j in range(n):
                if not self.is_mine(i, j):
                    change = [-1, 0, 1]
                    for pluss_i in change:
                        for pluss_j in change:
                            if i + pluss_i in range(0, n) and j + pluss_j in range(0, n) and \
                                    self.is_mine(i + pluss_i, j + pluss_j):
                                self.a[i][j].val += 1

    def is_mine(self, x, y):
        return self.a[x][y].is_mine()

    def __str__(self):
        ret = ''
        for i in range(self.n):
            for j in range(self.n):
                if not self.is_mine(i, j):
                    ret += str(self.a[i][j].val) + ' '
                else:
                    ret += '* '
            ret += '\n'
        return ret

    def show(self, x, y):
        for i in range(self.n):
            for j in range(self.n):
                win.blit(self.a[i][j].pict, (x + i * sz, y + j * sz))
        pygame.display.update()

    def check_mine(self, x, y):
        ret = self.a[x][y].check_mine()
        self.cells_to_open -= 1
        if self.a[x][y].val == 0:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if x + i in range(0, self.n) and y + j in range(0, self.n):
                        if not self.a[x + i][y + j].open:
                            self.check_mine(x + i, y + j)
        return ret

    def inverse_flag(self, x, y):
        self.a[x][y].inverse_flag()


class Game:
    def __init__(self, field):
        self.field = field
        self.alive = True
        self.win = False
        self.step_type = 'open_mine'
        self.n = field.n
        self.num_mines = field.num_mines
        self.cells_to_open = self.n ** 2 - self.num_mines

    def show(self):
        print_screen('Всего мин: ' + str(self.field.num_mines), 'calibri', 20,
                     (255, 255, 255), 10, 10)
        if self.step_type == 'open_mine':
            print_screen('Для переключения на флаг нажмите - f', 'calibri',
                         20, (255, 255, 255), SZ - 10 - 340, 10)
        else:
            print_screen('Для отключения флага нажмите - m', 'calibri', 20, (255, 255, 255),
                         SZ - 10 - 340, 10)

        self.field.show((SZ - sz * self.field.n) // 2, (SZ - sz * self.field.n) // 2)

        pygame.display.update()

    def step_style_flag(self):
        self.step_type = 'set_flag'

    def step_style_mine(self):
        self.step_type = 'open_mine'

    def step(self, x, y):
        print('step', x, y)
        if x not in range(0, self.field.n) or y not in range(0, self.field.n):
            return False
        if self.step_type == 'set_flag':
            self.field.inverse_flag(x, y)
        else:
            if self.field.check_mine(x, y):
                self.alive = False
            self.cells_to_open = self.field.cells_to_open
            if self.cells_to_open == 0:
                self.win = True
        self.show()


def get_xy_by_click(x, y):
    return (x - (SZ - sz * N) // 2) // sz, (y - (SZ - sz * N) // 2) // sz


def print_screen(text, font, size, color, x, y, grey_under=True):
    if grey_under:
        leng = len(text) * 10
        pygame.draw.rect(win, WIN_COLOR, (x, y, x + leng, y + 10))
    calibri_font = pygame.font.SysFont(font, size)
    text = calibri_font.render(text, 1, color)
    win.blit(text, (x, y))
    pygame.display.update()


def input_number_from_screen(text):
    print_screen(text, 'calibri', 20, (255, 255, 255), (SZ - len(text * 20)) // 2, 50)
    pygame.display.update()
    arr = pygame.event.get()
    while not arr or arr[0].type != pygame.KEYDOWN or not arr[0].unicode.isdigit():
        arr = pygame.event.get()
    return int(arr[0].unicode)


def inp_n():
    global N
    N = input_number_from_screen('Введите размер поля от 2 до 14')
    if N == 1:
        N = N * 10 + input_number_from_screen('')


def inp_m():
    global MINES, N
    MINES = randrange(N - N // 3, N + (N // 3) + 1)


def start_game():
    global N

    win.fill(WIN_COLOR)
    pygame.display.update()

    inp_n()
    inp_m()
    win.fill(WIN_COLOR)
    pygame.display.update()

    game = Game(Field(N, MINES))

    game.show()

    while game.alive and not game.win:
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                exit()
            if i.type == pygame.MOUSEBUTTONDOWN:
                if i.button == 1:
                    game.step(*get_xy_by_click(*i.pos))
                    break
            if i.type == pygame.KEYDOWN:
                if i.key == pygame.K_f:
                    game.step_style_flag()
                elif i.key == pygame.K_m:
                    game.step_style_mine()
                game.show()

    if game.alive:
        print_screen('ПОБЕДА!!!', 'calibri', 100, (255, 255, 0), 130, SZ // 2, grey_under=False)
    else:
        print_screen('ПОРАЖЕИЕ!!!', 'calibri', 100, (248, 0, 0), 100, SZ // 2, grey_under=False)
    pygame.time.delay(1000)
    print_screen('Если вы больше не хотите играть нажмите Esc.', 'calibri', 20, (255, 255, 255), 200,
                 SZ // 4, grey_under=False)
    print_screen('Для продолжения игры нажмите любую клавишу.', 'calibri', 20, (255, 255, 255), 200,
                 SZ // 4 + 15, grey_under=False)
    pygame.event.get()
    arr = pygame.event.get()
    while not arr or arr[0].type != pygame.KEYDOWN:
        arr = pygame.event.get()
    print(arr)
    if arr[0].key == pygame.K_ESCAPE:
        return False
    return True


SZ = 800
sz = 50
N = 10
MINES = 10
WIN_COLOR = (111, 111, 111)
pygame.init()
win = pygame.display.set_mode((SZ, SZ))

not_oppened_cell_pict = pygame.image.load('pictures/not_oppened_cell.png')
flag_cell_pict = pygame.image.load('pictures/flag_cell.png')
mine_cell_pict = pygame.image.load('pictures/mine_cell.png')
numbers = [pygame.image.load('pictures/' + str(i) + '.png') for i in range(9)]


while start_game():
    pass

pygame.quit()
