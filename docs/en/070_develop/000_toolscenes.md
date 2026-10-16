---
title: Tool Scenes
---

The engine ships some **helper tool scenes for development**, located in the `Scripts/Scenes/TOOL/` and `Scripts/Scenes/TEST/` directories. They are only used during development and are not part of the actual game flow; you can rewrite or even delete them at any time.

Like normal scenes, these are entered with `Scenes.switchTo`. To make one the startup scene, just change `FirstRoom` in `conf_pure.lua`:

```lua
Global.SetVariable("FirstRoom", "TOOL.TweenEase")
```

!!! note "Scene path notation"
    The dot in `Scenes.switchTo("TOOL.TweenEase")` corresponds to the folder hierarchy: `Scripts/Scenes/TOOL/TweenEase.lua` → `TOOL.TweenEase`. The `TEST` directory works the same way, e.g. `TEST.gb`.

---

## Bezier Easing Editor

The easing library's Bézier curves can be hand-written with control points, or sculpted **visually** with this scene.

Open the scene `TOOL.TweenEase`, and you'll see operation buttons on the left and a coordinate-system canvas on the right: **the horizontal axis is the time progress `t` (0~1), and the vertical axis is the eased output value (0~1)**. The more "bulged" the curve, the more pronounced the easing acceleration/deceleration.

### Meanings of the shapes on the canvas

| Shape | Meaning |
| --- | --- |
| Green square | Start/end anchors; the two ends of the curve must land on `(0,0)` and `(1,1)` |
| Orange dot | A middle control point that determines the curve's bend shape |
| Yellow halo | The currently selected point |
| Blue curve | The current Bézier easing curve |
| Gray diagonal | Linear reference line (`y = x`); the closer the curve hugs it, the closer to constant speed |

The curve is evaluated using the **De Casteljau algorithm**, so the number of control points can be increased or decreased freely, not limited to cubic Bézier.

### Left-side buttons

| Button | Action |
| --- | --- |
| `Add Point` | Add a new control point |
| `Delete Point` | Delete the currently selected control point |
| `Play Animation` | Play a preview animation once |
| `Export Animation` | Export the easing code |

### Instructions

- **Select / drag**: Left-click a point inside the canvas to select it and start dragging; the point's coordinates are clamped to the `[0,1]` range. Click empty space to deselect.
- **Add a point**: `Add Point` inserts a new point based on the current selection — when a middle point is selected, it inserts the midpoint between it and the next point; when nothing is selected, it inserts a point on the curve at `t = 0.5`.
- **Delete a point**: `Delete Point` requires selecting a middle control point first; **start/end anchors cannot be deleted**. Attempting to delete them prints `Cannot delete start or end anchor point` to the terminal. The keyboard `Delete` / `Backspace` also triggers deletion.
- **Play preview**: `Play Animation` moves a small red square along the curve from start to end; the canvas bottom shows `t` and `y` in real time, and a red vertical line marks the current progress.
- **Exit**: Press `Esc` to quit the game.

### Exporting code

After clicking `Export Animation`, the code is **printed to the terminal** and **written to `Debug/exported_bezier.lua`**. The exported content registers a custom easing named `myBezier` via `Tween.CreateCustomTween`, in the form below:

```lua
--[[
  Exported Bezier Easing Curve
  Paste this code into your project, then use:
  tween.CreateTween(setter, "myBezier", "", beginVal, endVal, duration)
--]]

Tween.CreateCustomTween("myBezier", function(t)
    local pts = {
        {x = 0.0000, y = 0.0000},
        {x = 0.3300, y = 0.6700},
        {x = 0.6700, y = 0.3300},
        {x = 1.0000, y = 1.0000},
    }
    local n = #pts
    local px, py = {}, {}
    for i = 1, n do
        px[i], py[i] = pts[i].x, pts[i].y
    end
    for level = n, 2, -1 do
        for i = 1, level - 1 do
            px[i] = px[i] * (1 - t) + px[i + 1] * t
            py[i] = py[i] * (1 - t) + py[i + 1] * t
        end
    end
    return py[1]
end)
```

After pasting this into your project, you can use it just like a normal easing:

```lua
Tween.CreateTween(function(value)
    print(value)
    poseur.x = value
end, "myBezier", "", 0, 600, 60)
```

### A simpler approach

If you just want a fixed-shape Bézier easing, the library also provides `Tween.CreateBezierEasing(name, points)`, which registers control points directly and is equivalent to the whole manual block above:

```lua
Tween.CreateBezierEasing("myBezier", {
    {x = 0,    y = 0},
    {x = 0.33, y = 0.67},
    {x = 0.67, y = 0.33},
    {x = 1,    y = 1},
})

Tween.CreateTween(function(value)
    print(value)
end, "myBezier", "", 0, 100, 60)
```

In other words: use the editor to **sculpt the shape**, then hand the exported control-point list to `CreateBezierEasing` — no need to keep that De Casteljau evaluation code around.

!!! tip "On easing names and direction"
    A custom easing's name itself does not distinguish type or direction; just pass the name directly as `CreateTween`'s `easingType` and leave the direction parameter as an empty string `""`.
