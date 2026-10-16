---
title: sock networking
---

`Scripts/Libraries/Network/sock.lua` is a copy of **[sock.lua v0.3.0](https://github.com/camchenry/sock.lua)**,
wrapping an **event-name + data-table** interface on top of [ENet](http://enet.bespin.org/) (built into LÖVE, reliable UDP):

```lua
client:send("playerMove", { x = 100, y = 200 })
-- the other end
server:on("playerMove", function(data, client) ... end)
```

You don't unpack packets yourself, don't worry about serialization, and don't touch `enet`'s peer/channel details.

There are also two **serialization libraries** in the same directory; `sock` picks one to use:

| File | Description |
|---|---|
| `Scripts/Libraries/Network/bitser.lua` | the one `sock` uses by default (Robin Wellner's bitser) |
| `Scripts/Libraries/Network/binser.lua` | another similarly named library (Calvin Rose's binser); **`sock` does not auto-load it** |

---

## Loading

```lua
local sock = ImportFile("Network.sock")
```

!!! bug "The line that imports enet leaks a global variable"
    Line 37 of sock.lua reads `enet = require "enet"` — **no `local`**.
    After loading, `_G.enet` will be set. This is just namespace pollution and harmless functionally,
    but if you also use the name `enet` elsewhere, be careful not to conflict.

---

## Two roles

| | Create | Per frame | Send message |
|---|---|---|---|
| Server | `sock.newServer(address, port, ...)` | `server:update()` | `sendToAll` / `sendToAllBut` / `sendToPeer` |
| Client | `sock.newClient(address, port, ...)` | `client:update()` | `send` |

!!! example "`newServer`"
    `sock.newServer(address, port, maxPeers, maxChannels, inBandwidth, outBandwidth)`

    - `address` the address to bind, defaults to `"localhost"`. To accept LAN / external connections you must pass `"*"`.
    - `port` the port, defaults to `22122`.
    - `maxPeers` max number of connections, defaults to `64`.
    - `maxChannels` number of channels, defaults to **1**.
    - `inBandwidth` / `outBandwidth` bandwidth limit (bytes/second), defaults to `0` = unlimited.

!!! example "`newClient`"
    `sock.newClient(serverOrAddress, port, maxChannels)`

    - Common usage: `sock.newClient("127.0.0.1", 22122)`.
    - Second usage: pass an **enet peer**, and use it directly as an existing connection (the server internally builds client objects this way).

!!! danger "Both ends' `maxChannels` must match"
    ENet requires the client and server to have the same number of channels.
    The default is **1**, meaning if you want multiple channels, both sides must explicitly pass the same number, otherwise they can't connect.

!!! warning "A used port will directly `error()`"
    ```lua
    if not server.host then
        error("Failed to create the host. Is there another server running on :"..server.port.."?")
    end
    ```
    It does not return `nil`. To handle it gracefully, wrap it in a `pcall`.

---

## Lifecycle

```lua
-- server
server = sock.newServer("*", 22122)
server:on("connect", function(data, client) print("someone connected") end)

-- client
client = sock.newClient("127.0.0.1", 22122)
client:on("connect", function(data) print("connected") end)
client:connect()          -- actually connecting takes a few updates

-- inside love.update (both ends)
server:update()
client:update()
```

!!! warning "Nothing happens if you don't call `update()`"
    `connect()` only sends the connection request; the handshake is advanced by subsequent `update()` calls;
    received messages are also dispatched only inside `update()`. **Forgetting to call it is the most common "why can't I connect".**

!!! warning "`update()` throws if there's no serializer"
    ```lua
    if not self.deserialize then
        error("Can't deserialize message: deserialize was not set")
    end
    ```
    It won't trigger as long as `bitser` loads normally (the default). When manually `setSerialization`, don't set only half.

---

## Events

### Built-in events

| Event name | When it fires | Callback parameters |
|---|---|---|
| `connect` | connection established | server `(data, client)`, client `(data)`; `data` is the connection code number |
| `disconnect` | disconnected | same as above; `data` is the disconnect code number |

### Custom events

`on(event_name, callback)` registers; multiple callbacks can be attached to the same event name, executed in registration order.

```lua
-- server: one extra client parameter, representing "who sent it"
server:on("chat", function(data, client)
    print(client:getConnectId(), "says:", data.text)
    server:sendToAll("chat", data)
end)

-- client: only data
client:on("chat", function(data)
    print(data.text)
end)
```

- `removeCallback(callback)` removes using the return value from registration.
- When an event with no corresponding callback is received, only a warning is logged; it doesn't error.

---

## Sending data

!!! example "Server"
    - `sendToAll(event, data)` broadcasts to everyone.
    - `sendToAllBut(client, event, data)` broadcasts to everyone except someone.
        - What's passed is a **sock Client object**; internally compared with `p ~= client.connection`.
    - `sendToPeer(peer, event, data)` sends to only one enet peer (e.g. to resend initial state to someone who just connected).

!!! example "Client"
    - `send(event, data)` sends to the server.

```lua
-- player movement: use unreliable mode, dropping a frame or two is fine
client:setSendMode("unreliable")
client:send("move", { x = px, y = py })

-- chat: must be reliable
client:send("chat", { text = "hi" })   -- reliable by default
```

### Send mode

| Mode | Meaning | Use |
|---|---|---|
| `reliable` | guaranteed arrival and ordering (**default**) | chat, state sync, commands |
| `unsequenced` | guaranteed arrival, not guaranteed order | reliable messages where order doesn't matter |
| `unreliable` | not guaranteed arrival | per-frame position, particles |

- `setSendMode(mode)` only takes effect for the **next message**, and reverts automatically after sending.
- `setDefaultSendMode(mode)` changes the default.
- When an invalid value is passed, `setSendMode` prints a warning and falls back to `reliable`; `setDefaultSendMode` directly `error()`s.

### Channels

- `setSendChannel(n)` / `setDefaultSendChannel(n)`, **starting from 0**, max `maxChannels - 1`.
- Out of range prints a warning and falls back to 0.

---

## Schema: save bandwidth

By default, a keyed table is sent, and the key names also take up bytes. After both ends agree on an order, you can send only an array:

```lua
-- server (receiver) declares the order
server:setSchema("move", { "x", "y", "vx", "vy" })

-- client (sender) sends only an array
client:send("move", { 100, 200, -4.5, 23.1 })

-- the server callback still gets a keyed table
server:on("move", function(data, client)
    print(data.x, data.y)
end)
```

!!! warning "Schema must be set on the **receiver**"
    The conversion happens inside `Listener:trigger` — meaning **whoever `on`s this event is whoever `setSchema`s it**.
    The client sends an array, so the server `setSchema`s; the server sends an array, so the client `setSchema`s. Setting it backwards has no effect.

!!! note "Set it once for each direction"
    The server and client each have an independent `listener`. If both directions use a schema, both sides must set it.

---

## Connection state

```lua
if (client:isConnected())    then ... end   -- connected
if (client:isConnecting())   then ... end   -- connecting (within a few frames after connect())
if (client:isDisconnecting())then ... end
if (client:isDisconnected()) then ... end
print(client:getState())                    -- string
```

`getState()` returns one of `sock.CONNECTION_STATES`:
`disconnected` / `connecting` / `acknowledging_connect` / `connection_pending` /
`connection_succeeded` / `connected` / `disconnect_later` / `disconnecting` /
`acknowledging_disconnect` / `zombie` / `unknown`.

There are three ways to disconnect:

| Method | Behavior |
|---|---|
| `disconnect(code)` | normal disconnect |
| `disconnectLater(code)` | disconnect after the queued packets are sent |
| `disconnectNow(code)` | disconnect immediately |
| `reset()` | force disconnect, **server receives no notification** |

!!! note "Connection state is not immediate"
    After `connect()`, `isConnected()` is still `false`; it takes a few `update()` calls to become `true`.
    Disconnecting is similarly delayed in effect. Don't use it in the UI as "changes the moment the button is clicked".

---

## Diagnostics and tuning

!!! example "Statistics"
    - `getRoundTripTime()` round-trip latency (milliseconds); only accurate after being connected for a while.
    - `getTotalSentData()` / `getTotalReceivedData()` cumulative byte counts.
    - `getTotalSentPackets()` / `getTotalReceivedPackets()` cumulative message counts.
    - Server: `getClientCount()` / `getClients()` / `getClient(peer)` / `getClientByConnectId(id)` / `getClientByIndex(i)`.

!!! example "Tuning"
    - `setPingInterval(ms)` ping interval, default 500.
    - `setTimeout(limit, minimum, maximum)` timeout for judging disconnect (default `32, 5000, 30000`).
    - `setThrottle(interval, acceleration, deceleration)` adjusts the unreliable-packet drop probability.
    - `setBandwidthLimit(incoming, outgoing)` bandwidth limit.
    - `setMessageTimeout(ms)` the wait milliseconds for `host:service()` inside `update()`, default 0 (non-blocking).
    - `enableCompression()` turns on compression; **both ends must either both turn it on or both leave it off**, and lua-enet has no off switch.

!!! example "Logging"
    - `client.logger.printEventData = true` prints all received events.
    - `logger.printErrors` / `printWarnings` are on by default.
    - `logger.messages` stores all complete log lines.
    - `client:log("error", "...")` manually logs one.

---

## A minimal runnable example

```lua
-- server process
local sock = ImportFile("Network.sock")
local server = sock.newServer("*", 22122)

server:setSchema("move", { "x", "y" })

server:on("connect", function(data, client)
    print("new player", client:getConnectId())
    server:sendToPeer(client.connection, "welcome", { id = client:getConnectId() })
end)

server:on("move", function(data, client)
    server:sendToAllBut(client, "move", { data.x, data.y })
end)

server:on("disconnect", function(data, client)
    print("player left", client:getConnectId())
end)

function love.update(dt)
    server:update()
end
```

```lua
-- client process
local sock = ImportFile("Network.sock")
local client = sock.newClient("127.0.0.1", 22122)
local others = {}

client:on("welcome", function(data) my_id = data.id end)
client:on("move",    function(data) others[data.id] = { x = data.x, y = data.y } end)

client:connect()

function love.update(dt)
    client:update()
    if (client:isConnected()) then
        client:setSendMode("unreliable")
        client:send("move", { x = player.x, y = player.y })
    end
end
```

---

## Pitfall summary

!!! warning "ENet is UDP, with no NAT traversal"
    `sock` only handles send/receive, and **does not provide** hole-punching, room matchmaking, or relay servers.
    To let someone from outside the network connect in, you must set up port forwarding / a cloud server / or use a platform network like Steam yourself.

!!! warning "bitser can't serialize functions and userdata"
    Can send: tables, numbers, strings, booleans, `nil`.
    Can't send: functions, `coroutine`, **LÖVE objects like `Image` / `Source` / `Canvas` (userdata)**, and class instances with a metatable that weren't registered.
    To send sprites/sounds, load them on each end and send only the filename or index.

!!! warning "The Client object the server gets is incomplete"
    Inside `Server:update` it is built via `sock.newClient(event.peer)`, taking the "pass peer" branch —
    its `host` field is `nil`. So calling methods that depend on `self.host`, like `getSocketAddress()` / `getTotalSentData()`, on it will error.
    For statistics, call the `server`'s own methods.

!!! warning "`sendToAllBut` takes a Client, not a peer"
    Internally it compares `p ~= client.connection`. Passing an enet peer in won't match, and the result equals `sendToAll`.

!!! note "The default address is `localhost`"
    `sock.newServer()` with no address only listens on the local machine. To be a host for others to connect to, write `sock.newServer("*", port)`.

!!! note "Don't confuse the two serialization libraries"
    In the directory, `bitser.lua` and `binser.lua` are **two different libraries** (different authors, different APIs).
    `sock` only knows `bitser`; `binser.lua` is just placed alongside, and you can manually hook it up yourself via `ImportFile("Network.binser")` if you want.

!!! note "Messages are dispatched synchronously"
    Messages received inside `update()` call the callback **immediately**. Heavy work in the callback freezes that frame,
    and you should also be careful about calling code inside the callback that would trigger `update()` again (re-entrancy).
