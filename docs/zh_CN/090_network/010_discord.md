---
title: Discord RPC
---

`Scripts/Libraries/DiscordRPC.lua` 让玩家在 Discord 上的个人资料显示成"正在玩 XX"，也就是 **Rich Presence**：

```
SoulEngine
Fighting Sans
Route: Genocide
已玩 12 分钟
```

和小图标、大厅人数、加入按钮这些，都来自这一个库。

---

## 选用 `discord-rpc` 而非 Game SDK 的原因

文件头的注释写得很清楚，这里复述一遍：**不要把这个库"升级"成 Game SDK**。

!!! quote "`DiscordRPC.lua:12-18`"
    Why not the Discord Game SDK (discord_game_sdk.dll)?
    The Game SDK proved unstable / unusable through a direct LuaJIT FFI binding:
    `DiscordCreate` succeeds, but `get_activity_manager()` etc. return NULL no
    matter what (any flags/version/app-id), so calling any activity method
    dereferences a NULL pointer and hard-crashes the game.

也就是说：**Discord Game SDK 走 FFI 会直接让游戏崩溃**（拿到的是 NULL 管理器指针），
而老的 `discord-rpc` 库只有几个平铺的 C 函数（`Discord_Initialize` / `Discord_UpdatePresence`），
没有 vtable、没有 manager getter，在 LÖVE 中已验证可用。

!!! note "DiscordGameSDK 目录不是空的，只是没人用"
    这个目录**没被删掉**， `x64/` 与 `x86/` 子目录下保留着 7 个文件（ `discord_game_sdk.dll` / `.dll.lib` / `.so` / `.dylib` / `.bundle` ），都还在版本控制里。

    留着它们是当年尝试过这条路的痕迹，**引擎代码没有引用任何一个**。
    真正加载的是隔壁 `Resources/Libs/DiscordRPC/discord-rpc-x64.dll` 。
    **不要因为它们的存在就改用 Game SDK**：上面那段注释记录的崩溃是实测结果。

---

## 依赖与可用条件

| 条件 | 说明 |
|---|---|
| LuaJIT 的 `ffi` | LÖVE 的 LuaJIT 构建才有。纯 Lua 构建下整个库退化成空操作 |
| 原生库文件 | `Resources/Libs/DiscordRPC/discord-rpc-x64.dll` / `discord-rpc-x86.dll` |
| Discord 客户端在运行 | 没开 Discord 就只是显示不出来，不会报错 |

