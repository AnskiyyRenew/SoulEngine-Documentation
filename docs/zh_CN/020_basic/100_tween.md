---
title: 缓动
---

缓动库用于生成动画的过渡效果。

缓动库路径： `Scripts/Libraries/Tween.lua`

---

## 新建缓动任务

使用 `Tween.CreateTween(variableSetter, easingType, direction, begin, final, duration, delay, destroyAfter)` 创建一个缓动任务操作。

- `variableSetter` 回调函数，在执行过程中这个函数会 **不断执行** 。
- `easingType` 什么类型的缓动，例如： `Quad` 、 `Bounce` 等，支持全小写。
- `direction` 什么方向，指 `In` 、 `Out` 或 `InOut` ，支持全小写。
- `begin` 缓动的起始值。
- `final` 缓动的最终值。
- `duration` 缓动任务持续时间（帧）。
- `delay` 缓动任务推迟执行时间（帧）。
- `destroyAfter` 缓动任务在开始一瞬间计时多久后清除（帧），默认为 `duration` ，执行完会自动回收。

!!! example "图片示例"
    下面的示例会让 `poseur` 从 x 为 `320` 处，通过 60 帧的 `bounce out` 缓动动画移动到 `600` 。

    移动过程中，终端会持续输出 `poseur.x` ，动画在 `60` 帧后结束。

    ```lua
    local poseur = Sprites.CreateSprite("poseur.png", 0)
    Tween.CreateTween(
        function(value)
            print(value)
            poseur.x = value
        end,
    "Bounce", "Out", poseur.x, 600, 60)
    ```

!!! example "任意变量示例"
    `CreateTween` 的第一个参数为回调函数，其中的赋值语句均可执行。

    下面的代码中， `poseur` 在 `60` 帧后变为红色。

    ```lua
    local poseur = Sprites.CreateSprite("poseur.png", 0)
    Tween.CreateTween(
        function(value)
            poseur.color = {value, 0, 0}
        end,
    "Quad", "Out", 0, 1, 60)
    ```

---

## 自定义缓动动画

### 函数缓动

使用 `Tween.CreateCustomTween(name, easingFunc)` 来自定义缓动。

!!! example "示例"

    ```lua
    Tween.CreateCustomTween("smooth", function(t)
        return t * t * (3 - 2 * t)
    end)

    Tween.CreateTween(function(value)
        print(value)
    end, "smooth", "", 0, 100, 60)
    ```

### 贝塞尔缓动

可通过手写控制点创建贝塞尔缓动，也可通过场景生成。

关于场景生成，详见 **[辅助开发 → 场景辅助工具](../070_develop/000_toolscenes.md)** 。

使用 `Tween.CreateBezierEasing(name, points)` 创建一个贝塞尔曲线缓动。

`points` 使用格式：
```
{
    {x = 0, y = 0},
    {x = ..., y = ...},
    {x = 1, y = 1},
    ......
}
```

起始点必须为 `0` ，终点必须为 `1` 。

!!! example "示例"

    ```lua
    Tween.CreateBezierEasing("mybezier", {
        {x = 0, y = 0},
        {x = 0.25, y = 0.1},
        {x = 0.25, y = 1},
        {x = 1, y = 1},
    })

    Tween.CreateTween(function(value)
        print(value)
    end, "mybezier", "", 0, 100, 60)
    ```