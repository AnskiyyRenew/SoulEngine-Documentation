---
title: Beat
---

Align in-game events to the beat of the music.

Beat library path: `Scripts/Libraries/Beat.lua`

!!! warning "This is a standalone library you must wire up yourself"
    `main.lua` does **not** automatically load `Beat`, nor does it call `Update` for it every frame.<br>
    To use it, you must first obtain the module yourself, then advance it every frame:

    ```lua
    local beats = ImportFile("Beat")   -- equivalent to require("Scripts.Libraries.Beat")
    ```

---

## Basic Concepts

The music timeline is measured in **BPM (beats per minute)**:

- `beats.beat` is an accumulator starting at `0` that keeps growing with `Update`, representing "which beat we've reached."
- 1 beat = `60 / BPM` seconds. At `120 BPM` a beat is `0.5` seconds, at `180 BPM` it is `1/3` second.
- Integer beats are the common "beat 1, beat 2"; fractional beats (e.g. `2.5`) mean half a beat.

---

## Common Interfaces

### Set Speed `SetBPM(bpm)`

```lua
beats.SetBPM(180)   -- falls back to 120 when omitted or nil
```

### Advance Each Frame `Update(dt)`

**Must be called once per frame.** It is responsible for accumulating `beats.beat` and checking whether all registered events should trigger. Put it in the scene's `scene.update`:

```lua
function scene.update(dt)
    beats.Update(dt)
end
```

### Trigger Callback on Beat `CreateEvent(target, call, offset)`

Executes `call` once at beat `target`, then **auto-removes itself** (one-shot).

- `target` the target beat, supports fractional values.
- `call` the callback executed when the beat is hit.
- `offset` extra offset in **milliseconds**, positive means pushed later. When omitted, uses the module-level default `beats.offset` (default `0`).

```lua
beats.CreateEvent(4, function()
    print("beat 4")
end)

-- 200 milliseconds after beat 4
beats.CreateEvent(4, function()
    print("beat 4 +200ms")
end, 200)
```

### Beat Check `OnBeat(target)`

!!! danger "The current implementation has a pitfall; do not use it for timing"
    `OnBeat` internally uses floating-point **exact equality** (`beats.beat == target`), while `beats.beat` is a frame-by-frame accumulated float, which **almost never hits exactly**.<br>
    Testing: running 600 frames each at `60 / 30 / 144 FPS` produced `0` hits every time.<br>
    To "do something at a certain beat," use `CreateEvent` instead.

---

## Complete Example

The "execute a batch of events at a certain beat" style of `event.lua`, once wired up, looks roughly like this:

```lua
local beats = ImportFile("Beat")

function scene.load()
    beats.SetBPM(120)

    -- Beat 1: a batch of events fire together
    beats.CreateEvent(1, function()
        EventU1()
        EventU2()
        EventU3()
        EventU5()
    end)

    -- Beats 2, 2.5, 3, 3.5, 4: each fires once
    for b = 2, 4, 0.5 do
        beats.CreateEvent(b, Event2)
    end
end

function scene.update(dt)
    beats.Update(dt)
end
```

---

## Caveats

- **One-shot**: events registered with `CreateEvent` are immediately removed from the internal table after firing. To repeat, re-register.
- **State does not auto-reset**: `beats.beat` is an in-module accumulator; when switching songs or restarting a scene you must reset `beats.beat` to `0` yourself and re-set BPM as needed.
- **`offset` is converted by BPM**: the offset is converted to beats using the **current** BPM at trigger-check time, so changing BPM midway simultaneously affects the offsets of not-yet-fired events.
