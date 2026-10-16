---
title: 游戏逻辑与世界规则
---

`Game/Logics/` 存放**仅属于当前游戏的内容**：世界的初始状态、等级成长方式、剧情开关、箱子内容。修改这里**不需要改动引擎**。

路径： `Game/Logics/init.lua` （世界的初始状态与规则表）、 `Game/Logics/items.lua` （物品表）。

> 本页说明世界规则这一层。<br>
> `DATA` 每个字段在运行时怎么用见 [Overworld → 初始化与场景骨架](../040_overworld/000_init.md) ；<br>
> 物品表怎么用也在这篇的 `ITEMS` 一节；<br>
> Game 区的覆盖顺序见 [Game 区与资源覆盖](./110_game_area.md) 。

---

## 它是怎么被加载的

```lua
-- Scripts/Libraries/Overworld/init.lua
DATA  = DATA or require("Game.Logics")
FLAG  = DATA.flags
CHEST = DATA.chests
```

!!! warning "这个文件没有引擎兜底"
    引擎是**硬 require** `Game.Logics` 的，不像贴图、波次那样在 Game 区缺失时回退到 `Scripts/` 。<br>
    缺失 `Game/Logics/init.lua` 会导致主世界无法启动。

!!! tip "这张表就是存档"
    存档页执行的是 `Global.SetSaveVariable("Overworld", DATA)` —— **整张 `DATA` 直接写盘**。<br>
    所以在 Logics 里加一个字段，等于给存档加一个字段。

`items.lua` 是例外，它走 Game 优先： `Game.Logics.items` → `Scripts.Logics.items` （当前工程里引擎那份并不存在，实际只有 Game 区这份）。

---

## 文件的骨架

```lua
local path = (...):match("(.-)[^%.]+$")
local logic = {}

Global.SetVariable("FUN", math.random(0, 100))   -- ① 顶层就能设全局变量

logic = { ... }            -- ② 世界的默认状态（玩家、位置、背包…）
logic.flags   = { ... }    -- ③ 剧情开关
logic.chests  = { ... }    -- ④ 箱子里有什么
logic.lv_data = { ... }    -- ⑤ 世界规则：等级曲线

-- Global.DeleteSaveVariable("Overworld")          -- ⑥ 调试时强制开新档
if (Global.GetSaveVariable("Overworld")) then
    logic = Global.GetSaveVariable("Overworld")    -- ⑦ 存过档就用存档那份
end

return logic
```

- **①** 顶层可以直接设全局变量。 `FUN` 对应 UNDERTALE 中的有趣度，每次开新档重新随机。
- **⑦** 存在存档时整份替换默认值，因此**修改 Logics 后未生效**由该逻辑导致，见 [Overworld → 初始化与场景骨架](../040_overworld/000_init.md) 里的 `DATA` 一节。调试时可注释该语句，或用 **⑥** 直接删除存档。

---

## lv_data：成长曲线

满级等级、每级血量、升级所需经验都记录在这一张表中。

| 字段 | 含义 |
|---|---|
| `lv` | 等级 |
| `hp` | 升到这一级时的**最大血量**（直接覆盖 `maxhp` ） |
| `at` | 攻击力 → 写进 `DATA.player.atk` |
| `df` | 防御力 → 写进 `DATA.player.def` |
| `totalExp` | 升到这一级所需的**累计** EXP，而非本级所需的经验 |

??? example "引擎自带的 20 级表"
    ```lua
    logic.lv_data = {
        { lv = 1,  hp = 20,  at = 10,  df = 10, totalExp = 0      },
        { lv = 2,  hp = 24,  at = 12,  df = 10, totalExp = 10     },
        { lv = 3,  hp = 28,  at = 14,  df = 10, totalExp = 30     },
        { lv = 4,  hp = 32,  at = 16,  df = 10, totalExp = 70     },
        { lv = 5,  hp = 36,  at = 18,  df = 11, totalExp = 120    },
        { lv = 6,  hp = 40,  at = 20,  df = 11, totalExp = 200    },
        { lv = 7,  hp = 44,  at = 22,  df = 11, totalExp = 300    },
        { lv = 8,  hp = 48,  at = 24,  df = 11, totalExp = 500    },
        { lv = 9,  hp = 52,  at = 26,  df = 12, totalExp = 800    },
        { lv = 10, hp = 56,  at = 28,  df = 12, totalExp = 1200   },
        { lv = 11, hp = 60,  at = 30,  df = 12, totalExp = 1700   },
        { lv = 12, hp = 64,  at = 32,  df = 12, totalExp = 2500   },
        { lv = 13, hp = 68,  at = 34,  df = 13, totalExp = 3500   },
        { lv = 14, hp = 72,  at = 36,  df = 13, totalExp = 5000   },
        { lv = 15, hp = 76,  at = 38,  df = 13, totalExp = 7000   },
        { lv = 16, hp = 80,  at = 40,  df = 13, totalExp = 10000  },
        { lv = 17, hp = 84,  at = 42,  df = 14, totalExp = 15000  },
        { lv = 18, hp = 88,  at = 44,  df = 14, totalExp = 25000  },
        { lv = 19, hp = 92,  at = 46,  df = 14, totalExp = 50000  },
        { lv = 20, hp = 99,  at = 48,  df = 14, totalExp = 99999  }
    }
    ```

### 升级是怎么结算的

