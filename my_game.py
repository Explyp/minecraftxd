import pygame
import random
import sys
import json



class Steve():
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
        friendly_mob.__init__(self, hp=10, speed=2)  # наследование хар-ки от родительского, и заполение своими


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


# сыны сюжета


# оформление
class boxText:
    def __init__(self, x, y, wight, height):
        self.rect = pygame.Rect(x, y, wight,
                                height)  # как я понял х и у это координаты верхнего левого угла,а дальше размер
        self.text = ""  # полный текст
        self.speaker = ""
        self.name_font = pygame.font.Font("arialmt.ttf", 24)
        self.display_text = ""  # то что уже напечаталось
        self.font = pygame.font.Font("arialmt.ttf", 28)
        self.flag_finished = False
        self.index = 0  # чтобы понимать какое кол-во слов выводится
        self.time_accum = 0.0
        self.cps = 12  # cкорость символа как я понял
        self.dot_time = 0.0  # таймер для точек
        self.dot_interval = 0.4  # как часто переключаются точки(сек)
        self.dot_count = 0  # 0..3 (0=нет точек,1="." и т.д)
        self.padding = 16  # отступы внутри бокса
        self.line_spacing = 6  # расстояние между строками (пиксели)

    def wrap_text(self, text, max_width):
        # поддержим ручные переносы \n
        words = text.replace("\n", " \n ").split(" ")

        lines, current = [], ""
        for w in words:
            if w == "\n":  # принудительный перевод строки
                lines.append(current)
                current = ""
                continue

            test = (current + " " + w).strip() if current else w
            if self.font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                # если слово само длиннее строки — режем по символам
                if self.font.size(w)[0] > max_width:
                    parts, cur = [], ""
                    for ch in w:
                        t = cur + ch
                        if self.font.size(t)[0] <= max_width:
                            cur = t
                        else:
                            parts.append(cur)
                            cur = ch
                    if cur:
                        parts.append(cur)
                    lines.extend(parts[:-1])
                    current = parts[-1] if parts else ""
                else:
                    current = w

        if current:
            lines.append(current)
        return lines

    def set_text(self, text, speaker=""):
        self.text = text
        self.display_text = ""
        self.index = 0
        self.time_accum = 0.0
        self.flag_finished = False
        self.speaker = speaker

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
        if self.speaker:
            name_surface = self.name_font.render(self.speaker, True, (255, 255, 160))
            # рисуем имя в верхнем левом углу рамки, с небольшим отступом
            surf.blit(name_surface, (self.rect.x + self.padding, self.rect.y - name_surface.get_height() - 4))
        text_to_draw = self.display_text
        if self.flag_finished and self.dot_count:
            text_to_draw += " " + "." * self.dot_count
        max_widht = self.rect.width - 2 * self.padding
        lines = self.wrap_text(text_to_draw, max_widht)
        x = self.rect.x + self.padding
        y = self.rect.y + self.padding
        for line in lines:
            surface = self.font.render(line, True, (230, 230, 230))
            surf.blit(surface, (x, y))
            y += surface.get_height() + self.line_spacing

    def skip_to_end(self):
        self.display_text = self.text
        self.index = len(self.text)
        self.flag_finished = True


# json
def load_scene_from_json(path, scene_id):
    # Читаем JSON и возвращаем:
    # -scene_meta: словарь метаданных сцены (фон, музыка, громкость, масштаб)
    # -scene_lines: список кортежей (text, speaker)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scene_obj = data.get("scenes", {}).get(scene_id, {})
    meta = scene_obj.get("meta", {})  # может не быть — тогда пусто
    items = scene_obj.get("lines", [])  # массив реплик

    # превращаем в [(text, speaker), ...]
    lines = []
    for it in items:
        text = it.get("text", "")
        speaker = it.get("speaker", "")
        lines.append((text, speaker))

    return meta, lines


def apply_scene_meta(snece_meta):
    global background
    bg_path = scene_meta.get("background")
    if bg_path:
        background = pygame.image.load(bg_path).convert()
    else:
        background = pygame.Surface((1200, 800))
        background.fill((10, 12, 18))
    music_path = scene_meta.get("music")
    if music_path:
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(float(snece_meta.get("music_volume")))
        except Exception as e:
            print("не удалось загрузить музыку:", e)

def switch_scene(next_id):
    """
       Переходим в другую сцену:
         - перечитываем JSON
         - обновляем фон/музыку
         - сбрасываем индекс реплики
         - запускаем первую реплику новой сцены
       """
    global current_scene_id, scene_meta, scene_lines, current_line
    current_scene_id = next_id
    scene_meta, scene_lines = load_scene_from_json("scenes.json", current_scene_id)
    apply_scene_meta(scene_meta)
    current_line = 0
    if scene_lines:
        box.set_text(scene_lines[current_line][0], scene_lines[current_line][1])




pygame.init()
pygame.mixer.init()
pygame.font.init()
steve = Steve()
screen = pygame.display.set_mode((1200, 800))

# Вся информация о сцене теперь в JSON:
current_scene_id = "The_awaking"
scene_meta, scene_lines = load_scene_from_json("scenes.json", current_scene_id)
apply_scene_meta(scene_meta)
current_line = 0
box = boxText(100, 600, 1000, 150)
box.set_text(scene_lines[current_line][0], scene_lines[current_line][1])
pygame.display.set_caption("live off lying")
clock = pygame.time.Clock()  # как я понял эта функция фпс
# фон: как я понял, нужен convert() и масштаб под окно
bg_path = scene_meta.get("background")
if bg_path:
    background = pygame.image.load(bg_path).convert()
else:
    background = pygame.Surface((1200, 800))  # запасной фон, если файла нет
    background.fill((10, 12, 18))

# масштаб под заданный размер (или под текущее окно)
scale_to = scene_meta.get("scale_to", [1200, 800])
if isinstance(scale_to, list) and len(scale_to) == 2:
    background = pygame.transform.scale(background, (scale_to[0], scale_to[1]))

# музыка: как я понял, нужно проигрывать в фоне и задать громкость
music_path = scene_meta.get("music")
if music_path:
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # -1 — зациклить, если надо один раз —  0)
        pygame.mixer.music.set_volume(float(scene_meta.get("music_volume", 0.1)))
    except Exception as e:
        print("Не удалось загрузить музыку:", e)
text, speaker = scene_lines[current_line]
box.set_text(text, speaker)
while True:
    dt = clock.tick(144) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not box.flag_finished:
                    box.skip_to_end()
                else:
                    current_line += 1
                    if current_line < len(scene_lines):
                        text, speaker = scene_lines[current_line]
                        box.set_text(text, speaker)
                    else:
                        next_id = scene_meta.get("next")
                        if next_id:
                            switch_scene(next_id)
                        else:
                            # если next нет — остаёмся на последней (как сейчас)
                            current_line = len(scene_lines) - 1

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not box.flag_finished:
                box.skip_to_end()
            else:
                current_line += 1
                if current_line < len(scene_lines):
                    text, speaker = scene_lines[current_line]
                    box.set_text(text, speaker)
                else:
                    next_id = scene_meta.get("next")
                    if next_id:
                        switch_scene(next_id)
                    else:
                        # если next нет — остаёмся на последней (как сейчас)
                        current_line = len(scene_lines) - 1

    box.update(dt)
    screen.blit(background, (0, 0))
    box.draw(screen)
    pygame.display.flip()
