---
title: ❕️ Typers
---

Typer location: the `Scripts/Libraries/Typers/` folder.

There are four kinds of Typers: `InstText` is only responsible for drawing the whole text directly, and the other three `EText` / `NText` / `SText` can all type out character by character normally.

All text on screen can be drawn through Typers, but we also have an additional way, which will be covered on the next page.

---

## Creating a Typer

The three **character-by-character** Typers are divided by "how tags are handled", namely `EText`, `NText` and `SText`.

The fourth, `InstText`, has no typing animation, and its usage differs a lot from them, so it is placed separately at the end of this section.

---

### EText Typer

`EText` stands for `Easy Text`; its feature is that the style is written inside the text, similar to `bbcode`.

Use `Typers.EText.New(text, position, layer, size, mode)` to create an `etext` mode typer.

- `text` The text to type; can be a string or a table; if a table is used, the text is split into a pageable type.
- `position` The position of the first character of the typer.
- `layer` The typer's Layer.
- `size` The size of the dialog box shown by the typer.
- `mode` The typer's mode: `manual` switch to the next sentence manually, `none` cannot be manually intervened, only switch to the next sentence through code. If no parameter is given at creation, the default is `manual` mode.

!!! example "Creation example"

    ```lua
    local t = Typers.EText.New({"This is the first sentence", "This is the second sentence"}, {320, 240}, 0)
    ```

**Modifying style:**

Set the style by adding tags with square brackets `[]` in the sentence.

!!! example "Usage case"

    ```lua
    local t = Typers.EText.New({"[colorHEX:ff0000]This is a red sentence."}, {320, 240}, 0)
    ```

??? example "All tags"
    - `[wait:x]` Makes the typer wait `x` seconds; only a direct number is allowed, no expressions like `1 / 2`.
        - The wait uses its **own timer**, so even if a `[speed:]` appears later, it cannot swallow this pause.
        - When the Player presses cancel to fast-forward, or this sentence carries `[skip]`, the wait is skipped directly and the remaining characters are typed out immediately.
    - `[speed:x]` Sets the typer's typing interval to `x` seconds; only a direct number is allowed, no expressions. Default value is `1/15=0.0667` seconds.
    - `[size:x]` Changes the font size of the **following** text to `x`; only a direct number is allowed. Characters already typed keep the size at creation, so text on screen will not "rewind" to shrink or grow. bondfont is not turned off by this; each character's scaling and spacing still apply.
    - `[colorRGB:r, g, b]` Sets character color in RGB format `(0 ~ 255)`.
    - `[colorHEX:rrggbb]` Sets character color in hexadecimal `(00 ~ ff)`.
    - `[font:x]` Sets the font to `x`. The path starts from `Resources/Fonts/`, but **`Game/Resources/Fonts/` is checked first**; same-named files in the Game region take priority. Setting the font conveniently turns off bondfont; to restore it you must turn it on again yourself.
    - `[effect:name, int]` Sets the character's effect.
        - `name` The effect name: `shake` vibrates in place, `rotate` does a slight rotation, other names mean no effect.
        - `int` Effect intensity, default `1`; larger number means stronger.
    - `[outline:r, g, b, a, t]` Sets the text's outer border.
        - `r, g, b, a` Border color and alpha.
        - `t` Border thickness.
    - `[voice:name]` Sets the typing sound effect; files are in `Resources/Sounds/Voices/`, just write the file name.
    - `[portrait:frames|interval|mode]` Sets the animation played simultaneously while typing, generally a character playing a speaking animation while talking.
        - `frames` Frame images, **separated by English commas**, e.g. `a.png, b.png`.
        - `interval` Seconds per frame, default `1/30`.
        - `mode` Playback mode, default `looponce` (return to the first frame after one round).
        - The three segments are separated by `|`; only `frames` is required: `[portrait:a.png, b.png|0.05|looponce]`.
    - `[portrait:remove]` Removes the speaking animation (writing `hide` / `clear` / `none` has the same effect).
    - `[skip]` Fast-forwards this sentence; takes no value. Fast-forward skips all `[wait:]` waits.
    - `[noskip]` Forbids this sentence from being fast-forwarded by the cancel key, the opposite of `[skip]`.
    - `[next]` After this sentence finishes typing, immediately turn to the next sentence, without waiting for the Player to press confirm; also takes effect in `manual` mode.
        - A bubble belongs to "the sentence that displays it", so `[next]` clears the bubble together with the text; if you want to keep using the bubble in the next sentence you must re-`[showbubble:]`.
    - `[showbubble:dir, pos]` Shows the bubble dialog box. `dir` is the tail direction, can be `left` / `right` / `up` / `down` (default `left`); `pos` is the tail's position along the border `0 ~ 1`, default `0.5`.
    - `[hidebubble]` Hides the bubble dialog box.
    - `[func:name]` Calls a function named `name`. **Lookup order**: first check this typer's `funcs` registry (registered with `typer:SetFunc`), if not found fall back to the `_G[name]` global. So local / closure / upvalue functions, as long as registered first with `:SetFunc`, can also be called from text, without polluting the namespace by attaching to global.
    - `[func:name|a, b, c]` Calls a function named `name`, and can pass parameters, separated by English commas. Lookup order is the same as above.
        - Numeric strings are auto `tonumber`'d into numbers; other parameters are passed as strings as-is.
        - Function execution errors are wrapped in `pcall`, only printing `[EText] func callback error: ...` without interrupting typing.
        - When not found, prints `[EText] function not found in typer.funcs or _G: <name>` and skips.
    - `^` This symbol can be used to directly reset all styles to default.

