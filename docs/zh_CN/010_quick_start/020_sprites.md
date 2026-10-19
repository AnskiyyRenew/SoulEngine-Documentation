---
title: 贴图的创建
---

本页属于**通用底座**的一部分，两条路线都要用到。

游戏中所有可见的部分都是渲染出的 `颜色` 。<br>
在 2D 游戏中，渲染的颜色由 `贴图` 承载。全部属性见 [基础开发 → 贴图](../020_basic/020_sprites.md) 。

---

## 创建图片

和上一页的末尾一样，使用 `Sprites.CreateSprite(path, layer)` 来创建一个贴图。

- `path` 图片的路径：<u>先到 `Game/Resources/Sprites/` 找，找不到再回退到 `Resources/Sprites/`</u> （Game 区优先）。
- `layer` 图层，可以使用数字，也可以使用文字。如果输入文字后发现图层并不存在，会默认返回0，同时终端会有提示。

!!! warning "终端的提示"
    `[WARNING] Layers.add: Layer "xxx" not found, defaulting to 0`

!!! example "案例"
    下面将创建一个图层为0的 `poseur` 图片。
    ```lua
    Sprites.CreateSprite("poseur.png", 0)
    ```

---

## 编辑图片

**首先需要掌握一个常用的操作：赋值**，即将函数返回的结果赋予某个变量。

创建贴图时也可以一次性传入全部参数，例如：

```lua
Sprites.CreateSprite("poseur.png", 0, 320, 240, 0, 1, 0, 0, nil, {1, 1, 1}, 1, 2, 2)
```

引擎未采用该设计： `Sprites.CreateSprite(path, layer)` 只接收两个参数，位置、颜色、缩放等均在取得贴图之后逐个赋值。

!!! danger "如果它真的收一长串参数"
    若创建函数要求一次填完所有属性，仅修改 `xscale` 时需写成：

    ```lua
    Sprites.CreateSprite("a.png", 0, nil, nil, nil, nil, nil, nil, nil, nil, nil, 2, 2)
    ```

    此时难以分辨各个 `nil` 对应的参数位置，因此引擎将属性改为创建后逐个赋值。

---

`CreateSprite` 会返回一个代表该贴图的对象，可将其赋值给变量：

!!! example "接住图片"
    ```lua
    image = Sprites.CreateSprite("poseur.png", 0)
    ```

在创建后单独修改图片的属性：

!!! example "修改x/yscale"
    ```lua
    image.xscale = 2
    image.yscale = 2
    ```

**下面是所有可修改属性及其代表的概念，如果想要更全面的说明，请点开 [基础开发](../020_basic/index.md) ：**

!!! tip "可修改属性"
    - `x` 水平方向上的位置。
    - `y` 竖直方向上的位置。
    - `rotation` （角度制）图片的角度，随角度增大顺时针旋转。
    - `xscale` 水平方向上的缩放，默认为 1 ，会按倍数放大图片。
    - `yscale` 竖直方向上的缩放，默认为 1 ，会按倍数放大图片。
    - `color` 图片的颜色，使用一个表来赋值。
    - `alpha` 图片的透明度（0 ~ 1），数字越大，越清晰可见。
    - `pixel_snap` 是否让这张图做像素吸附（默认跟随全局 `sprites.pixel_snap` ，也就是开着）。设成 `false` 就单独放过这一张，常用于拼装体里不该被单独取整的零件。
    - `velocity` 图片的速度

---

## 验证点

在场景的第一层区域写下这段，进入场景后屏幕正中央应出现放大一倍的 `poseur` 图片：

```lua
image = Sprites.CreateSprite("poseur.png", 0)
image.xscale = 2
image.yscale = 2
```

!!! warning "图片没有出现"
    路径从 `Game/Resources/Sprites/` 与 `Resources/Sprites/` 两处查找，子目录要写全，例如 `Overworld/Frisk/spr_frisk_0.png` 。<br>
    文件名区分大小写。Windows 上大小写写错仍能匹配，打包到 Android 或 Linux 后该图会找不到。