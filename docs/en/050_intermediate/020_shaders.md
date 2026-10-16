---
title: Shaders
---

**Shaders** are small GLSL programs that run on the GPU. You hand the frame to it, and per the rules you wrote, it decides **pixel by pixel** what color each point ends up being.

In LÖVE, most of the time you only need to write a **fragment shader** (the `effect` function) — it is like a "filter that every pixel goes through".

This page covers the **engine's regular Shader usage**. If you want to directly port ready-made effects from the web, see [ShaderToy Conversion Library](./010_shadertoy.md); if you want to understand the "ping-pong" drawing flow of screen shaders, see [Canvas and Screen](../020_basic/070_screen.md); the underlying LÖVE drawing API list is in [With LÖVE → Graphics Drawing](../060_with_love/000_graphics.md).

---

## The smallest possible Shader

The smallest runnable Shader is just this function:

```glsl
vec4 effect(vec4 color, Image tex, vec2 tex_coords, vec2 screen_coords) {
    vec4 pixel = Texel(tex, tex_coords);
    return pixel * color;
}
```

The effect of this code is **doing nothing** — it takes the texture out as-is, multiplies by the draw color, and returns. Understand this one line and you understand the entire skeleton of a Shader.

### The four parameters of `effect`

| Parameter | Type | Meaning |
| --- | --- | --- |
| `color` | `vec4` | The current draw color, from `setColor` or the sprite's `color` / `alpha` |
| `tex` | `Image` | The texture being drawn — usually the image itself |
| `tex_coords` | `vec2` | Texture UV, range `0~1`, **computed per drawn shape** |
| `screen_coords` | `vec2` | Screen coordinates, unit is pixels |

Its **return value** is the final color of this pixel (including alpha), directly deciding what you see on screen.

!!! warning "Sampling a texture must use Texel"
    In LÖVE the function to get a texture's color is `Texel(tex, uv)`, not the standard GLSL `texture()`. A wrong write will fail to compile directly.

!!! warning "`tex_coords` is the shape's own UV, not screen coordinates"
    For an image that fills the whole screen, `tex_coords` happens to equal "the normalized screen coordinates".
    Attach it to a 32×32 small image, and `tex_coords` still only runs between `0~1`
    — the effect gets "compressed into that 32×32 area" instead of filling the screen.
    This is fundamentally different from ShaderToy's `fragCoord` (see the ShaderToy page for details).

### Want to change shape, not color?

Then use the **vertex shader** entry `position`, which decides where each vertex is drawn:

```glsl
vec4 position(mat4 transform_projection, vec4 vertex_position) {
    return transform_projection * vertex_position;
}
```

The vertex entry is used far less. For everyday effects, just focus on `effect`.

---

## uniform: let Lua feed parameters in

The shader itself is "dead". To make it move, you rely on **uniform** — parameters sent in from outside each frame.

GLSL side declares with `extern`:

```glsl
extern number time;        // in LÖVE, number is equivalent to float
extern vec2 amplitude;
extern Image mask;
```

Lua side assigns with `send`:

```lua
shader:send("time", 1.5)
shader:send("amplitude", {0.02, 0.05})
shader:send("mask", someImage)
```

### Type correspondence

| GLSL declaration | Value passed to `send` in Lua |
| --- | --- |
| `extern number x;` | A number |
| `extern vec2 / vec3 / vec4 v;` | `{1, 2}` / `{1, 2, 3}` / `{1, 2, 3, 4}` |
| `extern Image img;` | An Image / Canvas |
| `extern mat4 m;` | Matrix (rare) |
| `extern bool b;` | `true` / `false` |

!!! tip "`number` is `float`"
    In LÖVE, `number` is an alias for `float`, and the engine's own shaders use both writings. Writing `float` is also completely fine.

!!! example "Check before sending, to avoid silent failures"
    `shader:hasUniform("time")` tells you whether a uniform exists.
    When the name is misspelled, LÖVE may not error, yet the effect "doesn't move at all" — self-check with it first to save trouble:

    ```lua
    if shader:hasUniform("time") then
        shader:send("time", t)
    end
    ```

---

## Three usages, from small to large

| Usage | How to write | Good for |
| --- | --- | --- |
| **Sprite-level** | `spr:SetShaders({shader})` | Add an effect to a specific image / sprite |
| **Global screen** | `Global.SetVariable("ScreenShaders", {shader})` | Full-screen filter (to set the screen mood) |
| **Fully custom** | `SE.graphics.setShader(shader)` + your own `setCanvas` | When you want full control of draw timing and target |

