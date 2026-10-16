---
title: Timer
---

Execute some code after a number of frames or seconds.

Timer library path: `Scripts/Libraries/Timer.lua`

!!! warning "Needs to be wired up manually"
    Like the Beat library, this repo's `main.lua` does **not** load `Timer`, nor does it call its `Update` every frame.<br>
    Before using it, obtain the module yourself and advance it every frame:

    ```lua
    local timers = ImportFile("Timer")   -- equivalent to require("Scripts.Libraries.Timer")
    ```

---

## Two Time Units

Timers come in two families; the only difference is whether they count in **frames** or in **seconds**.

| Purpose | By frames | By seconds |
|---|---|---|
| Execute at intervals | `runFrame` | `runSecond` |
| Execute continuously after delay | `duringFrame` | `duringSecond` |

The frame-based versions add `+1` to an internal counter each `Update`, so an interval of `60` means "every 60 frames"; the second-based versions accumulate `dt`, so `1.5` means "every 1.5 seconds."

---

## Execute at Intervals: `runFrame` / `runSecond`

```lua
timers.runFrame(func, interval, count)
timers.runSecond(func, interval, count)
```

- `func` the callback executed when due.
- `interval` the interval. `runFrame` is in **frames** (default `60`); `runSecond` is in **seconds** (default `1.0`).
- `count` how many times to execute in total (default `1`).

!!! example "Example"

    ```lua
    -- Triggers once every 30 frames, 4 times total
    timers.runFrame(function()
        print("tick")
    end, 30, 4)

    -- Triggers once every 0.5 seconds, 3 times total
    timers.runSecond(function()
        print("half second")
    end, 0.5, 3)
    ```

---

## Execute Continuously After Delay: `duringFrame` / `duringSecond`

```lua
timers.duringFrame(func, delay, during, afterfunc)
timers.duringSecond(func, delay, during, afterfunc)
```

Waits `delay` (frames / seconds) first, then executes `func` **every frame** for the next `during` (frames / seconds), then calls `afterfunc` once after the whole segment ends (optional).

- `delay` the delay, default `0`.
- `during` the duration, default `1`.
- `afterfunc` the end callback, may be omitted.

!!! example "Example"

    ```lua
    -- Wait 1 second, then run every frame for 2 seconds, then clean up
    timers.duringSecond(function()
        -- runs every frame
    end, 1, 2, function()
        -- end callback
    end)
    ```

---

## Advance Each Frame `Update`

```lua
function scene.update(dt)
    timers.Update(dt)
end
```

---

## The Returned Timer Object

All four functions above return a timer object that you can control mid-flight:

!!! example "Timer fields and methods"
    - `t.time` the current accumulation (frames or seconds).
    - `t.count` how many times it has fired.
    - `t.running` whether it is running (becomes `false` when paused).
    - `t.active` whether it is still alive (when `false`, it is reclaimed on the next `Update`).
    - `t:pause()` / `t:unpause()` / `t:togglePause()` pause / resume / toggle.
    - `t:isPaused()` whether it is paused.
    - `t:stop()` stop and reclaim immediately.
    - `t:restart()` reset and restart (both time and count return to the start).

```lua
local t = timers.runSecond(function()
    print("loop")
end, 1, 999)

t:pause()     -- don't run yet
t:unpause()   -- resume
```

---

## Caveats

- **Must `Update` every frame**: without calling it, the timer stays frozen in place forever.
- **The frame-based version follows the frame rate**: the "frames" of `runFrame` are determined by how often `Update` is called; dropped frames / different machines will change it accordingly. For stable rhythm, use `runSecond`.
- **Auto-reclaim**: `runFrame` / `runSecond` end on their own after firing `count` times; `during*` ends after the duration segment runs out. After ending, they are removed on the next `Update`.
