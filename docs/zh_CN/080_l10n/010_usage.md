---
title: 查词与替换
---

查词只有一个入口：

```lua
Localize.localizeText(键)
Localize.localizeText(键, 替换参数)
```

`Localize` 是全局（`main.lua` 启动时 `ImportFile("Localize")`），任何地方都能直接调。

---

## 键的两种写法

| 写法 | 例子 | 说明 |
|---|---|---|
| 字符串 | `"Battle.Spare"` | 最常用 |
| 表 | `{"Battle", "Spare"}` | 内部用 `.` 拼起来，等价于上面那种 |

```lua
Localize.localizeText("Battle.Spare")
Localize.localizeText({"Battle", "Spare"})     -- 同一个键
```

!!! warning "表里只有字符串元素会被拼进去"
    拼接时是 `if type(elements[i]) == "string"` 才收，数字、布尔会被**静默丢掉**。
    拼完是空表的话返回 `nil` 并打印 `Invalid localization key table.` 。

---

## 替换参数（formats）

第二个参数会交给 `string.format` ，支持 `%s` `%d` `%f` `%x` 等全部占位符。

```json
"Battle.HP.NotFull": "* 你回复了%sHP!"
```

```lua
Localize.localizeText("Battle.HP.NotFull", {12})
-- -> "* 你回复了12HP!"
```

### 多个占位符

按顺序填入，顺序错误会导致文本错乱：

```json
"Battle.WinTexts1": "* 你赢了！[wait:0.5]\n* 你获得了 %s XP 和 %s 金钱。\n"
```

```lua
Localize.localizeText("Battle.WinTexts1", {exp, gold})
```

### 单个值不用包表

传入非表值时，引擎会自动包一层表：

```lua
Localize.localizeText("Battle.HP.NotFull", 12)      -- 等价于 {12}
```

!!! warning "参数不匹配会返回原文"
    `string.format` 失败时（参数不够、类型不对、多了 `%` ）引擎**不报错**，
    只打印一行 `[L10N WARNING] string.format failed for key: ...` ，
    然后**原样返回带 `%s` 的字符串**。玩家会看到字面量的 `%s` 。

    ```lua
    Localize.localizeText("Battle.HP.NotFull")       -- 未传参数
    -- -> "* 你回复了%sHP!"   ← 原样返回，占位符未被替换
    ```

---

## 返回值不止是字符串

查到的值有两类合法类型，返回行为不同：

| JSON 里的值 | 不传 formats | 传 formats |
|---|---|---|
| 字符串 | 替换后返回字符串 | 同左 |
| 数组 | **原样返回整个数组** | **逐项**对每个字符串元素做替换，返回新数组 |

```json
"Overworld.Menu.Buttons": ["物品", "状态", "电话"],
"Battle.GameoverText": ["* 我们的命运都\n  寄托于你...", "* %s![wait:0.5]\n  保持你的决心..."],
"Overworld.Menu.Interval": [215, 312, 425]
```

```lua
Localize.localizeText("Overworld.Menu.Buttons")[1]           -- "物品"
Localize.localizeText("Battle.GameoverText", {Player.name})  -- 数组，两句话都替换了 %s
local x = tonumber(Localize.localizeText("Overworld.Menu.Interval")[1])  -- 215
```

!!! tip "本地化文件也用来存排版数值"
    `Overworld.Menu.Interval` 是一组 x 坐标，不是文字。
    因为不同语言按钮长度不同，把坐标放进翻译文件是合理用法。

!!! warning "数组里的非字符串元素原样保留"
    逐项替换时 `else result[i] = current[i]` —— 数字不会被 `string.format` 处理。

---

## 动态拼键

键可以在运行时拼接，用于为每个敌人/每个动作配置不同文本。
引擎的战斗场景采用该方式：

```lua
-- Scripts/Scenes/Battle/scene_battle_init.lua:24
Battle.BattleDialogue(
    Localize.localizeText("Battle.Actions.Texts." .. enemy.id .. "." .. action.id),
    "ACTIONSELECT"
)
```

对应 JSON 里的键：

```json
"Battle.Actions.Texts.Poseur.Check": ["* 颇似儿[wait:0.5] - 0 攻击 0 防御..."],
"Battle.Actions.Texts.Poseur.Pose":  ["* 你和颇似儿一起摆姿势..."]
```

!!! warning "拼出来的键不会自动找父级"
    `Battle.Actions.Texts.Poseur.Pose` 不存在就是不存在，
    **不会**回退到 `Battle.Actions.Texts.Poseur` 。缺一个敌人就少一段对话。

---

## 引擎在哪里查词

| 位置 | 用到的键 |
|---|---|
| `Game/Encounter/*.lua` | `Battle.Narration.Default` 、 `Battle.EnemiesName.*` 、 `Battle.Actions.Names.*` |
| `Scripts/Scenes/Battle/scene_battle*.lua` | `Battle.Actions.Texts.<敌人>.<动作>` |
| `Scripts/Scenes/scene_gameover.lua` | `Battle.GameoverText` |
| `Scripts/Libraries/Overworld/stat.lua` | `Overworld.Menu.Buttons` / `.Item` / `.Stat` / `.Interval` |
| `Scripts/Libraries/Overworld/shop.lua` | `Overworld.Shop.Action.<动作>` |
| `Scripts/Libraries/Overworld/Pages/save.lua` | `Overworld.Save.Buttons` / `.Success` |
| `Scripts/Libraries/Overworld/Pages/chest.lua` | `Overworld.Chest.Title` / `.Tip` |
| `Scripts/Waves/nobody_came.lua` | `Overworld.Text.NobodyCame` |
| `Scripts/Libraries/Controller/VirtualKeyboard.lua` | `VirtualKeyboard.*` |

