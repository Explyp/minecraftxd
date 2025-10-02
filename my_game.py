# -*- coding: utf-8 -*-
import sys
import json
import pygame

# ===== РЕЖИМЫ И СОСТОЯНИЯ =====
MODE_DIALOGUE = "dialogue"
MODE_BATTLE   = "battle"

# ===== ВСПОМОГАТЕЛЬНЫЕ UI-КОМПОНЕНТЫ =====
class Button:
    def __init__(self, x, y, w, h, text, font=None, on_click=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.on_click = on_click
        self.font = font or pygame.font.SysFont("fonts/arialmt.ttf", 32)
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

# ===== ДИАЛОГОВЫЙ БОКС =====
class boxText:
    def __init__(self, x, y, wight, height):
        # как я понял х и у это координаты верхнего левого угла,а дальше размер
        self.rect = pygame.Rect(x, y, wight, height)
        self.text = ""             # полный текст
        self.speaker = ""          # имя говорящего
        self.name_font = pygame.font.SysFont("fonts/arialmt.ttf", 34)
        self.display_text = ""     # то что уже напечаталось
        self.font = pygame.font.SysFont("fonts/arialmt.ttf", 38)
        self.flag_finished = False
        self.index = 0             # чтобы понимать какое кол-во букв выводится
        self.time_accum = 0.0
        self.cps = 12              # cкорость символа как я понял
        self.dot_time = 0.0        # таймер для точек
        self.dot_interval = 0.4    # как часто переключаются точки(сек)
        self.dot_count = 0         # 0..3 (0=нет точек,1="." и т.д)
        self.padding = 16          # отступы внутри бокса
        self.line_spacing = 6      # расстояние между строками (пиксели)

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
                self.index = min(len(self.text), self.index + chars_to_add)
                self.display_text = self.text[:self.index]
                if self.index >= len(self.text):
                    self.flag_finished = True
        if self.flag_finished:
            self.dot_time += dt  # время кадра
            if self.dot_time >= self.dot_interval:  # достаточно ли времени прошло для смены точек
                self.dot_time -= self.dot_interval  # чтобы после смены одной точки было две
                self.dot_count = (self.dot_count + 1) % 4  # 0->1->2->3->0
        else:
            self.dot_time = 0
            self.dot_count = 0

    def draw(self, surf):
        # временная поверхность размера прямоугольника
        temp = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # RGBA: последний параметр — альфа (0 = прозрачный, 255 = непрозрачный)
        pygame.draw.rect(temp, (20, 22, 30, 160), temp.get_rect(), border_radius=10)
        # рамка
        pygame.draw.rect(temp, (90, 95, 110, 255), temp.get_rect(), 2, border_radius=10)
        surf.blit(temp, self.rect.topleft)

        # имя говорящего (над рамкой)
        if self.speaker:
            name_surface = self.name_font.render(self.speaker, True, (255, 255, 200))
            surf.blit(name_surface, (self.rect.x + self.padding, self.rect.y - name_surface.get_height() - 4))

        # текст + точки ожидания
        text_to_draw = self.display_text
        if self.flag_finished and self.dot_count:
            text_to_draw += " " + "." * self.dot_count

        max_width = self.rect.width - 2 * self.padding
        lines = self.wrap_text(text_to_draw, max_width)
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

# ===== БОЕВАЯ МОДЕЛЬ =====
enemy_register = {}  # сюда регаем классы врагов по строковому id из JSON

def register_enemy(enemy_id):
    # декоратор: регистрирует класс врага
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

    # простая формула урона (потом можно усложнить)
    def deal_damage_to(self, other):
        raw = (self.atk + max(0, self.level - 1)) - other.defense
        dmg = max(1, raw)
        other.hp = max(0, other.hp - dmg)
        return dmg
#персонажи
class Hero(Creature):
    def __init__(self, level=1, sprite_path=None, **overrides):
        base = dict(name="Главный герой", hp=25, atk=10, defense=2)
        base.update(overrides)
        super().__init__(level=level, sprite_path=sprite_path, **base)

@register_enemy("sensei")
class SenseiEnemy(Creature):
    def __init__(self, level=1, sprite_path=None, **overrides):
        base = dict(name="Сенсей", hp=30, atk=5, defense=2)
        base.update(overrides)
        super().__init__(level=level, sprite_path=sprite_path, **base)

    # пример «фичи» класса: скейлимся от уровня
    def start_of_battle(self):
        bonus_hp = max(0, (self.level - 1) + 1)
        self.max_hp += bonus_hp
        self.hp += bonus_hp
        self.atk += max(0, self.level - 1)

# ===== SceneManager: JSON → сцена/фон/музыка/линии =====
class SceneManager:
    def __init__(self, json_path, start_scene_id, screen, fallback_size=(1200, 800)):
        self.json_path = json_path
        self.screen = screen
        self.fallback_size = fallback_size
        self.current_scene_id = start_scene_id
        self.meta = {}
        self.nodes = []   # сырые узлы из JSON (и реплики, и battle)
        self.lines = []   # [(text, speaker), …] — для бокса
        self.line_idx = 0
        self.background = None

    def load_scene(self, scene_id):
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.current_scene_id = scene_id
        scene_obj = data.get("scenes", {}).get(scene_id, {})
        self.meta = scene_obj.get("meta", {})
        items = scene_obj.get("lines", [])
        self.nodes = items[:]
        lines = []
        for it in items:
            if isinstance(it, dict) and it.get("type") == "battle":
                lines.append(("", ""))  # плейсхолдер, чтобы индексы совпадали
            else:
                text = it.get("text", "")
                speaker = it.get("speaker", "")
                lines.append((text, speaker))
        self.lines = lines
        self.line_idx = 0

    def apply_meta(self):
        bg_path = self.meta.get("background")
        if bg_path:
            try:
                self.background = pygame.image.load(bg_path).convert()
            except Exception:
                self.background = pygame.Surface(self.fallback_size)
                self.background.fill((10, 12, 18))
        else:
            self.background = pygame.Surface(self.fallback_size)
            self.background.fill((10, 12, 18))
        if "scale_to" in self.meta:
            w, h = self.meta["scale_to"]
            self.background = pygame.transform.scale(self.background, (w, h))
        bg_path = self.meta.get("background")
        if bg_path:
            self.background = pygame.image.load(bg_path).convert()
        else:
            self.background = pygame.Surface(self.fallback_size)
            self.background.fill((10, 12, 18))

        # ⚠️ растягиваем под текущее окно:
        sw, sh = self.screen.get_size()
        self.background = pygame.transform.smoothscale(self.background, (sw, sh))
        music_path = self.meta.get("music")
        if music_path:
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                if music_path == "music/wake_up.mp3":
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play()
                pygame.mixer.music.set_volume(float(self.meta.get("music_volume", 0.1)))
            except Exception as e:
                print("не удалось загрузить музыку:", e)

    def set_first_line_to_box(self, box):
        if self.lines:
            text, speaker = self.lines[self.line_idx]
            box.set_text(text, speaker)

    def get_current_node(self):
        if 0 <= self.line_idx < len(self.nodes):
            return self.nodes[self.line_idx]
        return None

    def advance_or_switch(self, box):
        self.line_idx += 1
        if self.line_idx < len(self.lines):
            node = self.get_current_node()
            if isinstance(node, dict) and node.get("type") == "battle":
                return "battle"
            text, speaker = self.lines[self.line_idx]
            box.set_text(text, speaker)
            return "line"
        else:
            next_id = self.meta.get("next")
            if next_id:
                self.load_scene(next_id)
                self.apply_meta()
                self.set_first_line_to_box(box)
                return "switched"
            else:
                self.line_idx = max(0, len(self.lines) - 1)
                return "end"

# ===== BattleSystem: логика боя, кнопки и отрисовка =====
class BattleSystem:
    GUARD_BONUS = 3

    def __init__(self, screen, scene_mgr: SceneManager, hero: Creature, box: boxText):
        self.screen = screen
        self.scene_mgr = scene_mgr
        self.hero = hero
        self.box = box
        self.active = False
        self.enemy = None
        self.log = []
        self.guard_active = False
        self.buttons = []
        self.panel_h = 200
        self.font = pygame.font.SysFont("fonts/arialmt.ttf", 32)

    def _make_enemy_from_node(self, node):
        enemy_id = node.get("enemy", "unknown")
        level = int(node.get("level", 1))
        sprite = node.get("sprite")
        overrides = node.get("override", {})
        EnemyCls = enemy_register.get(enemy_id)
        if not EnemyCls:
            return Creature(name=enemy_id, hp=10, atk=3, defense=1, sprite_path=sprite, level=level)
        enemy = EnemyCls(level=level, sprite_path=sprite, **overrides)
        if hasattr(enemy, "start_of_battle"):
            enemy.start_of_battle()
        return enemy

    def start(self, battle_node):
        self.enemy = self._make_enemy_from_node(battle_node)
        self.log = [f"Бой начался! Противник: {self.enemy.name} (Lv.{self.enemy.level})"]
        self.guard_active = False
        self.active = True
        self._build_buttons()

    def _build_buttons(self):
        self.buttons = []
        btn_font = pygame.font.SysFont("fonts/arialmt.ttf", 32)
        btn_w, btn_h = 160, 48
        base_y = self.screen.get_height() - self.panel_h + 16
        x = 20
        y = base_y + 108 + 8
        def on_attack():
            self.player_attack()
        def on_defense():
            self.player_defense()
        self.buttons.append(Button(x,           y, btn_w, btn_h, "Атака",   btn_font, on_attack))
        self.buttons.append(Button(x + 180,     y, btn_w, btn_h, "Защита",  btn_font, on_defense))

    def player_attack(self):
        if not (self.hero and self.enemy): return
        dmg = self.hero.deal_damage_to(self.enemy)
        self.log.append(f"{self.hero.name} бьёт на {dmg}.")
        if not self.enemy.is_alive():
            self.log.append("Победа!")
            self._finish_and_go_next()
            return
        self.enemy_attack()

    def player_defense(self):
        if not (self.hero and self.enemy): return
        self.guard_active = True
        self.log.append(f"{self.hero.name} встал в защитную стойку (+{self.GUARD_BONUS} к защите до следующего удара).")
        self.enemy_attack()

    def enemy_attack(self):
        if not (self.hero and self.enemy): return
        added = 0
        if self.guard_active:
            added = self.GUARD_BONUS
            self.hero.defense += added
        dmg = self.enemy.deal_damage_to(self.hero)
        if added:
            self.hero.defense -= added
            self.guard_active = False
        self.log.append(f"{self.enemy.name} атакует на {dmg}.")
        if not self.hero.is_alive():
            self.log.append("Поражение…")
            self._finish_and_go_next()

    def _finish_and_go_next(self):
        self.active = False
        self.scene_mgr.advance_or_switch(self.box)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.buttons:
                if b.handle_event(event):
                    return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.active = False
            self.scene_mgr.advance_or_switch(self.box)
            return True
        return False

    def draw(self):
        # фон сцены
        self.screen.blit(self.scene_mgr.background, (0, 0))

        # === НОВОЕ: спрайты и HP над ними ===
        # позиции под твой 1200x800: герой слева, враг справа
        self._draw_creature_slot(self.screen, self.hero, 320, 420, name_align="left")
        self._draw_creature_slot(self.screen, self.enemy, 880, 320, name_align="center")

        # панель внизу (как было)
        panel = pygame.Surface((self.screen.get_width(), self.panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 22, 30, 220), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (90, 95, 110), panel.get_rect(), 2, border_radius=12)
        self.screen.blit(panel, (0, self.screen.get_height() - self.panel_h))

        base_y = self.screen.get_height() - self.panel_h + 16
        self.screen.blit(self.font.render("BATTLE MODE", True, (230, 230, 230)), (20, base_y))
        self.screen.blit(self.font.render("Клик по кнопке: Атака/Защита", True, (200, 200, 200)), (20, base_y + 36))

        # кнопки боя
        for b in self.buttons:
            b.draw(self.screen)

    def _draw_hp_bar(self, surf, x, y, w, h, cur, mx):
        # фон полоски
        pygame.draw.rect(surf, (60, 65, 80), (x, y, w, h), border_radius=6)
        # заполнение
        ratio = 0 if mx <= 0 else max(0.0, min(1.0, cur / mx))
        fill_w = int(w * ratio)
        pygame.draw.rect(surf, (100, 220, 120), (x, y, fill_w, h), border_radius=6)
        # рамка
        pygame.draw.rect(surf, (20, 22, 30), (x, y, w, h), 2, border_radius=6)

    def _draw_creature_slot(self, surf, creature, cx, cy, name_align="center"):
        """
        Рисует спрайт по центру (cx,cy) и HP+имя над ним.
        Если спрайта нет — рисует заглушку.
        """
        name_font = self.font
        hp_font = self.font

        # 1) имя и HP сверху
        name_text = creature.name if creature else "???"
        hp_text = f"{creature.hp}/{creature.max_hp}" if creature else "?"
        name_surf = name_font.render(name_text, True, (230, 230, 230))
        hp_surf = hp_font.render(hp_text, True, (200, 200, 200))

        # выравнивание имени
        name_x = cx - name_surf.get_width() // 2
        if name_align == "left":
            name_x = cx - 120
        elif name_align == "right":
            name_x = cx - 40  # можно подвинуть, если нужно

        name_y = cy - 160
        surf.blit(name_surf, (name_x, name_y))
        surf.blit(hp_surf, (name_x, name_y + 28))

        # 2) полоска HP под цифрами
        bar_x, bar_y, bar_w, bar_h = name_x, name_y + 60, 220, 14
        if creature:
            self._draw_hp_bar(surf, bar_x, bar_y, bar_w, bar_h, creature.hp, creature.max_hp)
        else:
            self._draw_hp_bar(surf, bar_x, bar_y, bar_w, bar_h, 0, 1)

        # 3) спрайт (или заглушка)
        if creature and creature.sprite:
            img = creature.sprite
            # лёгкое безопасное масштабирование (если спрайт огромный)
            max_w, max_h = 320, 320
            iw, ih = img.get_width(), img.get_height()
            scale = min(1.0, max_w / max(1, iw), max_h / max(1, ih))
            if scale < 1.0:
                img = pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))
            rect = img.get_rect(center=(cx, cy))
            surf.blit(img, rect)
        else:
            # заглушка — «силуэт»
            placeholder = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.ellipse(placeholder, (80, 85, 110, 200), placeholder.get_rect())
            pygame.draw.ellipse(placeholder, (20, 22, 30), placeholder.get_rect(), 3)
            rect = placeholder.get_rect(center=(cx, cy))
            surf.blit(placeholder, rect)

def main():
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("live off lying")
    clock = pygame.time.Clock()
    box = boxText(100, 600, 1000, 150)
    start_scene_id = "The_awaking"
    scene = SceneManager("scenes.json", start_scene_id=start_scene_id, screen=screen)
    scene.load_scene(scene.current_scene_id)
    scene.apply_meta()
    scene.set_first_line_to_box(box)
    hero = Hero(level=1,sprite_path="sprites/hero.png")
    battle = BattleSystem(screen=screen, scene_mgr=scene, hero=hero, box=box)
    while True:
        dt = clock.tick(144) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if battle.active:
                if battle.handle_event(event):
                    continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not box.flag_finished:
                    box.skip_to_end()
                else:
                    result = scene.advance_or_switch(box)
                    if result == "battle":
                        node = scene.get_current_node()
                        battle.start(node)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not box.flag_finished:
                    box.skip_to_end()
                else:
                    result = scene.advance_or_switch(box)
                    if result == "battle":
                        node = scene.get_current_node()
                        battle.start(node)
        if battle.active:
            battle.draw()
        else:
            box.update(dt)
            screen.blit(scene.background, (0, 0))
            box.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
