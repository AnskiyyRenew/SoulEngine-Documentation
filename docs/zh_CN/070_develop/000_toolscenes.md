---
title: 场景辅助工具
---

引擎内置了一些 **辅助开发用的工具场景** ，放在 `Scripts/Scenes/TOOL/` 与 `Scripts/Scenes/TEST/` 目录下。它们只在开发阶段使用，不参与正式游戏流程，可随时改写或删除。

这些场景和普通场景一样用 `Scenes.switchTo` 进入。想让它成为启动场景，直接在 `conf_pure.lua` 里改 `FirstRoom` ：

```lua
Global.SetVariable("FirstRoom", "TOOL.TweenEase")
```

!!! note "场景路径写法"
    `Scenes.switchTo("TOOL.TweenEase")` 里的点号对应文件夹层级：`Scripts/Scenes/TOOL/TweenEase.lua` → `TOOL.TweenEase` 。`TEST` 目录同理，例如 `TEST.gb` 。

---

## 贝塞尔缓动编辑器

缓动库的贝塞尔曲线可以手写控制点，也可以用这个场景 **可视化地调整** 。

打开场景 `TOOL.TweenEase` 后，左侧是操作按钮，右侧是一块坐标系画布：**横轴是时间进度 `t`（0~1），纵轴是缓动后的输出值（0~1）** 。曲线的弯曲程度越大，缓动的加减速越明显。

### 画布上的图形含义

| 图形 | 含义 |
| --- | --- |
| 绿色方块 | 首尾锚点，曲线两端必须落在 `(0,0)` 与 `(1,1)` |
| 橙色圆点 | 中间控制点，决定曲线的弯曲形状 |
| 黄色光环 | 当前选中的点 |
| 蓝色曲线 | 当前的贝塞尔缓动曲线 |
| 灰色斜线 | 线性参考线（`y = x`），曲线越贴合它越接近匀速 |

曲线使用 **德卡斯特里奥（De Casteljau）算法** 求值，因此控制点数量可以任意增减，不受三次贝塞尔的限制。

### 左侧按钮

| 按钮 | 作用 |
| --- | --- |
| `Add Point` | 新增一个控制点 |
| `Delete Point` | 删除当前选中的控制点 |
| `Play Animation` | 播放一次预览动画 |
| `Export Animation` | 导出缓动代码 |

### 操作说明

- **选中 / 拖动**：在画布内左键点击一个点即可选中并开始拖动，点的坐标会被限制在 `[0,1]` 范围内。点击空白处取消选中。
- **新增点**：`Add Point` 会依据当前选中状态插入新点 —— 选中中间点时在它与后一个点之间取中点插入；未选中任何点时，在 `t = 0.5` 处的曲线上取一点插入。
- **删除点**：`Delete Point` 需要先选中一个中间控制点；**首尾锚点不可删除**，尝试删除时终端会提示 `Cannot delete start or end anchor point` 。键盘的 `Delete` / `Backspace` 也能触发删除。
- **播放预览**：`Play Animation` 会让一个红色小方块从曲线起点沿曲线运动到终点，画布下方实时显示 `t` 与 `y` 的值，红色竖线标记当前进度。
- **退出**：按 `Esc` 退出游戏。

### 导出代码

点击 `Export Animation` 后，代码会 **同时打印到终端** 并 **写入 `Debug/exported_bezier.lua`** 。导出的内容通过 `Tween.CreateCustomTween` 注册一条名为 `myBezier` 的自定义缓动，形式如下：

```lua
--[[
  Exported Bezier Easing Curve
  Paste this code into your project, then use:
  tween.CreateTween(setter, "myBezier", "", beginVal, endVal, duration)
--]]

Tween.CreateCustomTween("myBezier", function(t)
    local pts = {
        {x = 0.0000, y = 0.0000},
        {x = 0.3300, y = 0.6700},
        {x = 0.6700, y = 0.3300},
        {x = 1.0000, y = 1.0000},
    }
    local n = #pts
    local px, py = {}, {}
    for i = 1, n do
        px[i], py[i] = pts[i].x, pts[i].y
    end
    for level = n, 2, -1 do
        for i = 1, level - 1 do
            px[i] = px[i] * (1 - t) + px[i + 1] * t
            py[i] = py[i] * (1 - t) + py[i + 1] * t
        end
    end
    return py[1]
end)
```

将这段代码加入项目后，可按普通缓动的方式使用：

```lua
Tween.CreateTween(function(value)
    print(value)
    poseur.x = value
end, "myBezier", "", 0, 600, 60)
```

### 直接注册控制点

只需要一条固定形状的贝塞尔缓动时，还可以使用直接注册控制点的接口
`Tween.CreateBezierEasing(name, points)` ，等价于上面整段手写代码：

```lua
Tween.CreateBezierEasing("myBezier", {
    {x = 0,    y = 0},
    {x = 0.33, y = 0.67},
    {x = 0.67, y = 0.33},
    {x = 1,    y = 1},
})

Tween.CreateTween(function(value)
    print(value)
end, "myBezier", "", 0, 100, 60)
```

使用方式为：在编辑器中调整形状，再把导出的控制点列表交给 `CreateBezierEasing` ，
不需要保留那段德卡斯特里奥求值代码。

!!! tip "关于缓动名与方向"
    自定义缓动的名字本身不区分类型与方向，`CreateTween` 的 `easingType` 直接填这个名字、方向参数留空字符串 `""` 即可。
