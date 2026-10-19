---
title: Creating Sprites
---

This page is part of the **common base** — both paths need it.

All visible parts of a game are rendered as `color` , and in a 2D game that color is carried by `sprites`. The full property list is in [Basic development → Sprites](../020_basic/020_sprites.md) .

---

## Creating an Image

Just like at the end of the previous page, use `Sprites.CreateSprite(path, layer)` to create a sprite.

- `path` the image path: <u>first look in `Game/Resources/Sprites/`, then fall back to `Resources/Sprites/`</u> (Game area takes priority).
- `layer` the layer; can be a number or text. If you enter text and the layer doesn't exist, it defaults to returning 0, and the terminal will show a hint.

!!! warning "Terminal hint"
    `[WARNING] Layers.add: Layer "xxx" not found, defaulting to 0`

!!! example "Case"
    Below we'll create a `poseur` image on layer 0.
    ```lua
    Sprites.CreateSprite("poseur.png", 0)
    ```

---

## Editing an Image

**First you need to master an operation that will also be very common later: assignment.**<br>
<u>Sounds fancy, but it's actually just making something equal the result of a function call.</u>

You may have thought about creating an image in one go with a long string of parameters, like:

```lua
Sprites.CreateSprite("poseur.png", 0, 320, 240, 0, 1, 0, 0, nil, {1, 1, 1}, 1, 2, 2)
```

The good news is the engine **does not** design it this way: `Sprites.CreateSprite(path, layer)` only takes two parameters. Position, color, scale, etc. are all assigned one by one after you get the sprite.

!!! danger "If it really took a long string of parameters"
    Suppose the creation function really required you to fill in all properties at once; then to just change `xscale` you'd have to do this:

    ```lua
    Sprites.CreateSprite("a.png", 0, nil, nil, nil, nil, nil, nil, nil, nil, nil, 2, 2)
    ```

    Tell me within three seconds, which one is the third-to-last nil?<br>
    Obviously, you can't answer within three seconds, so the engine chose to split it up. That simple.

---

`CreateSprite` returns an `object`, which you can think of as representing this image, so we can write it like this:

!!! example "Catching the image"
    ```lua
    image = Sprites.CreateSprite("poseur.png", 0)
    ```

Modifying the image's properties separately after creation:

!!! example "Changing x/yscale"
    ```lua
    image.xscale = 2
    image.yscale = 2
    ```

**Below are all the modifiable properties and the concepts they represent. For a more complete explanation, open [Basic Development](../020_basic/index.md):**

!!! tip "Modifiable properties"
    - `x` the horizontal position.
    - `y` the vertical position.
    - `rotation` (degrees) the image's angle; increases clockwise as the angle grows.
    - `xscale` the horizontal scale; default 1, enlarges the image by a multiplier.
    - `yscale` the vertical scale; default 1, enlarges the image by a multiplier.
    - `color` the image's color, assigned using a table.
    - `alpha` the image's transparency (0 ~ 1); the larger the number, the more clearly visible.
    - `pixel_snap` whether this image does pixel snapping (defaults to following the global `sprites.pixel_snap`, i.e. on). Set to `false` to exempt just this image—commonly used for parts in an assembly that shouldn't be individually rounded.
    - `velocity` the image's velocity

---

## How to verify

Put this in the first-level region of a scene. After entering the scene, a `poseur` image at double size should appear centre screen:

```lua
image = Sprites.CreateSprite("poseur.png", 0)
image.xscale = 2
image.yscale = 2
```

!!! warning "The image does not appear"
    The path is looked up in `Game/Resources/Sprites/` and `Resources/Sprites/` , and subdirectories must be written out in full, e.g. `Overworld/Frisk/spr_frisk_0.png` .<br>
    File names are case-sensitive. A case mismatch that still matches on Windows will fail to find the image once packaged for Android or Linux.
