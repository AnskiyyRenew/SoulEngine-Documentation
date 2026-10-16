---
title: 边框
---

部分作品（例如 `Undertale BNP` ）除居中的游戏画面外，还带有一圈外边框。

边框库位置： `Scripts/Libraries/Utils/Border.lua`

![](../img/020_basic/040.png)

---

## 注册边框

引擎注册了一个边框，其中只有遗迹边框与默认边框可用。<br>
由于存在偏移与缩放问题， `idle` 边框不适用。曾在画布外圈绘制一圈 1px 白线作为替代方案，但该白线现已与边框一同关闭（见下）。

使用 `Border.RegisterImage(name, path)` 注册边框，注册后通过 `name` 调用。

- `name` 边框的代号。
- `path` 边框的路径，从 `Resources/Sprites/Border/` 文件夹开始算起。

---

## 启用边框

!!! warning "边框和那圈白线，现在都没在画"
    `main.lua` 的 `love.draw` 里**两处都被注释掉了**：

    - `Border.Draw()` —— 边框图本身。它当初是按固定窗口尺寸画的，偏移和缩放对不上。
    - 画布外圈那圈 `1px` 白线（ `rectangle("line", -1, -1, CANVAS_WIDTH + 2, CANVAS_HEIGHT + 2)` ）—— 曾经用来代替边框图的那圈白框。

    因此默认画面四周没有任何装饰。需要恢复时，取消对应行的注释，或在场景中手动调用 `Border.Draw()` 。库本身可正常工作：它会跟随 `SCREEN_SCALE` 缩放，并与画布一起居中。

查看边框效果时使用以下两个函数：

使用 `Border.SetEnabled(true)` 来启用边框。<br>
使用 `Border.FadeIn(dur)` 来设置淡入持续时长（秒）。

!!! example "其他函数"
    - `SetImage(img)` 将边框切换到注册过的图片名字。
    - `SetAlpha(a)` 设置边框的透明度，淡入淡出通过改变该值实现。
    - `FadeOut(dur)` 花费 `dur` 秒淡出消失。
    - `SetOpening(x, y)` 手动指定边框图上开窗（即游戏画面所在位置）的左上角像素坐标。
    - `GetOpening(imgW, imgH)` 返回开窗相对边框图左上角的偏移。没手动设置过时，会按画布居中自动算出来。

---

## 其他操作

若需在边框区域绘制其他内容，可修改 `Border.Draw` 函数，其中只能使用 `love2d` 的官方绘制方法，详见 [与LOVE开发 → 图像绘制](../060_with_love/000_graphics.md) 。