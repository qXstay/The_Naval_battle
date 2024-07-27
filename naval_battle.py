import random

# Класс, представляющий точку на доске
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Сравнение точек (для проверки попадания)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

# Класс, представляющий корабль
class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow  # начальная точка (нос корабля)
        self.length = length  # длина корабля
        self.direction = direction  # направление (0 - горизонтальное, 1 - вертикальное)
        self.lives = length  # количество жизней (единиц длины)

    # Метод для получения списка точек, занимаемых кораблем
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

# Класс, представляющий игровую доску
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size  # размер доски
        self.hid = hid  # скрыта ли доска (для доски компьютера)

        self.field = [["O"] * size for _ in range(size)]  # игровое поле
        self.busy_ships = []  # занятые точки кораблями
        self.busy_shots = []  # точки, куда уже стреляли
        self.ships = []  # список кораблей на доске

    # Метод для добавления корабля на доску
    def add_ship(self, ship):
        for d in ship.dots():
            if self.out(d) or d in self.busy_ships:
                raise Exception("Невозможно разместить корабль")
        for d in ship.dots():
            self.field[d.x][d.y] = "■"
            self.busy_ships.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Метод для проверки выхода точки за пределы доски
    def out(self, d):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    # Метод для обозначения контура вокруг корабля
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

    # Метод для подсчета оставшихся кораблей
    def count_ships(self):
        return sum(1 for ship in self.ships if ship.lives > 0)

    # Метод для отображения доски
    def __str__(self):
        res = ""
        res += " | 1 | 2 | 3 | 4 | 5 | 6 |\n"
        for i, row in enumerate(self.field):
            res += f"{i + 1} | " + " | ".join(row) + " |\n"

        if self.hid:
            res = res.replace("■", "O")
        return res

    # Метод для обработки выстрела по доске
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

# Базовый класс для игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board  # собственная доска игрока
        self.enemy = enemy  # доска противника

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

# Класс для игрока-человека
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

# Класс для игрока-ИИ
class AI(Player):
    def ask(self):
        d = Dot(random.randint(0, self.board.size - 1), random.randint(0, self.board.size - 1))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

# Класс для игры
class Game:
    def __init__(self, size=6):
        pl_board = self.random_board(size)
        ai_board = self.random_board(size, hid=True)
        self.ai = AI(ai_board, pl_board)
        self.user = User(pl_board, ai_board)

    # Метод для случайного создания доски с кораблями
    def random_board(self, size, hid=False):
        board = None
        while board is None:
            board = self.attempt_board(size, hid)
        return board

    # Попытка создать доску с кораблями
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

    # Приветственное сообщение
    def greet(self):
        print("Игра 'Морской бой'")
        print("Формат ввода: x y")
        print("x - номер строки, y - номер столбца")

    # Основной игровой цикл
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

    # Запуск игры
    def start(self):
        self.greet()
        self.loop()

# Запуск игры
g = Game()
g.start()