引擎自带键的完整清单直接看 `Localization/zh_CN.json` ，按前缀分组：

| 前缀 | 管什么 |
|---|---|
| `Battle.Narration.*` | 进入战斗的第一句旁白 |
| `Battle.Spare` / `.Flee` | 战斗按钮 |
| `Battle.HP.*` | 回血提示 |
| `Battle.Items.Page` / `Battle.WinTexts*` | 物品分页、胜利结算 |
| `Battle.GameoverText` | 游戏结束的两句话 |
| `Battle.EnemiesName.<敌人id>` | 敌人名字 |
| `Battle.Actions.Names.<动作id>` | ACT 菜单里的动作名 |
| `Battle.Actions.Texts.<敌人id>.<动作id>` | 选中动作后说的那几段话 |
| `Overworld.Menu.*` | 菜单按钮、STAT 面板排版 |
| `Overworld.Save.*` / `Overworld.Chest.*` | 存档页、箱子页 |
| `Overworld.Shop.Action.*` | 商店的买/卖/交谈/离开 |
| `VirtualKeyboard.*` | 虚拟按键编辑器的界面文案 |

!!! example "给自己的敌人加翻译"
    1. 在 `Game/Encounter/<敌人名>.lua` 中调用 `Localize.localizeText("Battle.EnemiesName.Sol")`
    2. 在 `Game/Localization/<语言>.json` 中加入 `"Battle.EnemiesName.Sol": "索尔"`
    3. F2 重载

    键名只要两侧一致即可；沿用引擎的前缀便于维护。

---

## 缺键会怎样

```lua
if current == nil then
    print("[L10N WARNING] Missing localization key: " .. tostring(elements))
    return nil
end
```

不报错，返回 `nil` 。但这个 `nil` 会被直接交给调用方：

```lua
-- 战斗里：nil 直接进了打字机
Battle.BattleDialogue(Localize.localizeText("..."), "ACTIONSELECT")
```

`Typers.EText.New(nil, ...)` 在后续遍历文本时会抛出错误，表现为按键之后才出错，
而不是显示空白。终端中出现 `Missing localization key` 是**崩溃或显示异常**的信号。

!!! warning "每帧查词会把警告刷满"
    菜单类代码每帧重绘、每帧查词，缺一个键就是每秒 60 行警告。
    需要补上该键，或像虚拟键盘那样自行缓存结果。

---

## 打字机标签原样透传

翻译文本里的 `[wait:0.5]` 、 `[speed:0.05]` 、 `\n` **不是本地化层处理的**，
`localizeText` 只做 `string.format` ，标签会原样交给打字机解释。

```json
"Battle.Narration.Default": "* 颇似儿摆了[wait:0.5]\n  [speed:0.05]一个姿势！"
```

!!! warning "写 JSON 时换行是 `\n`"
    JSON 里不能直接换行，必须写 `\n` 转义。打字机的排版（比如缩进两格）
    是靠字符串里的空格实现的，翻译时要把空格一起保留。

---

## 虚拟键盘的特殊通道

虚拟键盘不直接调 `localizeText` ，而是走自己的 `VirtualKeyboard.L(key)` ：

```lua
function VirtualKeyboard.L(key)
    -- ① 先查 "VirtualKeyboard." .. key
    local full = VirtualKeyboard.l10nPrefix .. key
    local ok, value = pcall(l.localizeText, full)
    cached = (ok and type(value) == "string" and value ~= "") and value or false
    if (cached) then return cached end

    -- ② 查不到就用内置词表
    local set = LABEL_SETS[resolveLanguage()] or LABEL_SETS.en
    return set[key] or LABEL_SETS.en[key] or key
end
```

| 字段 / 函数 | 作用 |
|---|---|
| `VirtualKeyboard.useLocalize` | 默认 `true` ，关掉就只用内置词表 |
| `VirtualKeyboard.l10nPrefix` | 默认 `"VirtualKeyboard."` |
| `VirtualKeyboard.SetLanguage("zh"/"en"/table)` | 强制指定，传表就是自定义整份词表 |
| `VirtualKeyboard.ClearLabelCache()` | 清缓存，**运行期切语言后必须调** |

!!! note "它是唯一带内置兜底词表的模块"
    其他模块缺键时返回 `nil` ，虚拟键盘缺键会回退到 `LABEL_SETS.en` ，
    最多显示英文，不会崩溃。修改其文案时，在 JSON 中加入 `VirtualKeyboard.<key>` 即可。

---

## 常见问题

!!! warning "值是数字/布尔会返回 nil"
    只有 `string` 和 `table` 合法。写 `"Battle.Foo": 123` 会打印
    `Invalid localization value for key: ...` 并返回 `nil` 。

!!! warning "JSON 中不要写尾部逗号与注释"
    dkjson 对宽松 JSON 的容忍度有限（它支持 `//` 和 `/* */` 注释，
    但尾部逗号不行）。解析失败会回退到 `en` 并打印位置信息：

    ```
    [L10N WARNING] Invalid language file.
                   Using default language. (en)
    [L10N Error]   ... JSON parse error at position 123 in ...: ...
    ```

    用那个 `position` 直接定位字符。

!!! warning "修改翻译未生效的排查顺序"
    1. 终端那行 `using language: xxx (路径)` 是否为所修改的文件
    2. 是不是改完没按 **F2**
    3. JSON 是不是解析失败了（会有 `Invalid language file` 警告）
    4. 键名是不是拼错了（会有 `Missing localization key` 警告）
    5. 中文是不是乱码（文件编码应为 UTF-8）
