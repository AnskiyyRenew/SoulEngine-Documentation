---
title: Canvas & Screen
---

The screen's position or size is determined by `CANVAS` (the canvas) together with the Camera.

Canvas location: `main.lua`, `conf.lua`<br>
Camera location: `Scripts/Libraries/Camera.lua`

---

## Main Canvas

**Note: this content should be used together with [With LOVE Development → Graphics](../060_with_love/000_graphics.md).**

The canvas size is written in `conf.lua`, mentioned in [Initialization Configuration](./000_conf.md).<br>
The vast majority of elements are drawn through `CANVAS`, except for `Border` [Border](./090_border.md).

??? tip "Canvas drawing code"

    ```lua
    SE.graphics.setCanvas({MAIN_CANVAS, stencil = true})
    SE.graphics.clear(0, 0, 0, 1)

    Camera:apply()
    Layers.draw()
    if (scene_.draw) then
        scene_.draw()
    end
    Camera:unload()

    local shaders = Global.GetVariable("ScreenShaders") or {}
    local source = MAIN_CANVAS
    local target = INTERMEDIATE_CANVAS

    if (#shaders > 0) then
        for i, shader in ipairs(shaders) do
            SE.graphics.setCanvas(target)
            SE.graphics.clear(0, 0, 0, 0)
            SE.graphics.setShader(shader)
            SE.graphics.draw(source)
            SE.graphics.setShader()
            source, target = target, source
        end
    end

    SE.graphics.setCanvas()
    SE.graphics.clear(0, 0, 0, 1)
    --Border.Draw()      -- commented out by default, see the "Border" section

    SE.graphics.push()
    SE.graphics.translate(DrawX, DrawY)
    SE.graphics.scale(ScreenScale, ScreenScale)

    SE.graphics.setColor(1, 1, 1, 1)
    SE.graphics.draw(source)
    local prevLineStyle = SE.graphics.getLineStyle()
    SE.graphics.setLineStyle("rough")
    SE.graphics.setLineWidth(1)
    SE.graphics.setColor(1, 1, 1)
    SE.graphics.rectangle("line", -1, -1, CANVAS_WIDTH + 2, CANVAS_HEIGHT + 2)
    SE.graphics.setColor(1, 1, 1, 1)
    SE.graphics.setLineStyle(prevLineStyle)
    SE.graphics.pop()
    ```

Before drawing, mount all content onto the canvas `MAIN_CANVAS` and enable the `stencil` feature, then draw the canvas.

??? tip "Simplified code"

    ```lua
    SE.graphics.setCanvas({MAIN_CANVAS, stencil = true})
    Layers.draw()
    SE.graphics.setCanvas()

    SE.graphics.draw(MAIN_CANVAS)
    ```

---

## Canvas Scaling (SCREEN_SCALE)

The canvas itself is always `CANVAS_WIDTH × CANVAS_HEIGHT`; what changes is only **how big it is drawn into the window**. This is determined by `SCREEN_SCALE` in `conf.lua`, and the canvas is **always centered** (the border also scales together with the canvas, so the window frame and game image will not be misaligned).

| Value | Meaning |
| --- | --- |
| `"integer"` | Only scales by **integer multiples**, pixel-perfect. Uses 1× when the window is only 1.5× larger, 4× when over 4× larger; scales down proportionally if the window is smaller than the canvas |
| `"auto"` | Tries to fill the window / screen, allowing fractional multiples |
| A number | Fixed to this multiple |
| `false` / `nil` | Keep 1:1 with no scaling |

The default value in `conf.lua` is `"auto"`.

It can also be changed at runtime, using two global functions provided by `main.lua`:

```lua
SetScreenScale("integer")   -- switch scaling mode
print(GetScreenScale())     -- read current multiple (e.g. 2)
```

The old `FILL_SCREEN` is now only a legacy switch: it **only takes effect when `SCREEN_SCALE` is `nil`** (meaning "use `auto` when fullscreen, otherwise 1:1"). New projects should just use `SCREEN_SCALE`.

---

## Intermediate Canvas

This canvas is not responsible for drawing content on screen directly; it has only one purpose: **Shaders**.

When you set a shader for the entire screen, the intermediate canvas comes in handy, responsible for the overlay operation of shaders, allowing at least two shaders to be displayed on screen at the same time.

**See [Intermediate Development → Shaders](../050_intermediate/020_shaders.md) for the detailed shader topic.**

A brief introduction to the drawing flow, which I call the ping-pong method. **The process is similar to switching all shaders back and forth between these two canvases, hence the name ping-pong method**:
```
1. First hit the first shader onto canvas 2.
2. Switch canvas; canvas 2 inputs into canvas 1, plus an extra shader.
3. The two canvases swap; canvas 1 now has two layers of effects stacked, inputs into canvas 2, plus another shader.
4. The two canvases swap again, back to step 2.
5. Repeat these two steps until all shaders are added.
```

This process takes very little time.

**Note: most so-called templates or engines that support multiple shaders at the same time basically also use this method; it's like I'm sharing part of the approach.**

---

## Camera

The canvas does not move, always standing in place, while the Camera's role is to offset the content **inside the canvas**.

By default, a Camera has already been created, called `Camera`; below are its properties and methods:

