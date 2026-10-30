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

`init` 做四件事：把 `app_id` 转成数字、存 `private_key` 、拼出 `base_url` 、清掉上一次遗留的登录状态。

??? quote "`init` 源码"
    ```lua
    function gamejolt.init(app_id, private_key)
        gamejolt.app_id = tonumber(app_id)
        gamejolt.private_key = private_key
        gamejolt.base_url = "https://api.gamejolt.com/api/game/v1_2"
        -- Pointing at another game must not keep the previous player logged in.
        gamejolt.logout()
        return (gamejolt.app_id ~= nil and gamejolt.private_key ~= nil)
    end
    ```

!!! note "没 init 会返回 false，不会拼 nil 抛错"
    `base_url` 只在 `init()` 里赋值。没初始化就调用任意接口时，
    库会先做 `requireConfig()` 检查，返回 `false, "GameJolt: call gamejolt.init(app_id, private_key) first"` 。
    切换到另一个 `app_id` 时 `init()` 会清掉旧的 `username` / `user_token` ，避免串号。

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

`request_path` 的参数值会先做百分号编码，再按编码后的字符串算签名，两边始终一致。

??? quote "`generateSignature` 与 `apiRequest`"
    ```lua
    local function generateSignature(request_path)
        local input = gamejolt.base_url .. request_path .. gamejolt.private_key
        return md5.sumhexa(input)
    end

    -- On failure returns false, message, kind, where kind is "transport" (unreachable, bad
    -- HTTP status, unparseable body) or "api" (the server explicitly refused).
    local function apiRequest(path)
        if (not https or type(https.request) ~= "function") then
            local platform = (SE and SE.system and SE.system.getOS and SE.system.getOS()) or "Unknown"
            local reason = https_error or "missing native https module"
            return false, "GameJolt API unavailable on "..tostring(platform)..": "..reason, "transport"
        end

        local url = gamejolt.base_url .. path .. "&signature=" .. generateSignature(path)

        -- lua-https (https.dll) API: returns code, body, headers. DNS and TLS failures raise
        -- instead of returning a code in some builds, hence the pcall.
        local raised, code, body = pcall(https.request, url)
        if (not raised) then return false, "HTTPS request failed: "..tostring(code), "transport" end
        if (not code) then return false, "HTTPS request failed: "..tostring(body), "transport" end
        if (code ~= 200) then return false, "HTTP error: "..tostring(code), "transport" end

        local data, pos, err = json.decode(body)
        if (type(data) ~= "table") then
            return false, "JSON decode error: "..tostring(err).."\nResponse: "..tostring(body), "transport"
        end

        -- A body that parses but carries no response envelope is not a valid success.
        local payload = data.response
        if (type(payload) ~= "table") then
            return false, "Malformed response: missing response envelope", "transport"
        end

        -- GameJolt reports success as the string "true"/"false", but tolerate a bare boolean
        -- so neither shape slips past the check.
        if (payload.success == false or payload.success == "false") then
            return false, payload.message or "API error", "api"
        end

        return payload
    end
    ```

`apiRequest` 收的是**不带 `signature` 的路径**，URL 与签名都由它在内部组装，调用方不需要自己拼。

### 返回值的统一约定

| 情况 | 返回 |
|---|---|
| 成功 | `data.response` （一张表），**没有第二个返回值** |
| 传输层失败（无 https 模块、网络异常、HTTP 状态码非 200、响应无法解析） | `false, 错误信息, "transport"` |
| 服务端拒绝（业务层返回失败） | `false, 错误信息, "api"`，错误信息即接口返回的 `message` |

第三个返回值 `kind` 用来区分"没连上"和"连上了但被拒"。库内部用它判断心跳要不要继续；调用方一般用不到，忽略即可。

```lua
local res, err = Gamejolt.fetchUser(nil, "somebody")
if (res == false) then
    print("失败了:", err)
else
    print(res.users[1].username)
end
```

!!! note "失败一定返回 `false`"
    成功只返回一张表，失败总是以 `false` 开头。`if (not res) then` 也能用，
    但 `res == false` 更贴近约定： `res` 为表时一定是成功。

---

## 方法一览

### 通用

!!! example "通用"
    - `init(app_id, private_key)` 设置 `app_id` / `private_key` / `base_url` ，返回两者是否都非空，并清掉旧登录状态。
    - `isAvailable()` 原生 `https` 模块是否就绪。失败时第二返回值是带平台名的说明。
    - `isLoggedIn()` 是否已有一份**被服务端接受过**的凭据，见下方说明。
    - `logout()` 清掉本地 `username` / `user_token` 并停掉心跳。纯本地操作，不发请求。

### 用户

!!! example "用户"
    - `fetchUser(user_id, username)` 查用户信息，两个参数给一个即可，**不需要登录**。
    - `authUser(username, user_token)` 验证用户名 + token。只有服务端接受之后，凭据才会存下来给后续接口用。
    - `logout()` 丢弃本地凭据，回到未登录状态。

!!! note "`authUser` 先验证、后写入"
    旧实现是先把 `username` / `token` 存下来再发请求，失败也不回滚，于是 `authUser` 返回 `false` 时
    `isLoggedIn()` 依然是 `true` ，后续接口带着无效 token 一路失败。现在是**验证通过才提交**：

    ```lua
    local path = "/users/auth/?game_id=" .. gamejolt.app_id ..
                 "&username=" .. urlencode(clean_user) ..
                 "&user_token=" .. urlencode(clean_token)

    local result, message = apiRequest(path)
    if (result == nil or result == false) then
        gamejolt.logout()
        return false, message
    end

    gamejolt.username = clean_user
    gamejolt.user_token = clean_token
    gamejolt._verified = true
    return true
    ```

    由此得到几条确定的行为：

    - `isLoggedIn()` 为 `true` 意味着这份凭据**至少成功通过一次** `/users/auth/`
    - `authUser` 失败会把库恢复到未登录状态，**不需要**调用方手动置 nil
    - 用户名与 token 会先去掉首尾空白再从非空才算合法，纯空格或非字符串入参直接返回 `false`
    - 重新登录失败时，上一次登录状态会被清掉，不会留半新半旧的凭据

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

