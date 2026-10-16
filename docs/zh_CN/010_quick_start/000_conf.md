---
title: 修改游戏信息
---

本页先完成游戏基础信息的配置，暂不涉及新增内容。

---

## 修改配置文件（conf.lua）

只需要看 `love.conf(t)` 这一行之前的内容即可：

```lua
-- Soul Engine Configuration File
_VER = "3.0.0-stable"

-- Set to true when building the game for release
_RELEASED = false

-- The game's information
_INFO = {
    TITLE = "Soul Engine - v3.0.0",
    VERSION = "0.0.0", -- THIS IS YOUR GAME'S VERSION, the "_VER" upon means the engine's version.
    AUTHOR = "end",
    CONTACT = "NaN",
    WEBSITE = "NaN",
}

-- This is your window size. Change these values to set your desired resolution.
LOGICAL_WIDTH, LOGICAL_HEIGHT = 640, 480
CANVAS_WIDTH, CANVAS_HEIGHT = 640, 480

-- How much the GAME SCREEN is scaled. It is ALWAYS kept dead-centre.
--     "integer" → whole-number scaling (pixel-perfect)
--     "auto"    → fill as much of the window / screen as possible (the default)
--     false/nil → 1:1, no scaling
SCREEN_SCALE = "auto"

-- Legacy switch, only used when SCREEN_SCALE is nil: true = "auto" while
-- fullscreen and 1:1 otherwise. Prefer SCREEN_SCALE.
FILL_SCREEN = true

-- Enable error handler to show custom error screen
-- If you don't know which error crashed the game. Then you need to set it to false.
USE_ERRHANDLER = true
```

!!! important "可修改变量"
    - `_RELEASED` 游戏是否为已发布版本，开启后通常会关闭所有 debug 功能，用于导出发布。
    - `_INFO` 的所有内容均可修改：
        - `TITLE` <u>Android端不生效。</u> 此为游戏窗口标题。
        - `VERSION` 游戏版本，可按需自行修改。
        - `AUTHOR` 游戏作者是谁，改为自己的名字。
        - `CONTACT` 作者/团队的联系方式。
        - `WEBSITE` 留空或者填写游戏发布页。
    - `LOGICAL_WIDTH` 窗口的宽度。
    - `LOGICAL_HEIGHT` 窗口的高度。
    - `CANVAS_WIDTH` 游戏内屏幕的宽度。
    - `CANVAS_HEIGHT` 游戏内屏幕的高度。
    - `SCREEN_SCALE` 游戏内屏幕画多大，画布**始终居中**： `"integer"` 只按整数倍放大（像素完美）、 `"auto"` 尽量铺满窗口（允许小数倍，默认值）、填一个数字则固定倍数、 `false` 保持 1:1 不缩放。运行中也可以用全局函数 `SetScreenScale(mode)` 切换、 `GetScreenScale()` 读取当前倍数。
    - `FILL_SCREEN` 是否填充整个屏幕。 <u>现在只算遗留开关</u> —— 只有当 `SCREEN_SCALE` 未设置（ `nil` ）时才生效，新项目直接修改 `SCREEN_SCALE` 即可。
    - `USE_ERRHANDLER` 是否启用自定义报错界面，默认为 `true` 。<u>该功能目前稳定性有限，绘制过程中出错可能导致闪退；如需查看完整报错，可暂时关闭。</u>

!!! warning "其他变量"
    这些变量也可以修改，但通常不建议修改

    - `_VER` 引擎版本标识，仅用于记录引擎版本，修改后不影响运行。

    <u>`_VERSION` 是 Lua 自带的全局变量，用于返回当前 Lua 的版本号，它**不在** `conf.lua` 中。</u>

---

## 修改初始化配置（conf_pure.lua）

在修改完 `conf.lua` 文件后，还需要对包括但不限于： `初始房间` 、 `主色调` 、 `所用语言` 等其他内容进行初始化设置。

初始化配置分成两份，**它们是叠加的，不是二选一**：

| 文件 | 作用 |
|---|---|
| 根目录 `conf_pure.lua` | 引擎默认值，定义所有用到的变量 |
| `Game/conf_pure.lua` | 游戏侧的覆盖，后执行，同名变量覆盖引擎默认值 |

配置方式为：只将需要修改的变量写入 `Game/conf_pure.lua` ，不改动引擎那份。未写入的变量自动沿用引擎默认值；若 Game 区的配置出错，引擎会整体回滚到默认值并打印 `[Conf] WARNING` ，不会中断运行。

下面是引擎默认的初始化内容（也就是根目录那份 `conf_pure.lua` ，节选）：

