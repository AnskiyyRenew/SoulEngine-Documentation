---
title: Displaying Text (Typers)
---

This page is part of the **common base** — both paths need it.

All visible text in the game is drawn by `Typers`.

The engine provides four kinds of typers: `EText`, `NText` and `SText` type out character by character, while `InstText` shows the whole text the instant it is created. This page covers only the most common two, `EText` and `InstText`; the other two and the full tag list are in [Basic Development → Typers](../020_basic/030_typers.md).

---

## EText: the most common typewriter

`EText` writes its style inside the text, similar to `bbcode`, which makes it the easiest to start with.

Create it with `Typers.EText.New(text, position, layer)`:

- `text` The text to type. Passing a table splits it into multiple sentences; after one finishes you confirm manually to advance to the next.
- `position` The position of the first character.
- `layer` The layer.

!!! example "Creation example"
    ```lua
    local t = Typers.EText.New({"Hello, this is the first sentence", "This is the second sentence"}, {320, 240}, 0)
    ```

Add square-bracket `[]` tags inside the text to change the style without touching code:

!!! example "Coloring with a tag"
    ```lua
    local t = Typers.EText.New({"[colorHEX:ff0000]This is a red sentence."}, {320, 240}, 0)
    ```

!!! tip "Common tags"
    - `[colorHEX:rrggbb]` Sets the character color in hexadecimal (`00` ~ `ff`).
    - `[wait:x]` Pauses for `x` seconds before continuing; uses its own timer, so a later `[speed:]` cannot override this pause.
    - `[speed:x]` Sets the typing interval to `x` seconds; the default is `1/15` second.
    - Tags can be written consecutively, e.g. `[colorHEX:ffff00][speed:0.1]`; effects stack in order.

---

## InstText: instant static text

`InstText` has no typing animation; the whole text appears on screen the instant it is created. It suits text that stays long-term and does not need to appear character by character (menu buttons, money readouts, status bars, etc.).

Create it with `Typers.InstText.New(text, position, layer, size)`:

!!! example "Creation example"
    ```lua
    local label = Typers.InstText.New("HP left: 20", {90, 270}, 0, {200, 0})
    label:SetAlign("center")
    ```

!!! note "No per-frame update needed"
    Once registered into a layer, `InstText` is drawn directly by `Layers` and is not processed every frame in `love.update`; it redraws itself after its content changes.

---

---

## How to verify

Put this in the first-level region of a scene. After entering the scene, the text should type out character by character from the centre of the screen, and confirming advances to the second sentence:

```lua
local t = Typers.EText.New({"Hello, this is the first sentence", "This is the second sentence"}, {320, 240}, 0)
```

`InstText` has no typing phase; the whole line appears the moment it is created:

```lua
local label = Typers.InstText.New("HP left: 20", {90, 270}, 0, {200, 0})
label:SetAlign("center")
```

---

For the complete tag reference and the usage of `NText` and `SText`, see [Basic Development → Typers](../020_basic/030_typers.md).
