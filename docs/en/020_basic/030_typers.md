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

In addition, `Typers.CCAdd` builds on `InstText` to provide animated floating text, also placed at the end of this section.

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
        - `int` Effect intensity; larger number means stronger. **Both the comma and the value must be written**: `[effect:shake, 1]`. Writing only `[effect:shake]` makes the whole tag do nothing (parsing relies on the comma separator). A value that is not a number falls back to `1`.
    - `[outline:r, g, b, a, t]` Sets the text's outer border.
        - `r, g, b, a` Border color and alpha, in the `0 ~ 1` range, handed straight to `setColor`.
        - `t` Border thickness, in pixels.
        - All five segments accept **integers only**; a decimal such as `0.5` makes the whole tag fail silently.
    - `[voice:name]` Sets the typing sound effect; files are in `Resources/Sounds/Voices/`, just write the file name. The default is `v_monster.wav`; setting it replaces the voice list with that single entry.
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
    - `[showbubble:dir, pos]` Shows the bubble dialog box. `dir` is the tail direction, can be `left` / `right` / `up` / `down` (default `left`); `pos` is the tail's position along the border `0 ~ 1`, default `0.5`. **Both the comma and `pos` must be written**; `[showbubble:left]` alone has no effect.
    - `[hidebubble]` Hides the bubble dialog box.
    - `[func:name]` Calls a function named `name`. **Lookup order**: first check this typer's `funcs` registry (registered with `typer:SetFunc`), if not found fall back to the `_G[name]` global. So local / closure / upvalue functions, as long as registered first with `:SetFunc`, can also be called from text, without polluting the namespace by attaching to global.
    - `[func:name|a, b, c]` Calls a function named `name`, and can pass parameters, separated by English commas. Lookup order is the same as above.
        - Numeric strings are auto `tonumber`'d into numbers; other parameters are passed as strings as-is.
        - Function execution errors are wrapped in `pcall`, only printing `[EText] func callback error: ...` without interrupting typing.
        - When not found, prints `[EText] function not found in typer.funcs or _G: <name>` and skips.
    - `^` Resets color, alpha, outline, scale and effect to their defaults, **and adds a `0.3` second pause** (same dedicated timer as `[wait:]`, skipped while fast-forwarding). Font and font size are **not** reset; to change them back, write `[font:]` / `[size:]` again.

!!! example "Instance methods"
    - `typer:SetFunc(name, fn)` Registers function `fn` into this typer's `funcs` table, so `[func:name]` can call local / closure / upvalue.
        - `name` String name (corresponds to `[func:name]` in text); empty string or non-string returns directly.
        - `fn` When it is a `function`, registers it; when `nil` is passed, **clears** that name's entry.
        - Returns the typer itself, supporting chaining: `t:SetFunc("shake", shake):SetFunc("heal", heal)`.
        - **Registration timing**: must be completed **before** the text scans the `[func:]` tag — usually just register immediately after creating the typer.
        - The old global function style is still compatible (`_G[name]` fallback), existing text need not change.

!!! tip "Tags can be written consecutively"
    `[font:x][colorHEX:ffff00][effect:shake, 2]` written consecutively like this is fine; effects stack in order.

!!! example "Special characters in text"

    Besides square-bracket tags, a few characters in the text are handled directly by the Engine:

    - `\n` Line break; the cursor returns to the start of the line and moves down one row.
    - `\t` Tab, as wide as four spaces.
    - `* ` A leading asterisk plus space is treated as a dialogue prefix. The Engine normalizes `*X` into `* X`, and gives every wrapped line a **two-space hanging indent**. Panel text should not start with `* `, or the indent will push the characters out of the panel; see [Shop](../040_overworld/060_shop.md).

