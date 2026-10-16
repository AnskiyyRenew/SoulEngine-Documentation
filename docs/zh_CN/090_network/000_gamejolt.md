---
title: GameJolt API
---

`Scripts/Libraries/GamejoltAPI.lua` 封装了 [GameJolt Game API v1.2](https://gamejolt.com/game-api/doc) 的常用接口：用户、奖杯、会话、数据存储、分数榜。

全部请求都是 **HTTPS + MD5 签名**，走 `Resources/Libs/https.dll` 这个原生模块。

---

## 准备工作

### 1. 拿到 App ID 与 Private Key

在 GameJolt 上建好游戏后，进入游戏的 **Manage → Game API** 页面能看到两个东西：

| 字段 | 说明 | 填到哪 |
|---|---|---|
| `game_id` | 游戏 ID，一般 6~7 位数 | `Game/conf_pure.lua` 的 `GamejoltID` |
| `private_key` | 私钥，**不要**随游戏分发给玩家以外的人看 | `Game/conf_pure.lua` 的 `GamejoltPK` |

```lua
-- Game/conf_pure.lua
Global.SetVariable("GamejoltID", 123456)
Global.SetVariable("GamejoltPK", "abcdef0123456789abcdef0123456789")
```

!!! tip "两份 `conf_pure.lua` 是叠加的"
    根目录那份是引擎默认值， `Game/conf_pure.lua` 那份盖在上面。
    配置写在 **`Game/conf_pure.lua`** ，见 [配置文件](../010_quick_start/000_conf.md) 。

!!! danger "私钥会被打进游戏包"
    GameJolt 的 `private_key` 不是"绝对保密"的，它被设计成随客户端分发（每个玩家的包里都有一份）。
    但**不要**把它当成权限控制——任何人拆包都能拿到。真正的写权限靠 `username + user_token` 校验。<br>
    想让解包的人翻不到明文，可以把密钥编译进原生库再经 FFI 取回，见 [开发辅助 → 密钥原生库](../070_develop/050_secrets.md) 。
    那是**混淆不是加密**，而且引擎目前不会自动接线，得自己调 `Secrets.gamejoltPK()` 。

### 2. 初始化（由调用方执行）

```lua
Gamejolt.init(Global.GetVariable("GamejoltID"), Global.GetVariable("GamejoltPK"))
```

`init` 只做三件事：把 `app_id` 转成数字、存 `private_key` 、拼出 `base_url` 。

??? quote "`init` 源码"
    ```lua
    function gamejolt.init(app_id, private_key)
        gamejolt.app_id = tonumber(app_id)
        gamejolt.private_key = private_key
        gamejolt.base_url = "https://api.gamejolt.com/api/game/v1_2"
        return (gamejolt.app_id ~= nil and gamejolt.private_key ~= nil)
    end
    ```

!!! warning "必须先 init"
    `base_url` 只在 `init()` 里赋值。没初始化就调 `fetchUser()` 等方法，
    会在拼 URL 时因为拼接 `nil` 直接抛错，而且是**运行到那一行才报**，不是加载时。

### 3. 确认能不能用

```lua
local ok, err = Gamejolt.isAvailable()
if (not ok) then print(err) end
```

拿不到 `https` 模块时返回 `false` 和一句说明（含 `SE.system.getOS()` 的当前平台名）。

---

## 签名是怎么算的

每个请求都要带一个 `signature` 参数，值为：

```lua
md5.sumhexa(base_url .. request_path .. private_key)
```

其中 `request_path` 是**不含 signature 本身的完整路径+参数**。库里的每个方法都会自行拼一遍，调用方不需要处理。

??? quote "`generateSignature` 与 `apiRequest`"
    ```lua
    local function generateSignature(request_path)
        local input = gamejolt.base_url .. request_path .. gamejolt.private_key
        return md5.sumhexa(input)
    end

    local function apiRequest(url)
        if (not https or type(https.request) ~= "function") then
            local platform = (SE and SE.system and SE.system.getOS and SE.system.getOS()) or "Unknown"
            local reason = https_error or "missing native https module"
            return false, "GameJolt API unavailable on "..tostring(platform)..": "..reason
        end

        -- lua-https (https.dll) API: returns code, body, headers
        local code, response, headers = https.request(url)

        if (code ~= 200) then
            return false, "HTTP error: "..tostring(code)
        end

        local data, pos, err = json.decode(response)
        if (not data) then
            return false, "JSON decode error: "..tostring(err).."\nResponse: "..tostring(response)
        end

        if (data.response and data.response.success == "false") then
            return false, data.response.message or "API error"
        end

        return data.response
    end
    ```

### 返回值的统一约定

| 情况 | 返回 |
|---|---|
| 成功 | `data.response` （一张表），**没有第二个返回值** |
| 失败 | `false, 错误信息字符串` |

所以调用时要么先判 `false` ，要么像某些方法那样自己包一层：

```lua
local res, err = Gamejolt.fetchUser(nil, "somebody")
if (res == false) then
    print("失败了:", err)
else
    print(res.users[1].username)
end
```

!!! bug "成功时第二返回值也是 nil，别把它当错误码"
    比如 `fetchUser` 成功时只返回 `data.response` ，第二个返回值是 `nil` 。
    写成 `local res, err = ...; if err then ...` 是安全的，但 `if (not res) then` 在
    某些接口返回空表时也会误判，统一使用 `res == false` 判断。

---

## 方法一览

### 通用

!!! example "通用"
    - `init(app_id, private_key)` 设置 `app_id` / `private_key` / `base_url` ，返回两者是否都非空。
    - `isAvailable()` 原生 `https` 模块是否就绪。失败时第二返回值是带平台名的说明。
    - `isLoggedIn()` `user_token` 与 `username` 是否都已设置（**不校验有效性**，见下方警告）。

### 用户

!!! example "用户"
    - `fetchUser(user_id, username)` 查用户信息，两个参数给一个即可，**不需要登录**。
    - `authUser(username, user_token)` 验证用户名 + token。成功后 `gamejolt.username` / `gamejolt.user_token` 留着给后续接口用。

!!! bug "`authUser` 失败后 `isLoggedIn()` 仍然是 true"
    源码是**先把 username/token 存下来、再发请求**：

    ```lua
    function gamejolt.authUser(username, user_token)
        gamejolt.username = username       -- 先存
        gamejolt.user_token = user_token
        ...
        local success, err = apiRequest(url)
        return success ~= false, err
    end
    ```

    网络失败 / token 错误时它返回 `false, err` ，但两个字段**已经写进去了**，
    于是 `isLoggedIn()` 依旧返回 `true` ，后面所有需要登录的接口都会带着错 token 去请求。

    需要在调用方补一层清理：

    ```lua
    local ok, err = Gamejolt.authUser(name, token)
    if (not ok) then
        Gamejolt.username = nil
        Gamejolt.user_token = nil
    end
    ```

### 奖杯（成就）

!!! example "奖杯"
    - `fetchAchievements(achieved_only)` 拉奖杯列表，`achieved_only` 传 `true` 只返回已解锁的，**需要登录**。
    - `unlockAchievement(trophy_id)` 解锁指定奖杯，`trophy_id` 是 GameJolt 后台建奖杯时分配的数字 ID，**需要登录**。

```lua
local res = Gamejolt.fetchAchievements(true)
if (res ~= false and res.achievements) then
    for _, a in ipairs(res.achievements) do
        print(a.id, a.title, a.achieved)
    end
end

Gamejolt.unlockAchievement(1047)
```

!!! note "`trophy_id` 不是数组下标"
    建奖杯时后台显示的 ID 是全局数字（比如 1047），不是"第几个"。填错会返回 API 错误。

### 会话（在线时长/状态）

GameJolt 用它统计"谁在玩、玩了多久"。

!!! example "会话"
    - `sessionOpen()` 开一次会话。手动模式下只需调用这一句。
    - `sessionUpdate(interval, status)` 开一次会话并开启自动心跳。`interval` 单位**秒**（默认 30，最小 1），`status` 默认 `"active"` 。
    - `sessionPing(status)` 手动 ping 一次，可切换状态（ `"active"` / `"idle"` ）。
    - `sessionClose()` 关会话，同时停掉自动心跳。
    - `update(dt)` 自动心跳的计时器。引擎已在 `love.update(dt)` 里每帧调用，**不需要重复调用**（重复调用会使 ping 频率加倍）。

```lua
Gamejolt.sessionUpdate(30, "active")
-- 之后引擎每帧 Gamejolt.update(dt) 会累计 dt ，满 30 秒自动 ping 一次
```

自动状态存在 `Gamejolt._session_auto` 里，可以读：

| 字段 | 说明 |
|---|---|
| `enabled` | 自动心跳是否开着 |
| `interval` | 间隔（秒） |
| `status` | 当前上报的状态 |
| `elapsed` | 距上次 ping 已累计的秒数 |
| `last_error` | 上一次 ping 的错误信息（成功时置 nil） |

!!! warning "`interval` 是秒不是毫秒"
    `state.elapsed = state.elapsed + dt` ，`dt` 是秒。写成 `30000` 会得到 30000 秒一次心跳。

### 数据存储（云存档 / 全局数据）

一套简单的 key-value 存储。

!!! example "数据存储"
    - `dataStore(key, data, user_data)` 写入。
        - `user_data` 为 `true` 时存到**该用户**名下（需登录），否则存到**游戏全局**。
    - `dataFetch(key, user_data)` 读一个键。
    - `dataFetchAll(user_data)` 读全部键。
    - `dataDelete(key, user_data)` 删一个键。
    - `dataGetKeys(user_data)` 只拉键名列表。

```lua
-- 玩家自己的存档（需要 authUser 过）
Gamejolt.dataStore("slot1", json.encode(mySave), true)
local res = Gamejolt.dataFetch("slot1", true)
if (res ~= false and res.data) then mySave = json.decode(res.data) end

-- 游戏全局的公告（不需要登录）
Gamejolt.dataStore("motd", "今天服务器维护")
```

!!! danger "`key` 和 `data` 没有做任何 URL 编码"
    源码是裸字符串拼接：

    ```lua
    local url = gamejolt.base_url .. "/data-store/set/?game_id=" .. gamejolt.app_id ..
                "&key=" .. key .. "&data=" .. data .. ...
    ```

    只要 key 或 data 里出现 `&` 、 `=` 、 `#` 、空格、中文，URL 就会被截断/解析错，
    而且**签名是按拼好的字符串算的**，服务端对不上会直接返回签名错误。

    可行的处理方式：

    - key 只用 `[A-Za-z0-9_-]`
    - data 先 `json.encode` 再做一次**自行实现**的百分号编码（或 base64）再传
    - 不要直接把玩家输入的文本拼进去

### 分数榜

!!! example "分数榜"
    - `fetchScoresLocal(table_id)` 拉榜单前 N 名，**不需要登录**。`table_id` 省略则取游戏的主榜。
    - `fetchScoresGlobal(table_id)` 带 `username + user_token` 请求，返回里会多出玩家自己的排名/前后名次，**需要登录**。
    - `submitScore(score, table_id, sort, extra_data)` 提交分数。`sort` 是展示用的数值，`extra_data` 是额外文本（比如用时、等级）。

```lua
Gamejolt.submitScore(12345, 535, 12345, "LV19|Genocide")
local res = Gamejolt.fetchScoresLocal(535)
if (res ~= false and res.scores) then
    for _, s in ipairs(res.scores) do print(s.score, s.user) end
end
```

!!! bug "`submitScore` 不带用户名/token，提交的是游客分数"
    拼 URL 时**没有**附加 `username` / `user_token` （对比 `fetchScoresGlobal` 就带了），
    所以即使已调用 `authUser` ，分数也是以 **guest** 身份提交的，不会挂到玩家账号上。

    想提交实名分数，自己照着库的写法补一个带凭据的版本，或改这个库。

---

## 一个完整的登录流程

```lua
-- 场景的 load / 某个一次性初始化点
Gamejolt.init(Global.GetVariable("GamejoltID"), Global.GetVariable("GamejoltPK"))

local function login(name, token)
    local ok, err = Gamejolt.authUser(name, token)
    if (not ok) then
        Gamejolt.username, Gamejolt.user_token = nil, nil
        return false, err
    end

    Gamejolt.sessionUpdate(30, "active")      -- 之后自动心跳

    local res = Gamejolt.fetchAchievements(true)
    if (res ~= false and res.achievements) then
        -- 同步本地成就状态
    end
    return true
end
```

---

## 注意事项汇总

!!! warning "全部请求都是**同步阻塞**的"
    `https.request(url)` 会一直等到服务器响应才返回。在国内连 GameJolt 通常是几百毫秒到几秒，
    **这一帧整个游戏是卡住的**。

    - 绝对不要在 `love.update` 里每帧发请求
    - 一次性的请求可以接受（比如提交分数时卡一下）
    - 想要不卡就得自己套协程／线程，库没有提供异步版本

!!! warning "失败不会抛异常，只返回 `false`"
    没判返回值的话，失败会被静默忽略。所有调用都建议写成 `if (res == false) then ...` 。

!!! warning "GameJolt 返回的 `success` 是字符串"
    库里判的是 `data.response.success == "false"` —— 注意是字符串 `"false"` 不是布尔。
    这是照 GameJolt API 的实际返回写的，别去"修正"它。

!!! note "非 Windows 平台直接不可用"
    `https.dll` 是 Windows 动态库。`isAvailable()` 会返回 `false` ，所有请求返回统一的不可用提示。
    打包 Android 时，把 GameJolt 相关逻辑包在 `if Gamejolt.isAvailable() then` 内。

!!! note "`app_id` 被转成数字"
    `gamejolt.app_id = tonumber(app_id)` 。传字符串 `"123456"` 也能用，但不要传带空格或字母的值。
