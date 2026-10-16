---
title: GameJolt API
---

`Scripts/Libraries/GamejoltAPI.lua` wraps the common endpoints of the [GameJolt Game API v1.2](https://gamejolt.com/game-api/doc): users, trophies, sessions, data storage, and score tables.

All requests use **HTTPS + MD5 signing** and go through the native module `Resources/Libs/https.dll`.

---

## Preparation

### 1. Get the App ID and Private Key

After creating your game on GameJolt, go to the game's **Manage → Game API** page, where you'll find two things:

| Field | Description | Where to put it |
|---|---|---|
| `game_id` | The game ID, usually 6–7 digits | `GamejoltID` in `Game/conf_pure.lua` |
| `private_key` | The private key. **Do not** let anyone other than the players see it | `GamejoltPK` in `Game/conf_pure.lua` |

```lua
-- Game/conf_pure.lua
Global.SetVariable("GamejoltID", 123456)
Global.SetVariable("GamejoltPK", "abcdef0123456789abcdef0123456789")
```

!!! tip "The two `conf_pure.lua` files are layered"
    The one in the root directory holds the engine defaults, and the one in `Game/conf_pure.lua` overrides it.
    Put your configuration in **`Game/conf_pure.lua`**; see [Configuration file](../010_quick_start/000_conf.md).

!!! danger "The private key is baked into the game package"
    GameJolt's `private_key` is not "absolutely secret" — it is designed to be distributed with the client (every player's copy contains one).
    But **do not** treat it as access control — anyone who unpacks the game can get it. Real write permission relies on `username + user_token` validation.<br>
    To keep it out of plain text, compile it into a native library and read it back through FFI — see [Developer Tools → Native Secret Store](../070_develop/050_secrets.md).
    That is **obfuscation, not encryption**, and nothing in the engine calls it yet; you wire up `Secrets.gamejoltPK()` yourself.

### 2. Initialize (the engine won't do it for you)

```lua
Gamejolt.init(Global.GetVariable("GamejoltID"), Global.GetVariable("GamejoltPK"))
```

`init` only does three things: converts `app_id` to a number, stores `private_key`, and builds `base_url`.

??? quote "Source of `init`"
    ```lua
    function gamejolt.init(app_id, private_key)
        gamejolt.app_id = tonumber(app_id)
        gamejolt.private_key = private_key
        gamejolt.base_url = "https://api.gamejolt.com/api/game/v1_2"
        return (gamejolt.app_id ~= nil and gamejolt.private_key ~= nil)
    end
    ```

!!! warning "You must init first"
    `base_url` is only assigned inside `init()`. If you call `fetchUser()` and other methods without initializing,
    URL building will throw an error because it concatenates `nil` — and it happens **when that line runs**, not at load time.

### 3. Check whether it can be used

```lua
local ok, err = Gamejolt.isAvailable()
if (not ok) then print(err) end
```

When the `https` module cannot be obtained, it returns `false` and an explanation (which includes the current platform name from `SE.system.getOS()`).

---

## How the signature is computed

Every request must carry a `signature` parameter, whose value is:

```lua
md5.sumhexa(base_url .. request_path .. private_key)
```

Here `request_path` is the **full path + parameters excluding the signature itself**. Each method in the library assembles it itself, so you don't need to worry about it.

??? quote "`generateSignature` and `apiRequest`"
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

### Unified return-value convention

| Situation | Returns |
|---|---|
| Success | `data.response` (a table), **no second return value** |
| Failure | `false, error message string` |

So when calling, either check `false` first, or wrap it yourself like some methods do:

```lua
local res, err = Gamejolt.fetchUser(nil, "somebody")
if (res == false) then
    print("failed:", err)
else
    print(res.users[1].username)
end
```

!!! bug "On success the second return value is also nil — don't treat it as an error code"
    For example, `fetchUser` returns only `data.response` on success, and the second return value is `nil`.
    Writing `local res, err = ...; if err then ...` is safe, but `if (not res) then` can also misfire when
    some interface returns an empty table — using `res == false` uniformly is the safest.

---

## Method overview

### General

