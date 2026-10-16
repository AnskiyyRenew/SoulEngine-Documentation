---
title: Interaction and Dialogue
---

What happens after the player touches something is entirely decided by **your scene script**. The engine only tells you "you touched it, and who you touched".

---

## How Interactions Arise

The physics world's collision callback records the contacted objects into `World.interactions`:

!!! example "interactions fields"
    - `can_interact` whether you are currently touching some interactive object.
    - `current_object` the type touched (`"warp"` / `"chest"` / `"sign"` / `"save"` / `"trigger"`).
    - `current_id` the `id` of the touched object.
    - `current_obj` the runtime object actually touched, whose `properties` you can read.
    - `touching` the list of **all objects currently being touched** (possibly more than one).

!!! tip "No need to face it"
    The check only looks at collision, **and does not require the player to face that direction**. The original game's "must walk in front of the sign" restriction is not implemented here — touching it counts.

---

## Reading Interactions

!!! example "Reading methods"
    - `Overworld.getInteractResult(obj_type, id, extra_key)` whether you are currently touching something matching the condition.
        - `obj_type` the type name, e.g. `"warp"`.
        - `id` if omitted, returns `true` as long as the type matches.
        - `extra_key` if omitted (or passed a number), matches by `id`; if passed a **string**, matches by that named **custom property** (e.g. `"rr"`).
        - When matching by property, **the value of that property is returned** (not `true`) — if `rr` is `3`, it returns `3`, directly usable as a number.
    - `Overworld.getTouchResult(obj_type, id, extra_key)` same as above, but checks **every** object in `touching` rather than only the last one touched.
    - `Overworld.FindObject(obj_type, id, extra_key)` doesn't require being touched — searches the whole map directly and returns the runtime object table.
        - `obj_type` is written in **singular** (`"warp"` / `"mark"` / `"chest"`), internally concatenated into `objects["warps"]` for lookup.

!!! warning "`getTouchResult` is **not** subject to two common protections"
    Both `getInteractResult` and `onConfirm` have two gates: the frame right after a dialog ends returns `false` directly, and when `Char.controlling` is `false` returns `nil` directly. <br>
    **`getTouchResult` has neither.** It only reads the `touching` list, so:

    - It still returns `true` when the player is locked (in dialog / in menu);
    - When using `getTouchResult` for triggers, it's easy to get "the confirm key that closed the dialog re-opens it". You must add your own deduplication via `FLAG`, etc.

!!! tip "The 4th parameter of old scripts is ignored"
    `getInteractResult`'s old signature had a 4th parameter (back then a "must face" switch). <br>
    It is now **accepted but ignored**, just so old scene scripts still run. The facing check itself is gone (see above) — don't write it in new code.

!!! warning "Use getTouchResult when overlapping"
    `getInteractResult` only looks at "the last one touched". When two trigger regions overlap, the one touched first gets overridden by the one touched later. <br>
    In cases where hitting any one counts (e.g. "entered a certain room"), always use `getTouchResult`.

```lua
-- touched a warp with id 1
if (Overworld.getInteractResult("warp", 1)) then ... end

-- touched a trigger whose custom property rr equals 1
if (Overworld.getInteractResult("trigger", 1, "rr")) then ... end

-- touching any sign at all
if (Overworld.getInteractResult("sign")) then ... end
```

---

## One-key Confirm

`onConfirm` merges "touching + pressed confirm" into one call — the most common pattern:

!!! example "Confirm methods"
    - `Overworld.onConfirm(type_name, id, sub_key, func)` executes `func` when the condition is met and the confirm key is pressed.
        - `sub_key` optional; if passed, additionally matches by that custom property.
        - When `sub_key` is omitted, the third parameter is directly the callback function.

```lua
Overworld.onConfirm("sign", 1, function ()
    Overworld.dialogNew({"* 这是一块告示牌。"})
end)

Overworld.onConfirm("trigger", 1, "rr", function ()
    Overworld.ChangeScene("Overworld.scene_ruins", 2, "down")
end)
```