!!! example "Camera properties"
    - `x / y` The Camera's horizontal and vertical coordinate position, default at `(320, 240)`, i.e. the center of the screen.
    - `w / h` The Camera's view size, i.e. how large an area the Camera can see starting from the center, default `(640, 480)`, i.e. the whole screen.
    - `xscale / yscale` The Camera's scaling in horizontal and vertical directions, default `(1, 1)`, i.e. original size.
    - `r` The Camera's angle, default `0`.
    - `shaker` A variable used to make the Camera shake.

Below are the commonly used Camera methods; some methods **already correctly used and not needing a second call** will not appear here:
!!! example "Common Camera methods"
    - `Camera:setPosition(x, y)` Moves the Camera to `(x, y)`.
    - `Camera:setSize(w, h)` The Camera's width/height view.
    - `Camera:setScale(x, y)` The Camera's view stretch multiple.
    - `Camera:setBounds(min_x, min_y, max_x, max_y)` Sets the Camera's bounds, restricting the Camera within the rectangular bounds formed by the two points `(min_x, min_y)` and `(max_x, max_y)`.
    - `Camera:setBoundsBox(x, y, width, height)` Sets the Camera's bounds, restricting it within a rectangle **centered at `(x, y)`** of size `width × height`.
    - `Camera:unBounds()` Removes all the Camera's bounds.
    - `Camera:reset()` Restores the Camera entirely to its birth state (position, view, scale, angle, bounds all reset).
    - `Camera:setAngle(r)` Sets the Camera's angle.
    - `Camera:shake(mag, duration, decay)` Issues a Camera shake task.
        - `mag` Maximum amplitude.
        - `duration` Shake duration.
        - `decay` Whether the shake weakens over time.

About creating a Camera:<br>
A newly created Camera will not be used unless you actually modify `main.lua` so there is no longer a single `Camera` main camera determining offset and scale.

---

## About Overworld Boundary Framing

In `v3.0.0` and later versions, all `Overworld` maps automatically add the practice of detecting the map boundary to frame the Camera, without needing to manually enter functions like `setBounds` again.

Specific flow:
```
Draw the map → engine counts non-empty tiles → computes the union → insets by half a viewport → sets the bounds
```

The key code is in the `AutoCameraBounds` function in `Scripts/Libraries/Overworld/init.lua`; the code is long so it is collapsed by default:

??? tip "Auto-set border"

    ```lua
    function overworld.AutoCameraBounds()
        local m = overworld.map._map
        if (not m) then return end

        local tw = m.tilewidth
        local th = m.tileheight

        -- Covered pixel rectangle (min/max), built from the non-empty tiles.
        local min_px_x, min_px_y, max_px_x, max_px_y
        local function union(x0, y0, x1, y1)
            if (not min_px_x) then
                min_px_x, min_px_y, max_px_x, max_px_y = x0, y0, x1, y1
            else
                min_px_x = math.min(min_px_x, x0)
                min_px_y = math.min(min_px_y, y0)
                max_px_x = math.max(max_px_x, x1)
                max_px_y = math.max(max_px_y, y1)
            end
        end

        for _, layer in ipairs(m.layers) do
            if (layer.type == "tilelayer" and layer.visible ~= false) then
                if (layer.chunks) then
                    -- Infinite map: each chunk sits at an absolute (maybe negative)
                    -- tile coordinate; its own data grid is 1..width x 1..height.
                    for _, chunk in ipairs(layer.chunks) do
                        if (chunk.data) then
                            for cy = 1, chunk.height do
                                for cx = 1, chunk.width do
                                    local tile = chunk.data[cy] and chunk.data[cy][cx]
                                    if (tile) then
                                        union(
                                            (chunk.x + cx - 1) * tw,
                                            (chunk.y + cy - 1) * th,
                                            (chunk.x + cx)     * tw,
                                            (chunk.y + cy)     * th
                                        )
                                    end
                                end
                            end
                        end
                    end
                else
                    -- Regular map: tile (x, y) renders at layer.x/y + (x-1)*tile.
                    local ox = layer.x or 0
                    local oy = layer.y or 0
                    for ly = 1, layer.height do
                        for lx = 1, layer.width do
                            local tile = layer.data and layer.data[ly] and layer.data[ly][lx]
                            if (tile) then
                                union(
                                    ox + (lx - 1) * tw,
                                    oy + (ly - 1) * th,
                                    ox + lx * tw,
                                    oy + ly * th
                                )
                            end
                        end
                    end
                end
            end
        end

        if (not min_px_x) then return end

        -- Convert the covered pixel rectangle into overworld units (*2).
        local sx_l = min_px_x * 2
        local sx_r = max_px_x * 2
        local sy_t = min_px_y * 2
        local sy_b = max_px_y * 2

        -- The visible world area equals the internal canvas (1:1 camera zoom).
        local view_w = CANVAS_WIDTH
        local view_h = CANVAS_HEIGHT
        local hw = view_w * 0.5
        local hh = view_h * 0.5

        local min_x, max_x
        if ((sx_r - sx_l) >= view_w) then
            min_x = sx_l + hw
            max_x = sx_r - hw
        else
            min_x = (sx_l + sx_r) * 0.5
            max_x = min_x
        end

        local min_y, max_y
        if ((sy_b - sy_t) >= view_h) then
            min_y = sy_t + hh
            max_y = sy_b - hh
        else
            min_y = (sy_t + sy_b) * 0.5
            max_y = min_y
        end

        Camera:setBounds(min_x, min_y, max_x, max_y)
    end
    ```
