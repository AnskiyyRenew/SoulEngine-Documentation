---
title: Game 区与资源覆盖
---

`Game/` 是**每个游戏自己的内容根目录**，也就是本文档中反复出现的 `Game 区` 。<br>
引擎自带的资源全部放在各自的原始目录里；游戏自身的内容一律放进 Game 区。

这样区分的目的：**更新引擎时保留游戏内容。**

---

## 两条路径的分工

| | 引擎目录 | Game 区 |
|---|---|---|
| 作用 | 引擎自带的默认内容 | 当前游戏的内容 |
| 更新引擎时 | 会被整体替换 | **原样保留** |
| 优先级 | 低（兜底） | 高（优先） |

因此开发时遵循以下规则：**不直接修改引擎目录下的内容。**

需要改动引擎自带的行为或资源时，将其复制一份到 Game 区，再在 Game 区那份上修改。引擎目录的内容保持原样，升级引擎时直接覆盖，改动不会丢失。

---

## 总规则：Game 优先，主目录兜底

除了少数只认 Game 区的内容，其余资源在查找时都遵循同一套顺序：

1. 先查找 Game 区是否存在同名文件。
2. 有 → 直接用 Game 区这一份（**覆盖生效**）。
3. 没有 → 回退到引擎目录那一份。

这套顺序对**路径**生效，与文件类型无关：场景、贴图、音频、翻译、回合脚本、地图、攻击模式、灵魂、物品表都走这个逻辑。

---

## 哪些内容支持覆盖

| 内容 | Game 区路径 | 引擎兜底路径 |
|---|---|---|
| 场景 | `Game/Scenes/<name>.lua` | `Scripts/Scenes/<name>.lua` |
| 贴图 | `Game/Resources/Sprites/` | `Resources/Sprites/` |
| 音效 | `Game/Resources/Sounds/` | `Resources/Sounds/` |
| 音乐 | `Game/Resources/Music/` | `Resources/Music/` |
| 字体 | `Game/Resources/Fonts/` | `Resources/Fonts/` |
| 翻译（按键叠加） | `Game/Localization/` | `Localization/` |
| 回合脚本 | `Game/Waves/<name>.lua` | `Scripts/Waves/<name>.lua` |
| 攻击模式 | `Game/Attacks/<name>.lua` | `Scripts/Libraries/Battle/PlayerAttacks/<name>.lua` |
| 灵魂 | `Game/Souls/<name>.lua` | `Scripts/Libraries/Battle/Player/Souls/<name>.lua` |
| 地图 | `Game/` 下同相对路径 | `Maps/` |
| 物品表 | `Game/Logics/items.lua` | `Scripts/Logics/items.lua` |

!!! note "两个需要注意的点"
    - **字体**写文件名即可： `Fonts.New("determination_mono.ttf", 27)` 会先查 `Game/Resources/Fonts/` 。引擎里所有字体加载都已走这个入口，无需修改调用代码，放入同名文件即可替换。
    - **物品表的引擎兜底目录 `Scripts/Logics/` 目前并不存在**（引擎自带没有这一份），所以物品表现在事实上只有 `Game/Logics/items.lua` 一个来源。同目录的 `Game/Logics/init.lua` 更是硬性 require，连回退都没有。

---

## 哪些内容只认 Game 区

下面这些内容**没有**可用的引擎侧同名目录，属于游戏独有数据，直接写在 Game 区即可，不需要考虑覆盖问题：

| 内容 | 路径 |
|---|---|
| 遭遇战 | `Game/Encounter/` |
| 怪物动画 | `Game/Animations/` |
| 游戏逻辑数据 | `Game/Logics/` |
| Hack 脚本 | `Game/Hacks/` |
| 整模块替换映射 | `Game/Overrides.lua` |
| 配置覆盖 | `Game/conf_pure.lua` |

因此这几项在文档中只出现一个路径：它们属于游戏自身，引擎不提供默认版本。

其中 **`Game/conf_pure.lua` 是「叠加」而不是「兜底」**，与其他几项不同：引擎先执行根目录的 `conf_pure.lua` 定义全部默认值，再执行 Game 区这份覆盖同名变量。因此只需写入要修改的行。若该文件执行中途报错，引擎会整体回滚到默认值，并打印 `[Conf] WARNING: ... exists but failed to load; using the engine defaults ...` ，游戏正常启动。

!!! tip "游戏逻辑里装的是什么"
    世界规则（等级曲线、满级怎么扩、剧情开关、箱子内容）单独有一页： **[游戏逻辑与世界规则](./120_game_logics.md)** 。

!!! warning "`Game/Logics` 与 `Game/Hacks` 的区别"
    这两个目录名称相近，但职责不同： `Game/Logics/` 存放**数据**（等级表、箱子内容）， `Game/Hacks/` 存放**代码**（改写引擎行为）。下一节说明后者。

