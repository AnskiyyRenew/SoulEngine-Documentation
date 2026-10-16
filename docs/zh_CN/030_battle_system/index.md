---
title: 战斗系统
---

本专题描述 `SoulEngine` 的战斗模块，涵盖 Battle、UI、Player、PlayerAttacks、Game、Wave、Animation 等库的职责与协作方式。

> 这些库在战斗系统中分层承担不同职责，彼此依赖。文档中按库分篇说明，便于定位代码，单个库不独立运行。

> 本专题中反复出现的 `Game 区` 概念与资源查找顺序，统一说明见 **[基础开发 → Game 区与资源覆盖](../020_basic/110_game_area.md)** 。

战斗流程如下：
```
进入战斗
  ↓
Game 提供遭遇数据
  ↓
Wave 初始化波次
  ↓
UI 进入战斗状态（stateinner）
  ↓
Player 接收输入 → PlayerAttacks 结算
  ↓
Animation 播放表现
  ↓
Wave 推进回合
  ↓
UI 更新状态 / 判断结束
  ↓
（循环回 Player 或退出）
```

---

---

## 本专题页面

| 页面 | 内容 |
|---|---|
| [战斗初始化](./000_init.md) | 战斗场景图层、遭遇文件、敌人动画 |
| [UI](./010_ui.md) | 战斗框下的界面、按钮、状态中枢 |
| [战斗框](./020_arena.md) | Arena 的创建、缩放、挖洞、遮罩 |
| [玩家与灵魂](./030_player.md) | Player 数据、四种灵魂、单向平台 |
| [攻击模式](./040_attack.md) | 校准条、伤害公式、自定义武器 |
| [回合脚本](./050_waves.md) | 敌人回合怎么写 |
| [弹幕库](./060_bullets.md) | 骨头、骨墙、3D 骨架、追踪炮 |
| [战斗场景与回调](./070_scene.md) | 场景骨架、回调一览、流程控制 |

---

## 游戏

负责定制遭遇战的数据和敌人。

遭遇战路径： `Game/Encounter/` 。

Game 区路径： `Game/` （包含 `Animations` 、 `Encounter` 、 `Waves` 、 `Souls` 等内容的根目录）。

---

## 怪物动画

负责播放敌人动画。

路径： `Game/Animations/` 。

---

## UI

路径： `Scripts/Libraries/Battle/UI/` 。

屏幕上其余可见内容由 `UI` 库统一管理，其中 `stateinner.lua` 覆盖从进入战斗到选项处理、敌人回合、战斗结束的完整流程。

[UI](./010_ui.md) 页面另对 `stateinner` 之外的部分作详细说明。

---

## 玩家

路径： `Scripts/Libraries/Battle/Player/` 。

玩家独立灵魂路径： `Game/Souls/` （Game 区，优先）、 `Scripts/Libraries/Battle/Player/Souls/` （引擎默认，兜底）。

玩家攻击路径： `Game/Attacks/` （Game 区，优先）、 `Scripts/Libraries/Battle/PlayerAttacks/` （引擎默认，兜底）。

---

## 回合

负责敌人回合。

路径： `Game/Waves/` （Game 区，优先）、 `Scripts/Waves/` （引擎默认，兜底）。

按照引擎的 `Game 优先、主目录兜底` 约定：先在 `Game/Waves/` 中查找同名波次，找到就直接使用；没有才回退到 `Scripts/Waves/` ，并会在终端输出一条警告。

弹幕库的路径： `Scripts/Libraries/Attacks/` 。

---