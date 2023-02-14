import os
import pygame
import datetime
import math
import sys
import random
import sqlite3
import numpy as np
from collections import Counter


class Camera:
    """
    Оцентровывает данный объект

    Attributes:
        x: float
            Позиция игрока по оси абсцисс относительно положения, занимаемого в начале прохождения,
             не зависит от клетки, в которой находится target
        y: float
            Позиция игрока по оси ординат относительно положения, занимаемого в начале прохождения,
             не зависит от клетки, в которой находится target

    Methods:
        update(target)
            target - объект в чью систему отсчета войдет камера (объект, который будет по центру экрана)
            Перемещает все объекты так, чтобы target оказался по центру экрана
    """
    def __init__(self):
        self.x, self.y = 0, 0

    def update(self, target):
        delta_x = (target.x + target.width // 2 - CAMERA_WIDTH // 2)
        delta_y = (target.y + target.height // 2 - CAMERA_HEIGHT // 2)

        self.x += delta_x
        self.y += delta_y

        for _object in all_gameObjects:
            _object.x -= delta_x
            _object.y -= delta_y


class WorldGenerator:
    """
    Класс WorldGenerator создает, отрисовывае и изменяет игровое поле

    Attributes:
         _camera: Camera
            Позиция игрока будет считаться с помощью этой камеры
        cell: list * list
            Игровое поле, каждый элемент которого представляет одну клетку,
            каждый элемент одной клетки - это объект и шанс создания этого объекта
        patterns: list
            Список всех возможных видов клеток
        character_cell: list
            Показывает в какой клетке находится игрок

    Methods:
        new_cell():
            Уничтожает объекты, которые находятся вне клеток, которые окружают игрока
            Создает объекты, которые находятся в клетках окружающих игрока
            Случайно выбирает новые паттерны для новых клеток (в которых раньше не бал игрок)
            При выходе за пределы поля, расширяет поле на один слой во все стороны
    """
    def __init__(self, _camera):
        self.cells = [[[[PatternPlatform(0, 0, 50, 50, 'Left wall.png',
                                           ['Wall'], ['Wall']), 0]]]]
        self.patterns = [[[PatternPlatform(0, 0, WIDTH // 2 - 100, 50, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 + 100, 0, WIDTH // 2 - 100, 50, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(0, HEIGHT - 50, WIDTH // 2 - 100, 50, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 + 100, HEIGHT - 50, WIDTH // 2 - 100, 50, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(0, 0, 50, HEIGHT // 2 - 100, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(0, HEIGHT // 2 + 100, 50, HEIGHT // 2 - 100, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH - 50, 0, 50, HEIGHT // 2 - 100, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH - 50, HEIGHT // 2 + 100, 50, HEIGHT // 2 - 100, None, ['Wall'], ['Wall']), 1],
                          [PatternEnemy1(WIDTH // 2 - 75, HEIGHT // 2 - 75), 0.9],
                          [PatternEnemy2(WIDTH // 2 + 75, HEIGHT // 2 - 75, 8), 0.9],
                          [PatternEnemy2(WIDTH // 2 - 75, HEIGHT // 2 + 75, 8), 0.9],
                          [PatternEnemy1(WIDTH // 2 + 75, HEIGHT // 2 + 75), 0.9],
                          [PatternAidKid(WIDTH // 2 - 25, HEIGHT // 2 - 25), 0.5],
                          [PatternAidKid(WIDTH // 2 + 25, HEIGHT // 2 - 25), 0.5],
                          [PatternAidKid(WIDTH // 2 - 25, HEIGHT // 2 + 25), 0.5],
                          [PatternAidKid(WIDTH // 2 + 25, HEIGHT // 2 + 25), 0.5]],
                         [[PatternPlatform(WIDTH // 2 - 200, HEIGHT // 2 - 200, 200, 200, None,
                                           ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2, HEIGHT // 2, 200, 200, None,
                                           ['Wall'], ['Wall']), 1],
                          [PatternEnemy2(WIDTH // 2, HEIGHT // 2 - 150, 8), 1],
                          [PatternEnemy2(WIDTH // 2 + 100, HEIGHT // 2 - 50, 8), 1],
                          [PatternEnemy2(WIDTH // 2 - 150, HEIGHT // 2, 8), 1],
                          [PatternEnemy2(WIDTH // 2 - 50, HEIGHT // 2 + 100, 8), 1],
                          [PatternAidKid(WIDTH // 2, HEIGHT // 2 - 50), 0.8],
                          [PatternAidKid(WIDTH // 2, HEIGHT // 2 - 100), 0.8],
                          [PatternAidKid(WIDTH // 2 + 50, HEIGHT // 2 - 50), 0.8],
                          [PatternAidKid(WIDTH // 2 - 50, HEIGHT // 2), 0.8],
                          [PatternAidKid(WIDTH // 2 - 100, HEIGHT // 2), 0.8],
                          [PatternAidKid(WIDTH // 2 - 50, HEIGHT // 2 + 50), 0.8]],
                         [[PatternSpikes(0, 0, 500, 250, 'Spike 500 250.png'), 1],
                          [PatternSpikes(500, 250, 500, 250, 'Spike 500 250.png'), 1],
                          [PatternSpikes(1000, 500, 500, 250, 'Spike 500 250.png'), 1],
                          [PatternSpikes(1500, 750, 500, 250, 'Spike 500 250.png'), 1]],
                         [[PatternSpikes(0, HEIGHT - 250, 500, 250, 'Spike 500 250.png'), 1],
                          [PatternSpikes(500, HEIGHT - 500, 500, 250, 'Spike 500 250.png'), 1],
                          [PatternSpikes(1000, HEIGHT - 750, 500, 250, 'Spike 500 250.png'), 1],
                          [PatternSpikes(1500, 750, 0, 250, 'Spike 500 250.png'), 1]],
                         [[PatternPlatform(0, 0, WIDTH, HEIGHT, None, ['Wall'], ['Wall']), 1]],
                         [[PatternPlatform(0, HEIGHT // 2 - 150, WIDTH, 50, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(0, HEIGHT // 2 + 100, WIDTH, 50, None, ['Wall'], ['Wall']), 1]],
                         [[PatternPlatform(WIDTH // 2 - 150, 0, 50, HEIGHT, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 + 100, 0, 50, HEIGHT, None, ['Wall'], ['Wall']), 1]],
                         [[PatternPlatform(0, HEIGHT // 2 - 150, WIDTH // 2 - 100, 50, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(0, HEIGHT // 2 + 100, WIDTH // 2 - 100, 50, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 + 100, HEIGHT // 2 - 150, WIDTH // 2 - 100, 50,
                                           None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 + 100, HEIGHT // 2 + 100, WIDTH // 2 - 100, 50,
                                           None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 - 150, 0, 50, HEIGHT // 2 - 100, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 + 100, 0, 50, HEIGHT // 2 - 100, None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 - 150, HEIGHT // 2 + 100, 50, HEIGHT // 2 - 100,
                                           None, ['Wall'], ['Wall']), 1],
                          [PatternPlatform(WIDTH // 2 + 100, HEIGHT // 2 + 100, 50, HEIGHT // 2 - 100,
                                           None, ['Wall'], ['Wall']), 1]],
                         [[PatternItemSpawner(WIDTH // 2 - 100, HEIGHT // 2 - 100), 1],
                          [PatternItemSpawner(WIDTH // 2 - 100, HEIGHT // 2 + 75), 1],
                          [PatternItemSpawner(WIDTH // 2 + 75, HEIGHT // 2 - 100), 1],
                          [PatternItemSpawner(WIDTH // 2 + 75, HEIGHT // 2 + 75), 1]]]

        self.character_cell = [0, 0]
        self.camera = _camera
        self.new_cell()

    def update(self):
        if self.camera.x > WIDTH // 2:
            self.character_cell[0] += 1
            self.camera.x = -WIDTH // 2
            self.new_cell()
        elif self.camera.x < -WIDTH // 2:
            self.character_cell[0] -= 1
            self.camera.x = WIDTH // 2
            self.new_cell()

        if self.camera.y > HEIGHT // 2:
            self.character_cell[1] -= 1
            self.camera.y = -HEIGHT // 2
            self.new_cell()
        elif self.camera.y < -HEIGHT // 2:
            self.character_cell[1] += 1
            self.camera.y = HEIGHT // 2
            self.new_cell()

    def new_cell(self):
        try:
            if self.character_cell[0] < 1 or self.character_cell[1] < 1:
                raise IndexError
            for _object in all_gameObjects:
                if 'Indestructible' in _object.tags:
                    continue

                _object._kill()

            cells_for_create_pattern = [[-1, 0], [-1, -1], [-1, 1], [1, 0], [1, -1],
                                        [1, 1], [0, 0], [0, -1], [0, 1]]

            for index in cells_for_create_pattern:
                if not self.cells[self.character_cell[0] + index[0]][self.character_cell[1] + index[1]]:
                    pattern = random.choice(self.patterns)
                    for j in pattern:
                        self.cells[self.character_cell[0] + index[0]][self.character_cell[1] + index[1]]\
                            .append(j.copy())

                for j in range(len(self.cells[self.character_cell[0] + index[0]][self.character_cell[1] + index[1]])):
                    if random.random() < self.cells[self.character_cell[0] + index[0]][
                                                    self.character_cell[1] + index[1]][j][1]:
                        self.cells[self.character_cell[0] + index[0]][
                            self.character_cell[1] + index[1]][j][0].init(index[0], index[1])
                        self.cells[self.character_cell[0] + index[0]][self.character_cell[1] + index[1]][j][1] = 1
                    else:
                        self.cells[self.character_cell[0] + index[0]][self.character_cell[1] + index[1]][j][1] = 0

        except IndexError:
            for index in range(len(self.cells)):
                self.cells[index].insert(0, [])
                self.cells[index].append([])

            self.cells.insert(0, [[]] * len(self.cells[0]))
            self.cells.append([[]] * len(self.cells[0]))

            self.character_cell[0] += 1
            self.character_cell[1] += 1

            self.new_cell()


class Event:
    """
    Event - событие, сохраняемое в  массив EVENTS,
     с помощью которого можно выявить некое действие, происходящее в ходе игры

     Attributes:
         args: dict
            Словарь всех свойств данного события

    Methods: None
    """
    def __init__(self, **args):
        self.args = args
        self.calls = {}
        self.new_calls = {}

    def set_call(self, _object):
        if _object not in self.new_calls:
            self.new_calls[_object] = 0
        self.new_calls[_object] += 1

    def apply(self):
        for call in self.new_calls:
            if call not in self.calls:
                self.calls[call] = 0
            self.calls[call] += 1

        self.new_calls = {}


class GameObject:
    """
    Базовый класс для всех объектов, расположенный на игровом поле, с которыми можно взаимодействовать

    Attributes:
        x: float
            Позиция левого верхнего угла объекта по оси абсцисс
        y: float
            Позиция левого верхнего угла объекта по оси абсцисс
        width: float
            Длина объекта
        height: float
            высота объекта
        collision: Collision
            Коллайдер объекта
        tags: list
            Список свойств объекта
        id: int
            Уникальный номер объекта
        time: datetime.datetime
            Время создания обьекта

    Methods: None
    """
    COLOR = [252, 247, 190]
    FON_COLOR = [24, 28, 25]

    def __init__(self, x=0, y=0, width=0, height=0):
        global number_of_gameobjects
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.rect = pygame.Rect(self.x, self.y, width, height)
        self.collision = Collision(0, 0, width, height, self)
        self.tags = []
        self.id = number_of_gameobjects
        number_of_gameobjects += 1
        self.time = datetime.datetime.now()

    def wait(self, time, delay):
        if datetime.datetime.now() - time >= datetime.timedelta(seconds=delay):
            return True


class Collision(pygame.sprite.Sprite):
    """Имитирует collider объекта, неизменный прямоугольник,
     расположенный статично, относительно родительского объекта"""
    def __init__(self, x, y, width, height, game_object):
        pygame.sprite.Sprite.__init__(self, all_collisions)
        self.image = pygame.Surface((width, height),
                                    pygame.SRCALPHA, 32)
        self.image.set_alpha(1)
        pygame.draw.rect(self.image, pygame.Color("black"),
                         (0, 0, width, height))
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.gameObject = game_object
        self.tags = []

        self.rect = pygame.Rect(self.gameObject.x + self.x, self.gameObject.y + self.y, self.width, self.height)

    def update(self):
        self.rect = pygame.Rect(self.gameObject.x + self.x, self.gameObject.y + self.y, self.width, self.height)

    # Возвращает коллизии
    def can_move_collisions(self, delta_x=0, delta_y=0, needed_tags_of_object=None, needed_tags_of_collision=None):
        if needed_tags_of_object is None:
            needed_tags_of_object = []
        if needed_tags_of_collision is None:
            needed_tags_of_collision = []
        ghost = Collision(self.x + delta_x, self.y + delta_y, self.width, self.height, self.gameObject)
        all_contacts = list(filter(lambda x: set(needed_tags_of_object).issubset(set(x.gameObject.tags)) and set(
            needed_tags_of_collision).issubset(set(x.tags)) and x is not self,
                           pygame.sprite.spritecollide(ghost, all_collisions, False, pygame.sprite.collide_rect)))
        ghost.kill()

        return all_contacts


class Item:
    """
    Базовый класс для всех предметов, имеющих название, цену, носителя

    Attributes:
        name: str
            Название объекта
        price: int
            Цена обьекта
        carrier: GameObject
            Носитель объекта

    Methods:
        update()
            Срабатывает каждый кадр
        take_off()
            Срабатывает при снятии объекта
    """
    def __init__(self, name, price, carrier):
        self.name = name
        self.price = price
        self.carrier = carrier

    def update(self):
        pass

    def take_off(self):
        pass


class ItemSpawner(pygame.sprite.Sprite, GameObject):
    """
    Объект, дающий возможность получать новые предметы

    Attributes:
        Атрибуты GameObject
        items: list
            Список всех возможных объектов
        item: Item
            Случайно выбранный предмет из items
        time: datetime.datetime
            Время последней передачи предмета
        time_between_receiving_items: float
            Время через которое можно передавать предметы в секундах
        was_purchase: bool
            Показывает, был ли куплен предмет item

    Methods:
        update(tick=0)
            Пишет над объектом предмет, хранящийся в данном объекте и цену предмета
            Если с посленей передачи прдмета прошло болше времени чем time_between_receiving_items
            дает коллизии нормальные размеры
        wait(time, delay)
            Возаврыщает True, если с time прошло больше времени, чем delay
    """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        self.width, self.height = 50, 50
        GameObject.__init__(self, x, y, self.width, self.height)
        self.image = load_image('Item spawner.png', GameObject.FON_COLOR)

        self.tags = self.collision.tags = ['Item spawner']

        self.items = [Nothing(), Accelerator(10), DamageBooster(30), Arsonist(15), BulletPyro(100)]
        self.item = random.choice(self.items)
        self.time_between_receiving_items = 1

        self.was_purchase = False

        self.font = pygame.font.Font(None, 20)

    def update(self, tick=0):
        all_inscriptions['Item ' + str(self.id)] = [self.font.render(f'Item: {self.item.name}',
                                                                     True, GameObject.COLOR), self.x + self.width // 2 -
                                                    self.font.size(f'Item: {self.item.name}')[0] // 2, self.y - 40,
                                                    self.font.size(f'Item: {self.item.name}')[0],
                                                    self.font.size(f'Item: {self.item.name}')[1]]
        all_inscriptions['Price ' + str(self.id)] = [self.font.render(f'Price: {self.item.price}',
                                                                      True, GameObject.COLOR), self.x + self.width // 2 -
                                                     self.font.size(f'Price: {self.item.price}')[0] // 2, self.y - 20,
                                                     self.font.size('Price ' + str(self.id))[0],
                                                     self.font.size('Price ' + str(self.id))[1]
                                                     ]
        if self.wait(self.time, self.time_between_receiving_items):
            self.collision.width, self.collision.height = self.width, self.height
        self.collision.update()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def wait(self, time, delay):
        if datetime.datetime.now() - time >= datetime.timedelta(seconds=delay):
            return True

    def _kill(self):
        self.collision.kill()
        self.kill()


class PatternItemSpawner:
    """
    Класс, создающий объект ItemSpawner

    Attributes:
        x: float
            Позиция объекта по оси абсцисс, если бы игрок находился по центру клетки, к которой располагается объект
        y: float
            Позиция объекта по оси ординат, если бы игрок находился по центру клетки, к которой располагается объект
        width: float
            Ширины объекта
        height: float
            Высота объекта

    Methods:
        init(delta_x, delta_y)
            Создает объект Enemy1
    """
    def __init__(self, x, y):
        self.x, self.y = x, y

    def init(self, delta_x, delta_y):
        ItemSpawner(self.x + (CAMERA_WIDTH - WIDTH) // 2 - camera.x + WIDTH * delta_x,
                    self.y + (CAMERA_HEIGHT - HEIGHT) // 2 - camera.y - HEIGHT * delta_y)


class Enemy1(pygame.sprite.Sprite, GameObject):
    """
    Класс врага, стреляющего часто слабыми пулями, летящими по прямой

    Attributes:
        Атрибуты GameObject
        hp: float
            Здоровье объекта
        damage: float
            Урон, который наносит объект
        velocity_of_bullet: float
            Скорость пуль
        distance_of_attack: float
            Дистанция, с которой враг начнет атаковать игрока
        time: datetime.datetime
            Время, когда последний раз объект получил урон
        time_between_enemy_attack: float
            Время с последнего урона по объекту, в течение которого объект нельзя обижать
        time_attack: datetime.datetime
            Время последней атаки объекта
        time_between_attack_on_character: float
            Время между атаками объекта

    Methods:
        update(tick=0)
            Пишет над объектом оставшиеся здоровье
            Если объект соприкоснулся с объектом со свойством "Dangerous for enemy" и can_be_under_attack == True,
            по объекту наносится урон
            Если игрок в поле действия и прошло необходимое время, стреляет пулей Bullet в сторону игрока
            Если здоровье меньшу 1, уничтожает объект

        distance(target)
            Возвращает расстояние до target

        distance_x(target)
            Возвращает расстояние до target по оси абсцисс

        distance_y(target)
            Возвращает расстояние до target по оси ординат
        _kill(forever=False)
            Уничтожает объект,
            если forever равно True, то навсегда
    """
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, width, height)
        self.image = load_image('Turret 1.png', [24, 28, 25])

        self.tags = ['Enemy', 'Dangerous']
        self.collision.tags = ['Dangerous']
        self.hp, self.damage = 100, 10
        self.velocity_of_bullet = 800
        self.distance_of_attack = 500
        self.can_be_under_attack = True
        self.time, self.time_between_enemy_attack = datetime.datetime.now(), 0.1
        self.time_attack = datetime.datetime.now()
        self.time_between_attack_on_character = 0.2

        self.font = pygame.font.Font(None, 30)
        text = self.font.render(str(self.hp), True, [252, 247, 190])
        all_inscriptions[f'Enemy {self.id}'] = [text, self.x + (
                self.width - self.font.size(str(self.hp))[0]) // 2, self.y - self.font.size(str(self.hp))[1],
                                                self.font.size(str(self.hp))[0], self.font.size(str(self.hp))[1]]

    def update(self, tick=0):
        for dangerous_object in self.collision.can_move_collisions(0, 0, ['Dangerous for enemy']):
            if self.wait(self.time, self.time_between_enemy_attack):
                self.hp -= dangerous_object.gameObject.damage
                self.time = datetime.datetime.now()
                self.can_be_under_attack = False

            if 'One hit' in dangerous_object.gameObject.tags:
                dangerous_object.gameObject._kill()

        text = self.font.render(str(self.hp), True, [252, 247, 190])
        all_inscriptions[f'Enemy {self.id}'] = [text, self.x + (
                self.width - self.font.size(str(self.hp))[0]) // 2, self.y - self.font.size(str(self.hp))[1],
                                                self.font.size(str(self.hp))[0], self.font.size(str(self.hp))[1]]

        if self.distance(character) < self.distance_of_attack and self.wait(self.time_attack,
                                                                            self.time_between_attack_on_character):
            self.time_attack = datetime.datetime.now()
            c = (self.distance_x(character) * self.velocity_of_bullet / self.distance(character),
                 self.distance_y(character) * self.velocity_of_bullet / self.distance(character))

            Bullet(self.x + self.width // 2 - 5, self.y + self.height // 2 - 5, 10, 10,
                   c[0], c[1], 10, ['Dangerous', 'Indestructible', 'One hit'], ['Dangerous'])

        self.collision.update()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if self.hp <= 0:
            self._kill(True)

    def distance(self, target):
        return math.sqrt(self.distance_x(target) ** 2 + self.distance_y(target) ** 2)

    def distance_x(self, target):
        return target.x + target.width // 2 - (self.x + self.width // 2)

    def distance_y(self, target):
        return target.y + target.height // 2 - (self.y + self.height // 2)

    def _kill(self, forever=False):
        if forever:
            global KILLS
            KILLS += 1
            Coin(self.x + self.width // 2 - 5, self.y + self.height // 2 - 5)
            for index in range(len(world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                                   world_generator.character_cell[1] + self.y_of_cell])):
                if type(world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                            world_generator.character_cell[1] + self.y_of_cell][index][0]) == PatternEnemy1 and\
                        world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                            world_generator.character_cell[1] + self.y_of_cell][index][1] == 1:
                    world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                        world_generator.character_cell[1] + self.y_of_cell].pop(index)
                    break
        all_inscriptions.pop(f'Enemy {self.id}')
        self.collision.kill()
        self.kill()


class PatternEnemy1:
    """
    Класс, создающий объект Enemy1

    Attributes:
        x: float
            Позиция объекта по оси абсцисс, если бы игрок находился по центру клетки, к которой располагается объект
        y: float
            Позиция объекта по оси ординат, если бы игрок находился по центру клетки, к которой располагается объект
        width: float
            Ширины объекта
        height: float
            Высота объекта

    Methods:
        init(delta_x, delta_y)
            Создает объект Enemy1
    """
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = 50, 50

    def init(self, delta_x, delta_y):
        enemy = Enemy1(self.x + (CAMERA_WIDTH - WIDTH) // 2 - camera.x + WIDTH * delta_x,
                       self.y + (CAMERA_HEIGHT - HEIGHT) // 2 - camera.y - HEIGHT * delta_y, self.width, self.height)
        enemy.x_of_cell = delta_x
        enemy.y_of_cell = delta_y


class Enemy2(pygame.sprite.Sprite, GameObject):
    """
        Класс врага, стреляющего иногда мощными пулями, способными к изменению траектории

        Attributes:
            Атрибуты GameObject
            hp: float
                Здоровье объекта
            damage: float
                Урон, который наносит объект
            velocity_of_bullet: float
                Скорость пуль
            distance_of_attack: float
                Дистанция, с которой враг начнет атаковать игрока
            time: datetime.datetime
                Время, когда последний раз объект получил урон
            time_between_enemy_attack: float
                Время с последнего урона по объекту, в течение которого объект нельзя обижать
            time_attack: datetime.datetime
                Время последней атаки объекта
            time_between_attack_on_character: float
                Время между атаками объекта

        Methods:
            update(tick=0)
                Пишет над объектом оставшиеся здоровье
                Если объект соприкоснулся с объектом со свойством "Dangerous for enemy" и can_be_under_attack == True,
                по объекту наносится урон
                Если игрок в поле действия и прошло необходимое время, стреляет пулей SuperBullet в сторону игрока
                Если здоровье меньшу 1, уничтожает объект

            distance(target)
                Возвращает расстояние до target

            distance_x(target)
                Возвращает расстояние до target по оси абсцисс

            distance_y(target)
                Возвращает расстояние до target по оси ординат

            _kill(forever=False)
                Уничтожает объект,
                если forever равно True, то навсегда
        """
    def __init__(self, x, y, width, height, delta_velocity):
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, width, height)
        self.image = load_image('Turret 2.png', [24, 28, 25])

        self.tags = ['Enemy', 'Dangerous']
        self.collision.tags = ['Dangerous']
        self.hp, self.damage = 100, 10
        self.velocity_of_bullet = 600
        self.distance_of_attack = 800
        self.delta_velocity = delta_velocity
        self.time, self.time_between_enemy_attack = datetime.datetime.now(), 0.1
        self.time_attack = datetime.datetime.now()

        self.font = pygame.font.Font(None, 30)
        text = self.font.render(str(self.hp), True, [252, 247, 190])
        all_inscriptions[f'Enemy {self.id}'] = [text, self.x + (
                self.width - self.font.size(str(self.hp))[0]) // 2, self.y - self.font.size(str(self.hp))[1],
                                                self.font.size(str(self.hp))[0], self.font.size(str(self.hp))[1]]

    def update(self, tick=0):
        # print(self.collision.can_move_collisions())
        for dangerous_object in self.collision.can_move_collisions(0, 0, ['Dangerous for enemy']):
            if self.wait(self.time, self.time_between_enemy_attack):
                self.hp -= dangerous_object.gameObject.damage
                self.time = datetime.datetime.now()
                self.can_be_under_attack = False

            if 'One hit' in dangerous_object.gameObject.tags:
                dangerous_object.gameObject._kill()

        text = self.font.render(str(self.hp), True, [252, 247, 190])
        all_inscriptions[f'Enemy {self.id}'] = [text, self.x + (
                self.width - self.font.size(str(self.hp))[0]) // 2, self.y - self.font.size(str(self.hp))[1],
                                                self.font.size(str(self.hp))[0], self.font.size(str(self.hp))[1]]

        if self.distance(character) < self.distance_of_attack and self.wait(self.time_attack, 1):
            self.time_attack = datetime.datetime.now()
            c = (self.distance_x(character) * self.velocity_of_bullet / self.distance(character),
                 self.distance_y(character) * self.velocity_of_bullet / self.distance(character))

            SuperBullet(character, self.x + self.width // 2 - 10, self.y + self.height // 2 - 10, 20, 20, c[0], c[1],
                        self.delta_velocity, 20, ['Dangerous', 'Indestructible', 'One hit'], ['Dangerous'])

        self.collision.update()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if self.hp <= 0:
            self._kill(True)

    def distance(self, target):
        return math.sqrt(self.distance_x(target) ** 2 + self.distance_y(target) ** 2)

    def distance_x(self, target):
        return target.x + target.width // 2 - (self.x + self.width // 2)

    def distance_y(self, target):
        return target.y + target.height // 2 - (self.y + self.height // 2)

    def _kill(self, forever=False):
        if forever:
            global KILLS
            KILLS += 1
            Coin(self.x + self.width // 2 - 5, self.y + self.height // 2 - 5)
            for index in range(len(world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                                   world_generator.character_cell[1] + self.y_of_cell])):
                if type(world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                            world_generator.character_cell[1] + self.y_of_cell][index][0]) == PatternEnemy2 and\
                        world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                            world_generator.character_cell[1] + self.y_of_cell][index][1] == 1:
                    world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                        world_generator.character_cell[1] + self.y_of_cell].pop(index)
                    break
        all_inscriptions.pop(f'Enemy {self.id}')
        self.collision.kill()
        self.kill()


class PatternEnemy2:
    """
        Класс, создающий объект Enemy2

        Attributes:
            x: float
                Позиция объекта по оси абсцисс, если бы игрок находился по центру клетки, к которой располагается объект
            y: float
                Позиция объекта по оси ординат, если бы игрок находился по центру клетки, к которой располагается объект
            width: float
                Ширины объекта
            height: float
                Высота объекта

        Methods:
            init(delta_x, delta_y)
                Создает объект Enemy2
        """
    def __init__(self, x, y, delta_velocity):
        self.x, self.y = x, y
        self.width, self.height = 50, 50
        self.delta_velocity = delta_velocity

    def init(self, delta_x, delta_y):
        enemy = Enemy2(self.x + (CAMERA_WIDTH - WIDTH) // 2 - camera.x + WIDTH * delta_x,
                       self.y + (CAMERA_HEIGHT - HEIGHT) // 2 - camera.y - HEIGHT * delta_y, self.width, self.height,
                       self.delta_velocity)
        enemy.x_of_cell = delta_x
        enemy.y_of_cell = delta_y


class Gun:
    """
    Класс пистолета, является родительсим для всех классов оружия

    Attributes:
        carrier: GameObject
            Носитель оружия
        damage: float
            Урон, который будет наносить пуля
        time: datetime.datetime
            Время последнего выстрела
        time_between_attack: float
            Время, которое должно пройти с предыдущего выстрела, чтобы сделать новый (в секундах)

    Methods:
        hit(direction)
            Если прошло необходимое врея с предыдущего выстрела,
             создает объект Bullet, летящий в одном из четырех направлений
    """
    def __init__(self, carrier):
        self.carrier = carrier
        self.damage = 30
        self.time, self.time_between_attack = datetime.datetime.now(), 0.5

    def hit(self, direction):
        if not self.wait(self.time, self.time_between_attack):
            return None

        w = self.carrier.x + self.carrier.width // 2
        h = self.carrier.y + self.carrier.height // 2
        velocity_x = velocity_y = 0
        if direction == 'right':
            velocity_x = 800
            w = self.carrier.x + self.carrier.width + 5
        elif direction == 'left':
            velocity_x = -800
            w = self.carrier.x - 10
        elif direction == 'up':
            velocity_y = -800
            h = self.carrier.y - 10
        elif direction == 'down':
            velocity_y = 800
            h = self.carrier.y + self.carrier.height + 5
        else:
            return None

        Bullet(w, h, 10, 10, velocity_x, velocity_y, self.damage,
               ['Dangerous for enemy', 'Indestructible', 'One hit'], ['Dangerous for enemy'], self)

        self.time = datetime.datetime.now()

    def wait(self, time, delay):
        if datetime.datetime.now() - time >= datetime.timedelta(seconds=delay):
            return True


class MachineGun(Gun):
    """
    Класс автомата, стреляющего часто, но слабыми патронами

    Attributes:
        Атрибуты класса Gun

    Methods:
        hit(direction)
            То же что и метод hit класса Gun
    """
    def __init__(self, carrier):
        Gun.__init__(self, carrier)
        self.time_between_attack = 0.2
        self.damage = 5

    def hit(self, direction):
        if not self.wait(self.time, self.time_between_attack):
            return None

        w = self.carrier.x + self.carrier.width // 2
        h = self.carrier.y + self.carrier.height // 2
        velocity_x = velocity_y = 0
        if direction == 'right':
            velocity_x = 800
            w = self.carrier.x + self.carrier.width + 5
        elif direction == 'left':
            velocity_x = -800
            w = self.carrier.x - 10
        elif direction == 'up':
            velocity_y = -800
            h = self.carrier.y - 10
        elif direction == 'down':
            velocity_y = 800
            h = self.carrier.y + self.carrier.height + 5
        else:
            return None

        Bullet(w, h, 5, 5, velocity_x, velocity_y, self.damage,
                                   ['Dangerous for enemy', 'Indestructible', 'One hit'], ['Dangerous for enemy'], self)

        self.time = datetime.datetime.now()


class Rifle(Gun):
    """
        Класс винтовки, стреляющей редко, но сильными патронами

        Attributes:
            Атрибуты класса Gun

        Methods:
            hit(direction)
                То же что и метод hit класса Gun
        """
    def __init__(self, carrier):
        Gun.__init__(self, carrier)
        self.time_between_attack = 1
        self.damage = 20

    def hit(self, direction='right'):
        if not self.wait(self.time, self.time_between_attack):
            return None

        w = self.carrier.x + self.carrier.width // 2
        h = self.carrier.y + self.carrier.height // 2
        velocity_x = velocity_y = 0
        if direction == 'right':
            velocity_x = 2000
            w = self.carrier.x + self.carrier.width + 5
        elif direction == 'left':
            velocity_x = -2000
            w = self.carrier.x - 10
        elif direction == 'up':
            velocity_y = -2000
            h = self.carrier.y - 10
        elif direction == 'down':
            velocity_y = 2000
            h = self.carrier.y + self.carrier.height + 5
        else:
            return None

        Bullet(w, h, 7, 7, velocity_x, velocity_y, self.damage,
                                   ['Dangerous for enemy', 'Indestructible', 'One hit'], ['Dangerous for enemy'], self)

        self.time = datetime.datetime.now()


class Bullet(pygame.sprite.Sprite, GameObject):
    """
    Пуля, летящяя по прямой с константной скоростью

    Attributes:
        Аттрибуты класса GameObject
        velocity_x: float
            Скорость объекта по оси абсцисс
        velocity_y: float
            Скорость объекта по оси ординат
        time_of_live: float
            Максимальное время, которое может существовать объект (в секундах)
        carrier_gun: GameObject
            Объект, носитель оружия, из которого был произведен выстрел данной пули

    Methods:
        update(tick=0)
            Если объект стелкнулся с коллизией с тегом Wall или
            прошло время максимальное время жизни уничтожает объект
            Сдвигает объект по по горизнтали и вертикали
        _kill()
            Уничтожает объект
    """
    def __init__(self, x=0, y=0, width=0, height=0, velocity_x=0, velocity_y=0, damage=0,
                 tags=None, tags_of_collision=None, carrier_gun=None):
        if tags is None:
            tags = []
        if tags_of_collision is None:
            tags_of_collision = []
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, width, height)
        self.image = pygame.Surface((width, height),
                                    pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, [252, 247, 190],
                         (0, 0, width, height))

        self.tags = tags
        self.tags.append('Bullet')
        self.collision.tags = tags_of_collision

        self.velocity_x, self.velocity_y = velocity_x, velocity_y
        self.damage = damage
        self.time_of_live = 1
        self.carrier_gun = carrier_gun

    def update(self, tick=0):
        self.collision.update()
        if datetime.datetime.now().second - self.time.second > self.time_of_live or self.collision.can_move_collisions(
                needed_tags_of_collision=['Wall']):
            self._kill()

        self.x += self.velocity_x * tick
        self.y += self.velocity_y * tick
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def _kill(self):
        if self.carrier_gun:
            global EVENTS
            EVENTS.append(Event(tags=['Bullet death', 'Bullet of character'],
                                x=self.x + self.width // 2, y=self.y + self.height // 2))
        self.collision.kill()
        self.kill()


class SuperBullet(pygame.sprite.Sprite, GameObject):
    """
        Пуля, изменяющая свое направление, но с константной скоростью

        Attributes:
            Аттрибуты класса GameObject
            velocity_x: float
                Скорость объекта по оси абсцисс
            velocity_y: float
                Скорость объекта по оси ординат
            velocity: float
                Векторная скорость пули
            time_of_live: float
                Максимальное время, которое может существовать объект (в секундах)
            carrier_gun: GameObject
                Объект, носитель оружия, из которого был произведен выстрел данной пули
            target: GameObject
                Объект, который направляется пуля
            delta_velocity: float
                Длина вектор на который пуля меняет свою траекторию

        Methods:
            update(tick=0)
                Если объект стелкнулся с коллизией с тегом Wall или
                прошло время максимальное время жизни уничтожает объект
                Прибавляет к вектору скорости пули ветор с модулем равным delta_velocity
                и я направлением из координат объекта до координат target
                Нормализует вектор скорости объекта
                Сдвигает объект по по горизнтали и вертикали
            _kill()
                Уничтожает объект
        """
    def __init__(self, target, x=0, y=0, width=0, height=0, velocity_x=0, velocity_y=0,
                 delta_velocity=0, damage=0, tags=None, tags_of_collision=None):
        if tags is None:
            tags = []
        if tags_of_collision is None:
            tags_of_collision = []
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, width, height)
        self.image = pygame.Surface((width, height),
                                    pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, [252, 247, 190],
                         (0, 0, width, height))

        self.tags = tags
        self.tags.append('Bullet')
        self.collision.tags = tags_of_collision

        self.damage = 10
        self.velocity_x, self.velocity_y = velocity_x, velocity_y
        self.velocity = math.sqrt(velocity_x ** 2 + velocity_y ** 2)

        self.start_time = datetime.datetime.now()
        self.damage = damage
        self.target, self.delta_velocity = target, delta_velocity

    def update(self, tick=0):
        self.collision.update()
        if datetime.datetime.now().second - self.start_time.second > 3 or self.collision.can_move_collisions(
                needed_tags_of_collision=['Wall']):
            self._kill()
        c = (self.distance_x(self.target) * self.delta_velocity / self.distance(self.target),
             self.distance_y(self.target) * self.delta_velocity / self.distance(self.target))
        self.velocity_x += c[0]
        self.velocity_y += c[1]
        size_of_vector = math.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2)

        self.velocity_x *= self.velocity / size_of_vector
        self.velocity_y *= self.velocity / size_of_vector

        self.x += self.velocity_x * tick
        self.y += self.velocity_y * tick
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def distance(self, target):
        return math.sqrt(self.distance_x(target) ** 2 + self.distance_y(target) ** 2)

    def distance_x(self, target):
        return target.x + target.width // 2 - (self.x + self.width // 2)

    def distance_y(self, target):
        return target.y + target.height // 2 - (self.y + self.height // 2)

    def _kill(self):
        self.collision.kill()
        self.kill()


class InertBullet(pygame.sprite.Sprite, GameObject):
    """
            Пуля, изменяющая свое направление и с меняющееся скоростью

            Attributes:
                Аттрибуты класса GameObject
                velocity_x: float
                    Скорость объекта по оси абсцисс
                velocity_y: float
                    Скорость объекта по оси ординат
                velocity: float
                    Векторная скорость пули
                time_of_live: float
                    Максимальное время, которое может существовать объект (в секундах)
                carrier_gun: GameObject
                    Объект, носитель оружия, из которого был произведен выстрел данной пули
                target: GameObject
                    Объект, который направляется пуля
                delta_velocity: float
                    Длина вектор на который пуля меняет свою траекторию

            Methods:
                update(tick=0)
                    Если объект стелкнулся с коллизией с тегом Wall или
                    прошло время максимальное время жизни уничтожает объект
                    Прибавляет к вектору скорости пули ветор с модулем равным delta_velocity
                    и я направлением из координат объекта до координат target
                    Сдвигает объект по по горизнтали и вертикали
                _kill()
                    Уничтожает объект
            """
    def __init__(self, target, x=0, y=0, width=0, height=0, velocity_x=0, velocity_y=0,
                 delta_velocity=0, damage=0, tags=None, tags_of_collision=None):
        if tags is None:
            tags = []
        if tags_of_collision is None:
            tags_of_collision = []
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, width, height)
        self.image = pygame.Surface((width, height),
                                    pygame.SRCALPHA, 32)
        pygame.draw.rect(self.image, [252, 247, 190],
                         (0, 0, width, height))

        self.tags = tags
        self.tags.append('Bullet')
        self.collision.tags = tags_of_collision

        self.damage = 10
        self.velocity_x, self.velocity_y = velocity_x, velocity_y
        self.velocity = math.sqrt(velocity_x ** 2 + velocity_y ** 2)

        self.start_time = datetime.datetime.now()
        self.damage = damage
        self.target, self.delta_velocity = target, delta_velocity

    def update(self, tick=0):
        self.collision.update()
        if datetime.datetime.now().second - self.start_time.second > 3 or self.collision.can_move_collisions(
                needed_tags_of_collision=['Wall']):
            self.collision.kill()
            self.kill()
        c = (self.distance_x(self.target) * self.delta_velocity / self.distance(self.target),
             self.distance_y(self.target) * self.delta_velocity / self.distance(self.target))

        self.velocity_x += c[0]
        self.velocity_y += c[1]

        self.x += self.velocity_x * tick
        self.y += self.velocity_y * tick
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def distance(self, target):
        return math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)

    def distance_x(self, target):
        return target.x - self.x

    def distance_y(self, target):
        return target.y - self.y


class Character(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y, width, height, *groups):
        pygame.sprite.Sprite.__init__(self, groups)
        GameObject.__init__(self, x, y, width, height)
        self.image = load_image('Smile.png', [24, 28, 25])

        self.weapon = MachineGun(self)

        self.v = 500

        self.tags = ['Character', 'Indestructible']
        self.hp = 100
        self.coins = 0
        self.time, self.time_between_enemy_attack = datetime.datetime.now(), 0.5

        self.items = [Nothing(), Nothing(), Nothing()]
        for item in self.items:
            item.init(self)

        self.font = pygame.font.Font(None, 35)

        # self.collision.width, self.collision.height = 0, 0

    def update(self, tick=0):
        for item in self.items:
            item.update()

        text = self.font.render('Hp: ' + str(self.hp), True, [252, 247, 190])
        all_inscriptions['Character'] = [text, 10, 10, self.font.size('Hp: ' + str(self.hp))[0],
                                         self.font.size('Hp: ' + str(self.hp))[1]]
        all_inscriptions["Character's coins"] = [self.font.render(f'Coins: {self.coins}', True, [252, 247, 190]), 10, 50,
                                                 self.font.size(f'Coins: {self.coins}')[0],
                                                 self.font.size(f'Coins: {self.coins}')[1]]
        all_inscriptions['FPS: '] = [self.font.render(f'FPS: {int(clock.get_fps())}', True, [252, 247, 190]),
                                     CAMERA_WIDTH - 150, 10, self.font.size(f'FPS: {int(clock.get_fps())}')[0],
                                     self.font.size(f'FPS: {int(clock.get_fps())}')[1]]
        for index in range(len(self.items)):
            self.items[index].update()
            all_inscriptions['Item ' + str(index)] = [self.font.render(
                f'Item {index + 1}: {self.items[index].name}', True, [252, 247, 190]), 10,
                90 + index * (self.font.size('I')[1]),
                self.font.size(f'Item {index + 1}: {self.items[index].name}')[0],
                self.font.size(f'Item {index + 1}: {self.items[index].name}')[1]]

        for _collision in self.collision.can_move_collisions():
            if 'Dangerous' in _collision.tags:
                if self.wait(self.time, self.time_between_enemy_attack):
                    self.hp -= _collision.gameObject.damage
                    self.time = datetime.datetime.now()

                if 'One hit' in _collision.gameObject.tags:
                    _collision.gameObject._kill()

            if 'AidKid' in _collision.gameObject.tags:
                self.hp += _collision.gameObject.adding_of_hp
                _collision.gameObject._kill(True)

            if 'Dangerous' in _collision.tags or 'AidKid' in _collision.gameObject.tags:
                if self.hp >= 80:
                    self.image = load_image('Smile hp 80.png')
                elif self.hp >= 40:
                    self.image = load_image('Smile hp 40.png')
                elif self.hp >= 0:
                    self.image = load_image('Smile hp 0.png')

            if 'Coin' in _collision.gameObject.tags:
                self.coins += 1
                _collision.gameObject._kill()

            if 'Item spawner' in _collision.gameObject.tags:
                if _collision.gameObject.was_purchase or self.coins >= _collision.gameObject.item.price:
                    if not _collision.gameObject.was_purchase:
                        self.coins -= _collision.gameObject.item.price
                    _collision.gameObject.was_purchase = True
                    self.items[-1].take_off()
                    _item = _collision.gameObject.item
                    _collision.gameObject.item = self.items[-1]
                    for i in range(len(self.items) - 1, 0, -1):
                        self.items[i] = self.items[i - 1]

                    self.items[0] = _item
                    self.items[0].init(self)

                    _collision.gameObject.collision.width = 0
                    _collision.gameObject.collision.height = 0
                    _collision.gameObject.time = datetime.datetime.now()
                    _collision.gameObject.item.price = 0

        all_pressed = pygame.key.get_pressed()
        global EVENTS
        for i in range(len(EVENTS)):
            if 'Weapon change' in EVENTS[i].args['tags'] and\
                    'Character' in EVENTS[i].args['tags'] and self not in EVENTS[i].calls:
                self.weapon = EVENTS[i].args['weapon'](self)
                EVENTS[i].set_call(self)

        delta_x, delta_y = 0, 0
        if all_pressed[pygame.K_w]:
            delta_y = -self.v * tick
        if all_pressed[pygame.K_s]:
            delta_y = self.v * tick
        if all_pressed[pygame.K_a]:
            delta_x = -self.v * tick
        if all_pressed[pygame.K_d]:
            delta_x = self.v * tick

        self.move(delta_x, delta_y)

        if all_pressed[pygame.K_LEFT]:
            self.weapon.hit('left')
        elif all_pressed[pygame.K_RIGHT]:
            self.weapon.hit('right')
        elif all_pressed[pygame.K_UP]:
            self.weapon.hit('up')
        elif all_pressed[pygame.K_DOWN]:
            self.weapon.hit('down')

        self.collision.update()

        if self.hp <= 0:
            font = pygame.font.Font(None, 250)
            text = font.render('Game over', True, [252, 247, 190])
            all_inscriptions.clear()
            all_inscriptions['Game over'] = [text, (CAMERA_WIDTH - font.size(
                'Game over')[0]) // 2, (CAMERA_HEIGHT - font.size('Game over')[1]) // 2,
                                             font.size('Game over')[0], font.size('Game over')[1]]

            self.collision.kill()
            self.kill()

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, delta_x, delta_y):
        if not self.collision.can_move_collisions(delta_x, delta_y, [], ['Wall']):
            self.x += delta_x
            self.y += delta_y

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


class Platform(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y, width, height, image, tags_of_game_object=None, tags_of_collision=None):
        if tags_of_game_object is None:
            tags_of_game_object = []
        if tags_of_collision is None:
            tags_of_collision = []
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, width, height)
        if image is None:
            self.image = pygame.Surface((width, height),
                                        pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, GameObject.COLOR,
                             (0, 0, width, height))
        else:
            self.image = load_image(image, GameObject.FON_COLOR)

        self.tags = tags_of_game_object
        self.collision.tags = tags_of_collision
        self.damage = 10

    def update(self, tick=0):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.collision.update()

    def _kill(self):
        self.collision.kill()
        self.kill()


class PatternPlatform:
    """
        Класс, создающий объект Enemy1

        Attributes:
            x: float
                Позиция объекта по оси абсцисс, если бы игрок находился по центру клетки, к которой располагается объект
            y: float
                Позиция объекта по оси ординат, если бы игрок находился по центру клетки, к которой располагается объект
            width: float
                Ширины объекта
            height: float
                Высота объекта
            color: list
                Цвет в виде RGB
            tags_of_game_object: list
                Список тегов объекта
            tags_of_collision: list
                Список тегов коллизии объекта

        Methods:
            init(delta_x, delta_y)
                Создает объект Platform
        """
    def __init__(self, x, y, width, height, image, tags_of_game_object=None, tags_of_collision=None):
        if tags_of_game_object is None:
            tags_of_game_object = []
        if tags_of_collision is None:
            tags_of_collision = []

        self.x, self.y = x, y
        self.width, self.height = width, height
        self.image = image
        self.tags_of_game_object = tags_of_game_object
        self.tags_of_collision = tags_of_collision

    def init(self, delta_x=0, delta_y=0):
        Platform(self.x + (CAMERA_WIDTH - WIDTH) // 2 - camera.x + WIDTH * delta_x,
                 self.y + (CAMERA_HEIGHT - HEIGHT) // 2 - camera.y - HEIGHT * delta_y,
                 self.width, self.height, self.image, self.tags_of_game_object, self.tags_of_collision)


class AidKid(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, 50, 50)

        self.image = load_image('Aid kid.png', [24, 28, 25])

        self.adding_of_hp = 10
        self.tags = ['AidKid']

        self.x_of_cell = self.y_of_cell = None

    def update(self, tick=0):
        self.collision.update()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def kill_object(self):
        self.collision.kill()
        self.kill()

    def _kill(self, forever=False):
        if forever and self.x_of_cell is not None and self.y_of_cell is not None:
            for index in range(len(world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                                   world_generator.character_cell[1] + self.y_of_cell])):
                if type(world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                            world_generator.character_cell[1] + self.y_of_cell][index][0]) == PatternAidKid and\
                        world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                            world_generator.character_cell[1] + self.y_of_cell][index][1] == 1:
                    world_generator.cells[world_generator.character_cell[0] + self.x_of_cell][
                        world_generator.character_cell[1] + self.y_of_cell].pop(index)
                    break

        self.collision.kill()
        self.kill()


class PatternAidKid:
    """
        Класс, создающий объект Enemy1

        Attributes:
            x: float
                Позиция объекта по оси абсцисс, если бы игрок находился по центру клетки, к которой располагается объект
            y: float
                Позиция объекта по оси ординат, если бы игрок находился по центру клетки, к которой располагается объект

        Methods:
            init(delta_x, delta_y)
                Создает объект AidKid
        """
    def __init__(self, x, y):
        self.x, self.y = x, y

    def init(self, delta_x, delta_y):
        aid_kid = AidKid(self.x + (CAMERA_WIDTH - WIDTH) // 2 - camera.x + WIDTH * delta_x,
                         self.y + (CAMERA_HEIGHT - HEIGHT) // 2 - camera.y - HEIGHT * delta_y)
        aid_kid.x_of_cell = delta_x
        aid_kid.y_of_cell = delta_x


class Spikes(pygame.sprite.Sprite, GameObject):
    def __init__(self, x, y, width, height, image, start_delay, delay_to_life, delay_to_death):
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, width, height)

        self.image = load_image(image, GameObject.FON_COLOR)

        self.damage = 10

        self.delay_to_life, self.delay_to_death = delay_to_life, delay_to_death
        self.time = datetime.datetime.now()
        self.delay = start_delay
        self.active = False
        self.image.set_alpha(0)
        if self.delay_to_life == 0 and self.delay_to_death == 0:
            self.image.set_alpha(255)
            self.tags = self.collision.tags = ['Dangerous']
            self.active = True
            self.delay = self.delay_to_death

    def update(self, tick=0):
        if not (self.delay_to_life == 0 and self.delay_to_death == 0):
            self.wait(self.delay, self.active)

        self.collision.update()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def wait(self, delay, active):
        if datetime.datetime.now() - self.time >= datetime.timedelta(seconds=delay):
            if not active:
                self.image.set_alpha(255)
                self.tags = self.collision.tags = ['Dangerous']
                self.active = True
                self.delay = self.delay_to_death
            else:
                self.image.set_alpha(0)
                self.tags = self.collision.tags = []
                self.active = False
                self.delay = self.delay_to_life

            self.time = datetime.datetime.now()

    def _kill(self):
        self.collision.kill()
        self.kill()


class PatternSpikes:
    """
        Класс, создающий объект Enemy1

        Attributes:
            x: float
                Позиция объекта по оси абсцисс, если бы игрок находился по центру клетки, к которой располагается объект
            y: float
                Позиция объекта по оси ординат, если бы игрок находился по центру клетки, к которой располагается объект
            width: float
                Ширины объекта
            height: float
                Высота объекта
            start_delay: float
                Время ожидание в начале
            delay_to_life: float
                Время, в течение которого объект выключен
            delay_to_death: float
                Время, в течение которого объект включен

        Methods:
            init(delta_x, delta_y)
                Создает объект Spikes
        """
    def __init__(self, x, y, width, height, image, start_delay=0, delay_to_life=0, delay_to_death=0):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.image = image
        self.start_delay, self.delay_to_life, self.delay_to_death = start_delay, delay_to_life, delay_to_death

    def init(self, delta_x, delta_y):
        Spikes(self.x + (CAMERA_WIDTH - WIDTH) // 2 - camera.x + WIDTH * delta_x,
               self.y + (CAMERA_HEIGHT - HEIGHT) // 2 - camera.y - HEIGHT * delta_y, self.width, self.height,
               self.image, self.start_delay, self.delay_to_life, self.delay_to_death)


class Coin(pygame.sprite.Sprite, GameObject):
    """
    Класс монеты, дающей деньги на покупку прдметов

    Attributes:
        Атрибуты GameObject
        time_of_live: float
            Время, в течение которого объект существует

    Methods:
        update(tick=0)
            Уничтожает объект, если прошло с создания времени больше чем time_of_live
        kill()
            Уничтожает объект
    """
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, 10, 10)

        self.image = load_image('Coin.png', [24, 28, 25])

        self.tags = ['Coin', 'Indestructible']

        self.time_of_live = 5

    def update(self, tick=0):
        self.collision.update()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if datetime.datetime.now() - self.time > datetime.timedelta(seconds=self.time_of_live):
            self._kill()

    def _kill(self):
        self.collision.kill()
        self.kill()


class Nothing(Item):
    """
    Класс отсутствия предмета

    Attributes:
        Атрибуты Item

    Methods:
        Методы Item
    """
    def __init__(self):
        self.price = 0
        self.name = 'Nothing'

    def init(self, carrier):
        super().__init__(self.name, self.price, carrier)


class Accelerator(Item):
    """
        Класс предмета, ускоряющего носителья

        Attributes:
            Атрибуты Item
            delta_velocity: float
                Изменения скорости носителя

        Methods:
            Методы Item
            init(carrier)
                Активирует предмет и добавляет delta_velocity к скорости носителя
            take_off()
                Вычитает из скорости носителя delta_velocity
        """
    def __init__(self, price):
        self.price = price
        self.name = 'Accelerator'
        self.delta_velocity = 200

    def init(self, carrier):
        super().__init__(self.name, self.price, carrier)
        self.carrier.v += self.delta_velocity

    def take_off(self):
        self.carrier.v -= self.delta_velocity


class DamageBooster(Item):
    """
        Класс предмета, увеличивающий урон

        Attributes:
            Атрибуты Item
            delta_damage: float
                Изменение урона оружия носителя

        Methods:
            Методы Item
            update(carrier)
                Активирует предмет и прибавляет к урону оружия носителя delta_damage
            take_off()
                Вычитает delta_damage из урона оружия носителя
        """
    def __init__(self, price):
        self.price = price
        self.name = 'Damage booster'
        self.delta_damage = 5

    def init(self, carrier):
        super().__init__(self.name, self.price, carrier)
        self.carrier.weapon.damage += self.delta_damage

    def take_off(self):
        self.carrier.weapon.damage -= self.delta_damage


class Arsonist(Item):
    """
    Класс предмета, создающего Fire на месте игрока

    Attributes:
        Атрибуты Item
        time: deltatime.deltatime
            Время создания последего Fire
        delay: float
            Время, которое должно пройти с последнего создания Fire, чтобы создать Fire

    Methods:
        Методы Item
        update(carrier)
            Активирует предмет
        update()
            Если с последнего создания Fire прошло больше времени чем delay, создает Fire на месте носителя
    """
    def __init__(self, price):
        self.price = price
        self.name = "Arsonist"
        self.time = datetime.datetime.now()
        self.delay = 0.1

    def init(self, carrier):
        super().__init__(self.name, self.price, carrier)

    def update(self):
        if self.wait(self.time, self.delay):
            Fire(self.carrier.x + self.carrier.width // 2 - 25, self.carrier.y + self.carrier.height // 2 - 25,
                 3, ['Dangerous for enemy'])
            self.time = datetime.datetime.now()

    def wait(self, time, delay):
        if datetime.datetime.now() - time >= datetime.timedelta(seconds=delay):
            return True


class BulletPyro(Item):
    """
        Класс предмета, создающий Fire при уничтожении пули на координатах этой пули

        Attributes:
            Атрибуты Item

        Methods:
            Методы Item
            update(carrier)
                Активирует предмет
            update()
                Если пуля, выпущенная носителем уничтожается, создыет Fire на координатах пули
        """
    def __init__(self, price):
        self.price = price
        self.name = "BulletPyro"

    def init(self, carrier):
        super().__init__(self.name, self.price, carrier)

    def update(self):
        global EVENTS
        for i in range(len(EVENTS)):
            if 'Bullet death' in EVENTS[i].args['tags'] and 'Bullet of character' in EVENTS[i].args['tags']\
                    and self.carrier not in EVENTS[i].calls:
                Fire(EVENTS[i].args['x'] - 25, EVENTS[i].args['y'] - 25, 3, ['Dangerous for enemy'])
                EVENTS[i].set_call(self.carrier)


class Shrapnel(Item):
    def __init__(self, price):
        self.price = price
        self.name = "Shrapnel"

    def init(self, carrier):
        super().__init__(self.name, self.price, carrier)

    def update(self):
        global EVENTS
        for i in range(len(EVENTS)):
            if 'Bullet death' in EVENTS[i].args['tags'] and 'Bullet of character' in EVENTS[i].args['tags']\
                    and self.carrier not in EVENTS[i].calls:
                Bullet(EVENTS[i].args['x'] + 10, EVENTS[i].args['y'], 10, 10, 500, 0, 10,
                       ['Dangerous for enemy', 'Indestructible', 'One hit'], ['Dangerous for enemy'])
                Bullet(EVENTS[i].args['x'] - 10, EVENTS[i].args['y'], 10, 10, -500, 0, 10,
                       ['Dangerous for enemy', 'Indestructible', 'One hit'], ['Dangerous for enemy'])
                Bullet(EVENTS[i].args['x'], EVENTS[i].args['y'] + 10, 10, 10, 0, 500, 10,
                       ['Dangerous for enemy', 'Indestructible', 'One hit'], ['Dangerous for enemy'])
                Bullet(EVENTS[i].args['x'], EVENTS[i].args['y'] - 10, 10, 10, 0, -500, 10,
                       ['Dangerous for enemy', 'Indestructible', 'One hit'], ['Dangerous for enemy'])
                EVENTS[i].set_call(self.carrier)


class Fire(pygame.sprite.Sprite, GameObject):
    """
    Круг огня

    Attributes:
        Атрибуты GameObject
        time_of_live: float
            Время, в течение котого объект существует

    Methods:
        update(tick=0)
            Уничтожает объект, если прошло время time_of_live
        _kill()
            Уничтожает объект
    """
    def __init__(self, x, y, time_of_life, tags):
        pygame.sprite.Sprite.__init__(self, all_gameObjects)
        GameObject.__init__(self, x, y, 50, 50)

        self.image = load_image('Fire.png', [24, 28, 25])

        self.tags = tags + ['Indestructible']
        self.collision.tags = tags
        self.damage = 1

        self.time_of_life = time_of_life

    def update(self, tick):
        if self.wait(self.time, self.time_of_life):
            self._kill()

        self.collision.update()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def _kill(self):
        self.collision.kill()
        self.kill()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)

    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()

    return image


def print_inscriptions():
    for inscriptions in all_inscriptions.values():
        pygame.draw.rect(screen, (24, 28, 25), (inscriptions[1], inscriptions[2],
                                                inscriptions[3] - 1, inscriptions[4]))
        screen.blit(inscriptions[0], [inscriptions[1], inscriptions[2]])


def load_fon(intro_text):
    pass
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color(GameObject.COLOR))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


con = sqlite3.connect('data/Pygame_DB.db')
cur = con.cursor()
pygame.init()

data = cur.execute("""SELECT * FROM passing""").fetchall()
_id = cur.execute("""SELECT id FROM passing""").fetchall()[-1][0] + 1
_datetime = str(datetime.datetime.now())
KILLS = 0

SIZE = WIDTH, HEIGHT = 2000, 1000
CAMERA_WIDTH, CAMERA_HEIGHT = 1000, 600
screen = pygame.display.set_mode([CAMERA_WIDTH, CAMERA_HEIGHT])

intro_text_1 = ["<Название проекта>", "",
                "Нажмите Enter для начала игры",
                "Нажмите Tab для просмотра статистики",
                "Нажмите Control для просмотра статистики",
                "Нажмите Escape, чтобы выйти"]
intro_text_2 = ["Статистика:",
                "    Последнее прохождение:",
                "        Дата прохождения: " + data[-1][1],
                "        Количество убийств: " + str(data[-1][2]),
                "        Предметы: " + ', '.join(data[-1][3:6]),
                "        Оставшиеся здоровье: " + str(data[-1][6]),
                "        Максимальная дистанция, на которую отошел игрок: " + str(data[-1][7]),
                "    Средние покозатели:",
                "        Среднее количество убийств: " + str(int(sum([passing[2] for passing in data]) / len(data))),
                "        Среднее оставшиеся здоровье: " + str(int(sum([passing[6] for passing in data]) / len(data))),
                "        Наиболее часто выбираемый предмет: " + max(Counter(np.concatenate([
                    passing[3:6] for passing in data], axis=None)).items(), key=lambda p: p[::-1])[0],
                "        Среднее расстояние от начала: " + str(int(sum([passing[7] for passing in data]) / len(data))),
                "    Лучшие результаты:",
                "        Наибольшее количество убийств: " + str(max([passing[2] for passing in data])),
                "        Наибольшее оставшиеся здоровье: " + str(max([passing[6] for passing in data])),
                "        Наибольшее расстояние от начала: " + str(max([passing[7] for passing in data])),
                "Чтобы начать игру нажмите Enter",
                "Нажмите Control для просмотра статистики",
                "Нажмите Escape, чтобы выйти"]
intro_text_3 = ["Правила:", "",
                "   Для перемещения используйте WASD",
                "   Для стрельбы используйте стрелочки",
                "   Для того, чтобы сменить оружие нажимайте на tab",
                "   В левом верхнем углу будет написано соатвшиеся здоровье и носимые предметы",
                "   Если ваше здоровье опустится до 0, вы проиграете", "",
                "Нажмите Enter, чтобы начать игру",
                "Нажмите Tab, чтобы посмотреть статистику",
                "Нажмите Escape, чтобы выйти"]
intro_text = intro_text_1
load_fon(intro_text)

images = list(map(lambda x: load_image(x), ['Turret 1.png', 'Turret 2.png', 'Spike.png',
                                            'Item spawner.png', 'Fire.png', 'Aid kid.png']))
size_x = size_y = 50
cells = [[None for j in range(CAMERA_WIDTH // size_x)] for i in range(CAMERA_HEIGHT // size_y)]
cells[5][5] = cells[5][6] = cells[5][7] = cells[4][7] = cells[3][6] = random.choice(images)
time = datetime.datetime.now()
running = True
while running:
    if datetime.datetime.now() - time > datetime.timedelta(seconds=0.2):
        time = datetime.datetime.now()
        screen.fill(GameObject.FON_COLOR)
        new_cells = [[j for j in i] for i in cells]
        for i in range(len(cells)):
            for j in range(len(cells[0])):
                total = 0
                a = [[-1, -1], [0, -1], [1, -1], [-1, -0], [1, 0], [-1, 1], [0, 1], [1, 1]]
                for x, y in a:
                    if cells[(i + x) % len(cells)][(j + y) % len(cells[0])]:
                        total += 1
                if cells[i][j] is None and total == 3:
                    new_cells[i][j] = random.choice(images)
                if cells[i][j] and not (total == 3 or total == 2):
                    new_cells[i][j] = None
        for y in range(len(new_cells)):
            for x in range(len(new_cells[0])):
                if new_cells[y][x]:
                    screen.blit(new_cells[y][x], [x * size_x, y * size_y])

        cells = [[j for j in i] for i in new_cells]
        load_fon(intro_text)
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            con.close()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            intro_text = intro_text_2
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL):
            intro_text = intro_text_3

        if event.type == pygame.MOUSEBUTTONDOWN:
            cells[event.pos[1] // size_y][event.pos[0] // size_x] = random.choice(images)
            screen.blit(cells[event.pos[1] // size_y][event.pos[0] // size_x],
                        [event.pos[0] // size_x * size_x, event.pos[1] // size_y * size_y])
            pygame.display.flip()

all_gameObjects = pygame.sprite.Group()
all_collisions = pygame.sprite.Group()
all_inscriptions = {}
number_of_gameobjects = 0

character = Character(CAMERA_WIDTH // 2 - 39, CAMERA_HEIGHT // 2 - 50, 75, 75, all_gameObjects)
camera = Camera()
clock = pygame.time.Clock()
world_generator = WorldGenerator(camera)
EVENTS = []

weapons_of_character = [Gun, MachineGun, Rifle]

running = True
while running:
    screen.fill([24, 28, 25])
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ItemSpawner(event.pos[0], event.pos[1])

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            AidKid(event.pos[0], event.pos[1])

        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            EVENTS.append(Event(tags=['Weapon change', 'Character'], weapon=weapons_of_character[
                (weapons_of_character.index(type(character.weapon)) + 1) % len(weapons_of_character)]))

    fps = clock.tick() / 1000

    all_gameObjects.update(fps)

    camera.update(character)
    # print(character.x)
    world_generator.update()

    all_gameObjects.draw(screen)
    print_inscriptions()
    for i in range(len(EVENTS)):
        EVENTS[i].apply()

    pygame.display.flip()

cur.execute(f"""INSERT INTO passing
                (id, datetime, kills, item_1, item_2, item_3, hp, max_distance)
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?);""", (_id, _datetime, KILLS, character.items[0].name,
                                               character.items[1].name, character.items[2].name,
                                               character.hp, len(world_generator.cells) - 3)).fetchall()
con.commit()
con.close()
