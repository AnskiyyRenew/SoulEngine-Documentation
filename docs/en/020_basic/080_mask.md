---
title: Mask
---

Simply put, a Mask is an object used to focus the Player's attention; for example, when you battle a monster, the bullets are framed within the battle box by a Mask.

Or when making a UI, with multiple options crammed into one window, an elegant method is to use a Mask to frame the range, so all options are only drawn within this range.

Mask library location: `Scripts/Libraries/Masks.lua`

---

## Creating a Mask

On the surface it is creating a Mask, but in fact it only temporarily creates a table, **so there is no need to worry about recycling.**

Use `Masks.New(shape, x, y, w, h, r, value)` to create a new Mask.

- `shape` Can be `rect` / `rectangle`, creating a rectangular Mask; can also be `ellipse` / `circle`, creating an elliptical Mask; `image` / `img` creates a sprite-shaped Mask (see the "Sprite Mask" section below for details).
- `x / y` The Mask's position, usually no need to set extra since there are methods to follow a sprite later.
- `w / h` The Mask's width/height, also no need to set extra.
- `r` Angle.
- `value` This feature can specify rendering onto a specific layer; normally just set to 1.

---

## Using a Mask

### Following an Image

After creating it, there is no need to manually set position and width/height; just use the `Follow` function to follow a sprite.

Use `mask:Follow(spr)` to make the Mask follow a `spr`.

!!! example "Following the battle box"
    This practice is common during rounds; you can directly make the Mask follow the black area.
    ```lua
    local mask = Masks.New("rect", 320, 320, 155, 130, 0, 1)

    function wave.Update(dt)
        mask:Follow(Arena.black)
    end
    ```

### Image Usage

Use `sprite:SetStencils({mask})` to set the sprite's Mask; multiple masks can be placed inside, e.g.: `sprite:SetStencils({mask1, mask2, mask3})`.

Below is a case of a big dog bullet using a Mask:

![](../img/020_basic/030.png)

---

## Sprite Mask

Although rectangular and elliptical Masks cover most scenes, there are always some shapes that cannot be drawn with one or two `love.graphics` primitives — such as a heart shape, a star shape, or even a certain monster silhouette. In this case you can use a **sprite Mask**.

### Principle

Inside `Masks.Draw` it calls `love.graphics.setStencilState("increment", "always", 1)` and disables color writing; at this point all "drawn" primitives add `+1` to the stencil buffer. The key point: **when `love.graphics.draw` draws an image, the transparent fragments discarded by the default sprite shader do not participate in the stencil action**, so the Mask's shape is exactly equivalent to the pixel region with "non-zero alpha" in the ImageData.

In short: **the sprite's alpha determines the Mask's shape**; fully opaque means full Mask, fully transparent means no Mask, semi-transparent parts are written proportionally — this is consistent with what the human eye sees.

### Creation

Just append an `image` parameter at the end of `Masks.New`:

```lua
local img = love.graphics.newImage("Sprites/shapes/heart.png")
local mask = Masks.New("image", 320, 320, 0, 0, 0, 1, img)
```

- `image` Can pass a `love.Image` object, or an engine sprite table (the return value of `Sprites.GetSprite` etc.); the latter auto-takes its `.image` field.
- At this point `w / h` is used to **scale the sprite as a whole to the target size** (e.g. 64×64); fill `0` to keep the original size. That is, the sprite Mask still supports `Follow` to follow the sprite's size changes.
- For finer scaling control, you can directly assign to `mask.scaleX` / `mask.scaleY`, which overrides the `w / h` conversion.
- `mask.ox` / `mask.oy` can customize the drawing origin, defaulting to the image's geometric center, making `(x, y)` correspond to the sprite center — consistent with the "geometric center at `(x, y)`" semantics of rectangular/elliptical Masks.

!!! tip "Sprite requirements"
    - Must have an alpha channel. PNG is recommended.
    - The alpha threshold is **exactly 0** — semi-transparent pixels between 0~255 will be written to the raster per the GPU's blending rules, and will not form a "hard edge".
    - Since the engine uses `nearest` filtering and disables mipmap for sprites by default, the Mask edges will not have unexpected blur; if you want anti-aliasing, pre-apply suitable alpha correction to the image yourself.

!!! warning "Performance"
    An image Mask rebuilds the sprite drawing cost every frame; multiple large image Masks may slow down stencil writing. If possible, reuse the same ImageData / love.Image.

### Usage and Following

The sprite Mask also follows the standard flow of `Masks.Draw` -> `Masks.Use` -> draw content -> `Masks.Clear`, and can also go through `sprite:SetStencils({mask})` to hand it to the sprite pipeline.

!!! example "Cropping bullets with a heart-shaped sprite"
    ```lua
    local img = love.graphics.newImage("Sprites/shapes/heart.png")
    local mask = Masks.New("image", 320, 320, 64, 64, 0, 1, img)

    function wave.Update(dt)
        mask:Follow(Arena.black)
    end

    bone_sprite:SetStencils({ mask })
    ```

The sprite Mask can also be mixed with rectangular/elliptical Masks; as long as their `value` is consistent, `Masks.Draw` accumulates them one by one into the stencil buffer, and the final crop is the union of the several shapes.