!!! warning "目前只有 Windows 的库"
    `Resources/Libs/DiscordRPC/` 下**只有两个 .dll** ，没有 Linux 的 `.so` 、也没有 macOS 的 `.dylib` 。
    源码里虽然写好了这两个平台的候选文件名，但文件没随引擎分发。
    需要支持其它平台时，从 [discord-rpc releases](https://github.com/discord/discord-rpc/releases) 下载并放进那个目录。

拿不到依赖时的行为：**不报错**。

```lua
local ok, err = Discord.init()
if (not ok) then print(err) end   -- 只是打印一句，游戏继续跑
```

无 `ffi` 时 `init` / `setActivity` / `on*` 全部被替换成同一个 `unavailable()` ，返回 `false, "DiscordRPC: LuaJIT FFI is unavailable..."` ；
`update` / `shutdown` / `isAvailable` 则变成安全的空函数。

---

## 引擎默认就接好了

`main.lua` 已经把整套流程走完了：

```lua
-- love.load()
Discord.application_id = Global.GetVariable("DiscordAppID")
Discord.init()

Discord.setActivity({
    details     = "Fighting Sans",
    state       = "Route: Genocide",
    large_image = "qq20250220-225345",
    large_text  = "It's a bad time.",
    start       = Discord.timestamp(),   -- 开始计时的时间戳
})

-- love.update(dt)
Discord.update(dt)

-- love.quit()
Discord.shutdown()
```

所以**常见的用法只有一步**：把 `Game/conf_pure.lua` 里的 ID 换成自己的应用 ID。

```lua
Global.SetVariable("DiscordAppID", "1234567890123456789")
```

!!! tip "写在 `Game/conf_pure.lua` 里，不要写进根目录那份"
    `conf_pure.lua` 有**两份并且是叠加的**：根目录那份是引擎默认值， `Game/conf_pure.lua` 那份盖在上面。
    改动应写在 **`Game/conf_pure.lua`** —— 改根目录那份会在引擎更新时被冲掉。
    两份的对照见 [配置文件](../010_quick_start/000_conf.md) 。

!!! danger "App ID 必须是字符串"
    19 位数字**超过 2^53**，Lua 的 number 是 double，写成数字字面量会丢精度，Discord 会拒绝连接。

    ```lua
    Global.SetVariable("DiscordAppID", "1342517648348680202")   -- 对
    Global.SetVariable("DiscordAppID", 1342517648348680202)     -- 错：精度丢失
    ```

    库内部会 `tostring(client_id)` ，但在写入配置时精度已经丢失。

---

## 方法

!!! example "生命周期"
    - `init(client_id, options)` 连接 Discord。省略 `client_id` 就用 `Discord.application_id` 。
        - `options.auto_register` 传 `true` 时尝试注册协议（一般不用）。
        - `options.steam_id` 关联 Steam（可选）。
    - `update(dt)` **必须每帧调用**，内部跑 `Discord_RunCallbacks()` 。引擎已在 `love.update(dt)` 里调了。
    - `shutdown()` 断开连接，`love.quit()` 里调（引擎已调）。
    - `isAvailable()` 是否已成功初始化。

!!! example "设置 Presence"
    - `setActivity(activity)` 设置/更新显示内容，参数是一张表（字段见下）。
    - `clearActivity()` 清空显示（玩家回到"什么都没玩"的状态）。
    - `timestamp(seconds)` 取当前 unix 时间戳（秒），可传入偏移量，用于 `start` / `finish`。

!!! example "回调"
    - `onReady(callback)` Discord 接受连接时触发，回调收到 `user` 表（ `userId` / `username` / `discriminator` / `avatar` ）或 `nil` 。
    - `onDisconnected(callback)` 断开时触发，回调收到 `(errorCode, message)` 。
    - `onError(callback)` 报错时触发，回调收到 `(errorCode, message)` 。**App ID 填错通常在这里体现**。
    - `onJoin(callback)` 别人通过邀请加入时触发，回调收到 `joinSecret` 字符串。
    - `onSpectate(callback)` 观战时触发，回调收到 `spectateSecret` 字符串。
    - `onJoinRequest(callback)` 有人申请加入时触发，回调收到 `user` 表。
    - `respond(user_id, reply)` 回应加入请求，`reply` 取 `Discord.JoinReply.No` / `.Yes` / `.Ignore` 。

!!! example "常量与状态"
    - `Discord.JoinReply` = `{ No = 0, Yes = 1, Ignore = 2 }` 。
    - `Discord.VERSION` 库版本，当前 `"2.1.0"` 。
    - `Discord.application_id` 当前应用的 App ID（字符串）。
    - `Discord.available` 是否已初始化。
    - `Discord.last_error` 最近一次失败的原因。

---

## activity 表可以填什么

两种命名风格都支持，下表以**下划线**一列为主（Game SDK 风格）：

| 字段 | 等价写法 | 含义 | 字节上限 |
|---|---|---|---|
| `details` | — | 第一行文字（"Fighting Sans"） | 128 |
| `state` | — | 第二行文字（"Route: Genocide"） | 128 |
| `start` | `startTimestamp` | 开始时间戳 → 显示"已玩 xx:xx" | — |
| `finish` / `end` | `endTimestamp` | 结束时间戳 → 显示"剩余 xx:xx" | — |
| `large_image` | `largeImageKey` | 大图资源 key | 32 |
| `large_text` | `largeImageText` | 鼠标悬停大图的文字 | 128 |
| `small_image` | `smallImageKey` | 小图（叠在大图右下角）资源 key | 32 |
| `small_text` | `smallImageText` | 悬停小图的文字 | 128 |
| `party_id` | `partyId` | 队伍/房间标识 | 128 |
| `party_size` | — | 传 `{当前人数, 上限}` 或 `{current=, max=}` | — |
| `partySize` / `partyMax` | — | 直接给两个数（没用 `party_size` 时生效） | — |
| `match_secret` | `matchSecret` | 匹配密钥 | 128 |
| `join_secret` | `joinSecret` | 邀请加入用的密钥 | 128 |
| `spectate_secret` | `spectateSecret` | 观战密钥 | 128 |
| `instance` | — | 是否可被加入，默认 `true` | — |

```lua
Discord.setActivity({
    details     = "探索废墟",
    state       = "LV " .. DATA.player.lv .. " · HP " .. DATA.player.hp,
    large_image = "ruins",
    large_text  = "Ruins",
    small_image = "frisk",
    small_text  = "Frisk",
    start       = Discord.timestamp(),      -- 从现在开始计时
    party_size  = {2, 4},                   -- 显示 (2 of 4)
})
```

!!! warning "字节上限不是字数上限"
    `state` / `details` 是 **128 字节**，UTF-8 下一个中文占 3 字节 —— **最多约 42 个汉字**，超了会被 Discord 直接丢弃整条 Presence。
    长文案请自己截断。

!!! warning "图片 key 要在后台上传过"
    `large_image` / `small_image` 填的是 **Discord Developer Portal → 应用 → Rich Presence → Art Assets** 里上传图片后得到的 key（文件名去掉扩展名），
    不是文件路径也不是 URL。没上传过的 key 会静默不显示图片。
    引擎默认的 `qq20250220-225345` 是 SoulEngine 自己应用下的资源，**更换 App ID 后该资源不再存在**，需要一并换掉。

!!! warning "`start` / `finish` 是秒级 unix 时间戳"
    `Discord.timestamp()` 返回 `os.time()` 。传毫秒会被当成公元 5 万年，计时显示会乱。

---

## 用法示例

**① 随场景切换 Presence**

```lua
function SceneBattle:load()
    Discord.setActivity({
        details = "与 " .. Battle.enemies[1].name .. " 战斗",
        state   = "LV " .. DATA.player.lv,
        start   = Discord.timestamp(),
    })
end
```

**② 用 `onReady` 确认 App ID 有没有填对**

```lua
Discord.onReady(function(user)
    if (user) then
        print("[Discord] 已连接:", user.username)
    else
        print("[Discord] 已连接（未拿到用户信息）")
    end
end)

Discord.onError(function(code, msg)
    print("[Discord] 错误", code, msg)   -- 多数情况是 App ID 不正确
end)
```

**③ 邀请好友加入**

```lua
-- 房主
Discord.setActivity({ ..., party_id = room.id, party_size = {n, 4}, join_secret = room.secret })

-- 房主这边收到申请
Discord.onJoinRequest(function(user)
    -- 此处决定是否同意加入
    Discord.respond(user.userId, Discord.JoinReply.Yes)
end)
```

---

## 注意事项汇总

!!! warning "`Discord.update(dt)` 必须每帧调用"
    它内部是 `Discord_RunCallbacks()` 。漏掉的话：Presence **不会刷新**、所有回调**不会触发**。
    引擎已经在 `love.update(dt)` 里调了，除非另行建立了独立的 `love.update` 分支，否则不要重复调用或删除。

!!! note "别动那句 `jit.off(discord.update)`"
    `Discord_RunCallbacks()` 会从 C 通过 FFI 回调**重新进入 Lua**。在 JIT 编译过的代码里这么做，
    LuaJIT 会抛 `unprotected error in call to Lua API` —— 而且是在连上 Discord 约 2 秒、ready 事件触发的那一刻。
    库里专门对 `update` 关掉了 JIT，让它永远走解释器：**删掉这行会在运行到回调时崩溃。**

??? quote "那段注释与代码"
    ```lua
    -- CRITICAL for LuaJIT: `discord.update` calls Discord_RunCallbacks, which
    -- re-enters Lua through the FFI callback trampolines above. ... Disable JIT
    -- for this function so it always runs in the interpreter. NOTE: `jit` is a
    -- LuaJIT builtin that must be loaded explicitly; the previous
    -- `local jit = nil` shadowed the global and silently broke this.
    local ok_jit, jit = pcall(require, "jit")
    if (ok_jit and jit and jit.off) then
        jit.off(discord.update)
    end
    ```

!!! warning "Presence 有更新频率限制"
    Discord 服务端会限流（大致 5 次 / 20 秒），超了更新会被静默丢弃并可能触发 `onError` 。
    **不要每帧 `setActivity`** ，只在状态真的变了的时候调（切场景、升级、进战斗）。

!!! note "连上要等一两秒"
    `init()` 返回 `true` 只代表本地调用成功，不代表 Discord 已经接受。
    要确认就挂 `onReady` ；Presence 一般 1~2 秒后才出现在客户端上。

!!! note "回调里抛异常不会中断游戏"
    用户在回调里写错代码时，库会 `pcall` 住并打印 `[DiscordRPC] callback error: ...` 。
    因为这些回调是从 C 侧进来的，普通 `pcall` 拦不住，所以库自己在每个代理里包了一层。

!!! note "`instance` 默认是开着的"
    `p.instance = (t.instance ~= false) and 1 or 0` —— 只有**显式写 `instance = false`** 才关。
    没配 `join_secret` 的话它开着也没用，不会凭空出现邀请按钮。