!!! note "心跳被服务端拒绝时会停掉并掉线"
    每次 ping 的失败原因由第三个返回值 `kind` 区分：

    - `"transport"` 网络不通、状态码非 200 等 —— 只记 `last_error` ，下一轮继续重试
    - `"api"` 服务端明确拒绝（凭据失效、会话过期等） —— 置 `_session_auto.enabled = false` 并把 `_verified` 置为 `false`

    后一种情况下 `isLoggedIn()` 会变成 `false` ，避免整个游戏周期内反复用无效凭据重试。
    玩家重新 `authUser` 成功后再调 `sessionUpdate()` 即可恢复。

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

!!! note "`key` 和 `data` 会被百分号编码"
    所有查询参数值都过一遍 `urlencode` ，再按编码后的字符串算签名：

    ```lua
    local path = "/data-store/set/?game_id=" .. gamejolt.app_id ..
                 "&key=" .. urlencode(key) .. "&data=" .. urlencode(data) .. credentials
    ```

    所以 `key` / `data` 里带空格、中文、`&` 、 `=` 、 `#` 都不会截断 URL 或导致签名不匹配。
    仍然建议对结构化数据先 `json.encode` 再存，方便读回来解析。

!!! note "`user_data` 为 true 时会先检查登录"
    旧实现在未登录时拼 `nil` 凭据直接抛错。现在 `user_data` 为 `true` 且未登录时返回
    `false, "GameJolt: not authenticated, call gamejolt.authUser(username, user_token) first"` 。

### 分数榜

!!! example "分数榜"
    - `fetchScoresLocal(table_id)` 拉榜单前 N 名，**不需要登录**。`table_id` 省略则取游戏的主榜。
    - `fetchScoresGlobal(table_id)` 带 `username + user_token` 请求，返回里会多出玩家自己的排名/前后名次，**需要登录**。
    - `submitScore(score, table_id, sort, extra_data, as_guest)` 提交分数。`sort` 是展示用的数值，`extra_data` 是额外文本（比如用时、等级）。
      - 已登录时自动带上凭据，分数挂到玩家账号上
      - 未登录时按游客提交，第五个参数 `as_guest` 传 `true` 则在已登录状态下也强制按游客提交

```lua
Gamejolt.submitScore(12345, 535, 12345, "LV19|Genocide")
local res = Gamejolt.fetchScoresLocal(535)
if (res ~= false and res.scores) then
    for _, s in ipairs(res.scores) do print(s.score, s.user) end
end
```

!!! note "凭据拼在所有可选参数之后"
    `submitScore` 先拼 `table_id` / `sort` / `extra_data` ，末尾再追加凭据，所以两者位置不会互相影响：

    ```lua
    local credentials = ""
    if (not as_guest and gamejolt.isLoggedIn()) then
        credentials = userParams()
    end

    local path = "/scores/add/?game_id=" .. gamejolt.app_id ..
                 "&score=" .. urlencode(score) ..
                 (table_id and "&table_id=" .. urlencode(table_id) or "") ..
                 (sort and "&sort=" .. urlencode(sort) or "") ..
                 (extra_data and "&extra_data=" .. urlencode(extra_data) or "") ..
                 credentials
    ```

    掉线后（比如心跳被服务端拒绝）凭据会自动消失，无需调用方干预，后续提交自然降级成游客分数。
    `score` 缺失时直接返回 `false, "GameJolt: score is required"` ，不会把 `nil` 拼进 URL。

---

## 一个完整的登录流程

```lua
-- 场景的 load / 某个一次性初始化点
Gamejolt.init(Global.GetVariable("GamejoltID"), Global.GetVariable("GamejoltPK"))

local function login(name, token)
    local ok, err = Gamejolt.authUser(name, token)
    if (not ok) then
        return false, err          -- 库内部已经logout()，不用手动清凭据
    end

    Gamejolt.sessionUpdate(30, "active")      -- 之后自动心跳

    local res = Gamejolt.fetchAchievements(true)
    if (res ~= false and res.achievements) then
        -- 同步本地成就状态
    end
    return true
end
```

退出登录走 `logout()` ；只想停会话但保持登录则用 `sessionClose()` 。

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

!!! note "GameJolt 返回的 `success` 是字符串"
    GameJolt 实际返回的是字符串 `"true"` / `"false"` 。库判的是
    `payload.success == false or payload.success == "false"` ，两种形式都能拦住，不用自己去转类型。

!!! note "请求失败不会抛出到 `love.update`"
    `https.request` 被包在 `pcall` 里。DNS 失败、TLS 握手失败等在某些 lua-https 构建里是**抛错**而非返回错误码，
    包一层之后统一转成 `false, 错误信息, "transport"` ，不会让整局崩掉。

!!! note "非 Windows 平台直接不可用"
    `https.dll` 是 Windows 动态库。`isAvailable()` 会返回 `false` ，所有请求返回统一的不可用提示。
    打包 Android 时，把 GameJolt 相关逻辑包在 `if Gamejolt.isAvailable() then` 内。

!!! note "`app_id` 被转成数字"
    `gamejolt.app_id = tonumber(app_id)` 。传字符串 `"123456"` 也能用，但不要传带空格或字母的值。
