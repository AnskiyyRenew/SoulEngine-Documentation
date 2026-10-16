---
title: Sprites
---

All art assets are handled through the Sprite library.

<u>Some people may be used to calling a Sprite a "sprite sheet"; in fact they mean the same thing.</u>

Path of all sprites: `Resources/Sprites/`<br>
Sprite library path: `Scripts/Libraries/Sprites.lua`

If you want to **override** an engine-built-in sprite (e.g. replace the default `px.png`), just put your own same-named image into `Game/Resources/Sprites/`; the Game region takes priority, with the main directory as fallback.

---

## Creating a Sprite

Use `Sprites.CreateSprite(path, layer)` to create a sprite:

- `path` The sprite's path; lookup starts from `Resources/Sprites/` as the root directory, and you need to add the `.png` extension when creating.
- `layer` The sprite's Layer, which can be a `number` or a `string`. If the corresponding Layer is not found via the string, it will not error; instead it automatically sets the layer to 0.

!!! example "Creating an image"

    ```lua
    Sprites.CreateSprite("poseur.png", 0)
    ```

By default, this image is generated at the exact center of the screen, i.e. position `(320, 240)`.

---

## Sprite Properties

Properties are set in two types: `direct properties` and `method calls`.

In `direct properties`, we use a dot (`.`) to set properties;<br>
In `method calls`, we use syntactic sugar, using a colon (`:`) to set properties.

!!! tip "Direct properties"
    - `x` Horizontal coordinate of the image; larger means further right.
    - `y` Vertical coordinate of the image; larger means further down.
    - `rotation` Rotation angle of the image, in `degrees`; the image rotates clockwise as the angle increases.
    - `xscale` Horizontal scaling factor of the image, default `1`, meaning original size.
    - `yscale` Vertical scaling factor of the image, default `1`, meaning original size.
    - `layer` The image's Layer; a larger number means a higher Layer.
    - `velocity` The image's velocity; setting it once lets the image keep moving at that speed:
        - `x` Horizontal speed.
        - `y` Vertical speed.
        - `r` Rotation speed.
    - `xpivot` Horizontal pivot point of the image, default `0.5`, representing the horizontal center.
    - `ypivot` Vertical pivot point of the image, default `0.5`, representing the vertical center.
    - `xpivot_px` Horizontal pivot point of the image, set by pixels.
    - `ypivot_px` Vertical pivot point of the image, set by pixels.
    - `xanchor` Adjusts the horizontal offset relative to the parent object, when it has a parent.
    - `yanchor` Adjusts the vertical offset relative to the parent object, when it has a parent.
    - `color` The image's color, made of a table of three numbers `0 ~ 1`. For example `{1, 0, 0}`, representing red, green, blue respectively.
    - `alpha` The image's transparency, made of a number `0 ~ 1`; the smaller the number, the more transparent the image.
    - `visible` Whether the image is visible, default `true`.
    - `pixel_snap` Whether this image does pixel snapping. Defaults to following the global switch `sprites.pixel_snap` (default `true`); writing `true` / `false` directly overrides only this one. See "Pixel Snapping" below.
    - `outline` The image's outline color and thickness, made of five parameters `{r, g, b, a, thickness}`, representing `{red, green, blue, alpha, thickness}` respectively.
    - `follow_mode` Settings for following the parent object, supporting two: `position`: follow position only, parent rotation does not interfere; the second is `full`: follow both the parent's position and rotation.
    - `isBullet` Whether it is a damageable type (bullet type); a sprite becomes a bullet through this variable, default `false`.
    - `HurtMode` What type of damage the bullet deals, e.g.: orange, blue, red, green...