---

## Dialogue

!!! example "Dialogue methods"
    - `Overworld.dialogNew(texts, position)` pops up a dialog box and returns the `dialog` object.
        - `texts` an array of text.
        - `position` `"down"` (bottom of screen, default) or `"up"` (top).
    - `Overworld.ui_prefer` the default value used when `position` is not passed.

The returned `dialog` has two fields: `block` (the white-bordered black-filled box) and `text` (the typewriter object).

The engine destroys the box and unlocks the player by default after the text finishes. To do something more, override `text._onComplete`:

```lua
local dialog = Overworld.dialogNew({"* 你捡起了一块石头。"})

dialog.text._onComplete = function ()
    dialog.block:Destroy()
    Char.controlling = true
    -- your own follow-up logic
end
```

![OW-04](../img/040_overworld/ow_04_dialog.png)

---

## Switching Scenes

!!! example "Scene-switching methods"
    - `Overworld.ChangeScene(scene, mark, direction)` fades out and switches to another scene.
        - `scene` the target scene name, e.g. `"Overworld.scene_ruins"`.
        - `mark` which spawn point of the target map to land on, default `1`.
        - `direction` facing after landing, default `"down"`.

It immediately locks the player and begins fading out, and only actually switches the scene once the black overlay is fully dark. At the same time it writes `DATA.room` / `marker` / `direction` into the save.

!!! tip "Use DATA to pass data across maps"
    `DATA` is global when switching scenes and won't be lost; state to carry over (story progress, dropped items, etc.) is written directly into `DATA` or `FLAG`.

---

## A Complete Scene Script

Putting the parts above together:

```lua
local scene = {}
local ow = ImportFile("Overworld")

ow.Init("Maps/main_scene/sol.lua")
ow.SetMusic("Start.ogg")

function scene.update(dt)
    ow.Update(dt)

    -- sign
    ow.onConfirm("sign", 1, function ()
        ow.dialogNew({"* 欢迎来到遗迹。", "* 请小心脚下。"})
    end)

    -- save point
    ow.onConfirm("save", 1, function ()
        local save = ow.FindObject("save", 1)
        ow.SaveInteract({"* 你感到了希望。"}, "遗迹 - 入口", save.position, "down")
    end)

    -- chest
    ow.onConfirm("chest", 1, function ()
        ow.ChestInteract("chest")
    end)

    -- warp
    ow.onConfirm("warp", 1, function ()
        ow.ChangeScene("Overworld.scene_ruins", 2, "down")
    end)

    -- custom trigger region: say one line when entered (only once)
    if (ow.getTouchResult("trigger", 1, "rr") and not FLAG["said_hello"]) then
        FLAG["said_hello"] = true
        ow.dialogNew({"* ……这里好安静。"})
    end
end

function scene.draw()
    ow.Draw()
end

function scene.clear()
    ow.Clear()
    Layers.clear()
end

return scene
```

---

## Common Pitfalls

!!! warning "On the frame right after a dialog ends, `getInteractResult` always returns false"
    The engine has a **single-frame lock**: on the frame the text finishes, all `getInteractResult` calls return `false` (`getTouchResult` is unaffected). <br>
    This prevents the infinite loop of "the confirm key that closed the dialog immediately re-opens it". <br>
    If you want to trigger two things in a row on that frame, the second will be swallowed — move it to the next frame, or write your own state machine.

!!! warning "When `Char.controlling` is false, `getInteractResult` does nothing"
    `getInteractResult` has `if (not Char.controlling) then return end` (note it returns `nil`, not `false`). <br>
    If you locked the player yourself but forgot to restore it, interactions via `getInteractResult` / `onConfirm` will **silently fail**. <br>
    But `getTouchResult` and `FindObject` **don't look at this field** — they always work normally.

!!! tip "Make the dialog box follow the camera"
    When making your own UI, use `GetRelativePos(x, y)` to convert coordinates; don't write screen coordinates directly — the camera moves.