!!! example "Auto-wrap"

    `EText`'s `typer.auto_wrap` is **off** by default. Turning it on wraps by `size[1]`, with the same rules as `InstText`: English wraps by word, Chinese and other equal-width characters wrap character by character.

    ```lua
    local t = Typers.EText.New({"A very very long sentence that certainly won't fit"}, {60, 270}, 0, {300, 0})
    t.auto_wrap = true
    ```

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
    - `GetWidth()` / `GetHeight()` Width of the widest line and total height of every line; see [Measuring the Text](#measuring-the-text).
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

---

### CCAdd Floating Text

`Typers.CCAdd` wraps `InstText` into **animated floating text**: after the text is created, an animation function controls its visibility and movement, and it disappears on its own once finished. It suits text that does not need to appear character by character, such as damage numbers and pickup hints.

Use `Typers.CCAdd(text, x, y, layer, align, anim_func)` to create.

- `text` The text to display, passed straight to `InstText.New`. Passing a table only takes item `1`; line breaks must be written as `\n`.
- `x` / `y` The **top-left** horizontal and vertical coordinates of the text, passed as two separate numbers, not a table.
- `layer` Layer, default `0`.
- `align` Alignment, default `"center"`, same values as `InstText:SetAlign`.
- `anim_func` The animation function, called every frame as `func(self)`. If omitted, the default animation is used.

The return value is the CC object itself, whose fields can be read and written directly:

!!! example "CC object fields"
    - `cc.inst` The underlying `InstText` instance; `alpha` / `x` / `y` / `fontsize` and similar properties can be assigned directly.
    - `cc.time` Frame counter, starting at `0`. The default animation increments it every frame; a custom animation must increment it itself.
    - `cc.func` The animation function itself.

!!! example "Creation example"

    ```lua
    local cc = Typers.CCAdd("+20", 320, 240, 0, "center")
    ```

!!! warning "Alpha is 0 at creation"
    `CCAdd` sets `cc.inst.alpha` to `0` after creation, so the text stays invisible until the animation raises the alpha.

**Default animation:**

When `anim_func` is omitted, the Engine creates four tweens on the first frame (`cc.time == 1`):

- `alpha` `0` → `1`, 40 ticks, fade in.
- `alpha` `1` → `0`, 70-tick delay then 40 ticks, fade out.
- `y` original → `y - 30`, 50 ticks, `Quad Out`, rising 30 pixels first.
- `y - 30` → `y - 60`, 70-tick delay then 50 ticks, `Quad In`, rising another 30 pixels.

Both duration and delay are measured in ticks, consistent with `Tween.CreateTween`.

**Custom animation:**

`anim_func` is called with a colon, so `self` is the CC object itself:

!!! example "Custom animation"

    ```lua
    local cc = Typers.CCAdd("MISS", 320, 200, 0, "center", function (self)
        self.time = self.time + 1
        self.inst.alpha = math.max(0, 1 - self.time / 60)
        self.inst.y = self.inst.y - 1
    end)
    ```

!!! warning "A custom animation must handle alpha and its own ending"
    `cc.inst.alpha` is `0` at creation; if a custom animation never writes `alpha`, the text stays invisible.
    The default animation's fade-out comes from a tween. A custom animation has no such layer and must decide when to end by itself.

!!! note "The default animation releases itself when it ends"
    At `cc.time == 125` the default animation destroys `cc.inst` and removes the CC from `Typers._cc`, so nothing else is needed.
    `125` comes from the last tween: a `70`-frame delay plus a `50`-frame duration means it writes its final value on frame `123`, and the rest is margin.

!!! warning "A custom animation is never released automatically"
    A custom `anim_func` has no end condition, so the CC stays in `Typers._cc` and the `anim_func` keeps being called every frame.
    Call `Typers.CCRemove(cc)` when the animation is over to destroy the instance and drop it from the list:

    ```lua
    Typers.CCRemove(cc)
    ```

    It can be called more than once, and also from inside the CC's own `anim_func`.

!!! note "Cleared wholesale on a scene switch"
    `Typers.ClearAll()` walks `Typers._cc`, destroys every `cc.inst` and empties the list; `Layers.clear()` calls it internally.

!!! note "Update timing"
    `Typers.Update` is called by `main.lua` inside `love.update`, **before** `scene.update`; it walks `Typers._cc` in reverse order and calls `func` on each entry.

---

## Measuring the Text

Every typer can report the size of the text it currently holds, through the same three methods. Sizes ignore `typer.x` / `typer.y`: they describe the letters themselves, not where they sit on screen.

!!! example "Measurement methods"
    - `typer:GetWidth()` Pixel width of the **widest line**. `\n` and auto-wrap start new lines, which are measured separately; the largest result wins.
    - `typer:GetHeight()` Pixel height from the top of the highest glyph to the bottom of the lowest one. Includes the gaps added between lines and each glyph's own `scale`.
    - `typer:GetLettersSize()` Both values in one call, returned as two numbers (width, height) rather than a table.

Code that holds a typer without knowing which module built it can use the module-level entry point, which accepts an instance of any of the four:

- `Typers.GetLettersSize(typer)` Same two return values; `0, 0` for a nil typer or for an object that has no measurement methods.

!!! example "Placing a second label next to the first"

    ```lua
    local gold = Typers.InstText.New("GOLD 120", {465, 420}, 1)
    local w, h = gold:GetLettersSize()

    -- Start 10 pixels past the first label instead of guessing a width.
    local lv = Typers.InstText.New("LV 3", {465 + w + 10, 420}, 1)
    ```

!!! example "Branching on the height of a typed-out sentence"

    ```lua
    local t = Typers.EText.New({"A short line", "A much longer line that wraps"}, {60, 270}, 0, {300, 0})

    --- Called once the sentence has finished typing.
    local function fits_one_row(typer)
        local _, h = Typers.GetLettersSize(typer)
        return h <= 27
    end
    ```

!!! note "`InstText` is final immediately, the other three grow over time"
    `InstText` lays out the whole text when it is created, so both values are final right after `New()`, `SetText()` or `Rebuild()`.
    `EText`, `NText` and `SText` only hold the letters typed so far, so the numbers keep growing until the sentence is done; a sentence that has not started yet contributes nothing.

!!! warning "Only letters are measured"
    Spaces create no letter, so they are absent from the result, while tags such as `[wait:x]` never appear in the layout at all.
    Effects like `shake` move glyphs at draw time and are not included, so the footprint on screen can be a few pixels larger than the returned value.
    Alignment does not change the size either: `SetAlign("center")` moves the letters without widening them.