!!! example "Instance methods"
    - `typer:SetFunc(name, fn)` Registers function `fn` into this typer's `funcs` table, so `[func:name]` can call local / closure / upvalue.
        - `name` String name (corresponds to `[func:name]` in text); empty string or non-string returns directly.
        - `fn` When it is a `function`, registers it; when `nil` is passed, **clears** that name's entry.
        - Returns the typer itself, supporting chaining: `t:SetFunc("shake", shake):SetFunc("heal", heal)`.
        - **Registration timing**: must be completed **before** the text scans the `[func:]` tag — usually just register immediately after creating the typer.
        - The old global function style is still compatible (`_G[name]` fallback), existing text need not change.

!!! tip "Tags can be written consecutively"
    `[font:x][colorHEX:ffff00][effect:shake, 2]` written consecutively like this is fine; effects stack in order.

---

### NText Typer

`NText` stands for `Neutral Text`; its feature is that the style is written in a style table, separated from the text, which makes it more convenient to modify the text.

Use `Typers.NText.New(text, position, layer, size, opts, mode)` to create an `ntext` mode typer.

- `text` The text to type; can be a string or a table; if a table is used, the text is split into a pageable type.
- `position` The position of the first character of the typer.
- `layer` The typer's Layer.
- `size` The size of the dialog box shown by the typer.
- `opts` Style table, with independent style settings inside.
- `mode` The typer's mode: `manual` switch to the next sentence manually, `none` cannot be manually intervened, only switch to the next sentence through code. If no parameter is given at creation, the default is `manual` mode.

!!! example "Usage case"

    ```lua
    local text = Typers.NText("&* 这&是一句话^...", {320, 240}, 0, {0, 0}, {
        {
            color = {1, 0, 0},
            outline = {0, 1, 1, 1, 2},
        },
        {
            color = {0, 1, 0}
        }
    }, "manual")
    ```

**Modifying style:**

Modify the style by adding `&` and `^` symbols in the sentence.

??? example "All styles"
    - `font` The font used; setting it auto-releases `bondfont`.
    - `size` Font size.
    - `color` The text's color, using `{r, g, b}`.
    - `alpha` The text's transparency `(0 ~ 1)`.
    - `outline` The text's outer border, using the `{r, g, b, a, t}` format.
    - `scale` The text's scaling factor, default `1`. Wide characters like Chinese are auto-handled by `bondfont`, drawn at `2`×.
    - `autowrap` Whether to auto-wrap.
    - `wait` Pause for how many seconds before continuing. Same as `[wait:x]`, uses an **independent timer**, later styles cannot override it, skipped during fast-forward.
    - `effect` Character effect, format `{name = "shake", intensity = 3}`.
    - `voice` Single typing sound file name, placed under `Resources/Sounds/Voices/`.
    - `voices` Typing sound list, randomly picks one per character to play.
    - `skip` Fast-forward settings table, can fill `canskip` (whether it can be fast-forwarded by cancel key), `skipping` (whether currently fast-forwarding), `skipcount` (how many characters per fast-forward), `absolute`.
    - `portrait` Character speaking expression switch, supports three ways of writing:

    ```lua
    -- 1. Full form
    portrait = {
        files = {"a.png", "b.png"},
        interval = 0.02,        -- seconds per frame, default 1/30
        mode = "looponce"       -- default looponce: return to first frame after one round
    }

    -- 2. Directly give a list of image paths (interval and mode use defaults)
    portrait = {"a.png", "b.png"}

    -- 3. Remove the speaking animation
    portrait = "remove"         -- writing "hide" / "clear" / "none" has the same effect
    ```

---

### SText Typer

`SText` stands for `Sequence Text`, a sequence typer; its feature is that the text is gradually concatenated during typing, which is very suitable for situations **with multiple checking conditions**.

!!! example "Usage case"

    ```lua
    local hp = 5
    local text = Typers.SText.New(function (self)
        self:addText("Hello")
        self:nextSentence()

        if (hp) then
            self:addText("HP is now " .. hp .. ".")
        else
            self:addText("I am blind and cannot see HP.")
        end
    end, {80, 60}, 0, {200, 100})
    ```

Below are all the functions available during construction:

