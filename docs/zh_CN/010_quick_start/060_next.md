---
title: 接下来读什么
---

两条路线走完后，项目中已有一份可运行的结果。本页按"接下来想做什么"给出查阅入口，末尾附一份卡住时的排查顺序。

---

## 战斗

| 想做的东西 | 去哪 |
|---|---|
| 加第二个敌人、换敌人动画 | [战斗系统 → 战斗初始化](../030_battle_system/000_init.md) |
| 改战斗界面、按钮、状态栏 | [战斗系统 → UI](../030_battle_system/010_ui.md) |
| 改战斗框大小、挖洞、遮罩 | [战斗系统 → 战斗框](../030_battle_system/020_arena.md) |
| 换灵魂模式、做单向平台 | [战斗系统 → 玩家与灵魂](../030_battle_system/030_player.md) |
| 改攻击校准、伤害公式、自定义武器 | [战斗系统 → 攻击模式](../030_battle_system/040_attack.md) |
| 敌人回合的完整写法 | [战斗系统 → 回合脚本](../030_battle_system/050_waves.md) |
| 放骨头、骨墙、追踪炮 | [战斗系统 → 弹幕库](../030_battle_system/060_bullets.md) |
| 控制战斗流程、回调一览 | [战斗系统 → 战斗场景与回调](../030_battle_system/070_scene.md) |

## 主世界

| 想做的东西 | 去哪 |
|---|---|
| 场景骨架、图层、存档数据 | [Overworld → 初始化与场景骨架](../040_overworld/000_init.md) |
| 新建地图、对象层属性、调试 | [Overworld → 地图与对象层](../040_overworld/010_map.md) |
| 图块集、动画图块 | [Overworld → STI 与图块集](../040_overworld/015_sti.md) |
| 玩家贴图、移动、朝向 | [Overworld → 角色](../040_overworld/020_char.md) |
| 切换场景、NPC 对话 | [Overworld → 交互与对话](../040_overworld/030_interact.md) |
| 菜单、存档点、箱子 | [Overworld → 菜单 · 存档 · 箱子](../040_overworld/040_menu.md) |
| 走路遇敌、接进战斗 | [Overworld → 遇敌](../040_overworld/050_encounter.md) |
| 商店买卖、交谈话题 | [Overworld → 商店](../040_overworld/060_shop.md) |

## 表现与资源

| 想做的东西 | 去哪 |
|---|---|
| 贴图的全部属性与动画 | [基础开发 → 贴图](../020_basic/020_sprites.md) |
| 打字机全部标签、另两种打字机 | [基础开发 → 打字机](../020_basic/030_typers.md) |
| 图层顺序与增删 | [基础开发 → 图层系统](../020_basic/040_layers.md) |
| 背景音乐与音效 | [基础开发 → 音频](../020_basic/050_audio.md) |
| 淡入淡出、位移、缩放 | [基础开发 → 缓动](../020_basic/100_tween.md) |
| 遮罩、边框、画布与屏幕 | [基础开发 → 遮罩](../020_basic/080_mask.md) / [边框](../020_basic/090_border.md) / [画布与屏幕](../020_basic/070_screen.md) |
| 菜单类界面控件 | [基础开发 → GUI 库](../020_basic/160_gui.md) |
| 输入与手柄、按键映射 | [基础开发 → 输入与控制器](../020_basic/150_controller.md) |
| 着色器、ShaderToy 转化 | [高级开发 → 着色器](../050_intermediate/020_shaders.md) / [ShaderToy 转化库](../050_intermediate/010_shadertoy.md) |
| 引擎自带哪些素材可用 | [辅助开发 → 内置资源一览](../070_develop/060_bundled_assets.md) |

## 系统与工程

| 想做的东西 | 去哪 |
|---|---|
| Game 区覆盖规则、Hack 改写引擎 | [基础开发 → Game 区与资源覆盖](../020_basic/110_game_area.md) |
| 全局变量、存档变量 | [基础开发 → 全局变量](../020_basic/060_global.md) |
| 等级曲线、剧情开关、箱子内容 | [基础开发 → 游戏逻辑与世界规则](../020_basic/120_game_logics.md) |
| 多语言文件与查词 | [本地化](../080_l10n/index.md) |
| 奖杯、分数榜、云端存档 | [网络开发 → GameJolt API](../090_network/000_gamejolt.md) |
| Discord 活动显示 | [网络开发 → Discord RPC](../090_network/010_discord.md) |
| 联机 | [网络开发 → sock 联机](../090_network/020_sock.md) |
| 资源预加载、避免首帧卡顿 | [辅助开发 → 资源预加载](../070_develop/040_preload.md) |

## 发布

| 想做的东西 | 去哪 |
|---|---|
| 打包成 exe / APK / 网页 | [导出与发布](../100_export/index.md) |
| 发布前的检查清单 | [导出与发布](../100_export/index.md) |
| 隐藏 GameJolt 私钥 | [辅助开发 → 密钥原生库](../070_develop/050_secrets.md) |

---

## 卡住时的排查顺序

1. **先看终端输出。** 文件找不到、模块加载失败、贴图缺失都会打印带 `[WARNING]` 的行。Windows 下控制台默认开启。
2. **按 F5 热重载。** 清掉模块缓存并重进当前场景，改完代码不必重启游戏。改的是 `conf_pure.lua` 时按 F2 。
3. **按 F6 打印环境信息。** 输出当前场景名、贴图数、图层对象数，用于确认改动是否真的生效。
4. **确认文件放对位置。** Game 区优先于引擎目录，两个根都找不到时才会报错。规则见 [基础开发 → Game 区与资源覆盖](../020_basic/110_game_area.md) 。
5. **确认路径大小写。** 图片路径在 Windows 上大小写不敏感，打包到 Android 或 Linux 之后会找不到该图。

!!! note "热键只在开发版生效"
    `F5` 与 `F6` 需要 `_RELEASED = false` ，打包发布后失效。全部热键见 [辅助开发 → 引擎热键](../070_develop/030_hotkeys.md) 。

!!! tip "不确定引擎自带了什么"
    [辅助开发 → 内置资源一览](../070_develop/060_bundled_assets.md) 列出了实际被引用的字体、音效与贴图。制作内容前先查该页，可以避免重复准备素材。

---

## 回到起点

[快速上手](./index.md)
