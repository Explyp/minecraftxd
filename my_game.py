import pygame
import random
import sys

from django.utils.termcolors import background
from numpy.core.numeric import True_


class Steave:
    hp = 20
    damage = 1
    shift_speed = 5.6
    normal_speed = 4.3


class friendly_mob:
    def __init__(self, hp, speed):
        self.hp = hp
        self.speed = speed


class enemy_mob:
    def __init__(self, hp, damage, speed):
        self.hp = hp
        self.damage = damage
        self.speed = speed


class neutral_mob:
    def __init__(self, hp, damage, speed):
        self.hp = hp
        self.damage = damage
        self.speed = speed


# cнизу ток парачка френдли мобов

class pig(friendly_mob):
    def __init__(self):
        super().__init__(10, 2)  # наследование хар-ки от родительского, и заполение своими


class cow(friendly_mob):
    def __init__(self):
        super().__init__(10, 2)


class chiken(friendly_mob):
    def __init__(self):
        super().__init__(4, 2)


class sheep(friendly_mob):
    def __init__(self):
        super().__init__(10, 2)


class horse(friendly_mob):
    def __init__(self):
        super().__init__(15, 4)


# вражеские мобы

class zombie(enemy_mob):
    def __init__(self):
        super().__init__(20, 2, 2)


class skeleton(enemy_mob):
    def __init__(self):
        super().__init__(20, 2, 2)
        self.strenght = 1

    def strength(self):
        self.strenght = random.randint(1, 3)  # типа сила натяжения лука поняли да, будет множителем для урона
        return self.strenght


class Creeping_Death(enemy_mob):
    def __init__(self):
        super().__init__(20, 1, 2)
        self.damage_boom = random.randint(11, 32)  # мне впадлу прописывать расстояния, поэтому взрыв рандомный

    def boom(self):
        self.hp = 0
        return self.hp


# нейтральные мобы

class Wherever_I_May_Roam(neutral_mob):  # типа эндермен
    def __init__(self):
        super().__init__(40, 0, 3)
        self.eyes = False

    def we_met_eyes(self):  # ну типа мы посмотрели в глаза или он в наши
        self.eyes = True
        self.damage = 4
        return self.eyes, self.damage


class bee(neutral_mob):
    def __init__(self):
        super().__init__(10, 2, 2)
        self.poison_damage = 1


class iron_golem(neutral_mob):
    def __init__(self):
        super().__init__(100, 7, 3)


# оформление
class boxText:
    def __init__(self, x, y, wight, height):
        self.rect = pygame.Rect(x, y, wight,
                                height)  # как я понял х и у это координаты верхнего левого угла,а дальше размер
        self.text = ""  # полный текст
        self.display_text = ""  # то что уже напечаталось
        self.font = pygame.font.Font("arialmt.ttf", 28)
        self.flag_finished = False
        self.index = 0  # чтобы понимать какое кол-во слов выводится
        self.time_accum = 0.0
        self.cps = 12  # cкорость символа как я понял
        self.dot_time = 0.0  # таймер для точек
        self.dot_interval = 0.4  # как часто переключаются точки(сек)
        self.dot_count = 0  # 0..3 (0=нет точек,1="." и т.д)

    def set_text(self, text):
        self.text = text
        self.display_text = ""
        self.index = 0
        self.time_accum = 0.0
        self.flag_finished = False

    def update(self, dt):
        if not self.flag_finished:
            self.time_accum += dt
            chars_to_add = int(self.time_accum * self.cps)  # сколько букв можно написать за время
            if chars_to_add > 0:
                self.time_accum -= chars_to_add / self.cps
                self.index = min(len(self.text),
                                 self.index + chars_to_add)  # увеличиваем индекс напечатанья, но не вылазя за рамки слова, если я правильно понял
                self.display_text = self.text[:self.index]
                if self.index >= len(self.text):
                    self.flag_finished = True
        if self.flag_finished:
            self.dot_time += dt  # время кадра не особо понимаю как это работает
            if self.dot_time >= self.dot_interval:  # достаточно ли времени прошло для смены точек
                self.dot_time -= self.dot_interval  # cчетчик тип как песочные часы чтобы после смены одной точки было две
                self.dot_count = (self.dot_count + 1) % 4  # 0->1->2->3->0
        else:
            self.dot_time = 0
            self.dot_count = 0

    def draw(self, surf):
        temp = pygame.Surface((self.rect.width, self.rect.height),
                              pygame.SRCALPHA)  # временная поверхность размера прямоугольника
        pygame.draw.rect(temp, (20, 22, 30, 160), temp.get_rect(),
                         border_radius=10)  # RGBA: последний параметр — альфа (0 = прозрачный, 255 = непрозрачный)
        pygame.draw.rect(temp, (90, 95, 110, 255), temp.get_rect(), 2, border_radius=10)  # тут параметры рамки
        surf.blit(temp, self.rect.topleft)
        x = self.rect.x + 16
        y = self.rect.y + 16
        text_surface = self.font.render(self.display_text, True, (230, 230, 230))
        text_to_draw = self.display_text
        if self.flag_finished and self.dot_count:
            text_to_draw += " " + "." * self.dot_count
        text_surface = self.font.render(text_to_draw, True, (230, 230, 230))
        surf.blit(text_surface, (x, y))
    def skip_to_end(self):
        self.display_text = self.text
        self.index = len(self.text)
        self.flag_finished = True

pygame.init()
pygame.mixer.init()
pygame.font.init()
screen = pygame.display.set_mode((1200, 800))
box = boxText(100, 600, 1000, 150)
pygame.display.set_caption("live off lying")
clock = pygame.time.Clock()  # как я понял эта функция фпс
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (1200, 800))
pygame.mixer.music.load("a-gde-ia-i-kazhetsia-ia-v-mire-main-pokhozhe-na-to.mp3")
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.1)
box.set_text("oh nooo it is world of minecraft")
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not box.flag_finished:
                    box.skip_to_end()
    screen.blit(background, (0, 0))
    box.draw(screen)
    dt = clock.tick(144) / 1000.0
    box.update(dt)
    pygame.display.flip()
    box.update(dt)
    clock.tick(144)
