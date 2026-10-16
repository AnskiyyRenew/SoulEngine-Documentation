---
title: Character
---

The little walking person in the Overworld. It is driven by a physics body, followed by a sprite, with the walking animation cycling through sprite frames.

Module path: `Scripts/Libraries/Overworld/char.lua`, exposed as the global `Char`.

---

## Walking Sprites

One frame group per direction, defaulting to the `Frisk` set:

```lua
Char.sprites = {
    up    = {"Overworld/Frisk/spr_f_maincharau_0.png", ...},
    down  = {"Overworld/Frisk/spr_f_maincharad_0.png", ...},
    left  = {"Overworld/Frisk/spr_f_maincharal_0.png", ...},
    right = {"Overworld/Frisk/spr_f_maincharar_0.png", ...},
}
```

!!! example "Sprite methods"
    - `Char.SetPlayerSprites(tab)` replaces the whole group. The table structure must match the above (one array per direction).
    - `Char.SetPosition(x, y, direction)` sets position and facing. Called automatically by the engine after the map loads.
    - `Char.Init()` creates the sprite and physics body. Called automatically when the map loads; generally no need to call manually.
    - `Char.Destroy()` destroys the sprite and physics body.

!!! tip "Swap the protagonist without changing code"
    These paths are all resolved by `Sprites`, so they follow the **standard Game-area-first** rule. <br>
    To use your own character, drop a same-named file into `Game/Resources/Sprites/Overworld/Frisk/` and it will be used automatically, without touching a single line of code (provided the **file names and frame counts match**). <br>
    A more thorough approach is `Char.SetPlayerSprites{...}` inside the scene to switch to another set of paths.

The sprite's **anchor point is at the feet**, so `Char.currentSprite.y` is `20` less than the physics body's `y` (half a body height). Use the sprite coordinate when fetching "where the player's feet are", and use `Char.collision.body` when fetching "where the collision body is".

---

## Properties

!!! example "Char properties"
    - `currentSprite` the current sprite object. `nil` before the player is spawned, so check for nil before writing scene logic.
    - `direction` current facing (`"up"` / `"down"` / `"left"` / `"right"`).
    - `controlling` whether the **player can be controlled**. Dialogue, menus, and the save page all set this to `false`.
    - `isMoving` whether the player actually moved this frame.
    - `animationFrame` / `animationTime` walking animation frame number and timer.
    - `x` / `y` the spawn (or most recent `SetPosition`) coordinates.
    - `collision.body` / `.shape` / `.fixture` the physics trio. The collision box is `38 x 20` by default.
    - `friskdance` whether the Frisk Dance easter egg is enabled (read from the global switch `EnableFriskDance`).
    - `frisk_dancing` whether it is currently dancing.

---

## Locking Control

All interfaces that "interrupt the player" are implemented via `Char.controlling`:

```lua
Char.controlling = false   -- player stops, no longer reads input
-- ... performance ...
Char.controlling = true    -- resume
```

`Overworld.dialogNew`, `Save.Show`, `Chest.Show`, and the `Stat` menu all maintain it themselves, so in normal flow you don't need to worry — **unless you wrote something that needs to freeze the player**.

!!! warning "Don't forget to unlock"
    If it's set to `false` and never restored, the player can never move again, with no error message.

---

## Frisk Dance

The original game's easter egg of "press up+down against a wall". The switch is on the global variable `EnableFriskDance`, which the engine reads into `Char.friskdance` at startup.

- **Start**: facing up, pressed against a wall, holding up+down at the same time.
- **Maintain**: keep holding up+down, and the **vertical position doesn't move** (i.e. still against the wall), and it keeps dancing — **sliding left/right doesn't count as interruption**.
- **Interrupt**: the moment the vertical position moves (walking away from the wall, getting pushed through, falling down…), or releasing up/down, it stops immediately and turns back to facing up.

While dancing, the character toggles between the `up` / `down` sprite groups, while still being able to walk left/right.

To turn it off, write in the scene:

```lua
Char.friskdance = false
```

---

## How Movement Is Implemented

`Char.Update` does four things each frame:

1. Read the four arrow keys, compute the velocity (±2 per frame).
2. Remember the **first direction pressed**; it won't be stolen by another direction until released — so to turn around you must release first.
3. Write the velocity into the physics body and let Box2D handle wall collisions.
4. Let the sprite follow the physics body and switch walking frames by velocity.

!!! tip "Why you must keep holding up"
    The engine determines "pressed against a wall" by: the physics body had **no vertical displacement** this frame. So pushing diagonally doesn't work — you must face the wall head-on first; likewise, the moment the vertical position slides during the dance, the check fails and the easter egg stops. <br>
    The check has a `0.5`-pixel tolerance, so the tiny jitter when against a wall won't falsely break it.

---

## Teleporting the Player

Without switching scenes, just move the player:

```lua
Char.collision.body:setPosition(x, y)   -- physics body
Char.SetPosition(x, y, "down")          -- sync the record
```

To switch scenes, use `Overworld.ChangeScene`. See [Interaction and Dialogue](./030_interact.md).