---

## 用 Hack 改写引擎内部

上述方法的前提是内容可放在其他目录。部分内容不属于任何一类，例如战斗 UI 的排版、战斗流程的状态机、贴图库内部的行为，位于 `Scripts/Libraries/` 中，此前只能修改引擎目录。

Game 区给了两个受支持的入口：

### 1. `Game/Overrides.lua` —— 声明式整模块替换

一个 `["引擎模块名"] = "Game 模块名"` 的映射表，适用于整份重写某个模块：

```lua
-- Game/Overrides.lua
return {
    ["Scripts.Libraries.Battle.UI"] = "Game.UI.Battle",
}
```

### 2. `Game/Hacks/*.lua` —— 命令式打补丁

启动时按**文件名数字前缀**顺序各执行一次，适用于只改动其中一两个函数的情况：

```lua
-- Game/Hacks/010_my_battle.lua
return {
    name = "My battle tweak",
    apply = function(Hack)
        Hack.After("Scripts.Libraries.Battle", function(battle)
            -- 引擎加载完 Battle 之后跑一次
        end)
    end
}
```

可用的原语有 `Hack.Replace` （整模块替换）、 `Hack.After` （加载后回调）、 `Hack.Wrap` （包住某个函数）、 `Hack.Set` 、以及更偏内部的 `Hack.Patch` 。完整说明与注意事项见 `Game/Hacks/README.md` 。

!!! warning "文件名规则"
    `Game/Hacks/` 里**每一个 `.lua` 都会被当成一个入口执行**，只有以下划线 `_` 开头的文件会被跳过。<br>
    若需将整个模块放在该目录中作为替换素材，文件名必须以下划线开头（例如 `_my_ui.lua` ），否则会被当作入口执行，并提示该文件既未返回函数也未返回 `{apply = ...}` 。

!!! tip "改完按 F5"
    两个入口都在热重载时先撤销、再重新应用，因此修改配置文件后按 **F5** 即生效，无需重启。

---

## 覆盖坏了会发生什么

**覆盖失败时一定会输出提示，不会静默处理。**

引擎在查找资源时会把「文件不存在」和「文件存在但加载时报错」严格区分开，于是有三种结果：

!!! example "三种结果"

    **1. 正常覆盖** —— Game 区有，且能正常加载。无输出，直接用 Game 区那份。

    **2. 覆盖没找到，回退成功** —— Game 区没有，用的是引擎目录那份：

    ```
    [Battle] WARNING: 'bones.wave1' not found in Game.Waves. (fell back to Scripts.Waves.bones.wave1).
    ```

    这种情况**属于正常回退**，确认未编写该覆盖即可。

    **3. 覆盖存在但坏了** —— Game 区有这份文件，但它一加载就报错：

    ```
    [Battle] WARNING: 'Game.Waves.bones.wave1' exists but failed to load; using Scripts.Waves.bones.wave1 instead.
    [Battle]   <真正的错误信息>
    ```

    **出现 `exists but failed to load` 表示覆盖未生效**，同时会打印真正的错误信息，按错误信息修正即可。

不同子系统的警告前缀不同，可依据 `exists but failed to load` 判断：

| 前缀 | 出自 |
|---|---|
| `[Battle]` | 遭遇、波次、攻击模式、灵魂 |
| `[Scenes]` | 场景 |
| `[Overworld]` | 地图、物品表 |
| `[Conf]` | `Game/conf_pure.lua` |
| `[Hack]` | `Game/Hacks/` 与 `Game/Overrides.lua` |

!!! warning "区分文件不存在与加载失败"
    早期版本的实现是用 `pcall(require, ...)` 的成败来判断模块是否存在。<br>
    问题在于 `pcall` 返回 `false` 有两种不同的原因：**文件不存在**，以及**文件存在但顶层代码报错**。<br>
    把后者当作文件不存在会导致：回退链条被静默截断（覆盖未生效，实际执行的是旧版本），以及真正的错误被吞掉不显示。<br>
    因此现在的做法是**先检查文件是否存在，再决定是否 require** ，出现问题时一定会输出提示。

---

## 一些注意事项

- **路径一律用正斜杠 `/`** ，从项目根目录开始写。
- **文件名必须完全一致**，覆盖是**同名替换**而不是**就近合并**。Game 区放了 `px.png` ，引擎目录的 `px.png` 就整体不再被使用。
- **地图的图片引用是相对路径**。引擎的地图 `.lua` 里用 `../images/...` 引用图块，所以覆盖地图时，Game 区那份也要自带对应的 `../images/` 目录树，否则会出现图块丢失。
- **覆盖未生效时，先查看终端输出。** 上述第三种情况一定会打印警告。
