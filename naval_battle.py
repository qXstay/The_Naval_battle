import random

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.direction == 0:
                cur_x += i
            elif self.direction == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.field = [["O"] * size for _ in range(size)]
        self.busy_ships = []
        self.busy_shots = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots():
            if self.out(d) or d in self.busy_ships:
                raise Exception("Невозможно разместить корабль")
        for d in ship.dots():
            self.field[d.x][d.y] = "■"
            self.busy_ships.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def out(self, d):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots():
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not self.out(cur) and cur not in self.busy_ships:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy_ships.append(cur)

    def count_ships(self):
        return sum(1 for ship in self.ships if ship.lives > 0)

    def __str__(self):
        res = ""
        res += " | 1 | 2 | 3 | 4 | 5 | 6 |\n"
        for i, row in enumerate(self.field):
            res += f"{i + 1} | " + " | ".join(row) + " |\n"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def shot(self, d):
        if self.out(d):
            raise Exception("Выстрел за пределы поля")

        if d in self.busy_shots:
            raise Exception("Вы уже стреляли в эту точку")

        self.busy_shots.append(d)

        for ship in self.ships:
            if d in ship.dots():
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                else:
                    print("Корабль ранен!")
                return True

        self.field[d.x][d.y] = "T"
        print("Мимо!")
        return False

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except Exception as e:
                print(e)

class User(Player):
    def ask(self):
        while True:
            try:
                coords = input("Ваш ход: ").split()

                if len(coords) != 2:
                    raise ValueError("Введите 2 координаты")

                x, y = coords
                if not (x.isdigit() and y.isdigit()):
                    raise ValueError("Введите числа")

                x, y = int(x), int(y)
                return Dot(x - 1, y - 1)
            except ValueError as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(random.randint(0, self.board.size - 1), random.randint(0, self.board.size - 1))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

class Game:
    def __init__(self, size=6):
        pl_board = self.random_board(size)
        ai_board = self.random_board(size, hid=True)
        self.ai = AI(ai_board, pl_board)
        self.user = User(pl_board, ai_board)

    def random_board(self, size, hid=False):
        board = None
        while board is None:
            board = self.attempt_board(size, hid)
        return board

    def attempt_board(self, size, hid):
        board = Board(hid, size)
        attempts = 0
        for l, c in [(3, 1), (2, 2), (1, 4)]:
            for _ in range(c):
                while True:
                    attempts += 1
                    if attempts > 2000:
                        return None
                    ship = Ship(Dot(random.randint(0, size - 1), random.randint(0, size - 1)), l, random.randint(0, 1))
                    try:
                        board.add_ship(ship)
                        break
                    except:
                        pass
        return board

    def greet(self):
        print("Игра 'Морской бой'")
        print("Формат ввода: x y")
        print("x - номер строки, y - номер столбца")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.user.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count_ships() == 0:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.user.board.count_ships() == 0:
                print("-" * 20)
                print("Компьютер выиграл!")
                break

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()