- The list of sprite-level methods (`SetShaders` / `AddShader` / `InsertShader` / `RemoveShader` / `ClearShaders`) is in [Sprites → Common Methods](../020_basic/020_sprites.md).
  When multiple shaders are attached, the engine **ping-pongs** between two temporary canvases the same size as the sprite, stacking them one by one, so effects apply in list order.
- The global-screen `ScreenShaders` goes through the main canvas ↔ intermediate canvas ping-pong flow, explained in [Canvas and Screen](../020_basic/070_screen.md).
- The lowest-level `newShader` / `setShader` / `validateShader` are all wrapped under `SE.graphics`; the list is in [Graphics Drawing](../060_with_love/000_graphics.md).

---

## Write your first example quickest

Three steps: **write a `.glsl` file → write a test scene → set it as the startup scene**.

### Step 1: create `Scripts/Shaders/MyWave.glsl`

```glsl
extern number time;
extern number amplitude;

vec4 effect(vec4 color, Image tex, vec2 tex_coords, vec2 screen_coords) {
    // horizontal sine offset along the y axis: the lower you go, the more it twists
    vec2 uv = tex_coords;
    uv.x += sin(uv.y * 12.0 + time * 3.0) * amplitude;

    vec4 pixel = Texel(tex, uv);
    return pixel * color;
}
```

### Step 2: create test scene `Scripts/Scenes/TEST/scene_my_shader.lua`

```lua
local scene = {}

-- compile once, cache it. Never newShader every frame (that recompiles every frame)
local shader = SE.graphics.newShader("Scripts/Shaders/MyWave.glsl")

-- a white image that fills the screen, to "carry" the full-screen effect
local bg = Sprites.CreateSprite("px.png", 0)
bg:Scale(CANVAS_WIDTH, CANVAS_HEIGHT)
bg:SetShaders({shader})

local t = 0

function scene.update(dt)
    t = t + dt
    shader:send("time", t)          -- feed time every frame so the animation moves
    shader:send("amplitude", 0.02)
end

function scene.draw() end

function scene.clear()
    Layers.clear()
end

return scene
```

### Step 3: make it run on startup

In `conf_pure.lua`, point `FirstRoom` to it:

```lua
Global.SetVariable("FirstRoom", "TEST.scene_my_shader")
```

In the game you should see the whole screen gently swaying left and right. **Change `amplitude` from `0.02` to `0.2`**, and the effect immediately grows tenfold — this is the best part of tweaking shaders: change one number and see the result instantly.

!!! tip "Two loading methods"
    - `SE.graphics.newShader("Scripts/Shaders/MyWave.glsl")` — directly give the file path.
    - `ImportFile("MyWave", "shader")` — only give the name; the engine looks for `.glsl` under `Scripts/Shaders/` itself, and **throws a clear error with the path on compile failure**, which makes debugging easier.

    You can also pass the GLSL code directly as a string, skipping a file ([ShaderToy Conversion Library](./010_shadertoy.md) does exactly this).

!!! warning "Compile failure throws, not returns nil"
    A Shader syntax error makes `newShader` **throw directly**. When loading a shader from an uncertain source, wrap it in `pcall`, otherwise the whole scene fails to start. To check syntax ahead of time separately, use `SE.graphics.validateShader(code)`.

---

## The 7 shaders that ship with the engine

There are already 7 ready-to-use shaders in `Scripts/Shaders/`. **The laziest starting point for practice is to take them apart and modify them.**

| File | What it does | Key uniforms |
| --- | --- | --- |
| `ColorFilter.glsl` | Grayscale + tint (`mix` controls grayscale amount) | `grayscale` `tint_color` |
| `Gradiant.glsl` | Four-corner color gradient, rotatable angle | `topLeftColor` etc. four corners + `angle` |
| `WaveDistort.glsl` | Sine wave distortion, horizontal and vertical directions | `time` `amplitude` `frequency` `speed` `tex_size` |
| `Glow.glsl` | Samples neighboring pixels for brightness difference, glows at edges | `glow_color` `glow_intensity` `threshold` `tex_size` |
| `Dust.glsl` | Scanline dissolve fade-out (uses `if` branches and noise) | `dt` `scan_y` etc. |
| `FourPoint.glsl` | Four-point deformation, solves UV with inverse bilinear interpolation, `discard` when out of bounds | `p1` ~ `p4` |
| `PixelSmooth.glsl` | Uses `dFdx/dFdy` for pixel smoothing, fixes rotation aliasing | `texture_pixel_size` |

