---
title: 显示文字
---

本页属于**通用底座**的一部分，两条路线都要用到。

游戏中所有可见文字都由 `打字机（Typers）` 绘制。

引擎提供四种打字机： `EText` 、 `NText` 、 `SText` 会逐字打出， `InstText` 在创建瞬间整段显示。本页只讲解最常用的 `EText` 与 `InstText` ；其余两种与完整标签列表见 [基础开发 → 打字机](../020_basic/030_typers.md) 。

---

## EText：最常用的逐字打字机

`EText` 把样式写进文本内部，类似 `bbcode` ，上手最简单。

使用 `Typers.EText.New(text, position, layer)` 创建：

- `text` 要打的文字，传表会把内容分成多句，打完一句后手动确认可翻到下一句。
- `position` 第一个字符所在的位置。
- `layer` 图层。

!!! example "创建示例"
    ```lua
    local t = Typers.EText.New({"你好，这是第一句话", "这是第二句话"}, {320, 240}, 0)
    ```

在文本里加入带方括号 `[]` 的标签即可改变样式，无需改动代码：

!!! example "用标签上色"
    ```lua
    local t = Typers.EText.New({"[colorHEX:ff0000]这是一句红色的话。"}, {320, 240}, 0)
    ```

!!! tip "常用标签"
    - `[colorHEX:rrggbb]` 用十六进制设置字符颜色（ `00` ~ `ff` ）。
    - `[wait:x]` 暂停 `x` 秒后再继续，使用独立计时器，后续出现的 `[speed:]` 不会覆盖这段暂停。
    - `[speed:x]` 设置打字间隔为 `x` 秒，默认 `1/15` 秒。
    - 多个标签可连续书写，例如 `[colorHEX:ffff00][speed:0.1]` ，效果依次叠加。

---

## InstText：瞬间显示的静态文字

`InstText` 没有打字动画，创建后整段文字立刻出现在屏幕上，适合长期存在、无需逐字出现的文字（菜单按钮、金额读数、状态栏等）。

使用 `Typers.InstText.New(text, position, layer, size)` 创建：

!!! example "创建示例"
    ```lua
    local label = Typers.InstText.New("余下血量：20", {90, 270}, 0, {200, 0})
    label:SetAlign("center")
    ```

!!! note "无需每帧更新"
    `InstText` 注册进图层后由 `Layers` 直接绘制，不在 `love.update` 中每帧处理；修改内容后会自动重绘。

---

---

## 验证点

在场景的第一层区域写下这段，进入场景后应从屏幕中央开始逐字打出文字，打完第一句后按确认键翻到第二句：

```lua
local t = Typers.EText.New({"你好，这是第一句话", "这是第二句话"}, {320, 240}, 0)
```

`InstText` 没有打字过程，创建后整段文字立刻出现：

```lua
local label = Typers.InstText.New("余下血量：20", {90, 270}, 0, {200, 0})
label:SetAlign("center")
```

---

更完整的标签说明、以及 `NText` 与 `SText` 的用法，见 [基础开发 → 打字机](../020_basic/030_typers.md) 。
