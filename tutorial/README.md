# Sokoban

Sokoban je logická hra, v níž hráč posouvá bedny v bludišti a snaží se je umístit na vyznačené pozice (malé kosočtverce).
K naprogramování této hry bude potřeba knihovna `pyglet`, `math` a `sys`.
Veškeré obrázky, které budou použity, jsou volně dostupné na internetové adrese https://kenney.nl/assets/sokoban.

![Obrázek hry](screenshot.png)

Abychom nemuseli zvlášť každému obrázku přidávat sprite, tak si vytvoříme funkci, která to udělá za nás.
Jako atribut funkce bude proměnná image, která bude reprezentovat obrázek.
Kromě přidělování spritů zde i určíme měřítko spritu, aby vše mělo správnou velikost:

```python
def make_sprite(image):
    sprite = pyglet.sprite.Sprite(image)
    sprite.scale = TILE_SIZE / image.width
    return sprite
```

Vyzkoušíme si naprogramovat hru se třemi levely. Proto budeme potřebovat třídu Level, která bude mít v konstruktoru kromě atributu `self` i `name` (0, 1, 2) a `char` (charakter).
Uvnitř konstruktoru si nastavíme výšku a šířku dané úrovně.

Další třídou bude Game, v níž pracujeme s uživatelem vybraným levelem. Proto bychom měli nastavit počáteční souřadnice hráče na obou osách a přiřadit mu `sprite`.
Vytvoříme si i slovník `objects`, ten bude zatím prázdný, ale vrátíme se k němu při zjišťování, zda hráč vyhrál.
Rovněž zkontrolujeme i ostatní charaktery a vytvoříme jejich sprity, pro všechny cílové pozice pokladů nastavíme jejich vykreslování na `goal_batch` a pro ostatní charaktery
bude vykreslování `main_batch`.

Uvnitř třídy Game si vytvoříme funkci `is_won`. V ní budeme kontrolovat, zda poklad je na cílové pozici. Podle toho zjistíme jestli hráč vyhrál.
Další důležitou funkcí uvnitř třídy Game je `move`. Tato funkce bude zajišťovat pohyb objektů. Nejprve zkontrolujeme, zda hráč už nevyhrál, protože
v tom případě by se nepotřeboval pohybovat. Pomocí proměnných `new_x` a `new_y` budeme vytvářet nové souřadnice na obou osách. Dále musíme zajistit to, aby se hráč nemohl dostat
za zdi, které ohraničují hráčské pole. Do n-tice `bloking_objects` si nejprve vložíme všechny objekty. Když bude za hráčem poklad, který potřebuje posunout, tak mu to umožní
proměnné `behind_x` a `behind_y`. Pomocí n-tice `behind_objects` budeme kontrolovat, jestli je za tlačeným pokladem místo. Pakliže tam místo nebude hráči nepůjde poklad posunout.

Abychom si na začátku mohli vybrat level, který si chceme zahrát, tak se musíme dostat do souboru "levels.txt". K tomu slouží níže vložený kód.
.
```
try:
    levels_filename = sys.argv[1]
except IndexError:
    levels_filename = 'levels.txt'
```