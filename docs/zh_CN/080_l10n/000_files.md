---
title: 目录与语言文件
---

本地化只认两个目录，文件都是**一个语言一个 JSON**。

| 目录 | 归属 | 优先级 |
|---|---|---|
| `Game/Localization/` | 游戏自身 | **① 先查** |
| `Localization/` | 引擎默认 | ② 兜底 |

目录下的文件按 `<语言代码>.json` 命名，比如 `en.json` 、 `zh_CN.json` 。
当前工程里两个目录的状态：

```
Localization/
├── en.json          ← 引擎自带英文
└── zh_CN.json       ← 引擎自带中文

Game/Localization/
└── README.md        ← 目前是空的，需要你自己放 JSON 进去
```

---

## 查找顺序

两份同名文件**不是二选一**，而是**叠加**：`Game/Localization/` 是高优先级补丁层，
引擎那份是兜底层。

源码（`Scripts/Libraries/Localize.lua` 顶部）的候选层按优先级从高到低排列：

```lua
local ROOT_LOCALIZATION = "Localization/"          -- ② 兜底
local GAME_LOCALIZATION = "Game/Localization/"     -- ① 补丁
local LAYER_PATHS = { GAME_LOCALIZATION, ROOT_LOCALIZATION }
```

加载时**每一层存在的都读**，从最低优先级开始合并（`mergeInto`），高优先级逐键覆盖：

| 情况 | 结果 |
|---|---|
| Game 区有 `"A"` ，引擎没有 | 用 Game 区的 A |
| 两边都有 `"A"` | **使用 Game 区的值** |
| Game 区没写 `"A"` | **自动回退引擎那份** |

!!! note "Game 区只需要写要改的那几条"
    比如在 `Game/Localization/zh_CN.json` 里只放一句：

    ```json
    {
      "Battle.EnemiesName.Sol": "索尔"
    }
    ```

    其余上百个键（战斗按钮、菜单、存档页）仍从 `Localization/zh_CN.json` 取，
    终端不会刷 `[L10N WARNING] Missing localization key` 。

!!! warning "数组是整体替换，不是按下标合并"
    `"Battle.GameoverText": ["* A", "* B"]` 这种数组值，Game 区一旦写了就是**整份替换**。
    只修改其中一段时，也需要复制整个数组再修改。

!!! warning "某一层 JSON 解析失败时会被跳过"
    Game 区那份解析失败时，只会打印 `... (layer skipped)` 并继续使用引擎那份，
    **不会**导致整门语言失效，也**不会**退回 `en` 。（两层全部解析失败才会退回 `en` 。）

### 怎么确认当前用的是哪一份

启动时终端会把参与合并的所有层都打出来，箭头左边优先：

```
[L10N] L10n has started successfully, using language: zh_CN (Game/Localization/zh_CN.json > Localization/zh_CN.json)
```

也可以随时查：

```lua
print(Localize.GetLanguagePath("zh_CN"))   -- 优先级最高的那个路径
print(Localize.currentFile)                -- 同上，已加载语言的主来源
print(table.concat(Localize.GetSources(), " > "))   -- 参与合并的全部层，按优先级
```

---

## 选语言

语言在两个 `conf_pure.lua` 里设，**Game 区那份后执行、会覆盖引擎的**：

```lua
-- conf_pure.lua（引擎根）
Global.SetVariable("Language", "en")
Global.SetVariable("Language", "zh_CN")    -- 同一个变量写两次：后写的生效
```

游戏需要指定语言时，修改 `Game/conf_pure.lua` 中的同一行（该文件为根目录那份的完整副本）。

启动时 `main.lua` 读它：

```lua
Localize.setFile(Global.GetVariable("Language"))
```

!!! warning "Language 必须是字符串"
    `setFile` 第一行就是 `if (type(language) ~= "string")` —— 传 `nil` 会打印
    `[L10N WARNING] Invalid language file.` 然后**直接返回**，一门语言都不加载。
    之后第一次调 `localizeText` 才会懒加载 `en` ，但 `currentLanguage` 仍然是 `nil` ，
    依赖它的地方（比如虚拟键盘判断中英文）会按英文处理。

### 语言代码没有限制

`en` 、 `zh_CN` 、 `zh_TW` 、 `ja` 、 `ko` 等均可，只要与文件名一致。
唯一会解析它的是虚拟键盘，按**前两个字符**判断是不是中文：

```lua
if (code and code:sub(1, 2):lower() == "zh") then return "zh" end
```

---

## 加一门新语言

以加日文为例：

