import pygame
import random
import sys
import json

enemy_register = {}


def register_enemy(enemy_id):
    def deco(cls):
        enemy_register[enemy_id] = cls
        return cls

    return deco


class Creature:
    def __init__(self, name, hp, atk, defense, sprite_path=None, level=1):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.level = level
        self.sprite = None
        if sprite_path:
            try:
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
            except Exception:
                self.sprite = None

    def is_alive(self):
        return self.hp > 0

    def deal_damage_to(self, other):
        raw = (self.atk + max(0, self.level - 1)) - other.defense
        damage = max(1, raw)
        other.hp = max(0, other.hp - damage)
        return damage



# сыны сюжета
class Hero(Creature):
    def __init__(self, level=1, sprite_path=None, **overrides):
        base = dict(name="Главный герой", hp=25, atk=7, defense=2)
        super().__init__(level=level, sprite_path=sprite_path, **base)


@register_enemy("sensei")  # id, который будет в JSON
class SenseiEnemy(Creature):
    def __init__(self, level=1, sprite_path=None, **overrides):
        base = dict(name="Сенсей", hp=30, atk=5, defense=2)
        super().__init__(level=level, sprite_path=sprite_path, **base)

    # пример «фичи» класса: скейлимся от уровня
    def start_of_battle(self):
        # лёгкий автоскейл: + (lvl-1)*3 HP и + (lvl-1) ATK
        bonus_hp = max(0, (self.level - 1) * 3)
        self.max_hp += bonus_hp
        self.hp += bonus_hp
        self.atk += max(0, self.level - 1)


# оформление
class boxText:
    def __init__(self, x, y, wight, height):
        self.rect = pygame.Rect(x, y, wight,
                                height)  # как я понял х и у это координаты верхнего левого угла,а дальше размер
        self.text = ""  # полный текст
        self.speaker = ""
        self.name_font = pygame.font.Font("fonts/arialmt.ttf", 24)
        self.display_text = ""  # то что уже напечаталось
        self.font = pygame.font.Font("fonts/arialmt.ttf", 28)
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


class Button:
    def __init__(self, x, y, w, h, text, font=None, on_click=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.on_click = on_click
        self.font = font or pygame.font.SysFont("font/arialmt.ttf", 22)
        # стили
        self.bg = (35, 38, 50)
        self.bg_hover = (50, 55, 75)
        self.border = (90, 95, 110)
        self.fg = (230, 230, 230)

    def draw(self, surf):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surf, self.bg_hover if hovered else self.bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, self.border, self.rect, 2, border_radius=10)
        label = self.font.render(self.text, True, self.fg)
        lx = self.rect.x + (self.rect.w - label.get_width()) // 2
        ly = self.rect.y + (self.rect.h - label.get_height()) // 2
        surf.blit(label, (lx, ly))

    def handle_event(self, event):
        # вызывай внутри блока MOUSEBUTTONDOWN
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False


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
    items = scene_obj.get("lines", [])
    global scene_mode
    scene_mode = items[:]
    lines = []
    for it in items:
        if it.get("type") == "battle":
            lines.append(("", ""))  # текст не показываем — вместо этого войдём в бой
            continue
        text = it.get("text", "")
        speaker = it.get("speaker", "")
        lines.append((text, speaker))

    return meta, lines


def make_enemy_from_json_node(node):
    """
    node: {"type":"battle","enemy":"sensei", "level":2, "sprite":"...", "override":{...}}
    """
    enemy_id = node.get("enemy", "unknown")
    level = int(node.get("level", 1))
    sprite = node.get("sprite")  # опционально
    overrides = node.get("override", {})  # например {"hp": 40}

    EnemyCls = enemy_register.get(enemy_id)
    if not EnemyCls:
        # запасной враг, если id не найден
        return Creature(name=enemy_id, hp=10, atk=3, defense=1, sprite_path=sprite, level=level)

    enemy = EnemyCls(level=level, sprite_path=sprite, **overrides)
    return enemy


def apply_scene_meta(scene_meta):
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
            pygame.mixer.music.set_volume(float(scene_meta.get("music_volume")))
        except Exception as e:
            print("не удалось загрузить музыку:", e)


def draw_batlle(surf):
    surf.blit(background, (0, 0))
    panel_h = 180
    panel = pygame.Surface((surf.get_width(), panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 22, 30, 220), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (90, 95, 110), panel.get_rect(), 2, border_radius=12)
    surf.blit(panel, (0, surf.get_height() - panel_h))

    f = pygame.font.SysFont("arial", 24)
    name = battle_enemy.name if battle_enemy else "???"
    hp = f"HP: {battle_enemy.hp}/{battle_enemy.max_hp}" if battle_enemy else "HP: ?"

    surf.blit(f.render("BATTLE MODE", True, (230, 230, 230)), (20, surf.get_height() - panel_h + 16))
    surf.blit(f.render(f"Противник: {name}", True, (230, 230, 230)), (20, surf.get_height() - panel_h + 52))
    surf.blit(f.render(hp, True, (230, 230, 230)), (20, surf.get_height() - panel_h + 88))


def ensure_hero():
    global hero
    if hero is None:
        hero = Hero(level=1)


