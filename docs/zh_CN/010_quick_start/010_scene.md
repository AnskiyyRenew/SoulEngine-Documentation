---
title: 新建与跳转场景
---

场景可视为一个独立的运行单元，其中的全部行为由场景自身定义。

---

## 新建场景

在 `SoulEngine` 中，拥有两个底层场景模板： `scene_template.lua` 与 `scene_template_full.lua`

初次使用时复制轻量版 `scene_template.lua` 即可。

放置在路径 `Scripts/Scenes/` 中， <u>也就是 `scene_template.lua` 同目录下</u> 。想覆盖引擎自带的场景，就把同名文件放进 `Game/Scenes/` ，Game 区优先、引擎目录兜底。

!!! tip "调整初始化配置"
    随后需将 `Game/conf_pure.lua` 里的 `FirstRoom` 改为新建场景的名称。

---

## 编辑场景

### 场景的内容

```lua
local scene = {}

function scene.update(dt)
end

function scene.draw()
end

function scene.clear()
    Layers.clear()
end

return scene
```

轻量版场景内部仅这些代码，该模板将场景代码分为几个不同部分，各部分功能如下：

!!! tip "同级代码"
    分级按 `包裹次数` 计算：在 `function - end` 包裹区域内算作一层。

    若还有新的包裹块，则再加一层。

1. 第一层区域，在所有 `function - end` 区域之外、 `return` 之前，将会在进入场景的一瞬间执行 <u>仅仅一次</u> 。
2. 第二层区域，在 `function` 内部，会在特定情况下执行。

具体说明：

- `scene.update` 之内的区域每一刻（帧）都会执行，每秒大约执行 `60` 次（默认）。
- `scene.draw` 之内的区域每一刻（帧）都会执行，每秒大约执行 `60` 次（默认）。

### 制造第一次反馈

复制出新场景后，在 `第一层区域` 中键入下面这段：
```lua
print("这是我的新场景")
```

进入场景后，控制台会输出该字符串，即表示执行成功。

### Android 测试反馈

在 Android 上若无法查看控制台，可将如下代码复制到场景的 `第一层区域` ，用于确认是否成功跳转到新建场景：
```lua
Sprites.CreateSprite("poseur.png")
```

上面的代码会在屏幕正中央创建一个 `Poseur` 图片。