!!! tip "Method calls"
    - `GetPivotOffset()` Gets the current anchor's pixel offset.
    - `GetFilter()` Gets the rendering method currently used by the image.
    - `Dust(sound, remove, time)` Turns an image into dust.
        - `sound` Whether to play a sound effect.
        - `remove` Whether to remove the image after the dust animation finishes.
        - `time` How many seconds the dust animation plays.
    - `Outline(r, g, b, a, t)` Sets the sprite's border.
        - `r, g, b, a` Color and alpha, all values `0 ~ 1`.
        - `t` Border thickness; normally you can use `2`, thickening as needed.
    - `SetFourPointMode(enabled)` Whether to enable four-corner vertex mode, i.e. the common `leg stretch` deformation.
    - `SetFourPoint(p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y)` The coordinates of the four points in four-corner vertex mode; just fill them in order.
    - `SetFourPointP(index, x, y)` Sets the coordinate of the `index`-th point among the four to `(x, y)`.
    - `Move(x, y)` Moves the sprite at speed `(x, y)`.
    - `MoveTo(x, y)` Moves the sprite to position `(x, y)`.
    - `Set(p)` Sets the sprite's image to the image at path `p`. (Include the `.png` extension)
    - `SetAnimation(frames, interval, mode)` Sets the image's animation; animations are all composed of individual images.
        - `frames` The image sequence used by the animation.
        - `interval` How many seconds between each switch.
        - `mode` What mode the animation plays in, supporting `loop` loop, `oneshot` play once, `empty` play once and clear.
    - `Scale(x, y)` Sets the sprite's scaling size in horizontal and vertical directions to `(x, y)`.
    - `Pivot(x, y)` Sets the sprite's anchor offset in horizontal and vertical directions to `(x, y)`.
    - `PivotPixel(x, y)` Sets the sprite's anchor pixel offset in horizontal and vertical directions to `(x, y)`.
    - `Anchor(x, y)` With a parent object, sets the sprite's anchor offset in horizontal and vertical directions to `(x, y)`.
    - `AnchorPixel(x, y)` With a parent object, sets the sprite's anchor pixel offset in horizontal and vertical directions to `(x, y)`.
    - `SetParent(spr)` Sets a certain sprite as the current sprite's parent object; `spr` is a created sprite object.
    - `SetChildren(children)` Sets multiple sprite objects as the current sprite's child objects.
    - `AddChild(child)` Adds an additional child object `child` to the child group.
    - `RemoveChild(child)` Removes `child` sprite object from the child group.
    - `GetPosition()` Gets the image's coordinates, returns `x, y`, normally can be caught with two variables.
    - `GetPositionParent()` Gets the parent object's coordinates, returns `x, y`, normally can be caught with two variables.
    - `SetStencils(stencils)` Sets the sprite's Mask, multiple masks can be used.
    - `SetShaders(shaders)` Sets the sprite's Shader to `shaders`, multiple shaders can be used.
    - `GetShaders()` Gets the shaders in use.
    - `ClearShaders()` Clears all shaders of the sprite.
    - `AddShader(shader)` Adds an additional shader at the end.
    - `InsertShader(index, shader)` Inserts a shader at position `index`.
    - `RemoveShader(shader)` Removes the `shader` shader from the shader list.
    - `Solid(axis, box)` Adds a collision body to the sprite.
        - `axis` Can be `x` direction, `y` direction, or `xy` direction, representing having a collision volume only in this direction.
        - `box` Can fill `width` and `height` parameters, e.g.: `{width = 1, height = 1}`, this is a `1*1` collision box.
    - `UnSolid()` Removes the collision body from the sprite.
    - `IsSolid()` Returns whether the sprite currently has a collision body.
    - `GetImagePath()` Returns the image path currently used by this sprite (the resolved real path).
    - `GetAnimationPath()` Returns the current animation's frame sequence path, returns `nil` when there is no animation.
    - `SetPPCollision(enabled)` Toggles this image's **perfect pixel collision**, returns `(success, rectangle count)`. See "Perfect Pixel Collision" below.
    - `IsPPCollision()` Returns whether this image has perfect pixel collision on.
    - `SetHitboxShape(kind)` Collide as an **ellipse** instead of a rectangle: `"ellipse"` / `"rect"` (synonyms `circle` / `oval` and `rectangle` / `box`), returns `ok`. See below.
    - `GetHitboxShape()` Returns the current kind, `"rect"` when never set.
    - `Destroy() / Remove()` Deletes the sprite.

