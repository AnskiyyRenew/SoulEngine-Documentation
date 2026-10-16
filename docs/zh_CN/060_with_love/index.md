---
title: 与LOVE开发
---

`SoulEngine` 基于 `love` 构建，无法脱离 `love` 的底层。

`love2d` 的部分 API 在某些开发场景下必须使用，这些 API 并未包含在 `SoulEngine` 的任何文件中。

本专题介绍 `love2d` 原版 API 与 `SoulEngine` 的配合使用方式。

---

## `SE` 是什么

`main.lua` 启动时首先加载它：

```lua
SE = ImportFile("Engine.FuncProtector")
```

`FuncProtector` 返回一个表，按 LÖVE 的模块名分好类，里面**每一个函数都是对应 `love.xxx` 的直接转发**：

```lua
SE.graphics.newCanvas(640, 480)            -- 等价于 love.graphics.newCanvas(640, 480)
SE.audio.newSource("a.wav", "static")      -- 等价于 love.audio.newSource("a.wav", "static")
SE.filesystem.read("config.json")          -- 等价于 love.filesystem.read("config.json")
```

因此无需重新学习一套 API：**将 `love.` 替换为 `SE.` 即可**。参数、返回值、报错行为完全一致，可参照 [LOVE2D wiki](https://love2d.org/wiki) 中的说明。

!!! example "改写规则"

    ```lua
    love.graphics.rectangle("fill", 0, 0, 10, 10)
    SE.graphics.rectangle("fill", 0, 0, 10, 10)
    ```

    仅替换开头的模块名，其余部分不变。

### 该层的作用

打开 `Scripts/Libraries/Engine/FuncProtector.lua` ，每个函数体都长这样：

```lua
newCanvas = function(...)
    -- TODO: Implement adaptation logic
    return love.graphics.newCanvas(...)
end,
```

该 `TODO` （实现适配逻辑）用于后续适配：不同 LÖVE 版本、不同平台的个别行为并不完全一致，需要适配时**只修改这一层**，引擎内部与游戏代码均无需改动。

目前所有函数均为纯直通，没有额外行为，可等同于 `love` 使用。

### 它包了哪些模块

一共 20 个分类、316 个函数：

| `SE` 下的表 | 对应的 LÖVE 模块 | 函数数 |
| --- | --- | --- |
| `SE.graphics` | `love.graphics` | 101 |
| `SE.window` | `love.window` | 36 |
| `SE.filesystem` | `love.filesystem` | 31 |
| `SE.audio` | `love.audio` | 26 |
| `SE.physics` | `love.physics` | 22 |
| `SE.mouse` | `love.mouse` | 18 |
| `SE.math` | `love.math` | 16 |
| `SE.data` | `love.data` | 10 |
| `SE.keyboard` | `love.keyboard` | 9 |
| `SE.system` | `love.system` | 8 |
| `SE.event` | `love.event` | 6 |
| `SE.timer` | `love.timer` | 6 |
| `SE.joystick` | `love.joystick` | 6 |
| `SE.font` | `love.font` | 5 |
| `SE._top` | `love` 本身的顶层函数 | 4 |
| `SE.thread` | `love.thread` | 3 |
| `SE.touch` | `love.touch` | 3 |
| `SE.image` | `love.image` | 3 |
| `SE.sound` | `love.sound` | 2 |
| `SE.video` | `love.video` | 1 |

`SE._top` 较为特殊，它包含 `love` 表本身的顶层函数（这类函数不属于任何子模块）：

```lua
SE._top.getVersion()                      -- 等价于 love.getVersion()
SE._top.isVersionCompatible("11.4")
```

!!! note "未包含在 SE 中的内容"
    事件回调（ `keypressed` 、 `update` 、 `draw` 之类）不在这里 —— 引擎把事件转发给场景，写法见 [场景](../020_basic/010_scene.md) 。<br>
    LÖVE 的**对象方法**（ `source:play()` 、 `canvas:renderTo()` ）也不在这里，它们跟着对象走。

### 引擎自己加的函数

`FuncProtector.lua` 末尾另有两块非直通内容，为引擎自行实现的工具函数，当前即可使用：

!!! example "工具函数 SE.tools"

    - `SE.tools.hexColor(hexcode)` → `{r, g, b}`
        - 将十六进制颜色字符串转换为 `setColor` 所需的三个 `0 ~ 1` 的数值。支持 `#RGB` 与 `#RRGGBB` 两种写法， `#` 可省略。
        - 传入的不是字符串或长度不合法时返回 `nil` （不报错），可用于解析玩家或配置文件提供的颜色。

!!! example "绘制捷径 SE.draw_"

    - `SE.draw_.colorText(r, g, b, a, ...)` → 无
        - 先 `setColor` ，再用剩余参数调 `print` ，最后**自动把颜色还原成白色**。参数与 `love.graphics.print` 完全一样。
        - 该函数省去的是绘制后必须还原颜色这一步骤。未还原时颜色会影响后续所有绘制，详见 [图像绘制](./000_graphics.md) 中的相关说明。

```lua
SE.draw_.colorText(1, 0, 0, 1, "Hello", 100, 200)

local c = SE.tools.hexColor("#C14949")
SE.graphics.setColor(c[1], c[2], c[3], 1)
```

`conf_pure.lua` 中设置主色调的两行即采用该写法（默认处于注释状态，修改主色时取消注释）：

```lua
Global.SetVariable("MainColor", SE.tools.hexColor("#C14949"))
```

## 不适用 SE 的场景

`SE` 提供**底层兜底**，不优先使用。引擎已封装的部分优先使用引擎封装的版本，因为它们额外处理了 Game 区覆盖、缓存、音量跟随等逻辑：

| 想做的事 | 首选 | 而不是 |
| --- | --- | --- |
| 加载贴图 | `Sprites.New` | `SE.graphics.newImage` |
| 加载字体 | `Fonts.New` | `SE.graphics.newFont` |
| 播放音频 | `Audio.PlaySound` / `Audio.PlayMusic` | `SE.audio.newSource` |

反之，**引擎未封装的部分**（创建 Canvas、编写 Shader、直接绘制图形、读写文件等）使用 `SE` 。引擎内部同样如此： `Sprites.lua` 加载贴图的最底层即为 `SE.graphics.newImage` ，在其之上又封装了缓存、Game 区优先和像素吸附。

---

## 本专题内容

- [图像绘制](./000_graphics.md)：`SE.graphics` 与 `love.graphics` 的关系、全部 101 个函数一览
- [音频系统](./010_audio.md)：`SE.audio` 与引擎 `Audio` 库的分工

!!! info "提示"
    本专题所有内容均可在 [LOVE2D wiki](https://love2d.org/wiki) 中查看，此处选取其中常用的部分讲解。
