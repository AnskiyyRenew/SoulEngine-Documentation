---
title: Overworld 主世界系统
---

`Overworld` 覆盖在地图上行动的部分：地图、碰撞、移动、对话、存档点、箱子、遇敌。

路径： `Scripts/Libraries/Overworld/` 。<br>
场景路径： `Scripts/Scenes/Overworld/` ，同名文件也接受 `Game/Scenes/Overworld/` 覆盖。

> 这些模块同样不是能单独运行的独立库。 `init.lua` 负责总装与调度， `map` / `char` / `world` / `stat` / `shop` / `Pages` 各自负责一个部分，彼此通过 `DATA` 与物理世界的碰撞事件通信。

> 本专题中反复出现的 `Game 区` 概念与资源查找顺序，统一说明见 **[基础开发 → Game 区与资源覆盖](../020_basic/110_game_area.md)** 。

---

## 一次主世界的运转

```
进入主世界场景
  ↓
Overworld.Init(地图路径)
  ├─ 建物理世界、注册碰撞回调
  ├─ 扫描 Tiled 对象层 → 生成碰撞体与运行时对象
  ├─ 把玩家放到出生点（mark）
  └─ 按地图实际覆盖范围自动限制镜头
  ↓
每帧 Overworld.Update(dt)
  ├─ 菜单 / 地图 / 玩家 / 存档页 / 箱子页 / 遇敌计数
  └─ 玩家碰到 warp / chest / sign / save / trigger → 记进 interactions
  ↓
场景脚本读取 interactions 并决定后续行为（对话、切场景、开箱子）
```

---

## 本专题页面

| 页面 | 内容 |
|---|---|
| [初始化与场景骨架](./000_init.md) | 场景怎么写、图层、全局变量、DATA |
| [🔧 地图与对象层](./010_map.md) | Tiled 里要建哪些层、每个层的属性、调试 |
| [🔧 STI 与图块集](./015_sti.md) | 图块集必须嵌入地图、20 × 20 图块、图块图片路径、动画图块 |
| [角色](./020_char.md) | 玩家贴图、移动、碰撞体、Frisk Dance |
| [交互与对话](./030_interact.md) | 碰撞交互、对话、切换场景 |
| [菜单 · 存档 · 箱子](./040_menu.md) | 菜单、存档点、箱子页 |
| [遇敌](./050_encounter.md) | 步数遇敌、与战斗场景的衔接 |
| [商店](./060_shop.md) | 商店场景、买卖结算、拒收台词、交谈话题与队列 |

---

## 前置要点

!!! warning "主世界的坐标要乘 2"
    地图是 `20x20` 的瓦片，绘制时整体放大 **2 倍**。<br>
    因此**运行时坐标 = Tiled 里的像素坐标 × 2** ：一个 `20x20` 的瓦片在世界里占 `40x40` 。<br>
    引擎在生成碰撞体时已完成换算，因此 `obj.x` 即为世界坐标；手动写死数值时需自行乘 2。

!!! warning "镜头是限制在地图上的"
    `Overworld.Init` 会自动扫描地图里所有非空瓦片，算出真实覆盖范围并调用 `Camera:setBounds` 。<br>
    若需自行控制，在 `Init` 之后再次调用 `Camera:setBounds` 覆盖该边界。

!!! tip "镜头默认跟着玩家"
    `Overworld.follow_player` 默认为 `true` 。设为 `false` 后镜头不跟随玩家，过场演出时可手动调用 `Camera:setPosition(x, y)` 移动镜头。
