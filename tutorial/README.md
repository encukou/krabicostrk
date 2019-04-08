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

