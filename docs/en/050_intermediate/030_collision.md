---
title: Collision Library
---

The collision library handles the **detection** of "do two shapes overlap", without any movement or pushing.

Path: `Scripts/Libraries/Collisions.lua`

It is imported as the global `Collisions` in `main.lua`, so you can use it directly without your own `ImportFile`:

```lua
-- top of main.lua
Collisions = ImportFile("Collisions")
```

!!! note "There is also a lowercase alias"
    The compat layer `Scripts/Libraries/Engine/2_0.lua` additionally mounts `collisions` (all lowercase).
    The two are the same table, but it is better to **consistently write the uppercase `Collisions`** — easier to find and won't collide with local variable names.

---

## Shape table

Every function in the library describes a rectangle/ellipse with the same "shape table":

```lua
{
    x = 320,    -- center x (world coordinates)
    y = 240,    -- center y (world coordinates)
    w = 32,     -- width
    h = 32,     -- height
    angle = 0,  -- rotation angle, **unit is degrees**
    shape = "rect"  -- optional: "ellipse" = test this as an ellipse,
                    -- anything else (or missing) = rectangle
}
```

- `x` / `y` are the **center**, not the top-left corner.
- `angle` is in **degrees**; the function internally calls `math.rad` itself. Do not pass radians.
- `w` / `h` are edge lengths in a rectangle; in an ellipse they are the **diameters of the two axes** (see warning below).
- `shape` is optional and says which kind this table is: `"ellipse"` makes it an ellipse inscribed in that same `w × h` box, anything else (including the field being absent) is a rectangle. See [Rectangle or ellipse](#rectangle-or-ellipse-sethitboxshape).

---

## Method overview

!!! example "All methods"

    | Function | Detection | Note |
    |---|---|---|
    | `Collisions.FollowShape(sprite)` | —— | Convert a **sprite** into a shape table (carries the sprite's `shape`) |
    | `Collisions.RectangleWithPoint(rect, point)` | rectangle × point | point is `{x = , y = }` |
    | `Collisions.CircleWithPoint(circle, point)` | ellipse × point | see warning below, `w/h` used as radius |
    | `Collisions.RectangleWithRectangle(rect1, rect2)` | rectangle × rectangle | uses SAT, supports any rotation |
    | `Collisions.RectangleWithCircle(rect, circle)` | rectangle × ellipse | ellipse handled with `w/2` semi-axis |
    | `Collisions.CircleWithCircle(c1, c2)` | ellipse × ellipse | two perfect circles use fast distance check |
    | `Collisions.ShapeWithShape(a, b)` | **any × any** | picks the pair test from each side's `shape` |
    | `Collisions.ShapeWithPoint(shape, point)` | **any × point** | ditto; fixes `CircleWithPoint`'s unit for you |
    | `Collisions.ShapeName(name)` | —— | `"circle"` → `"ellipse"`, `"box"` → `"rect"`, unknown → `nil` |
    | `Collisions.IsEllipse(shape)` | —— | whether a shape table says `"ellipse"` |

    All return `true` / `false`, **without any displacement** (the last two return a string / boolean).

!!! danger "CircleWithPoint's w/h unit is inconsistent with other functions"
    `CircleWithPoint` internally does `local a, b = circ.w, circ.h` then checks `X²/a² + Y²/b² ≤ 1`, which means it treats `w/h` as **radius (semi-axis)**.
    Whereas `CircleWithCircle` and `RectangleWithCircle` both use `w/2`, treating it as **diameter**.

    For the same `{w = 16, h = 16}` shape:

    | Function | Actual coverage |
    |---|---|
    | `CircleWithPoint` | 32 × 32 |
    | `CircleWithCircle` / `RectangleWithCircle` | 16 × 16 |

    To work around it, pass values that are **already divided by 2** to `CircleWithPoint`:

    ```lua
    local c = {x = px, y = py, w = 8, h = 8, angle = 0}   -- want radius 8
    Collisions.CircleWithPoint(c, {x = mx, y = my})
    ```

---

## Combining with sprites: FollowShape

Writing a shape table by hand is tedious. The real usage in the engine is to **just throw a sprite in**:

```lua
local shape = Collisions.FollowShape(mySprite)
-- -> {x, y, w, h, angle, shape}
```

It reads these fields of the sprite:

| Sprite field | How it participates |
|---|---|
| `x` / `y` | World coordinates (**no camera transform applied**, consistent with the translation at draw time) |
| `width` / `height` | Original image size |
| `xscale` / `yscale` | Scale factor, `w = width * xscale` |
| `rotation` | Angle (degrees) |
| `xpivot_px` / `ypivot_px` | Pixel anchor, **priority when non-zero** |
| `xpivot` / `ypivot` | Ratio anchor, defaults to `0.5` (center) |
| `_hitbox_shape` | Copied into `shape`: `"ellipse"` makes the result an ellipse, default `"rect"` |

Internal logic (simplified):

```lua
-- 1. offset from anchor to image center, in world units after scaling
local dx = (width * 0.5 - ox) * xscale
local dy = (height * 0.5 - oy) * yscale

-- 2. rotate this offset by the sprite's rotation angle into world direction (local -> world)
data_tab = {
    x = x + dx * cosA - dy * sinA,
    y = y + dx * sinA + dy * cosA,
    w = math.abs(w),
    h = math.abs(h),
    angle = angle,
    shape = sprite._hitbox_shape or "rect"
}
```

!!! warning "`Scale()` is a factor, not pixels"
    `spr:Scale(2, 2)` enlarges the image to 2×, `w` becomes `width * 2`.
    Only for a 1×1 pure-white image like `px.png` does `Scale(155, 130)` equal exactly 155×130 pixels (the battle box is drawn this way). For normal sprites don't treat `Scale`'s arguments as pixels.

!!! warning "Negative scale is taken as absolute value"
    Both `w` / `h` go through `math.abs`. A sprite flipped horizontally (`xscale = -1`) keeps the same collision box size — which is correct, but if you use negative scale to mean "smaller", the collision box won't shrink with it.

---

## Real example in the engine: bullet hits Soul

`Scripts/Libraries/Battle/Player/init.lua`'s `Player.Update` checks every bullet each frame:

```lua
for _, b in ipairs(Sprites.images) do
    if (b.isBullet) then
        local coll_b = Collisions.FollowShape(b)
        -- the Soul's own box: the sprite's geometric rectangle; if `_hitbox` is set, shrink to that size
        local coll_p = Sprites.GetHitbox(Player.sprite)

        -- both shapes carry their own kind, so an "ellipse" bullet is tested
        -- as an ellipse and a normal one as a rectangle
        if (Collisions.ShapeWithShape(coll_b, coll_p)) then
            -- rough hit. When either side enabled perfect pixel (SetPPCollision(true)),
            -- the real answer comes from the rectangulated shape; nil means neither side enabled, so use the rectangle result.
            local pp = Sprites.PPCollide(b, Player.sprite)
            if (pp == nil or pp == true) then
                Battle.OnHit(b)
                break
            end
        end
    end
end
```

Five things worth learning in this code:

1. **Iterate `Sprites.images` filtered by `isBullet`** — this is the engine's convention field marking "I am a bullet", set on bones, cannons, homing shots when created.
2. **`Sprites.GetHitbox(sprite)` instead of hand-editing `w/h`** — it shrinks the sprite's geometric rectangle to `_hitbox` (defaults to `{4, 4}`). The sprite may have a 32×32 glowing edge, but the check only uses the center 4×4, which is the key to the UNDERTALE feel (Soul hitbox far smaller than the image).
3. **`FollowShape` only computes `x/y/angle`** — anchor and rotation are handled inside; size is left to `GetHitbox`.
4. **`PPCollide` is the "second gate"** — only after the rectangle check hits do you do the pixel-level recheck; the order must not be reversed (reversed would send a huge number of impossible-to-hit bullets into the pixel algorithm).
5. **`ShapeWithShape` instead of `RectangleWithRectangle`** — it reads the `shape` field both sides carry, so a round bullet marked `"ellipse"` is tested as a round bullet with no extra code here (see below).

### Change the Soul hitbox

```lua
Player.SetHitBox(width, height)           -- change main Soul
Player.SetHitBox(width, height, soulObj)  -- change a specific Soul object
```

Defaults to `{4, 4}`.

!!! warning "SetHitBox silently changes 0 and negative numbers to 1"
    The source is `local w = (width > 0 and width or 1)`. To "disable the hitbox" passing `0` becomes `1`, the hitbox still takes effect. To really disable it, you must skip the check loop yourself (e.g. temporarily set `isBullet` to false).

---

## Rectangle or ellipse: SetHitboxShape

A round bullet tested as a rectangle is hit on the four empty corners of its own box — the player takes damage while the art is nowhere near them. Until now the only answer was **perfect pixel collision**, which pays for a rectangulation pass (and a rectangle list compared every frame) to solve what a circle solves in one line.

`SetHitboxShape` is the cheap middle ground: the sprite keeps one box, and that box is tested as the **ellipse inscribed in it**.

```lua
bullet:SetHitboxShape("ellipse")   -- this bullet is round from now on
bullet:SetHitboxShape("circle")    -- same thing (synonym)
bullet:SetHitboxShape("rect")      -- back to the plain box (the default)
bullet:GetHitboxShape()            -- -> "ellipse" / "rect"
```

!!! example "The whole set"

    | Call | Note |
    |---|---|
    | `sprite:SetHitboxShape(kind)` | `"ellipse"` / `"rect"` (synonyms `circle` / `oval`, `rectangle` / `box`), returns `ok` |
    | `sprite:GetHitboxShape()` | current kind, `"rect"` when never set |
    | `Player.SetHitboxShape(kind, soulObj)` | same switch for a Soul; `soulObj` nil = main Soul |
    | `Collisions.ShapeWithShape(a, b)` | overlap test that reads each side's `shape` |
    | `Collisions.ShapeWithPoint(shape, pt)` | point test that reads `shape` |
    | `Collisions.ShapeName(name)` | normalises a name to `"rect"` / `"ellipse"`, `nil` when unknown |

    The kind is stored on `sprite._hitbox_shape` and copied into every shape table the sprite produces (`FollowShape`, `Sprites.GetHitbox`), so it follows the sprite through the whole pipeline.

```lua
-- a round bullet, no perfect-pixel needed
local orb = Sprites.CreateSprite("Bullets/orb.png", 0)
orb.isBullet = true
orb:SetHitboxShape("ellipse")
```

!!! note "The ellipse is inscribed in the same box"
    `w` / `h` keep their meaning: a 32×32 bullet becomes a circle of radius 16 — same center, same extremes, only the corners are gone. The switch can therefore only **shrink** a hit area, never grow it. To make one bigger, change `_hitbox` or the image size.

    A non-square box simply gives a non-circular ellipse (`w = 40, h = 20` → a 40×20 oval), and rotation is carried over from `angle`.

!!! warning "Unknown shape names are refused, not defaulted"
    `SetHitboxShape("elipse")` (typo) prints a warning and returns `false`, leaving the sprite on the kind it already had. A typo can never silently change how a bullet behaves.

!!! warning "Perfect pixel outranks the shape"
    Once **either** side has perfect pixel on, `Sprites.PPCollide` gives the answer — and pixel shapes are rectangles, so the ellipse setting is not consulted at all. For genuinely irregular art (jagged rocks, thin arrows) keep using PP; the ellipse is for "round / oval", where it costs a fraction of the price.

!!! tip "Cost, and how to see it"
    The ellipse test is one analytic test per pair — no rectangulation when the sprite is created, no rectangle list to walk each frame, no extra memory. Roughly what `RectangleWithRectangle` (SAT) already costs.

    The engine's bullet loop and `Collisions.ShapeWithShape` are already wired to it, so both sides work with no extra code. Press `F7` in battle (or `Battle.ToggleHitboxes(true)`) and an ellipse-marked sprite is outlined as an ellipse, with its box still faintly underneath.

---

## Perfect pixel collision

The above is all **rectangles and ellipses**. If the art is a weirdly shaped figure (irregular rock, jagged edge, thin arrow), the rectangle check will visibly "slip".

The engine has built-in **perfect pixel collision** (Pixel-Perfect, underlying library in `Scripts/Libraries/PerfectPixel/`). The idea: read the sprite's **real pixels**, rectangulate the opaque parts into a bunch of small boxes, then compare those boxes against each other.

!!! example "Toggle and query"
    - `sprite:SetPPCollision(enabled)` toggles pixel-level collision for this sprite, returns `(ok, rect_count)`.
        - `ok` whether a usable rectangulation result was formed (fails when the sprite is fully transparent).
        - `enabled` = `false` turns it off.
    - `sprite:IsPPCollision()` whether it is currently on.
    - `Sprites.PPCollide(a, b)` checks two sprites. Returns **three states**:

    | Return | Meaning |
    |---|---|
    | `nil` | **Neither side enabled** — caller should keep the rectangle check's conclusion |
    | `true` | At least one side enabled, and real pixels hit |
    | `false` | At least one side enabled, but real pixels **did not** hit (false positive from rough check) |

    - `Sprites.GetPPRects(sprite)` gets the rectangulation result in **image space** — a list `{{x, y, w, h}, ...}` (origin at sprite top-left, y down, no scaling/rotation applied), mainly for debugging.
    - `Sprites.GetPPShapes(sprite)` gets the result in **world space** — `{{x, y, w, h, angle}, ...}` isomorphic to `Collisions.FollowShape`, can be thrown directly into `Collisions.RectangleWithRectangle`.
    - `Sprites.ClearPPCache()` clears the pixel-cached sprites.

!!! note "Rectangles overlap, they are not a jigsaw"
    The rectangulation algorithm aims for "maximum coverage area", not slicing the figure into disjoint small blocks, so adjacent rectangles overlap each other.
    This does not affect the check (every rectangle is inside the figure, the union is those opaque pixels), but **do not use the rectangle count as an area estimate**.

!!! tip "Why return `nil` instead of `false`"
    So the caller can write it as one line:

    ```lua
    local pp = Sprites.PPCollide(bullet, player.sprite)
    if (pp == nil or pp == true) then
        Battle.OnHit(bullet)
    end
    ```

    When pixel collision is off, `pp` is `nil`, the condition holds → keep the rectangle result;
    once on, `pp` is the real `true` / `false` → pixels decide. **No need to check the toggle state outside.**

!!! example "Toggle the entire Soul at once"
    ```lua
    Player.SetPerfectPixel(true)    -- main Soul + all extra Souls on together
    Player.SetPerfectPixel(false)   -- off together
    ```

    The check loop in `Battle` is already wired to this chain (see the previous example), so you just flip the switch.

!!! warning "Enabling it makes the hitbox bigger, not smaller"
    The default `_hitbox` is `4×4` — **far smaller** than a 16×16 red heart.
    After enabling perfect pixel, the hitbox becomes the heart's **real opaque pixels** (area roughly 4× that of 4×4).
    The feel becomes noticeably "tighter". The original graze feel comes from the small hitbox, not from pixel-level checking — don't mix the two.

!!! tip "Debug with F7"
    Press `F7` in battle (or call `Battle.ToggleHitboxes(true)`) to draw the hitbox overlay;
    where perfect pixel is on, it draws the **real pixel outline** instead of a rectangle, so you can see at a glance which side computed wrong.

!!! warning "Performance: pixel recheck is far more expensive than rectangle"
    `Sprites.PPCollide` is only worth calling **after the rectangle rough check already hit** (that's how the engine writes it).
    Don't use it as the first filter to iterate hundreds of bullets. Also there are two backends:

    | Backend | Location | Note |
    |---|---|---|
    | C | `Scripts/Libraries/PerfectPixel/cpp.dll` | Fast, roughly **10×** faster than pure Lua |
    | Pure Lua | `Scripts/Libraries/PerfectPixel/pure.lua` | Auto-falls back when the C library is unavailable, same result just slower |

    Source is in `Scripts/Libraries/PerfectPixel/rectangulation.cpp`, with `init.lua` uniformly picking the backend.

    Both compute the "union of overlap regions", so you can only assert "what should not leak didn't leak, what should leak did leak", don't compare rectangle counts.

---

## Write your own collision

!!! example "Click a sprite (mouse × rectangle)"
    `Keyboard.GetMousePosition()` returns **world coordinates** (already adjusted for scale and camera), in the same coordinate system as `FollowShape`'s output, so you can compare directly:

    ```lua
    local btn = Sprites.CreateSprite("button.png", 0)
    btn:MoveTo(320, 400)

    function scene.update(dt)
        local mx, my = Keyboard.GetMousePosition()
        local shape = Collisions.FollowShape(btn)
        if (Collisions.RectangleWithPoint(shape, {x = mx, y = my})) then
            btn.color = {1, 1, 0}       -- hover highlight
        else
            btn.color = {1, 1, 1}
        end
    end
    ```

!!! example "Custom bullet check (ellipse × rectangle)"
    ```lua
    -- a spherical bullet, compared against the Soul (rectangle hitbox)
    local bullet = Sprites.CreateSprite("bullet.png", 0)
    bullet.isBullet = true
    bullet:MoveTo(320, 200)

    local shape_b = Collisions.FollowShape(bullet)
    local shape_p = Sprites.GetHitbox(Player.sprite)   -- auto-shrink to _hitbox (default 4x4)

    if (Collisions.RectangleWithCircle(shape_p, shape_b)) then
        -- if you want this bullet checked by real pixels, add a recheck after the rough hit
        local pp = Sprites.PPCollide(bullet, Player.sprite)
        if (pp == nil or pp == true) then
            Battle.OnHit(bullet)
        end
    end
    ```

    Note `Sprites.GetHitbox` returns a **brand-new shape table**; editing it won't affect the sprite itself;
    but if you want to manually override the size, just edit the returned `w` / `h` (the old code's
    `shape_p.w, shape_p.h = Player.sprite._hitbox[1], ...` is now equivalent to this line).

    Choosing the pair test by hand gets old fast. Mark the bullet once with
    `bullet:SetHitboxShape("ellipse")` and write `Collisions.ShapeWithShape(shape_b, shape_p)`
    instead — same result, and the engine's own bullet loop picks it up too.

!!! example "Pure hand-written shape (no sprite needed)"
    Trigger zones, invisible walls, damage ranges can all skip creating a sprite:

    ```lua
    local zone = {x = 500, y = 300, w = 120, h = 80, angle = 0}
    if (Collisions.RectangleWithPoint(zone, {x = Player.sprite.x, y = Player.sprite.y})) then
        -- entered the zone
    end
    ```

---

## Pitfalls

!!! warning "Only checks, does not push"
    This library has **no** collision response. To push the player out of a box, or to slide along a wall, you must write it yourself.
    The battle box's push logic is in `Scripts/Libraries/Battle/Arenas.lua`, and it is **implemented inline** without calling `Collisions`.

!!! warning "Rotated rectangles must use RectangleWithRectangle"
    Don't use AABB-style writing like `abs(dx) < w/2 and abs(dy) < h/2` to check a rotated box — after turning 45°, the result is completely wrong. `RectangleWithRectangle` uses SAT (Separating Axis Theorem), supporting any angle.

!!! warning "Overworld contact detection does not go through here"
    In Overworld, "walk next to an NPC and press Z to talk" / "step on a teleport point" is handled by Overworld's own `FindObject` / `getTouchResult` / `getInteractResult` (based on the Tiled object layer), unrelated to this library. See **[Overworld → Interaction and Dialogue](../040_overworld/030_interact.md)**.

!!! warning "Performance: with many bullets this is O(n), pixel recheck is even more expensive"
    `Player.Update` runs one `FollowShape` + one SAT per `isBullet` every frame.
    With bullets in the hundreds this is hundreds of trig operations per frame. On mobile keep the count down, or do your own rough filter first (compute the center distance, skip directly if beyond threshold).

    `Sprites.PPCollide` internally does a cheap AABB rejection first (`shapeHalfExtents`); the expensive rectangulation comparison only runs when bounding boxes intersect. But again: **rough check first, then pixels**, don't use it as the first filter.

    And if the art is just *round*: `sprite:SetHitboxShape("ellipse")` kills most corner false-positives at roughly rectangle cost, so reach for it before turning pixels on.

!!! warning "Ellipse and perfect pixel do not stack"
    `SetHitboxShape("ellipse")` only describes the **single** shape a sprite contributes. Once perfect pixel is on for either side, `Sprites.PPCollide` answers with the rectangulated pixels and the ellipse is ignored — pick one per sprite, don't expect both.

!!! warning "Coordinates are world coordinates, no camera"
    `FollowShape` explicitly does **not** go through `love.graphics.transformPoint`.
    The benefit is it is directly comparable to `sprite.x/y`; the cost is: if the sprite is under a scene with a `Camera` offset, the draw position and collision position are consistent (because the camera is applied at draw time), so don't worry about that —
    but if you manually applied a camera offset yourself, the two sides must be synchronized.
