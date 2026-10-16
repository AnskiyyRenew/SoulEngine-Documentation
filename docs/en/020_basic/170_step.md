---
title: Step Hook
---

`Step` is not a library function — it is a **convention field**: attach it to an object, and the engine calls it once per frame whenever it finds it there.

Three places in the engine know about it: sprites (`Scripts/Libraries/Sprites.lua`), bones (`Scripts/Libraries/Attacks/Bones.lua`) and blue-soul platforms (`Scripts/Libraries/Battle/Player/init.lua`).

| Host | Signature | Who calls it | When |
|---|---|---|---|
| Sprite `sprite` | `function (self, dt)` | `Sprites.Update(dt)`, called automatically every frame by `main.lua` | After velocity is applied, before the animation advances |
| Bone `bone` | `function (self)` **no dt** | `bones.Update(dt)`, called manually from the wave | After position / rotation / part layout is fully resolved |
| Platform `platform` | `function (self)` **no dt** | `Player.UpdatePlatforms(dt)` | After the platform moves and `Sync()`s, before the ground check |

!!! note "It is not the same thing as Update"
    `Update` is the engine's own per-frame flow — you should not and cannot override it; `Step` is the slot the engine leaves for you in the middle of `Update`.<br>
    So never call `self:Update(dt)` from inside `Step`.

---

## Step on a Sprite

### Usage

```lua
local spr = Sprites.CreateSprite("poseur.png", "Map")
spr.Step = function (self, dt)
    -- runs here every frame
end
```

Removing the hook is just assigning `nil`: `spr.Step = nil`.

### Where it sits in the frame

`Sprites.Update(dt)` in `main.lua` walks every sprite in **reverse** order and calls `sprite:Update(dt)` on each. Inside `Update` the order is:

1. Reset `speed` / `is_moving`
2. Parent anchor (`parent` together with `follow_mode`)
3. Velocity displacement (`velocity` × `move_speed`)
4. **Call `self:Step(dt)`**
5. Advance the animation frame (`animation`)
6. Dust timer (`_dust`), shake offset (`_shake`)
7. Sync the solid body to the current position (`_solid`)

!!! example "Two conclusions follow"
    - Changing `x` / `y` / `rotation` inside `Step` is **final** — nothing later in the pipeline overwrites the coordinates.
    - Calling `self:Set(...)` inside `Step` is safe too: `Set` clears the running animation sequence on the way (see `Set` in `Sprites.lua`), so you won't get "swapped in, then overwritten by the next animation frame".

### Example: scale up, fade out, self-destruct

```lua
local shadow = Sprites.CreateSprite(Player.sprite.path, Player.sprite.layer)
shadow:MoveTo(Player.sprite:GetPosition())
shadow.Step = function (self)
    self:MoveTo(Player.sprite:GetPosition())
    self:Scale(
        self.xscale + (2 - self.xscale) / 8,
        self.yscale + (2 - self.yscale) / 8
    )
    self.alpha = self.alpha - 0.05

    if (self.alpha <= 0) then
        self:Destroy()
    end
end
```

That is the body of `Player.AddParticle()` (`Battle/Player/init.lua`) — the burst of afterimages when the soul switches.

### Example: frame-rate independent smoothing with dt

```lua
shadow.Step = function (self, dt)
    self:MoveTo(st.source:GetPosition())          -- follow the source

    local factor = math.min(1, (dt or 0) * 8)     -- dt-safe exponential approach
    self:Scale(
        self.xscale + (2 - self.xscale) * factor,
        self.yscale + (2 - self.yscale) * factor
    )

    st.time = st.time - (dt or 0)
    if (st.time <= 0) then
        self:Destroy()
    else
        self.alpha = st.base_alpha * (st.time / st.duration)
    end
end
```

The body of `Sprites.ShadowSprite()` (`Sprites.lua`). **This is what `dt` is for** — don't hardcode a fixed step like "+1 per frame", or the speed will drift with the frame rate.

---

## Step on a Bone

```lua
local bone = bones.New2D("sans", 60, {320, 240}, 0, {2, 0})
bone.Step = function (self)
    -- note: no dt
    self.rotation = self.rotation + 1
end
```

- **Call site**: inside `bones.Update(dt)`, after the bone's displacement, rotation, length and head/body/tail layout are **all** resolved. So changes to `self.x` / `self.rotation` / `self.length` inside `Step` only show up **next frame** (the engine comments state this is deliberate, matching the original).
- **You must call `bones.Update(dt)` yourself every frame** (see [Bullet Library → Bones](../030_battle_system/060_bullets.md)). Skip it and the bones neither move nor collide — and `Step` never runs once.
- Only composite bones call `Step`, i.e. the ones made by `New2D` / `New3D` (they have `concat = true` internally).

!!! warning "Bones get no dt"
    A bone's `Step` receives **no arguments at all**. For time-dependent logic, accumulate it yourself in the wave:

    ```lua
    local time = 0
    function wave.Update(dt)
        time = time + dt
        bones.Update(dt)
    end
    ```

    For delays and tweens use `Timer` or `Tween` instead — don't expect `Step` to hand you time.

---

## Step on a Platform

```lua
local p = Player.BluePlatform(320, 320, 60, {speed = {x = 1, y = 0}})
p.Step = function (self)
    -- the platform already moved and its highlight line synced; ground check hasn't run yet
    if (self.image.x > 500) then
        self.speed.x = -1
    end
end
```

`Player.UpdatePlatforms(dt)` runs: move by `platform.speed` → `Sync()` the highlight line → `platform:Step()` → soul ground check. Anything you want to do "after the platform has moved" (turn around at a boundary, disappear periodically, ...) belongs here. Again, **no dt**.

---

## Common Patterns

| Goal | How |
|---|---|
| Run once | `self.Step = nil` at the end of the function |
| Self-destruct when due | `self:Destroy()` when the condition hits |
| Timing | `self._t = (self._t or 0) + dt` |
| Frame-rate independent smoothing | Interpolate with `dt`, never a fixed step |
| Drop the hook temporarily | `obj.Step = nil` |

---

## Caveats

- **Step runs before `scene.update`.** `main.lua`'s order is `Tween` → `Sprites` → `Typers` → ... → `scene.update`. So input read inside `Step` is from the **previous frame**; the scene hasn't computed this frame yet.
- **Pausing does not stop Step.** `main.lua` only guards `scene_.update` behind `pausing`; `Sprites.Update(dt)` keeps running. If you need to freeze, check it yourself.
- **Sprites are walked in reverse** (`#sprites.images → 1`), so calling `self:Destroy()` inside `Step` is safe — the engine's own afterimages end that way.
- After `Destroy()` the object is removed from the list, so `Step` simply stops being called; no stray callbacks.
- **Don't do heavy work in Step.** It runs once per object per frame; a few hundred bones each carrying a heavy `Step` will eat the frame budget outright. If it can be done once at the wave / scene level, don't push it down to every object.
