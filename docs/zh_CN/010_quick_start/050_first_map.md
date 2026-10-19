---
title: 第一张地图
---

本页是路线 B：让角色在一张地图上走动，并能触发对话。

地图直接使用引擎自带的那张，不需要先准备素材。前置：[通用底座](./index.md) 四页已读完。

---

## 主世界由两部分组成

| 部分 | 负责什么 | 本页用哪个 |
|---|---|---|
| 地图文件 | 地面、墙、以及放置其上的交互对象 | 引擎自带 `Maps/main_scene/main_0.lua` |
| 主世界场景 | 载入地图、放音乐、每帧推进、处理交互 | `Game/Scenes/Overworld/myfirst.lua` |

自建地图需要用 Tiled 编辑，见本页末尾。

---

## 第一步：主世界场景

新建 `Game/Scenes/Overworld/myfirst.lua` ，内容如下：

```lua
local scene = {}
local ow = ImportFile("Overworld")

ow.Init("Maps/main_scene/main_0.lua")
ow.SetMusic("Start.ogg")

function scene.update(dt)
    ow.Update(dt)
end

function scene.draw()
    ow.Draw()
end

function scene.clear()
    ow.Clear()
    Layers.clear()
end

return scene
```

五个部分的作用：

| 代码 | 作用 |
|---|---|
| `ImportFile("Overworld")` | 导入主世界库，同时注册 `Map` / `Char` / `DATA` 等全局变量 |
| `ow.Init(路径)` | 载入地图，并把镜头限制到地图实际覆盖范围 |
| `ow.SetMusic(路径)` | 播放背景音乐，已在播放的同名音乐不会重复播放 |
| `ow.Update(dt)` 与 `ow.Draw()` | 每帧推进与绘制 |
| `ow.Clear()` 与 `Layers.clear()` | 离开场景时销毁地图并清图层 |

!!! danger "`scene.clear` 里两行都不能少"
    `ow.Clear()` 销毁地图的全部碰撞体与贴图、解开镜头边界、清掉整棵 `Scripts.Libraries.Overworld` 的模块缓存。<br>
    少写该行会导致第二次进入主世界时拿到上一局的残留状态。

!!! warning "地图路径的 Game 区覆盖"
    `Maps/main_scene/main_0.lua` 会先查找 `Game/Maps/main_scene/main_0.lua` ，存在则使用那份。<br>
    STI 按地图文件的相对路径找图块，因此 Game 区那份旁边必须有对应的 `../images/` 目录树，否则图块整片丢失。

---

## 第二步：设为初始场景

在 `Game/conf_pure.lua` 中加一行：

```lua
Global.SetVariable("FirstRoom", "Overworld.myfirst")
```

---

## 验证点

按 F5 重新载入（或重启游戏）后逐项核对：

| 检查项 | 预期结果 |
|---|---|
| 地图显示 | 地面与墙体出现在屏幕上 |
| 角色移动 | 用方向键控制角色走动，镜头跟随 |
| 墙体碰撞 | 走到墙边会被挡住，不会穿过去 |
| 背景音乐 | `Start.ogg` 开始播放 |

!!! warning "地图是纯黑或整片丢失"
    图块路径按地图文件的相对位置解析。把地图文件复制到别处而没有带上 `Maps/images/` 时，图块会全部找不到。

!!! warning "角色无法移动"
    检查 `scene.update` 里是否调用了 `ow.Update(dt)` ，以及 `scene.draw` 里是否调用了 `ow.Draw()` 。

---

## 加一个对话触发

主世界里的对话由**接触 + 确认**两步触发：玩家站在对象上时 `getInteractResult` 返回 `true` ，再按确认键才弹出对话。

在 `scene.update` 里加入：

```lua
function scene.update(dt)
    ow.Update(dt)

    if (ow.getInteractResult("trigger", 1)) then
        if (Controller.GetState("confirm") == 1) then
            ow.dialogNew({"* 这是一张测试地图。"})
        end
    end
end
```

- `getInteractResult("trigger", 1)` 的类型名对应地图里的对象层名（ `triggers` 层的对象类型为 `trigger` ），数字对应对象的 `id` 属性。
- `Controller.GetState("confirm") == 1` 表示确认键刚按下，长按不会重复触发。
- 引擎自带 `main_0` 地图中 `id` 为 1 的 trigger 位于 Tiled 坐标 `(20, 100)` ，运行时世界坐标约为 `(40, 200)` 。

!!! warning "运行时坐标是 Tiled 坐标的 2 倍"
    地图瓦片为 20 × 20，绘制时整体放大 2 倍，因此一个瓦片在世界里占 40 × 40。<br>
    引擎生成碰撞体时已完成换算， `obj.x` 即为世界坐标；手动写死数值时需要自行乘 2。

!!! tip "找不到交互对象在哪"
    把 `Overworld.debug` 设为 `true` ，所有对象的碰撞体会按类型分颜色画出来；按空格可将镜头瞬移到鼠标所指的世界坐标。

---

## 自建地图

引擎自带地图之外，新建一张需要用 Tiled 编辑，并遵守引擎对图层与属性的约定：

| 步骤 | 说明 |
|---|---|
| 建图块集 | 20 × 20 瓦片，图块集必须嵌入地图 |
| 建碰撞层 | `walls` 层，引擎据其生成碰撞体 |
| 建出生点 | `marks` 层， `id` 决定从哪个点进入 |
| 建交互层 | `triggers` / `signs` / `warps` / `saves` / `chests` |
| 导出 | 存为 `.lua` 放进 `Maps/` ，再传给 `ow.Init` |

完整说明见 [Overworld → 地图与对象层](../040_overworld/010_map.md) 与 [Overworld → STI 与图块集](../040_overworld/015_sti.md) 。

---

## 这条路线之后可以做的事

| 接下来想做 | 去哪 |
|---|---|
| 切换场景、NPC 对话 | [Overworld → 交互与对话](../040_overworld/030_interact.md) |
| 玩家贴图、移动、朝向 | [Overworld → 角色](../040_overworld/020_char.md) |
| 菜单、存档点、箱子 | [Overworld → 菜单 · 存档 · 箱子](../040_overworld/040_menu.md) |
| 走路遇敌并进入战斗 | [Overworld → 遇敌](../040_overworld/050_encounter.md) |
| 做一个商店 | [Overworld → 商店](../040_overworld/060_shop.md) |

全部去向见 [接下来读什么](./060_next.md) 。