```lua
-- Initialize
Global.SetVariable("FirstRoom", "Battle.scene_battle_init")   -- 同名变量写了好几次，最后一次生效
Global.SetVariable("MainColor", {1, 1, 1})
Global.SetVariable("Language", "zh_CN")
Global.SetVariable("UseRealTime(dt)", false)
Global.SetVariable("ScreenShaders", {})
Global.SetVariable("FPS", 60)
Global.SetVariable("F2Room", "scene_logo")
Global.SetVariable("Volume", {
    Master = 1,
    Music  = 1,
    Sounds = 1
})

Global.SetVariable("ControllerSimulation", {
    virtualKeyboard = false,
    joystick        = false,
})
Global.SetVariable("ControllerDeadzone", 0.15)

-- Network things
Global.SetVariable("GamejoltID", nil)
Global.SetVariable("GamejoltPK", nil)
Global.SetVariable("DiscordAppID", "1342517648348680202")

Global.SetVariable("SE_MEMORY_SAFETY", true)
Global.SetVariable("OPT_COUNT_SPRITES", 2000)
Global.SetVariable("OPT_COUNT_TYPERS", 300)
Global.SetVariable("OPT_MEMORY_MAXSIZE", 0.8)
Global.SetVariable("OPT_LRU_SPRITES", {false, 180})
Guard = ImportFile("Engine.MemorySafety")
```

下面是对所有 **全局变量** 的解释

### 正常初始化

- `FirstRoom` 初始化房间，进入引擎后会直接进入此路径的房间。引擎默认值是 `Battle.scene_battle_init` ，想换成自己的场景就在 `Game/conf_pure.lua` 里重新写一次。 <u>场景放在 `Scripts/Scenes/` ；要覆盖引擎自带场景，就在 `Game/Scenes/` 里放同名文件，Game 区优先。</u>
- `MainColor` 游戏主色调，大部分攻击与文本等都会遵循此变量定义的颜色，如需制作 `Underfell` 同人，可使用粉红色。
- `Language` 游戏使用的语言， <u>引擎先查 `Game/Localization/` ，缺的键再回退 `Localization/`</u> ，若无特定语言请自行编写。
- `UseRealTime(dt)` 一般为 `false` 关闭状态，若开启则可以对所有移动操作都会使用 **现实时间** 。
- `ScreenShaders` 暂不涉及。
- `FPS` 默认 60，可自行修改。
- `F2Room` 按下 `F2` 按键后会返回的场景，默认在 `scene_logo` 。
- `Volume` 默认的音量，若后续想要设置全局音量，修改此变量。
- `ControllerSimulation` 可以模拟触屏操控模式。
- `ControllerDeadzone` 手柄摇杆的死区（ `0 ~ 1` ），越大越不容易漂移、但精度越低。默认 `0.15` ，灵敏可调 `0.10` 、宽容可调 `0.20` 。

### 网络功能

- `GamejoltID` 在 `gamejolt` 上的游戏页面 ID，一般为 6 位数到 7 位数。详情见 [网络开发 → GameJolt](../090_network/000_gamejolt.md) 。
- `GamejoltPK` 是 `private_key` 的缩写，也可以在游戏发布页面进行查看。它以明文形式进包，如需隐藏见 [开发辅助 → 密钥原生库](../070_develop/050_secrets.md) 。
- `DiscordAppID` 可连接 `Discord RPC` 在 Discord 上个人活动显示游戏进度等内容，详情见 [网络开发 → Discord RPC](../090_network/010_discord.md) 。

### 内存保护

- `SE_MEMORY_SAFETY` 默认为 `true` 开启，可进行内存保护，防止内存泄露。
- `OPT_COUNT_SPRITES` 最大可创建的贴图，在 `2000` 会出现警告，在二倍数时则会禁止创建操作。
- `OPT_COUNT_TYPERS` 最大允许300个打字机同时在场。
- `OPT_MEMORY_MAXSIZE` 若内存占用达到了总内存的 80% 进行警告。
- `OPT_LRU_SPRITES` 贴图缓存回收，默认为 `{false, 180}` 即**关闭**：第二项的 `180` 秒是判定时长，但第一项为 `false` 时不会触发回收，贴图进入缓存后会一直保留。如需启用，改为 `{true, 180}` ，超过 `180` 秒未使用的贴图会被回收，下次用到时再重新读盘创建。

!!! danger "关于是否监控内存"
    `SE_MEMORY_SAFETY` 是主开关，若游戏确实需要如此大量的图片和打字机，可以关闭本变量

    但由此导致的内存泄漏问题需自行承担。