---
title: Graphics Drawing
---

The engine did not build its own drawing API; the principle of this section is just one sentence:

**Start with `SE.graphics`, and the rest is exactly the same as `love.graphics`.**

```lua
SE.graphics.setColor(1, 0, 0, 1)
SE.graphics.rectangle("fill", 100, 100, 40, 40)
```

The only reason to write `SE.graphics` instead of `love.graphics` is cross-platform adaptation (see [this topic's home page](./index.md)); functionally there is no difference — the `love.graphics.*` docs on the wiki can be used directly.

!!! warning "Before drawing to the screen, first think about whether it should use MAIN_CANVAS"
    The engine's entire game picture is drawn on a canvas called `MAIN_CANVAS` (size = `CANVAS_WIDTH x CANVAS_HEIGHT`), then uniformly scaled and centered onto the window by the engine.<br>
    So **don't draw directly to the window yourself inside `love.draw`** — window coordinates and in-game coordinates are different coordinate systems, and the window size also changes with the player's screen.<br>
    Drawing inside a scene works normally with regular calls; the engine has already set up the canvas, scale, and offset before you enter the scene. Details in [Screen and Canvas](../020_basic/070_screen.md).

## Function overview

Grouped by purpose below, listing all **101** `SE.graphics` functions in `FuncProtector`. The behavior, parameters, and return values of all functions are exactly the same as the same-named `love.graphics` functions; only a one-line description is given here, go to the wiki for details.

### Creation and loading

| Function | Effect |
| --- | --- |
| `newImage` | Build a texture from a file or `ImageData` (in the engine, `Sprites.New` is preferred) |
| `newFont` | Build a font (in the engine, `Fonts.New` is preferred) |
| `newImageFont` | Build a font from a character-sheet image |
| `newText` | Build a text object whose content can be changed anytime later (underlying call is `love.graphics.newTextBatch`) |
| `newCanvas` | Build an off-screen canvas, i.e. a render target |
| `newQuad` | Crop a rectangular region from a texture |
| `newShader` | Compile a shader (can take GLSL source directly, or a file path) |
| `newMesh` | Build a vertex mesh |
| `newSpriteBatch` | Build a sprite batch, used when the same texture is drawn many times |
| `newParticleSystem` | Build a particle system |
| `newVideo` | Build a video object |
| `newArrayImage` | Build an array texture (multiple layers, use `drawLayer` to specify a layer) |
| `newVolumeImage` | Build a 3D texture |
| `newCubeImage` | Build a cube texture |
| `getDefaultFilter` | Read the default sampling filter for newly created textures |
| `setDefaultFilter` | Set the default sampling filter for newly created textures (`"nearest"` nearest / `"linear"` linear) |

### Canvas and presentation

| Function | Effect |
| --- | --- |
| `setCanvas` | Send subsequent drawing output to the specified canvas; no argument = output to screen |
| `getCanvas` | Read the current canvas |
| `present` | Present this frame (the engine calls it automatically after `love.draw`, don't call it yourself) |
| `isActive` | Whether currently in a drawable state |
| `discard` | Discard canvas / depth / stencil contents, for performance optimization |

### Color and clearing

| Function | Effect |
| --- | --- |
| `setColor` | Set the current draw color; all subsequent drawing is multiplied by it |
| `getColor` | Read the current color |
| `setBackgroundColor` | Set the background color, used when the window is cleared |
| `getBackgroundColor` | Read the background color |
| `setColorMask` | Mask writing of certain color channels |
| `getColorMask` | Read the current channel mask state |
| `clear` | Clear the current canvas with the current color (or a specified color) |
| `reset` | Restore all draw states to default |

### Font and text

| Function | Effect |
| --- | --- |
| `setFont` | Set the current font |
| `getFont` | Read the current font |
| `setNewFont` | Two-in-one `newFont` + `setFont` |
| `print` | Draw a line of text (left-aligned, can rotate and scale) |
| `printf` | Auto-wrap within a given width, alignable by `"left"` / `"center"` / `"right"` / `"justify"` |

!!! note "Don't use print for formal text"
    Dialogue, menus, shop text all go through the engine's [Typewriter](../020_basic/030_typers.md), which has built-in wrapping, per-character typing, bubble width, and hanging asterisk indentation.<br>
    `print` / `printf` are generally only for debug info and text with minimal alignment requirements.

### Blend, line style, points and shaders

| Function | Effect |
| --- | --- |
| `setBlendMode` | Set blend mode (`"alpha"` default, `"add"` additive, `"multiply"` multiply …) |
| `getBlendMode` | Read the blend mode |
| `setLineWidth` | Line width |
| `getLineWidth` | Read the line width |
| `setLineStyle` | Line style (`"smooth"` default / `"rough"` hard edge, use the latter for pixel art) |
| `getLineStyle` | Read the line style |
| `setLineJoin` | Style at polyline joints |
| `getLineJoin` | Read the polyline joint style |
| `setPointSize` | Diameter of points drawn by `points` |
| `getPointSize` | Read the point diameter |
| `setWireframe` | Wireframe mode, for debug meshes |
| `isWireframe` | Whether in wireframe mode |
| `setShader` | Set the current shader; `setShader()` with no argument = release |
| `getShader` | Read the current shader |
| `validateShader` | Only compile-checks syntax, does not actually replace, used to catch shader errors early |

### Shape drawing

| Function | Effect |
| --- | --- |
| `draw` | Draw a texture / canvas / mesh / text object (in the engine, usually `Sprites`' `spr:Draw()`) |
| `drawLayer` | Draw only one layer of a sprite batch / mesh |
| `drawInstanced` | Instanced draw many times with the same vertex data |
| `flushBatch` | Immediately submit the current batch |
| `points` | Draw a set of points |
| `line` | Draw a polyline (vertex coordinates passed flat) |
| `rectangle` | Draw a rectangle (`"fill"` filled / `"line"` outlined, can take a corner radius) |
| `circle` | Draw a circle or arc sector |
| `ellipse` | Draw an ellipse |
| `arc` | Draw an arc |
| `polygon` | Draw a polygon |

### Transform and stack

| Function | Effect |
| --- | --- |
| `push` | Save the current draw state (`"transform"` saves only transform / `"all"` saves everything) |
| `pop` | Restore the last saved state |
| `rotate` | Rotate the current coordinate system, **argument is in radians** |
| `translate` | Translate the current coordinate system |
| `scale` | Scale the current coordinate system |
| `shear` | Shear the current coordinate system |
| `origin` | Reset the transform back to origin |
| `applyTransform` | Stack a `Transform` object on top of the current transform |
| `replaceTransform` | Replace the current transform with a `Transform` object |
| `transformPoint` | World coordinates → local coordinates |
| `inverseTransformPoint` | Local coordinates → world coordinates |
| `getStackDepth` | How many layers currently `push`ed |

!!! warning "Transforms are cumulative, and only affect subsequent drawing"
    A transform is not "setting a property on some object", it **changes the current coordinate system**. So the idiomatic writing is always `push` … draw … `pop`.<br>
    Forgetting `pop` makes **all subsequent** drawing skew, and it is hard to debug.

### Clipping and stencil

| Function | Effect |
| --- | --- |
| `setScissor` | Set a rectangular clip region; drawing outside the box is not shown |
| `intersectScissor` | Set a clip region, intersected with the current clip region |
| `getScissor` | Read the current clip region |
| `stencil` | Use a drawing result as a stencil; subsequent drawing only takes effect inside (or outside) the stencil range |
| `setStencilState` | Set the stencil comparison rule |
| `setStencilTest` | Toggle the stencil test |
| `getStencilTest` | Read the stencil test state |

### 3D, depth and face culling

| Function | Effect |
| --- | --- |
| `setDepthMode` | Set depth test and writing |
| `getDepthMode` | Read the depth mode |
| `setMeshCullMode` | Set back-face culling |
| `getMeshCullMode` | Read the back-face culling |
| `setFrontFaceWinding` | Set which face counts as front |
| `getFrontFaceWinding` | Read the front-face determination |

This group is only needed when doing 3D or custom meshes; 2D games basically don't touch it.

### Info and stats

| Function | Effect |
| --- | --- |
| `getWidth` / `getHeight` | Width / height of the current render target (returns canvas size in canvas mode) |
| `getDimensions` | Get width and height at once |
| `getPixelWidth` / `getPixelHeight` | Actual pixel size (considering DPI) |
| `getPixelDimensions` | Get actual pixel width and height at once |
| `getDPIScale` | Current DPI scale |
| `getRendererInfo` | Renderer, GPU name, driver version |
| `getSupported` | Which features the current device supports (compression formats, stencil, GLSL version, etc.) |
| `getSystemLimits` | Hard upper limits (max texture size, texture unit count, etc.) |
| `getTextureTypes` | Supported texture types |
| `getStats` | Draw stats: drawcall count, texture switch count, VRAM usage … |
| `isGammaCorrect` | Whether sRGB correction is currently on |
| `captureScreenshot` | Save the current frame to a file |
| `getCanvasFormats` | Supported canvas pixel formats |
| `getImageFormats` | Supported texture pixel formats |

## A complete drawing example

```lua
function MyScene:draw()
    SE.graphics.push()

    -- red filled circle
    SE.graphics.setColor(1, 0, 0, 1)
    SE.graphics.circle("fill", 320, 240, 40)

    -- white outline (change back to white before outlining)
    SE.graphics.setColor(1, 1, 1, 1)
    SE.graphics.setLineWidth(2)
    SE.graphics.circle("line", 320, 240, 40)

    -- centered text
    SE.graphics.printf("Hello LOVE", 0, 300, 640, "center")

    SE.graphics.pop()
end
```

!!! tip "push and pop are safer than manual restore"
    Color, font, line width, transform are all **global state**. `push` once, draw, `pop` once, and nothing changed in between leaks outside.

## Common pitfalls

!!! danger "Forgetting to restore color is the most common drawing bug"
    `setColor` is **global state**, retained until the next change. The classic crash is "drew a red text, forgot to change back to white", and after that all textures turn red.<br>
    In the engine several draw functions end with a dedicated line `setColor(1, 1, 1, 1)` precisely to prevent this color bleed — do the same yourself: **restore after drawing, or just use `push` / `pop`.**

!!! warning "rotate takes radians, not degrees"
    `SE.graphics.rotate(math.pi / 2)` is 90°.<br>
    But everywhere else in the engine (Soul facing, bone rotation, matrix math, etc.) uses **degrees**; don't mix the two units — remember `math.rad(degrees)` before passing in.

!!! warning "After setCanvas, the coordinate system and size both change"
    After `setCanvas(c)`, `getWidth()` / `getHeight()` return the **canvas** size, and `clear()` also clears the canvas. Don't forget to switch back with `setCanvas()` (no argument).

!!! warning "captureScreenshot is asynchronous"
    It does not return an image immediately; it waits for LÖVE to finish a draw cycle and read the frame back, and gives you the result via a callback.

---

## Related

- [This topic's home page](./index.md) — what the `SE` layer is, engine-built functions
- [Screen and Canvas](../020_basic/070_screen.md) — `MAIN_CANVAS`, scaling and centering
- [Sprites](../020_basic/020_sprites.md) — most drawing actually goes through `Sprites`
- [Typewriter](../020_basic/030_typers.md) — drawing formal text
