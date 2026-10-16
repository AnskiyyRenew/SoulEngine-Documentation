---
title: ShaderToy Conversion Library
---

[ShaderToy](https://www.shadertoy.com/) has a large number of ready-made GLSL fragment shaders. This library **automatically rewrites** their `mainImage` style into a Shader that LÖVE can compile, saving you the manual porting work.

Path: `Scripts/Libraries/ShaderToy/`

| File | Responsibility |
|---|---|
| `init.lua` | Entry point: create Shader, multi-pass project, update uniforms each frame |
| `convert.lua` | Text rewriting (detect uniforms, wrap `mainImage`, replace function names) |
| `rules.lua` | Rewrite rule table; edit here to extend support |

```lua
local shadertoy = ImportFile("ShaderToy")
```

!!! note "It is not a render pipeline"
    This library only handles "translating code into a LÖVE Shader" and "feeding uniforms each frame".
    Where to draw and how big is still decided by the sprite's `SetShaders` or your own `setCanvas`.
    For the engine's regular Shader usage, see **[Shaders](./020_shaders.md)**.

---

## Quickest start

The engine has a directly runnable test scene `Scripts/Scenes/TEST/scene_shader.lua`. Just paste the ShaderToy code as-is into `convert()`:

```lua
local shadertoy = ImportFile("ShaderToy")
local s = shadertoy.convert([[
void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    vec2 uv = fragCoord/iResolution.xy;
    vec3 col = 0.5 + 0.5*cos(iTime+uv.xyx+vec3(0,2,4));
    fragColor = vec4(col,1.0);
}
]])

local bg = Sprites.CreateSprite("px.png", 0)
bg:Scale(640, 480)
bg:SetShaders({s.shader})

function scene.update(dt)
    s:update(dt)      -- must be called every frame, otherwise iTime does not advance
end
```

!!! warning "`s.shader` is the real Shader"
    `convert()` returns a wrapper object. When passing it to `SetShaders` / `love.graphics.setShader`, use its `.shader` field.

---

## What it changes for you

`convert.lua` does the following to the original code (the rules are all in `rules.lua`):

| Original | Changed to | Reason |
|---|---|---|
| `texture(tex, uv)` | `Texel(tex, uv)` | LÖVE's sampling function has a different name |
| `gl_FragCoord` | `screen_coords` | LÖVE has no `gl_FragCoord` |
| `iChannelResolution[0]` | `iChannelResolution0` | GLSL ES 1.0 does not support indexing array uniforms like this |
| `precision ... float;` | deleted | LÖVE does not need it, and keeping it actually causes an error |
| `void mainImage(...) {...}` | `vec4 effect(...) {...}` | Replace with LÖVE's entry function |

At the same time, it **automatically inserts** the uniform declarations it detects at the very top of the code, so you do not write `extern` yourself:

| Appears in code | Auto-inserted | Auto-assigned each frame |
|---|---|---|
| `iTime` | `extern number iTime;` | Seconds accumulated from `dt` |
| `iResolution` | `extern vec3 iResolution;` | `{CANVAS_WIDTH, CANVAS_HEIGHT, 1}` |
| `iMouse` | `extern vec4 iMouse;` | x, y from `Keyboard.GetMousePosition()` |
| `iFrame` | `extern int iFrame;` | Frame count, +1 each `update` |
| `iChannel0` ~ `iChannel3` | `extern Image iChannelN;` | See next section |
| `iChannelResolution` | `extern vec3 iChannelResolutionN;` | Width/height of each channel's texture |

Declarations not appearing in the code are **not** inserted and not assigned — so deleting unused variables saves a bit of overhead.

### How fragCoord is computed

The converted `effect` function begins like this:

```glsl
vec2 fragCoord = vec2(texture_coords.x * iResolution.x,
                      iResolution.y - texture_coords.y * iResolution.y);
```

!!! warning "fragCoord comes from the drawn shape's UV, not screen coordinates"
    It is computed as `texture_coords` (sprite UV) × `iResolution`.
    **Only a shape that fills the whole screen** equals the screen coordinates on ShaderToy.
    Attach it to a 32×32 small sprite and you will see "the entire shader compressed into that 32×32 area".

    There is also a line at the end, `fragColor *= vec4(1.0,1.0,1.0, Texel(texture, texture_coords).a);`: **the result is multiplied by the sprite's alpha**. `px.png` (1×1 white) is the easiest; if the sprite has transparent areas, the colors there get multiplied to 0.

---

## Channel textures

ShaderToy's `iChannel0~3` default to noise images. This library's approach:

- At conversion time, whenever it detects `iChannelN` used in the code, it generates a **256×256 random noise** texture to stand in for it (`rules.DEFAULT_NOISE_SIZE`), so it will not fail to compile even if you do nothing.
- To swap in your own image, use `setChannel`.

```lua
s:setChannel(0, myImage)      -- channel 0 uses myImage
```

### Audio channel

`setAudioChannel(id, filepath)` turns audio into a **512×2** texture and feeds it into the shader:

| Row | Content | Value |
|---|---|---|
| Row 0 (y=0) | FFT spectrum | RGB all written the same value `v` |
| Row 1 (y=1) | Waveform | R channel written `wave * 0.5 + 0.5` |

```lua
s:setAudioChannel(0, "Resources/Music/mus_battle.ogg")
```

!!! warning "FFT is a naive O(N²) implementation"
    `simpleFFT` does a double loop over 512 samples, about **260,000** trig operations per frame, and it is **recomputed every frame**. On mobile this is real overhead; do not leave it on constantly on mobile.

---

## Methods of a single Shader

The object returned by `convert(code)` (called `s` below):

| Method | Effect |
|---|---|
| `s:update(dt)` | **Call every frame.** Advance `iTime` / `iFrame` / `iMouse` / `iResolution` and re-send channel textures |
| `s:apply()` | `setShader(s.shader)` |
| `s:use()` | Alias of `apply()` |
| `s:clear()` | `setShader()` to cancel |
| `s:setChannel(id, texture)` | Assign a texture to channel `id` (0-3) |
| `s:setAudioChannel(id, filepath)` | Connect audio to channel `id` and loop it |
| `s:unload()` | `release()` to free GPU resources |
| `s:printCode(mode, savePath)` | Print/save the converted code, a debugging godsend |
| `s:generateNoiseTexture(size)` | Manually generate a noise texture |

Fields: `s.shader` (the real Shader), `s.original` (original text), `s.code` (after conversion), `s.externs` (inserted declarations), `s.runtimeFlags` (which uniforms were detected), `s.time` / `s.frame`.

!!! example "When it won't convert, look at the conversion result first"
    ```lua
    s:printCode()                       -- print final GLSL
    s:printCode("original")             -- print original text
    s:printCode("extern")               -- print only inserted declarations
    s:printCode("final", "out.glsl")    -- save to file to study slowly
    ```
    The vast majority of "compile failures" can be spotted at a glance this way: whether some uniform was not detected, or whether parentheses broke the `mainImage` match.

---

## Multi-pass project

ShaderToy's "Buffer A / Buffer B / Image" is called a **pass** here. The output of the previous pass is automatically fed to the `iChannel` of the next pass (pass j → `iChannel(j-1)`).

```lua
local proj = shadertoy.newProject()

proj:addPass("bufferA", codeA)
proj:addPass("image",   codeB)

-- every frame
proj:update(dt)

-- draw (pick your own timing)
proj:draw()
```

| Method | Effect |
|---|---|
| `newProject()` | Create a new project |
| `proj:addPass(name, code)` | Add a pass; internally creates two canvases each for ping-pong |
| `proj:update(dt)` | Accumulate project time/frame count, and call `update(dt)` on each pass |
| `proj:draw()` | Render all passes in order, and draw the last result to screen |
| `proj:unload()` | Free all canvases and shaders |

!!! warning "Multiple passes eat video memory"
    Each pass creates **two** full-screen canvases (`CANVAS_WIDTH × CANVAS_HEIGHT`).
    3 passes means 6 full-screen canvases; weigh that on mobile. Remember to `unload()` when switching scenes.

---

## Pitfalls and limits

!!! danger "Only GLSL ES 1.0 is accepted"
    LÖVE's Shader is GLSL ES 1.0. Shaders on ShaderToy that use `textureLod`, `textureSize`, integer arithmetic, `switch`, `in` / `out` variables, `#version 300 es` will **definitely fail to compile**.
    When searching, pick older shaders tagged "Sound"/"Buffer" that are simple and have no cubemap — they have the highest success rate.

!!! warning "Unsupported uniforms are not auto-added"
    `iDate`, `iChannelTime`, `iSampleRate`, `iKeyboard` etc. are **not** in `rules.UNIFORM_RULES`.
    If the code references them, conversion will not insert a declaration → compile error "undefined variable".
    To support them, add the rule to `rules.lua` yourself (add the `extern` text + flag, then add a `send` block in `init.lua`'s `update`).

!!! warning "Functions other than `mainImage` are kept verbatim"
    The conversion only does a regex replacement on the `mainImage` block; all other functions are copied as-is. This is usually good (helper functions work normally), but if the original has **another** function matching the `void mainImage(...)` shape (e.g. a commented-out version), it will be rewritten too, causing a duplicate definition.

!!! danger "Compile failure is an error, not a returned nil"
    `convert()` internally calls `SE.graphics.newShader` directly, so a syntax error **throws**.
    When loading someone else's shader, always wrap it in `pcall`, otherwise the whole scene fails to start:

    ```lua
    local ok, s = pcall(shadertoy.convert, code)
    if (not ok) then
        print("Shader compile failed: " .. tostring(s))
        return
    end
    ```

!!! warning "iTime accumulates dt and is not affected by battle pause"
    Inside `update(dt)`, `self._time = self._time + dt` keeps going up.
    If the pause menu does not call `update`, it stops; if it does, it keeps going. To make the animation follow the game's rhythm, pass in a processed `dt` yourself.

!!! warning "The Y axis is flipped"
    Screen coordinate y is positive downward; the conversion already applies a flip (see the `fragCoord` formula above).
    But if the math copied from ShaderToy itself relies on "y up", it will visually be upside down — just flip the sign in the formula.
