---
title: 本地化
---

本地化（L10n）把**所有面向玩家的文字**从代码里抽出来，放进 JSON 文件。
代码中只写键名，运行时由 Lua 库查表、替换占位符，得到当前语言的实际文本。

三部分组成：

| 角色 | 路径 | 说明 |
|---|---|---|
| 引擎默认翻译 | `Localization/` | 引擎自带文案（`en.json` 、 `zh_CN.json` ），兜底 |
| 游戏覆盖翻译 | `Game/Localization/` | **游戏自身的文案放在此处**，同名文件**叠加在引擎之上** |
| 查找替换库 | `Scripts/Libraries/Localize.lua` | 负责读文件、查键、 `string.format` 替换 |

!!! note "「Game 优先」是引擎的全局约定"
    不只是翻译，贴图、音效、波次、地图等都遵循"先 `Game/` 、再引擎目录"的顺序。
    完整对照见 **[基础开发 → Game 区与资源覆盖](../020_basic/110_game_area.md)** 。

---

## 一句话流程

```
Game/conf_pure.lua 里 Global.SetVariable("Language", "zh_CN")
        ↓
main.lua 启动时 Localize.setFile(Global.GetVariable("Language"))
        ↓
Localize 读入 Game/Localization/zh_CN.json 与 Localization/zh_CN.json 两层，
        Game 层的键覆盖引擎层，Game 没写的键自动回退
        ↓
dkjson 解码后合并成一张扁平的「键 → 文本」表
        ↓
代码里 Localize.localizeText("Battle.Spare", {...})
        ↓
查表 + string.format 替换 %s → 返回最终字符串（或数组）
```

---

## 本专题页面

| 页面 | 内容 |
|---|---|
| [目录与语言文件](./000_files.md) | 两个目录的优先级、怎么选语言、怎么加一门新语言、热重载 |
| [查词与替换](./010_usage.md) | `localizeText` 的全部用法、动态键、缺失键的后果、打字机标签 |

---

## 最小例子

往 `Game/Localization/zh_CN.json` 加一个键：

```json
{
  "MyGame.Greeting": "* 你好，%s！"
}
```

代码里取：

```lua
local text = Localize.localizeText("MyGame.Greeting", {Player.name})
-- -> "* 你好，Frisk！"
```

改完按 **F2** 即可重载翻译，不用重启游戏。
