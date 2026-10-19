---
title: 第一场战斗
---

本页是路线 A：从零做出一场能打的战斗。读完并做完本页，敌人会显示在屏幕上，可以完成一次攻击结算与一个敌人回合。

前置：[通用底座](./index.md) 四页已读完。

---

## 一场战斗由三份文件组成

| 文件 | 负责什么 | 本页放的位置 |
|---|---|---|
| 遭遇文件 | 敌人是谁、多少血、掉多少 GOLD 与 EXP | `Game/Encounter/myfirst.lua` |
| 波次文件 | 敌人回合里发生什么、多久结束 | `Game/Waves/myfirst.lua` |
| 战斗场景 | 把前两份装起来，处理按钮与伤害 | `Game/Scenes/Battle/myfirst.lua` |

!!! note "为什么都放进 `Game/`"
    `Game/` 是每个游戏的内容根。与引擎目录同名时 Game 区优先，引擎升级不会覆盖这里的文件。完整规则见 [基础开发 → Game 区与资源覆盖](../020_basic/110_game_area.md) 。

---

## 第一步：遭遇文件

复制 `Game/Encounter/_temp.lua` ，在同一目录下改名为 `myfirst.lua` ，内容替换为下面这份：

```lua
local encounter = {
    narration = "* 第一场战斗开始了。",
    can_flee = true,
    flee_percent = 0.75,
    enemy_id = 1,
    enemies = {
        {
            id = "MyFirst",
            name = "练习木桩",
            animation = require("Game.Animations.Poseur"),

            maxdamage = 400,
            dmg_float = 2,

            show_hpbar = true,
            maxhp = 100,
            hp = 100,
            gold = 1,
            exp = 1,

            defensetext = "MISS",
            misstext = "MISS",

            canspare = true,
            killable = true,

            position = {320, 140},
            actions = {
                {id = "Check", name = "查看"},
            }
        },
    },

    state = "ACTIONSELECT",
    wave = "myfirst",

    player = {
        name = "Chara",
        lv = 1,
        maxhp = 20,
        hp = 20
    },

    items = {
        {id = "CHOCOLATE", _color = {0.4, 1, 1}, name = "Chocolate"},
    }
}

for i = 1, #encounter.enemies
do
    local e = encounter.enemies[i]
    e._id = encounter.enemy_id
    encounter.enemy_id = encounter.enemy_id + 1
end

return encounter
```

需要理解的字段如下，其余保持默认即可：

| 字段 | 含义 |
|---|---|
| `narration` | 进入战斗时战斗框上方的第一句旁白 |
| `enemies[].id` | 敌人标识，ACT 的台词按它查找 |
| `enemies[].name` | ACT 菜单里显示的名字 |
| `enemies[].animation` | `require` 一个动画模块，从 `Game/Animations/` 起算 |
| `enemies[].maxhp` / `hp` | 血量上限与当前血量 |
| `enemies[].show_hpbar` | 是否显示血条 |
| `enemies[].maxdamage` | 单次攻击的伤害上限，负值表示反过来回血 |
| `enemies[].position` | 敌人在画面上的位置，画布为 640 × 480 |
| `enemies[].actions` | ACT 菜单里出现的动作 |
| `state` | 进入战斗后的初始状态， `ACTIONSELECT` 表示立刻可以操作 |
| `wave` | 敌人回合使用的波次文件名，不带扩展名 |
| `player` | 玩家的名字、等级与血量 |
| `items` | 战斗中的背包，ITEM 菜单读它 |

!!! warning "`animation` 指向的文件必须存在"
    `require("Game.Animations.Poseur")` 对应 `Game/Animations/Poseur.lua` 。文件缺失时整个遭遇无法加载。<br>
    引擎自带 `Poseur` 、 `dummy` 、 `loox` 、 `sans` 四份，可直接引用。

!!! tip "从主世界进入时 `player` 会被覆盖"
    由 Overworld 触发的战斗会先读取存档数据，遭遇里的 `player` 只作为无存档时的模板。完整说明见 [战斗系统 → 战斗初始化](../030_battle_system/000_init.md) 。

---

## 第二步：波次文件

复制 `Scripts/Waves/_template.lua` 到 `Game/Waves/myfirst.lua` 。模板里 `EndWave()` 是注释状态，回合不会结束，改成下面这样：