!!! example "General"
    - `init(app_id, private_key)` sets `app_id` / `private_key` / `base_url` and returns whether both are non-empty.
    - `isAvailable()` whether the native `https` module is ready. On failure the second return value is an explanation with the platform name.
    - `isLoggedIn()` whether `user_token` and `username` are both set (**does not validate correctness**, see warning below).

### Users

!!! example "Users"
    - `fetchUser(user_id, username)` looks up user info; pass either of the two parameters, **login not required**.
    - `authUser(username, user_token)` validates the username + token. On success, `gamejolt.username` / `gamejolt.user_token` are kept for later interfaces.

!!! bug "`isLoggedIn()` is still true after `authUser` fails"
    The source code **stores the username/token first, then sends the request**:

    ```lua
    function gamejolt.authUser(username, user_token)
        gamejolt.username = username       -- stored first
        gamejolt.user_token = user_token
        ...
        local success, err = apiRequest(url)
        return success ~= false, err
    end
    ```

    On network failure / wrong token it returns `false, err`, but the two fields **have already been written**,
    so `isLoggedIn()` still returns `true`, and all subsequent interfaces that need login will request with the wrong token.

    Wrap it yourself:

    ```lua
    local ok, err = Gamejolt.authUser(name, token)
    if (not ok) then
        Gamejolt.username = nil
        Gamejolt.user_token = nil
    end
    ```

### Trophies (achievements)

!!! example "Trophies"
    - `fetchAchievements(achieved_only)` pulls the trophy list; pass `true` to `achieved_only` to return only unlocked ones, **login required**.
    - `unlockAchievement(trophy_id)` unlocks the specified trophy; `trophy_id` is the numeric ID assigned when the trophy was created in the GameJolt backend, **login required**.

```lua
local res = Gamejolt.fetchAchievements(true)
if (res ~= false and res.achievements) then
    for _, a in ipairs(res.achievements) do
        print(a.id, a.title, a.achieved)
    end
end

Gamejolt.unlockAchievement(1047)
```

!!! note "`trophy_id` is not an array index"
    The ID shown in the backend when creating a trophy is a global number (e.g. 1047), not "the nth one". Filling it wrong returns an API error.

### Sessions (playtime / status)

GameJolt uses this to track "who is playing, and for how long".

!!! example "Sessions"
    - `sessionOpen()` opens a session once. In manual mode you just call this line yourself.
    - `sessionUpdate(interval, status)` **recommended**. Opens a session once and starts the auto heartbeat. `interval` is in **seconds** (default 30, minimum 1); `status` defaults to `"active"`.
    - `sessionPing(status)` pings manually once, and can switch the status (`"active"` / `"idle"`).
    - `sessionClose()` closes the session and stops the auto heartbeat.
    - `update(dt)` the timer for the auto heartbeat. The engine already calls it every frame inside `love.update(dt)`, so **you don't call it again** (calling it would double the frequency).

```lua
Gamejolt.sessionUpdate(30, "active")
-- afterwards, Gamejolt.update(dt) accumulates dt each frame and auto-pings every 30 seconds
```

The auto state is stored in `Gamejolt._session_auto`; you can read it:

| Field | Description |
|---|---|
| `enabled` | whether the auto heartbeat is on |
| `interval` | interval (seconds) |
| `status` | the currently reported status |
| `elapsed` | seconds accumulated since the last ping |
| `last_error` | the error message from the last ping (set to nil on success) |

!!! warning "`interval` is seconds, not milliseconds"
    `state.elapsed = state.elapsed + dt`, and `dt` is in seconds. Writing `30000` would give a heartbeat every 30000 seconds.

### Data storage (cloud save / global data)

A simple key-value store.

!!! example "Data storage"
    - `dataStore(key, data, user_data)` writes.
        - when `user_data` is `true`, it is stored under **that user** (requires login); otherwise it is stored under **game global**.
    - `dataFetch(key, user_data)` reads one key.
    - `dataFetchAll(user_data)` reads all keys.
    - `dataDelete(key, user_data)` deletes one key.
    - `dataGetKeys(user_data)` pulls only the key-name list.