1. **复制** `Localization/en.json` 到 `Game/Localization/ja.json`
   （放在 Game 区可避免改动引擎目录；Game 区会自动叠加在引擎那份之上，
   因此**只写需要修改的键也可行**；需要完整翻译时，先复制整份再修改）
2. 逐条翻译，**只修改冒号右侧的值，不修改左侧的键**
3. `Game/conf_pure.lua` 里改成 `Global.SetVariable("Language", "ja")`
4. 运行游戏，看终端是否打印 `using language: ja (Game/Localization/ja.json)`
5. 之后改 JSON 按 **F2** 热重载即可

!!! note "缺键不再致命，但仍然会打警告"
    翻译时漏了某条、或者键名写错，运行时只是一行
    `[L10N WARNING] Missing localization key: ...` ，不会崩溃，但玩家会看到空白或乱码。
    由于 Game 区会自动回退到引擎那份，漏键只影响**新增的那部分**。

---

## 热重载

| 按键 | 行为 |
|---|---|
| **F2** | `Localize.reload()` + 重新执行两份 `conf_pure.lua` + 切到 `F2Room` 场景 |
| **F5** | 开发模式下额外清空模块缓存并重跑 Hack（含 `Localize.reload()` ） |

```lua
function localize.reload()
    if localize.currentLanguage then
        localize.setFile(localize.currentLanguage)
    else
        print("[L10N WARNING] No language loaded to reload.")
    end
end
```

!!! warning "改语言要改 conf 再 F2"
    `reload()` 只会重新读取**当前语言**的文件。切换到另一语言时，
    需先修改 `conf_pure.lua` 里的 `Language` ，再按 F2（F2 会重新执行 conf）。
    直接按 F2 不会切换语言。

!!! warning "运行期切换语言时需清除缓存"
    虚拟键盘会缓存查词结果，改完语言要调一次：

    ```lua
    VirtualKeyboard.ClearLabelCache()
    ```

---

## JSON 文件的结构

引擎的翻译表是**扁平**的：键就是一整串带点号的字符串。

```json
{
  "Battle.Spare": "饶恕",
  "Battle.HP.NotFull": "* 你回复了%sHP!",
  "Overworld.Menu.Buttons": ["物品", "状态", "电话"]
}
```

| 值的类型 | 允许 | 说明 |
|---|---|---|
| 字符串 | ✅ | 最常见，可含 `%s` 等占位符 |
| 数组 | ✅ | 多段文本（如 GameoverText）、或纯数值（如菜单坐标） |
| 数字 / 布尔 | ❌ | 会打印 `Invalid localization value` 并返回 `nil` |
| 嵌套对象 | ⚠️ | 存得进去但**取不出来**（查键是扁平的 `file["xxx"]` ） |

!!! warning "嵌套对象取不到"
    查词实现是 `local file = ...; current = file[key]` —— 一步到位，
    不会逐级下钻。 `"Items": {}` 这种嵌套结构目前写进去也读不出来
    （引擎里也没有任何地方在用它）。

    ```json
    "Items": { "Candy": { "name": "糖果" } }   // ✗ 取不到
    "Items.Candy.name": "糖果"                  // ✓ 这样才行
    ```

!!! note "BOM 可被 dkjson 解析，但不建议使用"
    dkjson 的 `scanwhite` 会跳过开头的 UTF-8 BOM，因此翻译文件带 BOM **通常也能读取**。
    但引擎里的 SafeJson **明确拒绝** BOM（见 **[高阶开发 → JSON 库](../050_intermediate/000_dkjson.md)** ）。
    保存时统一选择 `UTF-8`（不带 BOM）。

!!! warning "路径大小写敏感"
    引擎用 `love.filesystem.read("Localization/zh_CN.json")` 直读盘。
    Windows 上大小写无所谓，**打包到 Android / Linux 就整份读不到了**。
    文件名一律小写语言代码 + `.json` 。

!!! note "读的是 love.filesystem 的搜索路径"
    即先搜索存档目录，再搜索游戏目录。若使用 `love.filesystem.write`
    向存档目录写入过同名文件，该文件会**覆盖**游戏目录中的那份。

---

## 附：实现整份覆盖的方式

按键合并是默认行为。若需要让某一门语言**完全不受引擎文案影响**
（例如新版剧情修改了全部战斗文案、不继承任何旧值），删除引擎文件不会产生该效果，
需要在 Game 区把该语言所需的键**写全**，缺失的键仍会回退到引擎那份。

彻底断开的方式有两种：在 Game 区给一份不含该键的值，或者为这门语言使用引擎目录里
没有对应文件的语言名（此时只有 Game 这一层）。
