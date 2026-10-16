---
title: 画布与屏幕
---

屏幕的位置或大小由 `CANVAS` （画布）和 摄像机一起决定。

画布位置： `main.lua` 、 `conf.lua`<br>
摄像机位置： `Scripts/Libraries/Camera.lua`

---

## 主画布

**注：此内容需搭配 [与LOVE开发 → 图像绘制](../060_with_love/000_graphics.md) 使用。**

画布的尺寸被写在了 `conf.lua` 中，在 [初始化配置](./000_conf.md) 中有提到。<br>
绝大部分元素都会经过 `CANVAS` 进行绘制，除了 `Border` [边框](./090_border.md) 。

??? tip "画布的绘制代码"

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
    --Border.Draw()      -- 默认注释掉，见「边框」一节的说明

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

在绘制之前，将所有内容挂载到画布 `MAIN_CANVAS` 上，并启用 `stencil` 功能，随后绘制画布即可。

??? tip "精简代码"

    ```lua
    SE.graphics.setCanvas({MAIN_CANVAS, stencil = true})
    Layers.draw()
    SE.graphics.setCanvas()

    SE.graphics.draw(MAIN_CANVAS)
    ```

---

## 画布缩放（SCREEN_SCALE）

画布本身的尺寸始终为 `CANVAS_WIDTH × CANVAS_HEIGHT` ， `SCREEN_SCALE` 决定它绘制到窗口时的放大倍数，该配置位于 `conf.lua` 。画布**始终居中**（边框也随画布一起缩放，因此窗框与游戏画面不会错位）。

| 取值 | 含义 |
| --- | --- |
| `"integer"` | 只按**整数倍**放大，像素完美。窗口只有 1.5 倍大时用 1 倍，超过 4 倍时用 4 倍；窗口比画布还小就按比例缩小 |
| `"auto"` | 尽量铺满窗口 / 屏幕，允许小数倍 |
| 一个数字 | 固定用这个倍数 |
| `false` / `nil` | 保持 1:1 不缩放 |

`conf.lua` 里的默认值是 `"auto"` 。

运行中也能改，用的是 `main.lua` 提供的两个全局函数：

```lua
SetScreenScale("integer")   -- 切换缩放方式
print(GetScreenScale())     -- 读出当前倍数（例如 2）
```

旧的 `FILL_SCREEN` 现在只是遗留开关：**只有当 `SCREEN_SCALE` 为 `nil`** 时才起作用（含义是全屏时按 `auto` ，否则 1:1）。新项目使用 `SCREEN_SCALE` 。

---

## 中间画布

该画布不直接绘制屏幕内容，仅用于**着色器**处理。

为整个屏幕设置着色器时，中间画布负责着色器的叠加，使两个及以上的着色器同时生效。

**着色器的详细说明见 [高阶开发 → 着色器](../050_intermediate/020_shaders.md) 。**

绘制流程如下，该方法在两个画布之间来回切换以叠加着色器，称为乒乓法：
```
1. 先将第一个着色器打到2号画布。
2. 切换画布，2号画布输入到1号画布，额外加一个着色器。
3. 两画布互换，1号画布现在叠了两层特效，输入到2号画布，再加一个着色器。
4. 两画布再次互换，重新回到步骤2。
5. 重复这两个步骤直到所有着色器被加上。
```

该过程在单次绘制流程内完成。

**多数支持多个着色器的模板与引擎使用相同的方法。**

---

## 摄像机

画布位置固定，摄像机用于偏移**画布内部**的内容。

引擎默认生成一个名为 `Camera` 的摄像机，其属性与方法如下：

!!! example "摄像机属性"
    - `x / y` 摄像机的水平竖直坐标位置，默认位于 `(320, 240)` ，即屏幕正中心。
    - `w / h` 摄像机的视图大小，也就是摄像机从中心开始能看到多大的地方，默认 `(640, 480)` ，即整个屏幕。
    - `xscale / yscale` 摄像机在水平竖直方向上的缩放，默认 `(1, 1)` ，即原大小。
    - `r` 摄像机的角度，默认 `0` 。
    - `shaker` 摄像机震动相关变量。

以下列出常用方法；引擎内部已调用且无需再次调用的方法不在其中：
!!! example "常用摄像机方法"
    - `Camera:setPosition(x, y)` 移动摄像机至  `(x, y)` 。
    - `Camera:setSize(w, h)` 摄像机的宽高视图。
    - `Camera:setScale(x, y)` 摄像机的视图拉伸倍数。
    - `Camera:setBounds(min_x, min_y, max_x, max_y)` 设置摄像机的边界，将摄像机限制在以 `(min_x, min_y)` 和 `(max_x, max_y)` 两点围成的矩形边界中。
    - `Camera:setBoundsBox(x, y, width, height)` 设置摄像机的边界，限制在一个**以 `(x, y)` 为中心**、 `width × height` 大小的矩形里。
    - `Camera:unBounds()` 解除摄像机的所有边界。
    - `Camera:reset()` 把摄像机整个恢复成出生状态（位置、视图、缩放、角度、边界全部重置）。
    - `Camera:setAngle(r)` 设置摄像机的角度。
    - `Camera:shake(mag, duration, decay)` 发出一个摄像机震动任务。
        - `mag` 最大振幅。
        - `duration` 震动持续时长。
        - `decay` 是否随着时间增加而减弱震动。

关于新建摄像机：<br>
新建的摄像机不会被使用，除非修改 `main.lua` ，不再由单独的 `Camera` 主摄像机确定偏移与缩放。

---

## 关于 Overworld 边界框定

在 `v3.0.0` 及以后版本中，所有的 `Overworld` 地图都自动加上了检测地图边界框定摄像机的做法，无需再次手动输入 `setBounds` 等函数。

具体流程：
```
画地图 → 引擎数非空瓦片 → 算并集 → 内缩半个视口 → 设边界
```

关键代码位于 `Scripts/Libraries/Overworld/init.lua` 中的 `AutoCameraBounds` 函数，代码较长故默认折叠了起来：

??? tip "自动设置边框"

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