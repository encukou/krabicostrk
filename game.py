import math
import time

import pyglet


TILE_SIZE = 32

# Images are from https://kenney.nl/assets/sokoban

# For level definition, see "Making your own levels"
# in http://www.sneezingtiger.com/sokoban/docs.html

base = 'kenney-sokoban-pack/PNG/Default size/'
face_image = pyglet.image.load(base + 'playerFace.png')
tile_images = {
    '@': pyglet.image.load(base + 'Player/player_05.png'),
    '#': pyglet.image.load(base + 'Blocks/block_01.png'),
    '$': pyglet.image.load(base + 'Crates/crate_15.png'),
    '.': pyglet.image.load(base + 'Environment/environment_02.png'),
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

window = pyglet.window.Window(resizable=True)

def make_sprite(image):
    sprite = pyglet.sprite.Sprite(image)
    sprite.scale = TILE_SIZE / image.width
    return sprite


class Level:
    def __init__(self, name, chars):
        self.name = name
        self.chars = chars
        self.width = max(x for x, y in self.chars)
        self.height = max(y for x, y in self.chars)


class Game:
    def __init__(self, level):
        self.level = level
        self.player_x = 0
        self.player_y = 0
        self.player_sprite = make_sprite(tile_images['@'])

        self.objects = {}
        self.main_batch = pyglet.graphics.Batch()
        self.goal_batch = pyglet.graphics.Batch()
        for (x, y), chars in level.chars.items():
            for char in chars:
                if char == '@':
                    self.player_x = x
                    self.player_y = y
                    continue
                image = tile_images[char]
                sprite = make_sprite(image)
                sprite.x = x * TILE_SIZE
                sprite.y = y * TILE_SIZE
                if char == '.':
                    sprite.batch = self.goal_batch
                else:
                    sprite.batch = self.main_batch
                sprite.char = char
                self.objects.setdefault((x, y), {})[char] = sprite


    def draw(self):
        scale = min(
            window.width / (self.level.width + 3) / TILE_SIZE,
            window.height / (self.level.height + 3) / TILE_SIZE,
        )
        pyglet.gl.glTranslatef(window.width / 2, window.height / 2, 1)
        pyglet.gl.glScalef(scale, scale, 1)
        pyglet.gl.glTranslatef(
            -(self.level.width+1) * TILE_SIZE / 2,
            -(self.level.height+1) * TILE_SIZE / 2,
            0,
        )
        self.main_batch.draw()
        self.goal_batch.draw()
        self.player_sprite.x = self.player_x * TILE_SIZE
        self.player_sprite.y = self.player_y * TILE_SIZE
        if self.is_won():
            jump = abs(math.sin(time.time() * 10))
            self.player_sprite.y += jump * TILE_SIZE / 4
        self.player_sprite.draw()
        pyglet.gl.glLoadIdentity()

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
                        levels.append(Level(current_name, current_level))
                    current_level = {}
                    current_name = line
                    current_y = 0
        if current_level:
            levels.append(Level(current_name, current_level))
        self.levels = levels
        self.index = 0
        self.face_sprite = make_sprite(face_image)
        self.face_sprite.x = TILE_SIZE / 4
        self.game = None

    def draw(self):
        if self.game:
            self.game.draw()
        else:
            levels_on_screen = (window.height // TILE_SIZE)
            label = pyglet.text.Label(font_size=TILE_SIZE / 2)
            label.x = TILE_SIZE * 1.5
            for y in range(levels_on_screen):
                index = (self.index + y - levels_on_screen // 2)
                label.text = self.levels[index % len(self.levels)].name
                label.y = (levels_on_screen - y - 1 + 2/8) * TILE_SIZE
                label.draw()
            self.face_sprite.y = levels_on_screen // 2 * TILE_SIZE
            self.face_sprite.draw()

    def move(self, dx, dy):
        if self.game:
            self.game.move(dx, dy)
        else:
            self.index = (self.index - dy) % len(self.levels)
            if dx > 0:
                self.enter()

    def enter(self):
        if not self.game:
            self.game = Game(self.levels[self.index])
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