def start_battle(battle_node):
    """
    battle_node — это САМ узел из scene_nodes[current_line], где type == "battle"
    """
    ensure_hero()
    global mode, battle_enemy, battle_log
    batlle_btns = []
    global battle_btns
    btn_font = pygame.font.SysFont("arial", 22)
    btn_w, btn_h = 160, 48
    # позиция: на нижней панели боя, см. draw_batlle (панель высотой 180)
    x = 20
    y = screen.get_height() - 180 + 16 + 36 * 3  # чуть над нижним краем панели

    def on_attack():
        player_attack()

    battle_btns = [
        Button(x, y, btn_w, btn_h, "Атака", btn_font, on_attack),
        Button(x + 500, y, btn_w, btn_h, "Защита", btn_font, None)
    ]
    battle_enemy = make_enemy_from_json_node(battle_node)
    battle_log = [f"Бой начался! Противник: {battle_enemy.name} (Lv.{battle_enemy.level})"]
    mode = mode_battle


def enemy_attack():
    global hero_guard_active, battle_log, mode
    if not (hero and battle_enemy):
        return

    # временно добавим бонус к защите, если стойка активна
    added = 0
    if hero_guard_active:
        added = HERO_GUARD_BONUS
        hero.defense += added

    dmg = battle_enemy.deal_damage_to(hero)

    # откатываем бонус
    if added:
        hero.defense -= added
        hero_guard_active = False  # стойка сработала и погасла

    battle_log.append(f"{battle_enemy.name} атакует на {dmg}.")

    if not hero.is_alive():
        battle_log.append("Поражение…")
        mode = mode_dialogue
        skip_battle_and_go_next()


def player_attack():
    global hero_guard_active, battle_log, mode
    if not (hero and battle_enemy):
        return
    added = 0
    dmg = hero.deal_damage_to(battle_enemy)
    battle_log.append(f"{hero.name} бьёт на {dmg}.")
    if not battle_enemy.is_alive():
        battle_log.append("Победа!")
        mode = mode_dialogue
        skip_battle_and_go_next()


def player_defense():
    global hero_guard_active, mode
    if not (hero and battle_enemy):
        return
    hero_guard_active = True
    battle_log.append(f"{hero.name} встал в защитную стойку (+{HERO_GUARD_BONUS} к защите до следующего удара).")


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


def skip_battle_and_go_next():
    # после боя просто «нажмём» следующий шаг сцены
    global current_line
    current_line += 1
    if current_line < len(scene_lines):
        node = scene_mode[current_line]
        if isinstance(node, dict) and node.get("type") == "battle":
            # если подряд два боя (редко, но вдруг) — запустим следующий
            start_battle(node)
        else:
            text, speaker = scene_lines[current_line]
            box.set_text(text, speaker)
    else:
        next_id = scene_meta.get("next")
        if next_id:
            switch_scene(next_id)
        else:
            current_line = len(scene_lines) - 1


pygame.init()
pygame.mixer.init()
pygame.font.init()
screen = pygame.display.set_mode((1200, 800))
mode_dialogue = "dialogue"
mode_battle = "battle"
mode = mode_dialogue
hero = None
battle_enemy = None
battle_enemy_id = None
battle_log = []
hero_guard_active = False  # включена ли стойка
HERO_GUARD_BONUS = 3
# Вся информация о сцене теперь в JSON:
current_scene_id = "The_awaking"
scene_meta, scene_lines = load_scene_from_json("scenes.json", current_scene_id)
apply_scene_meta(scene_meta)
current_line = 0
box = boxText(100, 600, 1000, 150)
box.set_text(scene_lines[current_line][0], scene_lines[current_line][1])
pygame.display.set_caption("live off lying")
clock = pygame.time.Clock()  # как я понял эта функция фпс
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
        if mode == mode_battle:
            # клики по кнопкам боя
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # сначала пытаемся обработать клик кнопками
                handled = False
                for b in battle_btns:
                    if b.handle_event(event):
                        handled = True
                        break
                if handled:
                    continue  # не проваливаемся дальше в обработку

            # (опционально) выход из боя по SPACE — можешь временно отключить
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                mode = mode_dialogue
                skip_battle_and_go_next()
                continue
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
                        node = scene_mode[current_line]  # сырой узел из JSON
                        if isinstance(node, dict) and node.get("type") == "battle":
                            # запускаем бой из JSON: enemy id лежит в node["enemy"]
                            start_battle(node)
                            # ничего не сетим в box — мы в режиме боя
                        else:
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
                    node = scene_mode[current_line]  # сырой узел из JSON
                    if isinstance(node, dict) and node.get("type") == "battle":
                        # запускаем бой из JSON: enemy id лежит в node["enemy"]
                        start_battle(node)
                        # ничего не сетим в box — мы в режиме боя
                    else:
                        text, speaker = scene_lines[current_line]
                        box.set_text(text, speaker)
                else:
                    next_id = scene_meta.get("next")
                    if next_id:
                        switch_scene(next_id)
                    else:
                        # если next нет — остаёмся на последней (как сейчас)
                        current_line = len(scene_lines) - 1

    if mode == mode_dialogue:
        box.update(dt)
        screen.blit(background, (0, 0))
        box.draw(screen)
    else:
        draw_batlle(screen)
        for b in battle_btns:
            b.draw(screen)

    pygame.display.flip()