战斗结束时，引擎的 `Battle.SyncToOverworld()` （在 `Scripts/Libraries/Battle/init.lua` ，由 `Battle.Clear()` 调用）会把结果写回 `DATA` ：

```lua
DATA.player.exp = DATA.player.exp + (Battle.EXP or 0)
DATA.player.gold = DATA.player.gold + (Battle.GOLD or 0)
DATA.player.hp = math.max(0, math.min(DATA.player.maxhp, Player.hp))

while (DATA.lv_data[DATA.player.lv + 1] and
       DATA.player.exp >= DATA.lv_data[DATA.player.lv + 1].totalExp) do
    local old_max = DATA.player.maxhp
    DATA.player.lv = DATA.player.lv + 1

    local row = DATA.lv_data[DATA.player.lv]
    DATA.player.maxhp = row.hp
    DATA.player.atk = row.at
    DATA.player.def = row.df

    -- UNDERTALE 的规则：最大血量涨多少，当前血量也跟着涨多少
    DATA.player.hp = math.min(DATA.player.maxhp, DATA.player.hp + (DATA.player.maxhp - old_max))
end
```

!!! example "结算规则小结"
    - 一次战斗可以**连升多级**（是 `while` 不是 `if` ）。
    - `maxhp` / `atk` / `def` 是**按表覆盖**，不是累加；表里写多少就是多少。
    - 涨的那部分最大血量会**同时加到当前血量**上（升级即回血）。
    - `weapon` / `armor` / `gold` / `exp` 不归等级表管。

!!! warning "`watk` / `edef` 目前只是显示用"
    `player.watk` （武器攻击）与 `player.edef` （防具防御）只出现在 STAT 菜单的显示里，引擎**没有**把它们加到 `atk` / `def` 上。<br>
    需要装备生效时，需在结算或伤害计算处自行加入。

---

### 扩展到 LV 30

封顶完全由**表长**决定 —— 循环条件是 `DATA.lv_data[lv + 1]` 存在，所以：

```lua
{ lv = 21, hp = 106, at = 50, df = 15, totalExp = 150000 },
{ lv = 22, hp = 113, at = 52, df = 15, totalExp = 220000 },
-- ... 一直加到 30
```

添加后无需修改引擎代码，菜单、升级结算与经验显示会一并生效。

!!! warning "满级时打开 STAT 菜单会报错"
    `Overworld.CalcNextEXP()` 是这样写的：

    ```lua
    local next_total = DATA.lv_data[DATA.player.lv + 1].totalExp   -- 没有判空
    ```

    满级时 `lv_data[lv + 1]` 为 `nil` ，**直接索引 nil 会报错**，表现为升到满级后打开 STAT 页面即报错。<br>
    两种处理方式：将等级表**多写一行**（例如满级为 20 时写到 21， `totalExp` 保持一个足够大的值），或为 `CalcNextEXP` 补充判空（返回 0 或 `"--"` ）。

!!! tip "经验阈值的含义"
    `totalExp` 是**累计**经验，不是本级所需经验。第 20 级的 `99999` 表示累计攒够 99999 EXP 才能升到 20 级，而非再打 99999。

---

## flags：世界的开关

```lua
logic.flags = {
    test_killed = 0
}
```

引擎会把它挂成全局 `FLAG` ，直接用即可：

```lua
FLAG["test_killed"] = 1
if (FLAG["test_killed"] == 1) then
    -- 剧情分支
end
```

整张 `DATA` 都会写入存档， `flags` 因此**随存档保存**，无需额外操作。

## chests：箱子里有什么

```lua
logic.chests = {
    chest = { "Spider" },   -- 键名对应箱子的 id
    chest1 = {}
}
```

同样会挂成全局 `CHEST` 。开箱子时按 id 取此处的列表，取完需清空，否则可以重复开启（详见 [菜单 · 存档 · 箱子](../040_overworld/040_menu.md) ）。

---

## 新增字段时的注意事项

!!! warning "旧存档不包含新字段"
    存档按**整张表**保存。为 `player` 新增 `sanity = 100` 后，此前保存的存档中该字段为 `nil` 。<br>
    读取时可提供默认值（ `DATA.player.sanity or 100` ），或在开发期删除存档重开。

!!! warning "`getcell` 被引擎强制打开了"
    `player.getcell` 在 Logics 里写的是 `false` ，但 `Scripts/Libraries/Overworld/stat.lua` 顶层有一句 `DATA.player.getcell = true` 会把它覆盖掉。<br>
    因此 CELL（电话）菜单默认处于开启状态，修改 Logics 中的该字段不生效。

---

## 为什么单独有这一层

世界规律集中在一个文件中，**调整数值时无需修改引擎**：

| 想改什么 | 改哪儿 |
|---|---|
| 满级是 20 还是 30 | `lv_data` 加/删行 |
| 每级多少血、多少攻防 | `lv_data` 的 `hp` / `at` / `df` |
| 升级要多快 | `lv_data` 的 `totalExp` |
| 开局叫什么、拿什么、在哪出生 | `player` 与 `room` / `marker` / `position` |
| 剧情分支记在哪 | `flags` |
| 箱子里给什么 | `chests` |
| 物品有哪些 | 同目录的 `items.lua` |

世界观层面的设定（例如 20 级封顶或 30 级封顶）在 `Game/Logics/` 中即可确定，无需修改引擎。