```lua
local wave = ImportFile("Battle.Waves")
local EndWave = wave.EndWave
local Arena = Battle.mainarena
Player.canMove = true

local mask = Masks.New("rectangle", 320, 320, 155, 130, 0, 0)

local time = 0
function wave.Update(dt)
    mask:Follow(Arena.black)

    time = time + 1
    if (time == 180) then
        EndWave()
    end
end

return wave
```

- `time` 按帧累加，默认每秒 60 帧，因此 `180` 约等于 3 秒。
- `EndWave()` 结束敌人回合并把操作权交回玩家。**不调用该函数的回合不会结束。**

波次是敌人回合的全部内容，本页只做空回合。往里放弹幕的方式见 [战斗系统 → 弹幕库](../030_battle_system/060_bullets.md) 。

---

## 第三步：战斗场景

复制 `Scripts/Scenes/Battle/scene_battle_template.lua` 到 `Game/Scenes/Battle/myfirst.lua` ，改头部的两处：

```lua
Battle = ImportFile("Battle")
Battle.SetEndRoom("scene_end")
Game = Battle.SetGame("myfirst")
Game:InitAnimation(1, {320, 140})
```

- `Battle.SetGame("myfirst")` 的参数是 `Game/Encounter/` 下的文件名，不带 `.lua` 。
- `Game:InitAnimation(1, {320, 140})` 为第 1 个敌人创建动画实例并放在 `{320, 140}` 。

!!! danger "不调用 `InitAnimation` 时敌人不会出现"
    `enemy.animation` 在初始化之前只是动画**模块**，不是实例。引擎每帧只驱动带 `_bound` 标记的实例，模块会被直接跳过，也就不会创建任何贴图。<br>
    表现为战斗能进入、UI 与按钮都正常，但屏幕上看不到敌人，终端无报错。

场景末尾的三个函数是固定的，保持原样即可：

```lua
function scene.update(dt)
    Battle.Update(dt)
    Blasters.Update(dt)
end

function scene.clear()
    Layers.clear()
    Battle.Clear()
end
```

!!! warning "`scene.clear` 里两行都不能少"
    `Battle.Clear()` 清掉战斗库与本场遭遇、动画、波次、灵魂的模块缓存。<br>
    少写该行会导致第二次进入战斗时拿到上一场的残留状态。

---

## 第四步：设为初始场景

在 `Game/conf_pure.lua` 中加一行：

```lua
Global.SetVariable("FirstRoom", "Battle.myfirst")
```

---

## 验证点

按 F5 重新载入（或重启游戏）后逐项核对：

| 检查项 | 预期结果 |
|---|---|
| 敌人可见 | 屏幕上方出现敌人贴图，位于 `{320, 140}` |
| 战斗框 | 屏幕下方出现战斗框与 FIGHT / ACT / ITEM / MERCY 四个按钮 |
| 旁白 | 战斗框上方显示 `narration` 的内容 |
| 选 FIGHT | 进入攻击校准，结算后敌人 HP 减少 |
| 敌人回合 | 波次运行约 3 秒后自动结束，回到可操作状态 |
| 血条 | 敌人下方显示血条，随伤害变化 |

!!! warning "看不到敌人"
    检查场景里是否调用了 `Game:InitAnimation` ，以及 `Game/Animations/` 下的动画文件是否存在。

!!! warning "卡在敌人回合不结束"
    检查波次文件里 `EndWave()` 是否仍被注释。

!!! warning "终端提示 encounter 未找到"
    终端输出 `[Battle System] WARNING: encounter 'myfirst' not found` 时，核对 `Game/Encounter/myfirst.lua` 的文件名与 `Battle.SetGame` 的参数是否一致，两者都不带扩展名。

---

## 这条路线之后可以做的事

| 接下来想做 | 去哪 |
|---|---|
| 加第二个敌人、换敌人动画 | [战斗系统 → 战斗初始化](../030_battle_system/000_init.md) |
| 敌人回合里放骨头与弹幕 | [战斗系统 → 弹幕库](../030_battle_system/060_bullets.md) |
| 改攻击校准与伤害公式 | [战斗系统 → 攻击模式](../030_battle_system/040_attack.md) |
| 换灵魂模式（蓝、橙等） | [战斗系统 → 玩家与灵魂](../030_battle_system/030_player.md) |
| 让主世界能触发这场战斗 | [Overworld → 遇敌](../040_overworld/050_encounter.md) |

全部去向见 [接下来读什么](./060_next.md) 。
