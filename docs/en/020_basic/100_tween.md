---
title: Tween
---

Use the tween library to enrich various animations.

Tween library path: `Scripts/Libraries/Tween.lua`

---

## Create a Tween Task

Use `Tween.CreateTween(variableSetter, easingType, direction, begin, final, duration, delay, destroyAfter)` to create a tween task operation.

- `variableSetter` callback function that **keeps executing** during the tween.
- `easingType` the type of easing, e.g. `Quad`, `Bounce`, etc. Case-insensitive (all lowercase supported).
- `direction` the direction: `In`, `Out`, or `InOut`. Case-insensitive.
- `begin` the starting value of the tween.
- `final` the final value of the tween.
- `duration` the duration of the tween task (in frames).
- `delay` the delay before the tween task starts (in frames).
- `destroyAfter` how many frames after starting the tween task is cleared (in frames). Defaults to `duration`; it is automatically reclaimed once finished.

!!! example "Image example"
    The following example moves `poseur` from x = `320` to `600` via a 60-frame `bounce out` tween.

    During the movement you will see the terminal constantly printing `poseur.x` until the animation ends after `60` frames.

    ```lua
    local poseur = Sprites.CreateSprite("poseur.png", 0)
    Tween.CreateTween(
        function(value)
            print(value)
            poseur.x = value
        end,
    "Bounce", "Out", poseur.x, 600, 60)
    ```

!!! example "Any variable example"
    Since the first parameter of `CreateTween` is a callback function, you can assign any variable you want inside it.

    In the code below you can see `poseur` turning red-hot after `60` frames.

    ```lua
    local poseur = Sprites.CreateSprite("poseur.png", 0)
    Tween.CreateTween(
        function(value)
            poseur.color = {value, 0, 0}
        end,
    "Quad", "Out", 0, 1, 60)
    ```

---

## Custom Tweens

### Function Easing

Use `Tween.CreateCustomTween(name, easingFunc)` to define a custom tween.

!!! example "Example"

    ```lua
    Tween.CreateCustomTween("smooth", function(t)
        return t * t * (3 - 2 * t)
    end)

    Tween.CreateTween(function(value)
        print(value)
    end, "smooth", "", 0, 100, 60)
    ```

### Bézier Easing

You can either hand-roll a Bézier easing or generate it from a scene.

For scene-based generation, see **[Developer Tools → Tool Scenes](../070_develop/000_toolscenes.md)**.

Use `Tween.CreateBezierEasing(name, points)` to create a Bézier curve easing.

`points` format:
```
{
    {x = 0, y = 0},
    {x = ..., y = ...},
    {x = 1, y = 1},
    ......
}
```

Summary: the start point must be `0` and the end point must be `1`.

!!! example "Example"

    ```lua
    Tween.CreateBezierEasing("mybezier", {
        {x = 0, y = 0},
        {x = 0.25, y = 0.1},
        {x = 0.25, y = 1},
        {x = 1, y = 1},
    })

    Tween.CreateTween(function(value)
        print(value)
    end, "mybezier", "", 0, 100, 60)
    ```