Suggested reading order: `ColorFilter` → `WaveDistort` → `Glow` → `FourPoint`.
The first three are "change color / change UV / sample neighbors", covering 90% of daily needs; `FourPoint` is geometric-level, treat it as a math problem.

---

## How to practice further

The Shader learning curve is "steep at the start, flat afterward": **copy first, then modify, then write your own formula in the end**.

### Stage 1: change constants (almost no math needed)

Push the existing shader's uniform to extremes and watch thephenomenon:

- Move `ColorFilter`'s `grayscale` from `0` up to `1` gradually, watch the screen turn gray.
- Raise/lower `Glow`'s `threshold`, watch the glowing area grow or shrink.
- Pull `WaveDistort`'s `amplitude` from `0` to `0.5`, watch how the image gets twisted.

### Stage 2: change the formula (start touching math)

- Replace `sin(...)` with `cos(...)`, `abs(sin(...))`, `sqrt(...)`, watch how the waveform changes.
- Change the two axes' `sin` frequencies in `WaveDistort` to different numbers, to make the difference between "water ripple" and "jitter".
- Change `uv.x +=` to `uv.y +=`, understand the symmetry of "horizontal distortion" and "vertical distortion".

### Stage 3: write small effects from scratch

Each does only **one thing**, run it on a full-screen white image:

| Goal | Hint |
| --- | --- |
| Tint | `pixel.rgb * vec3(1.0, 0.5, 0.5)` |
| Grayscale | `dot(pixel.rgb, vec3(0.299, 0.587, 0.114))` |
| Invert | `1.0 - pixel.rgb` |
| Brightness / contrast | `(pixel.rgb - 0.5) * contrast + 0.5 + brightness` |
| Scanline | Use `tex_coords.y` with `sin` or `step` for stripes |
| Radial vignette | Use `distance(tex_coords, vec2(0.5))` for bright center, dark edges |
| Ripple | Use `sin(distance(uv, center) * k - time)` for concentric circles |

### Stage 4: combine and advance

- Use `SetShaders` to attach multiple shaders at once, and feel their **sequential stacking** effect.
- Start touching **neighbor sampling** (like `Glow` sampling up/down/left/right pixels) and **multi-sampling** (blur, outline).
- For big scenes, see [ShaderToy Conversion Library](./010_shadertoy.md), borrow community-ready code, then take it apart afterward.

### Recommended resources

- **The Book of Shaders** (`thebookofshaders.com`) — the best free tutorial for concepts, focus on the "color / shape / random / noise" chapters. Note its examples are WebGL style; when porting to LÖVE, switch to `effect` + `Texel`.
- **[ShaderToy](https://www.shadertoy.com/)** — a huge number of ready-made effects, usable directly with the engine's conversion library.
- **The 7 shaders that ship with the engine** — the best "local examples", because their style is exactly the one this project maintains long-term.

---

## Performance and pitfalls

!!! danger "Never create a shader every frame"
    `newShader` triggers **GPU compilation**, which is very expensive. The correct approach is to compile once when the scene loads, cache it at the module top level, and only `send` uniforms each frame. `send` is cheap, call it freely.

!!! warning "Reset after drawing"
    `SE.graphics.setShader(shader)` stays in effect until the next `setShader()` call.
    Restore it immediately when done, otherwise it pollutes all subsequent drawing:

    ```lua
    SE.graphics.setShader(shader)
    -- ... your drawing ...
    SE.graphics.setShader()      -- restore
    ```

!!! warning "Full-screen + neighbor sampling = expensive"
    `effect` runs **once per pixel**. A shader like `Glow` that samples 5 points at once is 5× the sampling on the whole screen; stack a few more passes and it grows multiplicatively.
    On mobile especially be restrained — this is also why the engine added caching optimization to `PixelSmooth` instead of `setFilter` every frame.

!!! danger "Only GLSL ES 1.0 is accepted"
    No `switch`, no `#version 300 es`, no dynamic array uniform indexing.
    When copying code from the web, confirm the version first; the concrete limits and "which writings definitely fail to compile" are listed in the pitfalls section of [ShaderToy Conversion Library](./010_shadertoy.md).

!!! note "About the Y axis"
    Screen coordinate y is positive downward. When writing "bottom to top" math, it is normal that your first instinct is off — flip the sign in the formula, or draw a reference line first to confirm direction.

!!! tip "Use validateShader to catch errors early"
    After editing GLSL you do not have to enter the game every time to find errors: `SE.graphics.validateShader(code)` only does a compile check, does not actually replace the current shader, good for running once in a tool or at startup.
