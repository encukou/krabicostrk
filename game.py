import pyglet

TILE_SIZE = 32

player_image = pyglet.image.load('img/player.png')
tile_types = {
    ' ': None,
    '#': pyglet.image.load('img/wall.png'),
    '$': pyglet.image.load('img/box.png'),
    '.': pyglet.image.load('img/goal.png'),
    '@': None,
}

window = pyglet.window.Window()

class State:
    def __init__(self, level):
        self.player_x = 0
        self.player_y = 0
        self.player_sprite = pyglet.sprite.Sprite(player_image)
        self.player_sprite.scale = TILE_SIZE / player_image.width
        self.init_level(level)

    def init_level(self, level):
        self.objects = {}
        self.batch = pyglet.graphics.Batch()
        for (x, y), char in level.items():
            if char == '@':
                self.player_x = x
                self.player_y = y
                continue
            image = tile_types[char]
            sprite = pyglet.sprite.Sprite(
                image,
                x=x * TILE_SIZE,
                y=y * TILE_SIZE,
                batch=self.batch,
            )
            sprite.scale = TILE_SIZE / image.width
            sprite.char = char
            self.objects[x, y] = {char: sprite}

    def draw(self):
        self.batch.draw()
        self.player_sprite.x = self.player_x * TILE_SIZE
        self.player_sprite.y = self.player_y * TILE_SIZE
        self.player_sprite.draw()

    def move(self, dx, dy):
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
                for objects in self.objects.values():
                    if '.' in objects:
                        if '$' not in objects:
                            break
                else:
                    exit('Good Job!')
            else:
                print(behind_objects)
                return
        self.player_x = new_x
        self.player_y = new_y


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
                    if all(c in tile_types for c in line):
                        for x, char in enumerate(line):
                            if char != ' ':
                                result[x, y] = char
                    else:
                        break
                return result
    raise ValueError(f'{caption} not found in {filename}')


level = load_level('levels.txt', 'Level 0')
state = State(level)


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


pyglet.app.run()