!!! example "Setting color and position"

    ```lua
    local a = Sprites.CreateSprite("poseur.png", 0)
    a.color = {1, 0, 0}
    a:MoveTo(320, 0)
    ```

    You will most likely see a red poseur with only its legs left at the top of the screen.

---

## Library-level Methods

All the above are methods of "a certain sprite"; the following are attached to the `Sprites` library itself:

!!! tip "Library-level methods"
    - `Sprites.CreateSpriteQuad(path, quad, layer)` Creates a sprite taking only the block specified by `quad` from the image; `quad` is filled as `{x = , y = , width = , height = }`. Useful for tileset cropping.
    - `Sprites.MultiDust(sprs, sound, remove, time)` Turns a **whole group** of sprites into dust together, diffusing across the bounding box, more natural than calling `Dust` one by one.
    - `Sprites.ShakeSprite(sprite, magnitude, duration, speed)` Shakes the sprite for a period of time. `magnitude` can be a number or `{x = , y = }`.
    - `Sprites.ShadowSprite(sprite, target_scale, duration, speed)` Generates a shadow that follows the sprite and scales up while fading out; returns that shadow sprite object.
    - `Sprites.GetCacheInfo()` Returns `(cache count, detail list)`, useful to see who is currently in the image cache.
    - `Sprites.CleanupCache()` Manually runs an LRU cleanup (under the normal flow the engine runs it automatically per `OPT_LRU_SPRITES`).

---

## Per-Frame Hook: Step

To make a sprite do something on its own every frame (drift, follow, self-destruct on a timer, ...), attach a `Step` function to it — the engine calls it every frame:

```lua
spr.Step = function (self, dt)
    -- once per frame
end
```

Bones and blue-soul platforms carry a hook with the same name (though without `dt`). Full details in [Step Hook](./170_step.md).

---

## Pixel Snapping

Pixel art most fears "half-pixel jitter": the sprite coordinate carries a decimal, and the sampled edges flicker bright and dark. The engine does this for you by default.

The global switch is `sprites.pixel_snap` (default `true`), and can also be changed with `Sprites.SetPixelSnap(enabled)`; a single image can override it itself:

```lua
sprites.pixel_snap = false      -- turn off globally
Sprites.SetPixelSnap(true)      -- turn on globally
spr.pixel_snap = false          -- let only this one through
```

The snapping rule is **snap the edges, not the center**: what actually gets rounded to an integer is the coordinate of the four **edges** of the quad, not the image's center point. These two only coincide exactly when the image size is even, so odd-sized sprites would be off by half a pixel if you just rounded the center.

For composite bodies (like bones made of head / body / tail pieced together) you must **round the shared anchor only once**: set each part to `pixel_snap = false`, then use `Sprites.SnapEdge(centre, offset)` to snap the anchor, then place the parts according to the anchor. If you let each part round on its own, the seams will misalign.

- `Sprites.SnapCoord(v)` Rounds a single number, equivalent to `math.floor(v + 0.5)`.
- `Sprites.SnapEdge(centre, offset)` Snaps the "edge" to an integer: `centre` is the center coordinate, `offset` is this edge's offset relative to the center (e.g. half-width), returns the snapped center coordinate.

!!! warning "Rotated sprites don't recognize 'edges'"
    Once a sprite is rotated, the quad is no longer parallel to the axes, so `SnapEdge` no longer applies. The correct approach for rotated parts is to leave snapping off, and ensure the geometry is exactly the same as it would be with snapping disabled.

---

## Perfect Pixel Collision

The default collision judgment uses a bounding box: a 32×32 heart-shaped image is judged as a 32×32 square. To make the judgment follow the sprite's real pixel shape, turn this on for that image:

```lua
spr:SetPPCollision(true)    -- returns ok, rectangle count
spr:SetPPCollision(false)   -- back to normal bounding box
spr:IsPPCollision()         -- query current state
```

