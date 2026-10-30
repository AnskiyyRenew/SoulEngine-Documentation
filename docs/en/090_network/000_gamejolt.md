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

`init` does four things: converts `app_id` to a number, stores `private_key`, builds `base_url`, and clears any login state left over from a previous game.

??? quote "Source of `init`"
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

!!! note "Without init the library returns false instead of concatenating nil"
    `base_url` is only assigned inside `init()`. Calling any endpoint before that hits a
    `requireConfig()` guard that returns `false, "GameJolt: call gamejolt.init(app_id, private_key) first"` —
    it does not throw. Switching to another `app_id` clears the stored `username` / `user_token`, so the two games cannot mix credentials.

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

Query parameter values are percent-encoded first, and the signature is computed over the encoded string, so the two always agree.

??? quote "`generateSignature` and `apiRequest`"
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

`apiRequest` takes the **path without `signature`**; both the URL and the signature are assembled internally, so callers never build either.

### Unified return-value convention

| Situation | Returns |
|---|---|
| Success | `data.response` (a table), **no second return value** |
| Transport failure (no https module, network error, non-200 status, unparseable body) | `false, error message, "transport"` |
| Server refusal (business-level failure) | `false, error message, "api"`, where the message is the `message` returned by the endpoint |

The third return value `kind` separates "could not reach the server" from "reached it and got refused". The library uses it to decide whether the heartbeat should continue; callers can ignore it.

```lua
local res, err = Gamejolt.fetchUser(nil, "somebody")
if (res == false) then
    print("failed:", err)
else
    print(res.users[1].username)
end
```

!!! note "Failures always start with `false`"
    Success returns nothing but a table; failure always begins with `false`.
    `if (not res) then` also works, but `res == false` matches the convention better: when `res` is a table, the call succeeded.

---

## Method overview

### General

!!! example "General"
    - `init(app_id, private_key)` sets `app_id` / `private_key` / `base_url`, returns whether both are non-empty, and clears any previous login state.
    - `isAvailable()` whether the native `https` module is ready. On failure the second return value is an explanation with the platform name.
    - `isLoggedIn()` whether a pair of credentials is stored **and was accepted by the server**; see below.
    - `logout()` drops the local `username` / `user_token` and stops the heartbeat. Local only, sends no request.

### Users

!!! example "Users"
    - `fetchUser(user_id, username)` looks up user info; pass either of the two parameters, **login not required**.
    - `authUser(username, user_token)` validates the username + token. The credentials are stored for later interfaces only after the server accepts them.
    - `logout()` discards the local credentials and returns to the logged-out state.

!!! note "`authUser` validates first, stores afterwards"
    The previous implementation stored the username/token before sending the request and never rolled them back,
    so `isLoggedIn()` stayed `true` after `authUser` returned `false`, and every later call went out with an invalid token.
    It now **commits only after validation passes**:

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

    This gives a few guaranteed behaviors:

    - `isLoggedIn()` returning `true` means the credentials **passed `/users/auth/` at least once**
    - a failed `authUser` restores the library to the logged-out state; callers do **not** need to nil out the fields
    - username and token are trimmed of surrounding whitespace first; blank or non-string input returns `false` directly
    - if a re-login fails, the previous login is dropped rather than leaving half-updated credentials behind

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

!!! note "A heartbeat refused by the server stops the heartbeat and logs the player out"
    The reason for each failed ping is reported by the third return value, `kind`:

    - `"transport"` unreachable, non-200 status, and so on — only `last_error` is recorded, and the next tick retries
    - `"api"` the server explicitly refused (invalid credentials, expired session) — `_session_auto.enabled` is set to `false` and `_verified` to `false`

    In the second case `isLoggedIn()` turns `false`, which keeps the game from retrying invalid credentials for the rest of the run.
    Calling `sessionUpdate()` again after a successful `authUser` restores it.

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

!!! note "`key` and `data` are percent-encoded"
    Every query parameter value goes through `urlencode`, and the signature is computed afterwards:

    ```lua
    local path = "/data-store/set/?game_id=" .. gamejolt.app_id ..
                 "&key=" .. urlencode(key) .. "&data=" .. urlencode(data) .. credentials
    ```

    Spaces, Chinese characters, `&`, `=`, and `#` inside `key` / `data` therefore cannot truncate the URL or break the signature.
    Encoding structured data with `json.encode` before storing it is still recommended, so it parses cleanly when read back.

!!! note "A `user_data` call checks the login first"
    The previous implementation concatenated `nil` credentials and threw when nobody was logged in. With `user_data` set to `true`
    and no active login, it now returns `false, "GameJolt: not authenticated, call gamejolt.authUser(username, user_token) first"`.

### Score tables

!!! example "Score tables"
    - `fetchScoresLocal(table_id)` pulls the top N entries, **no login required**. If `table_id` is omitted, it takes the game's main table.
    - `fetchScoresGlobal(table_id)` requests with `username + user_token`; the result includes the player's own rank / neighbors, **login required**.
    - `submitScore(score, table_id, sort, extra_data, as_guest)` submits a score. `sort` is the value used for display; `extra_data` is extra text (e.g. time used, level).
      - while logged in, the credentials are appended automatically and the score is filed under the player's account
      - with nobody logged in the score goes in as a guest; pass `true` for the fifth argument, `as_guest`, to force a guest submission even while authenticated

```lua
Gamejolt.submitScore(12345, 535, 12345, "LV19|Genocide")
local res = Gamejolt.fetchScoresLocal(535)
if (res ~= false and res.scores) then
    for _, s in ipairs(res.scores) do print(s.score, s.user) end
end
```

!!! note "Credentials go after every optional parameter"
    `submitScore` assembles `table_id` / `sort` / `extra_data` first and appends the credentials last, so the two never interfere:

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

    If the session drops (for example a heartbeat the server refused), the credentials disappear on their own and later submissions fall back to guest scores with no call-site changes.
    A missing `score` returns `false, "GameJolt: score is required"` instead of concatenating `nil` into the URL.

---

## A complete login flow

```lua
-- The scene's load / some one-time initialization point
Gamejolt.init(Global.GetVariable("GamejoltID"), Global.GetVariable("GamejoltPK"))

local function login(name, token)
    local ok, err = Gamejolt.authUser(name, token)
    if (not ok) then
        return false, err          -- the library already logged out; no manual cleanup needed
    end

    Gamejolt.sessionUpdate(30, "active")      -- auto heartbeat afterwards

    local res = Gamejolt.fetchAchievements(true)
    if (res ~= false and res.achievements) then
        -- sync local achievement state
    end
    return true
end
```

Use `logout()` to drop the credentials, or `sessionClose()` to stop the session while staying logged in.

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

!!! note "The `success` returned by GameJolt is a string"
    GameJolt actually returns the strings `"true"` / `"false"`. The library checks
    `payload.success == false or payload.success == "false"`, so both shapes are caught and there is nothing to convert.

!!! note "Failed requests never escape into `love.update`"
    `https.request` runs inside a `pcall`. In some lua-https builds DNS and TLS failures **raise** instead of returning an error code;
    the wrapper turns them into `false, error message, "transport"` so a connection problem cannot take down the whole run.

!!! note "Unavailable directly on non-Windows platforms"
    `https.dll` is a Windows dynamic library. `isAvailable()` returns `false`, and all requests return the unified unavailable message.
    When packaging for Android, it's safest to wrap GameJolt-related logic in `if Gamejolt.isAvailable() then`.

!!! note "`app_id` is converted to a number"
    `gamejolt.app_id = tonumber(app_id)`. Passing the string `"123456"` works, but don't pass a value with spaces or letters.
