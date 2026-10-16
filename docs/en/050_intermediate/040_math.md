---
title: Math Tutorial
---

This page doesn't cover math derivations; it only covers **how to write it in SoulEngine and what it does**.

Three parts: absolute value → trigonometric function `A·sin(ωx + φ)` → matrix transform (the rotating box's Soul).

!!! warning "Unit convention: angles in the engine are always in 'degrees'"
    The sprite `rotation`, Arena's `angle`, the shape table's `angle` — all are **degrees**.
    But Lua's `math.sin` / `math.cos` only take **radians**.

    So the correct writing is always:

    ```lua
    math.sin(math.rad(30))   -- correct
    math.sin(30)             -- wrong! 30 radians ≈ 1718 degrees
    ```

    Use `math.deg` for the reverse direction. `math.atan2(dy, dx)` returns radians; convert back to degrees before writing into `rotation`.

---

## Absolute value

`math.abs(x)` flips negatives to positive. What it really expresses is three things.

### Distance

The difference `dx` between two coordinates may be positive or negative; "how far apart" only looks at the magnitude:

```lua
local dx = a.x - b.x
if (math.abs(dx) < 4) then
    -- already very close horizontally
end
```

Combined with `dy` it is the most common **rough distance check**. Note this is not a circular check (a real circle needs `dx*dx + dy*dy < r*r`), but as a "rough filter first" writing it is the cheapest.

### Symmetry

Make some effect symmetric left/right or up/down, or "the same no matter which way you move":

```lua
-- the further the Soul is from the box center, the redder (same on both sides)
local offset = math.abs(Player.sprite.x - arena.x)
Player.sprite.color = {1, 1 - offset / 200, 1 - offset / 200}
```

### Convergence

The "move a fixed step toward the target every frame" writing used everywhere in the engine (the **local** function `smooth_value` at the top of `Arenas.lua`, not mounted on the `Arenas` table):

```lua
local function smooth_value(value, target, speed)
    if (value > target) then return math.max(value - speed, target) end
    if (value < target) then return math.min(value + speed, target) end
    return value
end
```

There is no `abs` written here, but **the distance itself is `abs(target - value)`**, and to know "how many frames until it arrives" you must compute it. `Arenas.lua`'s `ResizeWithTime` reverses the speed this way:

```lua
local dw = math.abs(arena.target.width - arena.width)
arena.speeds.width = math.floor(dw / timew)   -- want to finish in timew frames
```

!!! example "Common combinations"

    | What to do | Writing |
    |---|---|
    | Clamp in a range | `math.max(min, math.min(v, max))` |
    | Check if close | `math.abs(a - b) < eps` |
    | Amount of change | `math.abs(target - current)` |
    | No error even with negative scale | `w = math.abs(width * xscale)` |

---

## Trigonometric function: `A · sin(ω·x + φ)`

### Memorize these values first

| Angle | `sin` | `cos` |
|---|---|---|
| 0° | 0 | 1 |
| 90° | 1 | 0 |
| 180° | 0 | -1 |
| 270° | -1 | 0 |
| 360° | 0 | 1 |

`sin`'s output always swings within `[-1, 1]`, one full circle of 360°.
`cos` is `sin` **shifted forward 90°** (`cos(x) == sin(x + 90°)`).

!!! warning "The screen's y axis points down"
    In math class y points up; on screen y points down. So `+sin` moves things **down**;
    to make something float up, write `-A * sin(...)` or use the `-y` direction.

### What each of the three parameters controls

```
y = A * sin(ω * x + φ)
    │      │       └─ φ (phase): where on the waveform to start
    │      └─ ω (angular speed): how fast one round trip is
    └─ A (amplitude): how big the swing is
```

| Parameter | Intuition | Unit |
|---|---|---|
| `A` | Half-width of the swing. `A = 20` means 20 pixels each side of center, 40 pixels total width | pixels (or whatever unit you use) |
| `ω` | One circle is 360°, so **period `T = 360 / ω`** | degrees / unit x |
| `φ` | Shifts the whole wave left/right. Two objects differing by φ differ in **when** they start | degrees |

What `x` is is up to you; the engine has two ready-made time sources:

| Variable | Meaning | Note |
|---|---|---|
| `Battle.TIME_F` | Frame count since battle start, +1 per frame | Simple, but speed follows frame rate |
| `Battle.TIME_R` | Seconds since battle start, +dt per frame | Frame-rate independent, recommended |

!!! example "How long one swing, what ω to fill"

    | Desired effect | With frames `TIME_F` | With seconds `TIME_R` |
    |---|---|---|
    | One round trip per second (60fps) | `ω = 6` | `ω = 360` |
    | One round trip per 2 seconds | `ω = 3` | `ω = 180` |
    | Half-second round trip (fast jitter) | `ω = 12` | `ω = 720` |
    | Engine wave1 effect | `ω = 1` (6 seconds per trip) | —— |

### Scenario 1: back-and-forth patrol

The engine's built-in `Scripts/Waves/bones/wave1.lua` is written exactly like this:

```lua
p.image.x = 320 + 20 * math.sin(math.rad(Battle.TIME_F))
```

Broken down: center `320`, `A = 20`, `ω = 1°/frame` → period 360 frames ≈ 6 seconds, `φ = 0`.
The bone slowly sways between x = 300 and 340.

To make it sway twice as fast and a bit bigger:

```lua
p.image.x = 320 + 60 * math.sin(math.rad(Battle.TIME_F * 3))
```

### Scenario 2: float up and down

Item pickups, hint arrows, "interactable here" light points all use this:

```lua
-- float ±6 pixels in place, one trip per 2 seconds
local t = Battle.TIME_R
arrow.y = arrow_y0 - 6 * math.sin(math.rad(t * 180))
```

!!! note "Why the minus sign"
    On screen larger y is lower, so `-sin` is "float up".

### Scenario 3: breathing scale

```lua
-- size breathes between 0.95× ~ 1.05×
local s = 1 + 0.05 * math.sin(math.rad(Battle.TIME_R * 180))
heart:Scale(s, s)
```

### Scenario 4: blink / invincibility frames

`sin`'s range is `[-1, 1]`; to turn it into `[0, 1]` opacity, write `0.5 + 0.5 * sin(...)`:

```lua
-- alpha pulses between 0.2 ~ 1.0
Player.sprite.alpha = 0.6 + 0.4 * math.sin(math.rad(Battle.TIME_F * 12))
```

To do a hard "blink on and off" (not a gradient), binarize the result:

```lua
local v = math.sin(math.rad(Battle.TIME_F * 8))
Player.sprite.alpha = (v > 0) and 1 or 0.3
```

### Scenario 5: a row of bones in a wave (phase φ)

A row of 10 bones, each starting **a bit later** than the previous, forms a wave.
The difference is all in `φ`:

```lua
for i = 1, 10 do
    local phi = i * 30                      -- each differs by 30°
    bone[i].y = 300 + 25 * math.sin(math.rad(Battle.TIME_F * 4 + phi))
end
```

φ differs by 30°, ω is 4°/frame, equivalent to "each bone moves 30/4 = 7.5 frames later than the previous".

### Scenario 6: circle / circular arrangement

`cos` controls x, `sin` controls y, together they are circular motion:

```lua
-- a bullet circles center (320, 320), radius 90, one lap per 3 seconds
local a = math.rad(Battle.TIME_R * 120)
bullet.x = 320 + 90 * math.cos(a)
bullet.y = 320 + 90 * math.sin(a)
```

To arrange N bullets in a ring (bullet ring), change `φ` to "each differs by 360/N degrees":

```lua
for i = 1, 12 do
    local a = math.rad(Battle.TIME_R * 120 + (i - 1) * 30)   -- 360 / 12
    local b = Attacks.New(...)
    b.x = 320 + 90 * math.cos(a)
    b.y = 320 + 90 * math.sin(a)
end
```

### Scenario 7: half period as easing

`sin` going from 0° to 180° is one full round trip of `0 → 1 → 0`.
Used as "progress", it is a natural **ease-in-ease-out**:
slow at both ends, fast in the middle, no Tween needed.

```lua
-- t goes 0 to 1, value rises to 1 then falls back to 0
local t = progress            -- 0..1
local v = math.sin(math.rad(t * 180))
```

For a one-way `0 → 1` that is **slow at start and slow at end**, use the `cos` variant:

```lua
-- (1 - cos) / 2 : t=0 -> 0, t=1 -> 1, flat at both ends
local v = (1 - math.cos(math.rad(t * 180))) / 2
```

!!! note "How to choose against Tween"
    `Tween` is good for "go from A to B, end when you arrive"; `sin` is good for "loop forever, need the current value anytime".
    Continuous motion in Waves basically all uses `sin`; one-time performances use `Tween`.

### Scenario 8: decaying shake

A shake should "get smaller as it goes", done by shrinking `A` itself:

```lua
shake_time = 30                                  -- shake for 30 frames
-- each frame:
if (shake_time > 0) then
    local amp = shake_time / 30 * 8              -- amplitude 8 -> 0
    sprite.x = base_x + amp * math.sin(math.rad(shake_time * 30))
    shake_time = shake_time - 1
else
    sprite.x = base_x
end
```

### Pitfalls

!!! warning "Driving with frame count, speed follows frame rate"
    `math.sin(math.rad(Battle.TIME_F * 6))` is one trip per second at 60fps, but **0.5 seconds per trip** on a 120fps high-refresh screen.
    For frame-rate independence, uniformly use `Battle.TIME_R * 360 / seconds`.

!!! warning "Don't forget to multiply by A"
    `math.sin(...)` returns a value between ±1; writing it directly into `x` moves only 1 pixel.
    If "the animation is barely visible", check this item first.

!!! warning "sin's phase is added inside ω·x"
    To "start 0.5 seconds late", it is not `sin(ω*x) + 0.5`, but `sin(ω*x + ω*0.5)`.

---

## Matrix transform: rotating box

This is the hardest part of the page, but also the **Soul of the battle box**.
Understand it and the big block of coordinate math in `Arenas.lua` is all the same pattern.

### What problem to solve

The battle box rotates: `arena.rotation = 30`.
After rotating, "is the Player inside the box" can no longer be judged with `x > left and x < right` — the box edges are no longer horizontal and vertical.

**The idea is not to compute the slanted edges, but to rotate the point "back" into the box's local coordinate system.**
In the box's own coordinate system, it is a proper, un-rotated rectangle:

```
      World coordinates (box rotated 30°)     Local coordinates (box not rotated)
        ／￣￣￣￣＼                    ┌────────┐
       ／    ·P    ＼        ==>        │   ·P    │
       ＼          ／                   │         │
        ＼＿＿＿＿／                    └────────┘
     All four edges are slanted        Four edges horizontal/vertical, compare directly
```

### Two formulas (just memorize them)

Let the box center be `(cx, cy)`, rotation angle `θ`, `cos = cos(θ)`, `sin = sin(θ)`.

**World → Local** (use this to judge "is the point in this slanted box"):

```lua
local dx, dy = px - cx, py - cy
local lx = dx * cos + dy * sin      -- local x
local ly = dy * cos - dx * sin      -- local y
-- then treat the box as un-rotated:
local inside = (lx >= -w/2 and lx <= w/2 and ly >= -h/2 and ly <= h/2)
```

**Local → World** (use this when you know some position on the box and want to compute where it is on screen):

```lua
local wx = cx + lx * cos - ly * sin
local wy = cy + lx * sin + ly * cos
```

!!! tip "Memory trick"
    Local → World is the standard rotation matrix:

    ```
    [ wx ]   [ cos  -sin ] [ lx ]
    [ wy ] = [ sin   cos ] [ ly ]
    ```

    World → Local is its **inverse matrix**, and the inverse of a rotation matrix = its transpose (flip the sign of sin):

    ```
    [ lx ]   [  cos  sin ] [ dx ]
    [ ly ] = [ -sin  cos ] [ dy ]
    ```

    So the two formulas look almost the same, only the sign of `sin` changed. That is the entire content of "matrix transform" in this codebase.

### A computable example

The box is at `(320, 320)`, width 155, rotated 30°. Where is its **right edge midpoint** on screen?

- Local coordinates: `(77.5, 0)` (half the width, horizontal)
- `cos30 ≈ 0.866`, `sin30 = 0.5`

```lua
wx = 320 + 77.5 * 0.866 - 0 * 0.5 = 387.1
wy = 320 + 77.5 * 0.5   + 0 * 0.866 = 358.75
```

The right edge midpoint ends up at `(387, 359)` — to the right **and down**, which is exactly what a 30° clockwise rotation should look like.

---

### Five real code spots in the engine

The same matrix appears five times in the engine:

??? example "① Judge if a point can stand — `Arenas.lua`'s `is_point_valid`"
    ```lua
    local dx, dy = px - a.x, py - a.y
    local cos, sin = math.cos(math.rad(a.rotation)), math.sin(math.rad(a.rotation))
    local lx = dx * cos + dy * sin
    local ly = dy * cos - dx * sin

    -- after that it's a normal rectangle comparison (shrunk in by 8 pixels, because the Soul is 16×16)
    if (lx >= -w / 2 + 8 and lx <= w / 2 - 8 and ly >= -h / 2 + 8 and ly <= h / 2 - 8) then
        in_plus = true
    end
    ```

    Note this is a **file-level local function** (`local function is_point_valid`), not mounted on the `Arenas` table, and not exported globally — so you can't get it from outside, only be indirectly affected by its behavior through `Arenas`'s public behaviors.

??? example "② Push the Player out of the minus box — compute locally then rotate back to world"
    In `Arenas.lua` it is **inlined**, with no separate function name, but every line is those two formulas:

    ```lua
    -- world -> local: lx = dx·cos + dy·sin , ly = dy·cos − dx·sin
    while ((p.x - arena.x) * math.cos(math.rad(arena.rotation))
         + (p.y - arena.y) * math.sin(math.rad(arena.rotation)) < -w / 2 + 8) do
        ...
    end

    -- after the loop, rotate back to world
    p.x = arena.x + lx * cos - ly * sin
    p.y = arena.y + lx * sin + ly * cos
    ```

    The `cos` / `sin` in this block are recomputed every loop iteration, because `arena.rotation` may be changed mid-way.

??? example "③ Get a point on the box — `GetCornerPos` / `GetCenterPos`"
    Both methods use "compute the local offset first, then rotate to world":

    ```lua
    -- GetCornerPos: the corner's local coords are just a (±corner_x, ±corner_y), then rotate out
    res[1] = arena.x + corner_x * cos - corner_y * sin
    res[2] = arena.y + corner_x * sin + corner_y * cos
    ```

    `GetCenterPos(side)` looks a bit different (written as `arena.x + length * sin` / `arena.y - length * cos` cross form), but it is the same matrix in another form — `side == "up"` takes "the top edge midpoint of the rotated box":
    `Arena:GetCenterPos("up")` correctly follows rotation, and that is why.

??? example "④ Sprite to shape — `Collisions.FollowShape`"
    ```lua
    -- anchor offset relative to image center (dx, dy), rotated to world by the sprite's rotation angle
    x = x + dx * cosA - dy * sinA
    y = y + dx * sinA + dy * cosA
    ```

    The collision library uses the same matrix too, see **[Collision Library](./030_collision.md)**.
    The `imageRectsToWorld` inside the perfect-pixel collision set (`Sprites.GetPPShapes`) is a **verbatim copy** of this formula, so both check paths must describe the same box.

??? example "⑤ 3D bones too — `Attacks/Bones.lua`'s `_rotateZ`"
    ```lua
    return {
        center[1] + x * cos_a - y * sin_a,
        center[2] + x * sin_a + y * cos_a,
        point[3]
    }
    ```

    `_rotateX` / `_rotateY` / `_rotateZ` are all essentially the **same 2×2 matrix**, just applied to the three different axis pairs (y,z), (x,z), (x,y).

---

### After the Soul rotates: the probe

The blue Soul "flips over" (gravity points up), implemented by setting `Player.sprite.rotation` to 180.
Then "below the feet" is no longer at the bottom of the screen, but at the **local** bottom.

`Arenas.PlayerOnGround` is written like this:

```lua
local psin, pcos = math.sin(math.rad(player.rotation)), math.cos(math.rad(player.rotation))
return side_touching(player, -psin * 10, pcos * 10)
```

The probe offset `(-sin θ, cos θ) * 10` is the "local down" direction in world space:

| Soul rotation | Probe direction | On screen |
|---|---|---|
| 0 | `(0, 10)` | below feet ↓ |
| 90 | `(-10, 0)` | left ← |
| 180 | `(0, -10)` | top of head ↑ |
| 270 | `(10, 0)` | right → |

**One matrix transform handles all four gravity directions.**

!!! warning "`PlayerOnCeiling` flips BOTH x and y components' signs"
    Not just x reversed:

    ```lua
    -- PlayerOnGround
    return side_touching(player, -psin * 10,  pcos * 10)
    -- PlayerOnCeiling
    return side_touching(player,  psin * 10, -pcos * 10)
    ```

    Each component flips its sign once, because that is the **180°** opposite direction, not a mirror.
    Changing only one component gives a "side", the probe points left/right, and the judgment is naturally all wrong.

### Order of transforms

The correct order is always **scale → rotate → translate**:

1. First take the point by local size (`w/2`, `h/2`) — scale is already baked into `w/h`
2. Then multiply by the rotation matrix
3. **Last** add the center coordinates `cx, cy`

!!! warning "Translating before rotating flings the box away"
    Writing `x = (px + dx) * cos - ...` is wrong.
    Translation must be the final step.

---

### Pitfalls

!!! warning "Wrong angle unit"
    The box's `rotation` is degrees; the matrix wants radians. Forgetting `math.rad` usually results in "the box spinning wildly", because 30 radians ≈ 1718 degrees.

!!! warning "Positive angle is clockwise on screen"
    Because the y axis points down. `rotation = 90` is not "rotate 90° counterclockwise", it is visually 90° clockwise. Consistent with LÖVE's `love.graphics.rotate`.

!!! warning "Rotated rectangle can no longer use AABB"
    `abs(dx) < w/2 and abs(dy) < h/2` only holds for an un-rotated box.
    Either go through the local coordinates above, or use `Collisions.RectangleWithRectangle` (internally SAT).

!!! warning "Arenas' speeds do not multiply by dt"
    ```lua
    arena.rotation = smooth_value(arena.rotation, arena.target.rotation, arena.speeds.rotation)
    ```

    Here `speeds.rotation = 15` is **15 degrees per frame**, not per second.
    On a 120Hz machine the rotation is twice as fast. For frame-rate-independent rotation, scale `speeds` by `dt` yourself outside.

!!! warning "Scale only reads xscale/yscale"
    `FollowShape`'s `w = width * xscale` only looks at the sprite's own scale field, not parents, not layer scale. For a sprite under a parent node, multiply in the parent's factor yourself.
