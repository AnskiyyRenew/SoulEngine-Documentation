---
title: Networking
---

The networking topic covers the engine's three built-in networking/multiplayer libraries. They're independent of each other; use whichever you need:

| Role | Path | What it does |
|---|---|---|
| GameJolt API | `Scripts/Libraries/GamejoltAPI.lua` | Connect to GameJolt: login, achievements (trophies), scoreboards, cloud saves |
| Discord RPC | `Scripts/Libraries/DiscordRPC.lua` | Show "what you're playing" on your Discord profile (Rich Presence) |
| sock | `Scripts/Libraries/Network/sock.lua` | ENet-based multiplayer (C/S structure, event send/receive) |

Two global aliases are set up at the top of `main.lua` — use them directly:

```lua
Gamejolt = ImportFile("GamejoltAPI")
Discord  = ImportFile("DiscordRPC")
```

`sock` is **not** auto-loaded (not every game needs multiplayer), so import it yourself when needed:

```lua
local sock = ImportFile("Network.sock")
```

---

## What the Engine Already Does for You

All three libraries are "quiet" by default and won't crash the game just because they're unconfigured.

| Library | What the engine does for you | What you do |
|---|---|---|
| Discord | In `love.load()` reads `Global.GetVariable("DiscordAppID")` → `Discord.init()` → `setActivity()`; in `love.update(dt)` calls `Discord.update(dt)` every frame; in `love.quit()` calls `Discord.shutdown()` | Change `DiscordAppID` in `Game/conf_pure.lua` to your own |
| Gamejolt | In `love.update(dt)` calls `Gamejolt.update(dt)` every frame (only drives the session heartbeat) | **You must call `Gamejolt.init()` and `authUser()` yourself** — the engine won't do it for you |
| sock | None | Write it all yourself |

!!! warning "GameJolt does not auto-initialize"
    The engine only calls `Gamejolt.update(dt)` — **nowhere does it call `Gamejolt.init()`**.
    Calling other methods before `init()` will error directly because `gamejolt.base_url` is still `nil` (concatenating nil).
    See [GameJolt](./000_gamejolt.md).

---

## Dependencies & Platform Support

| Library | Dependency | Consequence if unavailable |
|---|---|---|
| Gamejolt | Native `https` module (`Resources/Libs/https.dll`, **Windows only**) | All requests return `false, "GameJolt API unavailable on ..."`, game runs normally |
| Discord | LuaJIT's `ffi` + native libs under `Resources/Libs/DiscordRPC/` (**Windows only**) | `init()` returns `false, reason`, other methods degrade to no-ops |
| sock | `enet` (**bundled with LÖVE**, no extra dll needed) + optional `bitser` | `require "enet"` failing will error directly (all standard LÖVE builds include it) |

!!! note "Android / Mobile"
    Both `https.dll` and `discord-rpc-*.dll` are **Windows-only** dynamic libraries and can't be loaded even if packed into an Android package.
    These two libraries auto-degrade on non-Windows platforms (`isAvailable()` returns `false`) — **don't** hang critical logic on them.

---

## Pages in This Topic

| Page | Content |
|---|---|
| [GameJolt](./000_gamejolt.md) | Initialization, login, achievements, session heartbeat, cloud saves, scoreboards, plus the unencoded-URL pitfall |
| [Discord RPC](./010_discord.md) | Changing Presence, callback events, image assets, byte limit, the origin of `jit.off` |
| [sock Multiplayer](./020_sock.md) | Server/client, events & schema, send modes & channels, a complete minimal example |

---

## Minimal Examples

**Discord — just change the config**

```lua
-- Game/conf_pure.lua
Global.SetVariable("DiscordAppID", "1234567890123456789")  -- note: it's a string
```

About 2 seconds after entering the game, the activity status appears on your Discord profile.

**GameJolt — you must initialize it yourself**

```lua
-- in some scene's load
Gamejolt.init(Global.GetVariable("GamejoltID"), Global.GetVariable("GamejoltPK"))
local ok, err = Gamejolt.authUser("my_name", "my_token")
if (ok) then
    Gamejolt.sessionUpdate(30, "active")   -- the engine pings for you every frame after this
end
```

**sock — both ends must run**

```lua
-- server
server = sock.newServer("*", 22122)
server:on("chat", function(data, client) server:sendToAll("chat", data) end)
-- in love.update: server:update()

-- client
client = sock.newClient("127.0.0.1", 22122)
client:connect()
client:on("chat", function(data) print(data.text) end)
-- in love.update: client:update()
```