!!! example "Construction functions"
    - `self:addText(text)` Adds text to the current sentence.
    - `self:addSkipText(text)` Adds text that needs to be **typed instantly** (appears immediately during fast-forward).
    - `self:setFont(name)` Sets the font. Setting the font conveniently turns off `bondfont`; to restore it you must turn it on again yourself.
    - `self:setWaitTime(time)` Pause for how many seconds before continuing. Uses an **independent timer**, later `setSpeed` cannot swallow it, skipped during fast-forward.
    - `self:setSpeed(interval)` Sets the typing interval (seconds).
    - `self:setEffect(name, intensity)` Sets the character effect; `name` is `shake` or `rotate`, `intensity` default `1`.
    - `self:setColor(r, g, b)` Sets color, `0 ~ 1` or `0 ~ 255` is auto-recognized by the engine.
    - `self:setColorHEX(hex)` Sets color in hexadecimal form, e.g. `"ff0000"`.
    - `self:setOutline(r, g, b, a, t)` Text border, drawn behind the character with 8-direction offset copies.
    - `self:setVoices(voices)` Sets the typing sound; can pass a file name, or a list.
    - `self:setPortrait(frames, interval, mode)` Sets the character speaking animation. `frames` is the image path string (or just a single file name), `interval` default `1/30`, `mode` default `looponce`.
    - `self:removePortrait()` Removes the speaking animation.
    - `self:showBubble(visible, dir, pos)` Shows / hides the bubble (`visible` `false` means hide).
    - `self:nextSentence()` Ends the current sentence and waits for Player confirm; after confirm, clears text and starts the next sentence.

---

### InstText Typer

`InstText` stands for `Instant Text`; its feature is **no typing animation**: the whole text is already drawn on screen the instant it is created.

It is suitable for text that **exists long-term but does not need to appear character by character** — battle menu buttons, the money readout in a shop, status bars, etc. Because it pre-renders each character into a sprite and **caches across instances**, drawing the same text for any length costs no extra performance, cheaper than running `printf` once per frame.

Use `Typers.InstText.New(text, position, layer, size)` to create.

- `text` The text to display. Passing a table only takes **item `1`**; to wrap lines you must write `\n` yourself (or turn on auto-wrap).
- `position` The position of the text's **top-left corner**.
- `layer` Layer.
- `size` `{width, 0}`, the first item is the **auto-wrap box width**, default `{640, 0}`; the second item is currently unused.

!!! example "Creation example"

    ```lua
    local label = Typers.InstText.New(
        "* " .. Localize.localizeText("Battle.Spare"),
        {90, 270},
        "UponArena"
    )
    label:SetAlign("center")
    label.fontsize = 24
    ```

!!! example "Instance methods"

    - `SetText(new_text)` Changes the text. Re-pre-renders, **does not** touch color.
    - `SetAlign(mode)` Alignment, `"left"` (default) / `"center"` / `"right"`. Alignment is computed relative to `position` by whole-line width.
    - `Rebuild()` Forces a re-layout once. After manually changing `size` or `auto_wrap` you must call it yourself.
    - `SetColor(r, g, b)` Changes color, `0 ~ 1` or `0 ~ 255` both accepted.
    - `UseBondFont(config)` Switches to a different Chinese/English font config, same structure as `EText`'s bondfont.
    - `Destroy()` / `Remove()` Destroys. Decrements the character's reference in the cache by one, **can be called repeatedly**.
    - `t.font` / `t.fontsize` These two properties are written directly; writing them conveniently re-lays out once, no need to `Rebuild()` yourself.

!!! warning "Color is baked into the character: change color first, then text"
    `InstText` pre-renders each character into a sprite, and does not re-color at draw time. So the order must be
    `SetColor` → `SetText` (or `SetColor` → `Rebuild()`).
    Reversing it — change text first then color — will produce no change on screen.

!!! example "Auto-wrap"

    ```lua
    local t = Typers.InstText.New("A very very long text that certainly won't fit...", {320, 60}, 0, {200, 0})
    t.auto_wrap = true
    t:Rebuild()          -- ← after changing auto_wrap / size you must re-layout yourself
    ```

    - Default **off**. If not turned on it always lays out a single line, so existing calls in the engine will not reflow at all.
    - After turning on, it wraps by `size[1]`, with rules consistent with `EText` / `NText`: English wraps **by word** (the whole word goes to the next line, not split in half), Chinese and other equal-width characters wrap **character by character**; only when a single word itself is wider than the box will it hard-break.
    - Like `EText`, it does **not recognize square-bracket tags**; things like `[wait:]` will be drawn as text as-is.

!!! note "It does not need updating every frame"
    `InstText` registers itself into the Layer and is drawn directly by `Layers`, **not going through `Typers.Update`**,
    so you don't need to manage it in `love.update` — after changing content it redraws itself.

!!! warning "Remember to destroy it yourself"
    `Layers.clear()` / `Typers.ClearAll()` will clear it together, but **calling `Destroy()` yourself is safest**.
    Creating repeatedly without destroying, the character sprites in the cache will only keep growing.
    `Typers.InstText.ClearCache()` can clear all character cache at once — but instances currently being drawn are also released together, use with caution.
