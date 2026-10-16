---
title: Object Debugger
---

`Debugger` is an **in-game object debugger** that lets you click, drag, and edit properties of sprites directly on screen while the game is running, and export the tuned parameters as code. It's ideal for positioning, testing scale, experimenting with colors, and pulling four-point deformations — saving you from repeatedly editing code and restarting.

Library path: `Scripts/Libraries/Engine/Debugger.lua`

!!! warning "Development build only"
    This is a development tool, loaded only when `_RELEASED` is `false` (see `conf.lua`, imported by `main.lua`). It is not loaded in packaged release builds, so there's no leftover to worry about.

---

## Hotkeys

| Key | Action |
| --- | --- |
| `Ctrl` + `D` | Toggle debug mode (enter / exit interaction state) |
| `F9` | Toggle the opacity of the on-screen info text (show / hide) |

When exiting debug mode, the property panel, the right-click menu, and any four-point handle being dragged are all automatically collapsed.

!!! tip "Why it can block your view"
    The purpose of `F9` is to let you hide that pile of object-property text covering the screen with one key, so you can see the result on a clean picture; open it again when needed.

---

## Selection and dragging

After entering debug mode:

- **Left-click** an object to select it; the selected object gets a red border drawn around it.
- Once selected, **hold left-click and drag** to move the object (there is a small drag threshold, so a slight click won't move it by accident).
- Click empty space to deselect.

After selecting an object, all of its fields are **printed item by item in the top-left of the screen**, so you can inspect its values in real time.

---

## Right-click menu

After selecting an object, **right-click** opens a context menu. When the menu gets close to a screen edge it automatically flips / collapses to stay fully visible inside the screen.

| Menu item | Action |
| --- | --- |
| `Clone` | Create another object with the same path and layer |
| `Export` | Export the current object as code (see below) |
| `Delete` | Destroy the object |
| `flip X` / `flip Y` | Flip horizontally / vertically (negate the scale in that direction) |
| `Rotate 90°` / `Rotate -90°` | Rotate ±90 degrees |
| `Properties` | Show / hide the right-side property panel |
| `Toggle Four-Point` | Toggle four-point deformation mode |
| `Reset Corners` | Reset the four corners of the four-point deformation to the object's original rectangle |

---

## Property panel

Opened via the `Properties` item in the right-click menu, located on the right side of the screen. You can **edit directly** these fields:

`X`, `Y`, `ScaleX`, `ScaleY`, `Rot` (rotation), `Alpha` (opacity).

Editing: **click a field** to start editing, type numbers, decimal points, and the minus sign directly, press `Backspace` to delete, `Enter` to apply, `Esc` to cancel.

If the object has a `color` field, a **color swatch** also appears at the bottom of the panel; click a swatch to change the object's color in real time, and the swatch for the current color gets a highlighted outline.

---

## Four-point deformation

When an object supports four-point deformation (has the `_four_point` field), you can enable it and drag the four corners to stretch and apply perspective freely.

Each handle has its own color for distinction:

| Handle | Position | Color |
| --- | --- | --- |
| `TL` | Top-left | Red |
| `TR` | Top-right | Green |
| `BL` | Bottom-left | Blue |
| `BR` | Bottom-right | Yellow |

- Click and drag a handle to move that corner.
- When four-point deformation is on, dragging the object body moves all four corners together as one.
- `Reset Corners` in the property panel restores the four corners to the object's original rectangle.

---

## Exporting objects

The `Export` item in the right-click menu writes the current object's full state as runnable code, output to `Debug/exported_object.lua`, and also printed to the terminal. The generated form is roughly:

```lua
-- Exported by Debugger
local spr = Sprites.CreateSprite("poseur.png", 0)
spr:MoveTo(320, 240)
spr:Scale(1, 1)
spr.rotation = 0
spr.alpha = 1
spr.color = {1, 1, 1}
spr.visible = true
spr:SetFourPointMode(true)
spr:SetFourPoint(
    260, 200,  -- top-left
    380, 200,  -- top-right
    260, 280,  -- bottom-left
    380, 280   -- bottom-right
)
```

Paste it into your scene code to reproduce the object you tuned.

---

## Making a sprite ignored

Some sprites are not meant to be selected or dragged by the debugger — for example a full-screen overlay, or a decorative background layer. Give them a flag:

```lua
spr.debugger_ignored = true
```

Once set, this sprite is **completely skipped** by the debugger — it cannot be selected, dragged, inspected, or exported.