!!! tip "Only need a circle? Skip the pixels"
    When the shape you want is just round or oval, `spr:SetHitboxShape("ellipse")` gets there with a single analytic test — no rectangulation pass, no rectangle list to walk each frame:

    ```lua
    spr:SetHitboxShape("ellipse")   -- this sprite is tested as an ellipse
    spr:SetHitboxShape("rect")      -- back to the box (default)
    spr:GetHitboxShape()            -- -> "ellipse" / "rect"
    ```

    The ellipse is inscribed in the same box, so it only ever removes the corners — see [Intermediate → Collision](../../050_intermediate/030_collision.md). Perfect pixel remains the tool for art an ellipse cannot describe.

The judgment itself uses `Sprites.PPCollide(a, b)`:

```lua
local ok = Sprites.PPCollide(bullet, Player.sprite)
-- true  = really collided
-- false = did not collide
-- nil   = neither side has perfect pixel on; use the bounding box conclusion
```

That is, it **only gives an answer when at least one side is on**; when it returns `nil`, do not treat it as "did not collide".

!!! warning "Judgment gets bigger once turned on"
    Perfect pixel judges using the sprite's **opaque pixels**. A 16×16 heart-shaped image with perfect pixel on will have a judgment range **much larger** than the default centered `{4, 4}` small box. If you want to "graze" use `_hitbox`; only turn this on when you want "shape-following" — pick one of the two.

Related helpers:

- `Sprites.GetPPRects(sprite)` Gets all rectangles of this image in local coordinates.
- `Sprites.GetPPShapes(sprite)` Gets the shapes after converting to world coordinates.
- `Sprites.GetHitbox(sprite)` Gets "bounding box + `_hitbox` override" in one step; the battle uses this for the Soul judgment.
- `Sprites.ClearPPCache()` Clears the rectangle cache. Call once after hot-reloading the library or sprite.

The underlying rectification algorithm is in `Scripts/Libraries/PerfectPixel/`, with two versions: a C backend (`cpp.dll`) and a pure Lua version (`pure.lua`); the former is about 10× faster and auto-enables when available. To turn on the F7 collision-box overlay to see the judgment shapes, see [Battle System → Battle Scene](../030_battle_system/070_scene.md).

---

## About Color

Here, color is divided into three basic colors `red, green, blue`, and all subsequent colors are mixed from these three.

Some commonly used colors are introduced below:

- `{1, 0, 1}` KR's big pink, mixed from red and blue in equal proportions.
- `{0.4, 0, 1}` Purple, but slightly deep blue.
- `{0, 1, 1}` Cyan bone color of blue attacks.
- `{1, 0.5, 0}` Orange attack.
- `{1, 1, 0}` Yellow confirm.

### Light and Dark Colors

When it comes to light and dark, we generally mix by adding white or black into a color, so we can do this:

Red is `{1, 0, 0}`, if you want a dark color, what should you do?<br>
The answer is to add `black` to this color, and black is `{0, 0, 0}`.

We start adding and taking the average:<br>

- `(1 + 0) / 2 = 0.5` The first color becomes 0.5.
- `(0 + 0) / 2 = 0` The second color becomes 0.
- `(0 + 0) / 2 = 0` The third color becomes 0.

Finally the dark red is: `{0.5, 0, 0}`.

We do the same for light colors:

- `(1 + 1) / 2 = 1` The first color becomes 1.
- `(0 + 1) / 2 = 0.5` The second color becomes 0.5.
- `(0 + 1) / 2 = 0.5` The third color becomes 0.5.

Finally the light red is: `{1, 0.5, 0.5}`.

**But normally, this mixing method may go too far, so you can change the added 1 to 0.5 etc.**

### Rainbow Color

Applying a periodic trigonometric transformation to `{r, g, b}`, and adjusting the phase, you can make a rainbow color effect.

```lua
r = math.sin(time / 8 + 0)
g = math.sin(time / 8 + 8)
b = math.sin(time / 8 + 16)
```

If you apply rgb to the color of an image, that image will start a rainbow color transformation.
