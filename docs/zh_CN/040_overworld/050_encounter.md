---
title: 遇敌
---

主世界的遇敌采用累积步数触发：玩家每移动一步累加计时，达到阈值后播放一段 `!` 动画，再切换到战斗场景。

模块路径： `Scripts/Libraries/Overworld/encounter.lua` ，以全局 `Step` 出场。

---

## 开一局遇敌

!!! example "遇敌方法"
    - `Overworld.InitEncounter(flag, start, range, amount)` 设置本张地图的遇敌参数。
        - `flag` 击杀计数用的开关名（存在 `FLAG` 里）。
        - `start` 基础步数。
        - `range` 在 `start` 之上再随机加 `0 ~ range` 步。
        - `amount` 这张地图一共可以遇多少只怪。
    - `Overworld.SetBattleScene(scene, game)` 指定遇敌后进哪个战斗场景、用哪个遭遇文件。
        - `scene` 场景名，例如 `"Battle.scene_battle_ow"` 。
        - `game` 遭遇文件名，例如 `"Poseur"` 。
    - `Overworld.Encounter(type)` 立刻触发一次遇敌演出。
        - `type` 演出类型，目前只有 `"default"` （省略也是它）。

```lua
ow.Init("Maps/main_scene/sol.lua")

-- 走 100~160 步遇一次怪，这张图一共 12 只
ow.InitEncounter("test_killed", 100, 60, 12)
ow.SetBattleScene("Battle.scene_battle_ow", "Poseur")
```

!!! tip "击杀越多，遇敌越慢"
    引擎会按 `FLAG[flag]` 已经杀了多少只来放慢节奏：

    ```lua
    rho = math.min(8, amount / (amount - 已杀))
    time_target = rho * (start + math.random(range))
    ```

    也就是说**剩余数量较少时，间隔最多会被拉长到 8 倍**，这与原版怪物被杀光时的表现一致。

!!! note "运行时终端会额外输出四个数字"
    `Step.Init` 最后有一行 `print(time_target, rho, start, range)` ，是早期调试留下的。<br>
    每次 `InitEncounter` 都会向终端输出一行这四个数，**不是报错**，可忽略。

---

## 步数的计算

`Step.UpdateTime()` 在玩家**实际发生移动**时才加一（贴着墙原地推不算）。该调用已由引擎接入 `char.Update` ，无需自行调用。

达到阈值触发遇敌的逻辑位于 `Step.Update()` 内，该方法由 `Overworld.Update` 每帧调用。

!!! warning "每张地图都要重新 InitEncounter"
    `rho` / `time_target` / `_run` 都是 `encounter.lua` 的**文件级局部变量**。<br>
    切场景时 `ow.Clear()` 会调 `ClearModuleTree("Scripts.Libraries.Overworld")` ，把整个模块丢掉重新加载——于是 `time_target` 又变回 `math.huge` 、 `_run` 又变回 `true` 。

    结果不是沿用上一张地图的参数，而是**这一局不会触发遇敌**（ `step.time >= time_target` 始终不成立），且不报错。<br>
    因此每张地图的 `InitEncounter` / `SetBattleScene` 都**必须写在该场景自身的 `update` 或场景初始化中**。

!!! tip "不要将 `InitEncounter` 放入 `scene.update`"
    每帧调用一次会持续重置 `step.time` 之外的字段（还会每帧输出一行数字）。<br>
    写入场景文件顶层，或在首次 `update` 时用标记控制调用次数。

---

## Nobody Came

当 `FLAG[flag]` 已经 >= `amount` （怪被杀光了），再走 `60` 步就会触发原版的 "Nobody came." ：

- 全局变量 `OVERWORLD_NOBODYCAME` 被置为 `true` 。
- 强制把战斗切成 `Battle.scene_battle_ow` + `NobodyCame` 遭遇文件。
- 演出结束后 `Overworld.ChangeScene` 会把它重置回 `false` 。

如需接入其他演出，读取该全局变量判断即可。

---

## 遇敌演出

`Overworld.Encounter()` 之后是一段固定长度的过场（按帧计）：

| 帧 | 发生什么 |
|---|---|
| 0 | 玩家头顶弹出 `!` （ `lv >= 10` 时用 `spr_exc_f.png` ） |
| 60 ~ 90 | `!` 消失，黑屏与灵魂每隔 5 帧闪一次，配 `snd_tong.wav` |
| 90 | 灵魂飞向战斗框位置，配 `snd_encounter_fall.wav` |
| 130 | 记录当前位置与朝向，切到战斗场景 |

![OW-08](../img/040_overworld/ow_08_encounter.png)

---

## 与战斗场景的桥接

这部分由引擎完成。只要主世界加载过（即 `Game/Logics` 那份全局 `DATA` 存在），任何战斗场景都会：

1. **进场**时（ `Battle.SetGame()` ）把 `DATA.player` 的数据写入 `Player` （名字、LV、最大血量、当前血量）并把 `kr` 清零 —— 该操作会覆盖遭遇文件里的模板数值。
2. **出场**时（ `Battle.Clear()` ）把 `Battle.EXP` / `Battle.GOLD` / 剩余血量写回 `DATA` ，并按 `DATA.lv_data` 结算升级（升级时最大血量按表提升，并把提升量加到当前血量上）。

两半都在 `Scripts/Libraries/Battle/init.lua` 里，叫 `Battle.SyncFromOverworld()` / `Battle.SyncToOverworld()` 。它们是幂等的：写回会把 `Battle.EXP` / `Battle.GOLD` 清零，所以场景自己再写一次也**不会重复计数**。

!!! warning "纯战斗游戏不受影响"
    `DATA` 只有主世界库会创建（ `require("Game.Logics")` ）。没有主世界的游戏 `DATA` 就是 `nil` ，两个方向都会跳过，不需要任何配置。

!!! warning "脚本化战斗要自己关掉"
    某场战斗如果要刻意覆盖 `Player.hp` 且不能碰 `DATA` ，在 `Battle.SetGame(...)` 之前写
    `Battle.auto_overworld_sync = false` 。

遇敌目标场景使用 `Scripts/Scenes/Battle/scene_battle_ow.lua` ：它还负责把结束场景设为 `DATA.room` ，即**战斗结束后回到进入战斗前所在的地图**。

!!! example "遇敌相关全局量"
    - `OVERWORLD_ENCOUNTER_BATTLE` `{战斗场景名, 遭遇文件名}` ，由 `SetBattleScene` 写入。
    - `OVERWORLD_NOBODYCAME` 是否处于"没人来"状态。
    - `FLAG_KILLING_COUNTER` 当前遇敌用的击杀计数开关名，由 `InitEncounter` 写入。
    - `Battle.EXP` / `Battle.GOLD` 本场战斗的收益，写回后会被清零。

自定义战斗场景时可参照 `scene_battle_ow.lua` 实现，数据交接由引擎完成。
