---
title: 网络开发
---

网络开发专题讲引擎自带的三个联网/联机相关的库。它们彼此独立，按需取用：

| 角色 | 路径 | 用途 |
|---|---|---|
| GameJolt API | `Scripts/Libraries/GamejoltAPI.lua` | 接 GameJolt 平台：登录、成就（奖杯）、分数榜、云存档 |
| Discord RPC | `Scripts/Libraries/DiscordRPC.lua` | 在 Discord 个人资料上显示「正在玩什么」（Rich Presence） |
| sock | `Scripts/Libraries/Network/sock.lua` | 基于 ENet 的多人联机（C/S 结构、事件收发） |

全局别名在 `main.lua` 顶部建好了两个，直接用即可：

```lua
Gamejolt = ImportFile("GamejoltAPI")
Discord  = ImportFile("DiscordRPC")
```

`sock` **不会**自动加载（联机不是每个游戏都要），需要时自己引：

```lua
local sock = ImportFile("Network.sock")
```

---

## 引擎内置的调用

三个库默认状态下都是"安静的"，不会因为没配置就崩游戏。

| 库 | 引擎内置的行为 | 需要补充的部分 |
|---|---|---|
| Discord | `love.load()` 里读 `Global.GetVariable("DiscordAppID")` → `Discord.init()` → `setActivity()` ；<br>`love.update(dt)` 里每帧 `Discord.update(dt)` ；<br>`love.quit()` 里 `Discord.shutdown()` | 把 `Game/conf_pure.lua` 里的 `DiscordAppID` 换成自己的应用 ID |
| Gamejolt | `love.update(dt)` 里每帧 `Gamejolt.update(dt)` （只驱动会话心跳） | **必须自己调 `Gamejolt.init()` 和 `authUser()`** ，引擎不代劳 |
| sock | 无 | 全部自己写 |

!!! warning "GameJolt 不会自动初始化"
    引擎只调用了 `Gamejolt.update(dt)` ，**没有任何地方调用 `Gamejolt.init()`** 。
    在 `init()` 之前调用其它方法会因为 `gamejolt.base_url` 还是 `nil` 直接报错（拼接 nil）。
    见 [GameJolt](./000_gamejolt.md) 。

---

## 三者的依赖与平台支持

| 库 | 依赖 | 拿不到的后果 |
|---|---|---|
| Gamejolt | 原生 `https` 模块（ `Resources/Libs/https.dll` ，**仅 Windows** ） | 所有请求返回 `false, "GameJolt API unavailable on ..."` ，游戏照常跑 |
| Discord | LuaJIT 的 `ffi` + `Resources/Libs/DiscordRPC/` 下的原生库（**仅 Windows** ） | `init()` 返回 `false, 原因` ，其余方法退化成空操作 |
| sock | `enet` （**LÖVE 自带**，无需额外 dll）+ 可选的 `bitser` | `require "enet"` 失败会直接报错（LÖVE 标准构建都带） |

!!! note "Android / 移动端"
    `https.dll` 与 `discord-rpc-*.dll` 都是 **Windows 专用**动态库，打进 Android 包也加载不了。
    这两个库在非 Windows 平台会自动降级（`isAvailable()` 返回 `false` ），**不要**把关键逻辑挂在它们身上。

---

## 本专题页面

| 页面 | 内容 |
|---|---|
| [GameJolt](./000_gamejolt.md) | 初始化、登录、成就、会话心跳、云存档、分数榜，以及 URL 未编码的处理 |
| [Discord RPC](./010_discord.md) | 改 Presence、回调事件、图片资源、字节数上限、`jit.off` 的原因 |
| [sock 联机](./020_sock.md) | 服务端/客户端、事件与 schema、发送模式与通道、完整最小例子 |

---

## 最小例子

**Discord（只改配置）**

```lua
-- Game/conf_pure.lua
Global.SetVariable("DiscordAppID", "1234567890123456789")  -- 注意是字符串
```

进游戏约 2 秒后，Discord 个人资料上就会出现活动状态。

**GameJolt —— 要自己初始化**

```lua
-- 某个场景的 load 里
Gamejolt.init(Global.GetVariable("GamejoltID"), Global.GetVariable("GamejoltPK"))
local ok, err = Gamejolt.authUser("my_name", "my_token")
if (ok) then
    Gamejolt.sessionUpdate(30, "active")   -- 之后引擎每帧调用 ping
end
```

**sock（两端都要跑）**

```lua
-- 服务端
server = sock.newServer("*", 22122)
server:on("chat", function(data, client) server:sendToAll("chat", data) end)
-- love.update 里：server:update()

-- 客户端
client = sock.newClient("127.0.0.1", 22122)
client:connect()
client:on("chat", function(data) print(data.text) end)
-- love.update 里：client:update()
```
