import math
import time

import pyglet


TILE_SIZE = 32

tile_images = {
    '@': pyglet.image.load('img/player.png'),
    '#': pyglet.image.load('img/wall.png'),
    '$': pyglet.image.load('img/box.png'),
    '.': pyglet.image.load('img/goal.png'),
}
tile_chars = {
    ' ': '',
    '#': '#',
    '$': '$',
    '.': '.',
    '@': '@',
    '*': '$.',
    '+': '@.',
}

window = pyglet.window.Window()

def make_sprite(image):
    sprite = pyglet.sprite.Sprite(image)
    sprite.scale = TILE_SIZE / image.width
    return sprite


class Game:
    def __init__(self, level):
        self.player_x = 0
        self.player_y = 0
        self.player_sprite = make_sprite(tile_images['@'])
        self.init_level(level)

    def init_level(self, level):
        self.objects = {}
        self.batch = pyglet.graphics.Batch()
        for (x, y), chars in level.items():
            for char in chars:
                if char == '@':
                    self.player_x = x
                    self.player_y = y
                    continue
                image = tile_images[char]
                sprite = make_sprite(image)
                sprite.x = x * TILE_SIZE
                sprite.y = y * TILE_SIZE
                sprite.batch = self.batch
                sprite.char = char
                self.objects.setdefault((x, y), {})[char] = sprite

    def draw(self):
        self.batch.draw()
        self.player_sprite.x = self.player_x * TILE_SIZE
        self.player_sprite.y = self.player_y * TILE_SIZE
        if self.is_won():
            self.player_sprite.y += abs(math.sin(time.time() * 10)) * TILE_SIZE / 4
        self.player_sprite.draw()

    def move(self, dx, dy):
        if self.is_won():
            return
        new_x = self.player_x + dx
        new_y = self.player_y + dy
        blocking_objects = self.objects.get((new_x, new_y), {})
        if '#' in blocking_objects:
            return
        elif '$' in blocking_objects:
            behind_x = new_x + dx
            behind_y = new_y + dy
            behind_objects = self.objects.setdefault((behind_x, behind_y), {})
            if set(behind_objects) <= {'.'}:
                sprite = blocking_objects.pop('$')
                behind_objects['$'] = sprite
                sprite.x = behind_x * TILE_SIZE
                sprite.y = behind_y * TILE_SIZE
            else:
                print(behind_objects)
                return
        self.player_x = new_x
        self.player_y = new_y

    def is_won(self):
        for objects in self.objects.values():
            if '.' in objects:
                if '$' not in objects:
                    return False
        return True


class LevelSelector:
    def __init__(self, filename):
        levels = []
        current_name = ''
        current_level = {}
        current_y = 0
        with open(filename, encoding='utf-8') as file:
            for line in file:
                line = line.rstrip()
                if not line:
                    continue
                if all(c in tile_chars for c in line):
                    for x, char in enumerate(line):
                        if char != ' ':
                            current_level[x, current_y] = tile_chars[char]
                    current_y += 1
                else:
                    if current_level:
                        levels.append((current_name, current_level))
                    current_level = {}
                    current_name = line
                    current_y = 0
        if current_level:
            levels.append((current_name, current_level))
        self.levels = levels
        self.index = 0
        self.levels_on_screen = (window.height // TILE_SIZE)
        self.player_sprite = make_sprite(tile_images['@'])
        self.player_sprite.y = self.levels_on_screen // 2 * TILE_SIZE
        self.game = None

    def draw(self):
        if self.game:
            self.game.draw()
        else:
            label = pyglet.text.Label(font_size=TILE_SIZE / 2, x=TILE_SIZE)
            _los = self.levels_on_screen
            for y in range(_los):
                index = (self.index + y - _los // 2) % len(self.levels)
                label.text, level = self.levels[index]
                label.y = (_los - y - 1 + 3/8) * TILE_SIZE
                label.draw()
            self.player_sprite.draw()

    def move(self, dx, dy):
        if self.game:
            self.game.move(dx, dy)
        else:
            self.index = (self.index - dy) % len(self.levels)
            if dx > 0:
                self.enter()

    def enter(self):
        if not self.game:
            name, level = self.levels[self.index]
            self.game = Game(level)
        elif self.game.is_won():
            self.game = None

    def exit(self):
        if self.game:
            self.game = None
            return True

    def tick(self, dt):
        pass


def load_level(filename, caption):
    result = {}
    with open(filename, encoding='utf-8') as file:
        for line in file:
            line = line.rstrip()
            if not line:
                continue
            if line == caption:
                for y, line in enumerate(file):
                    line = line.rstrip()
                    if all(c in tile_chars for c in line):
                        for x, char in enumerate(line):
                            if char != ' ':
                                result[x, y] = tile_chars[char]
                    else:
                        break
                return result
    raise ValueError(f'{caption} not found in {filename}')


level = load_level('levels.txt', 'Level 0')
state = LevelSelector('levels.txt')


@window.event
def on_draw():
    window.clear()
    state.draw()


@window.event
def on_key_press(code, mod):
    if code == pyglet.window.key.LEFT:
        state.move(-1, 0)
    elif code == pyglet.window.key.RIGHT:
        state.move(1, 0)
    elif code == pyglet.window.key.UP:
        state.move(0, 1)
    elif code == pyglet.window.key.DOWN:
        state.move(0, -1)
    elif code == pyglet.window.key.ENTER:
        state.enter()
    elif code == pyglet.window.key.ESCAPE:
        return state.exit()


pyglet.clock.schedule_interval(state.tick, 1/60)

pyglet.app.run()