```lua
-- The player's own save (requires authUser first)
Gamejolt.dataStore("slot1", json.encode(mySave), true)
local res = Gamejolt.dataFetch("slot1", true)
if (res ~= false and res.data) then mySave = json.decode(res.data) end

-- A game-global announcement (no login required)
Gamejolt.dataStore("motd", "Server maintenance today")
```

!!! danger "`key` and `data` are not URL-encoded at all"
    The source code concatenates raw strings:

    ```lua
    local url = gamejolt.base_url .. "/data-store/set/?game_id=" .. gamejolt.app_id ..
                "&key=" .. key .. "&data=" .. data .. ...
    ```

    If `key` or `data` contains `&`, `=`, `#`, spaces, or Chinese characters, the URL will be truncated / misparsed,
    and since **the signature is computed from the assembled string**, the server won't match it and returns a signature error directly.

    Workarounds:

    - use only `[A-Za-z0-9_-]` for the key
    - `json.encode` the data first, then apply your **own** percent-encoding (or base64) before sending
    - in short, don't put player-entered text in directly

### Score tables

!!! example "Score tables"
    - `fetchScoresLocal(table_id)` pulls the top N entries, **no login required**. If `table_id` is omitted, it takes the game's main table.
    - `fetchScoresGlobal(table_id)` requests with `username + user_token`; the result includes the player's own rank / neighbors, **login required**.
    - `submitScore(score, table_id, sort, extra_data)` submits a score. `sort` is the value used for display; `extra_data` is extra text (e.g. time used, level).

```lua
Gamejolt.submitScore(12345, 535, 12345, "LV19|Genocide")
local res = Gamejolt.fetchScoresLocal(535)
if (res ~= false and res.scores) then
    for _, s in ipairs(res.scores) do print(s.score, s.user) end
end
```

!!! bug "`submitScore` does not carry username/token — it submits a guest score"
    When assembling the URL, `username` / `user_token` are **not** appended (compare `fetchScoresGlobal`, which does attach them),
    so even if you have called `authUser`, the score is submitted as a **guest** and won't be attached to the player's account.

    To submit an authenticated score, write your own credentialed version following the library's approach, or modify this library.

---

## A complete login flow

```lua
-- The scene's load / some one-time initialization point
Gamejolt.init(Global.GetVariable("GamejoltID"), Global.GetVariable("GamejoltPK"))

local function login(name, token)
    local ok, err = Gamejolt.authUser(name, token)
    if (not ok) then
        Gamejolt.username, Gamejolt.user_token = nil, nil
        return false, err
    end

    Gamejolt.sessionUpdate(30, "active")      -- auto heartbeat afterwards

    local res = Gamejolt.fetchAchievements(true)
    if (res ~= false and res.achievements) then
        -- sync local achievement state
    end
    return true
end
```

---

## Pitfall summary

!!! warning "All requests are **synchronously blocking**"
    `https.request(url)` blocks until the server responds. Connecting to GameJolt from within China is usually a few hundred milliseconds to a few seconds,
    and **the whole game is frozen for that frame**.

    - Never send a request every frame inside `love.update`
    - One-off requests are acceptable (e.g. a brief freeze when submitting a score)
    - If you want non-blocking behavior you must set up coroutines / threads yourself; the library provides no async version

!!! warning "Failures don't throw — they only return `false`"
    If you don't check the return value, failures are silently ignored. All calls are recommended to be written as `if (res == false) then ...`.

!!! warning "The `success` returned by GameJolt is a string"
    The library checks `data.response.success == "false"` — note it is the string `"false"`, not a boolean.
    This follows the actual return of the GameJolt API, so don't "fix" it.

!!! note "Unavailable directly on non-Windows platforms"
    `https.dll` is a Windows dynamic library. `isAvailable()` returns `false`, and all requests return the unified unavailable message.
    When packaging for Android, it's safest to wrap GameJolt-related logic in `if Gamejolt.isAvailable() then`.

!!! note "`app_id` is converted to a number"
    `gamejolt.app_id = tonumber(app_id)`. Passing the string `"123456"` works, but don't pass a value with spaces or letters.
