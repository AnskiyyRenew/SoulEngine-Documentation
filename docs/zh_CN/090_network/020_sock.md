---
title: sock 联机
---

`Scripts/Libraries/Network/sock.lua` 是一个 **[sock.lua v0.3.0](https://github.com/camchenry/sock.lua)** 的副本，
在 [ENet](http://enet.bespin.org/)（LÖVE 内置，可靠 UDP）之上包了一层**事件名 + 数据表**的接口：

```lua
client:send("playerMove", { x = 100, y = 200 })
-- 另一端
server:on("playerMove", function(data, client) ... end)
```

调用方不需要自行拆包、处理序列化，也不需要接触 `enet` 的 peer/channel 细节。

同目录下还有两个**序列化库**，`sock` 会挑一个用：

| 文件 | 说明 |
|---|---|
| `Scripts/Libraries/Network/bitser.lua` | sock 默认使用的那个（Robin Wellner 的 bitser） |
| `Scripts/Libraries/Network/binser.lua` | 另一个同名相近的库（Calvin Rose 的 binser），**sock 不会自动加载它** |

---

## 加载

```lua
local sock = ImportFile("Network.sock")
```

!!! bug "导入 enet 的那一句会泄漏一个全局变量"
    sock.lua 第 37 行写的是 `enet = require "enet"` —— **没有 `local`** 。
    加载之后 `_G.enet` 会被设置。这只是个命名空间污染，功能上无害，
    但其它位置也用 `enet` 这个名字时要注意冲突。

---

## 两个角色

| | 创建 | 每帧 | 发消息 |
|---|---|---|---|
| 服务端 | `sock.newServer(address, port, ...)` | `server:update()` | `sendToAll` / `sendToAllBut` / `sendToPeer` |
| 客户端 | `sock.newClient(address, port, ...)` | `client:update()` | `send` |

!!! example "`newServer`"
    `sock.newServer(address, port, maxPeers, maxChannels, inBandwidth, outBandwidth)`

    - `address` 绑定的地址，默认 `"localhost"` 。要接受局域网/外网连接必须传 `"*"` 。
    - `port` 端口，默认 `22122` 。
    - `maxPeers` 最多连几个人，默认 `64` 。
    - `maxChannels` 通道数，默认 **1** 。
    - `inBandwidth` / `outBandwidth` 带宽上限（字节/秒），默认 `0` = 不限。

!!! example "`newClient`"
    `sock.newClient(serverOrAddress, port, maxChannels)`

    - 常规用法：`sock.newClient("127.0.0.1", 22122)` 。
    - 第二种用法：传一个 **enet peer** ，直接把它当已有连接用（服务端内部就是这么造客户端对象的）。

!!! danger "两端的 `maxChannels` 必须一致"
    ENet 要求客户端与服务端的通道数相同。
    默认是 **1**，需要使用多通道时两端都得显式传同一个数值，否则连不上。

!!! warning "端口被占用会直接 `error()`"
    ```lua
    if not server.host then
        error("Failed to create the host. Is there another server running on :"..server.port.."?")
    end
    ```
    不是返回 `nil` 。需要按非错误方式处理时，用 `pcall` 包一层。

---

## 生命周期

```lua
-- 服务端
server = sock.newServer("*", 22122)
server:on("connect", function(data, client) print("有人连进来了") end)

-- 客户端
client = sock.newClient("127.0.0.1", 22122)
client:on("connect", function(data) print("连上了") end)
client:connect()          -- 真正连上要等几次 update

-- love.update 里（两端都要）
server:update()
client:update()
```

!!! warning "不调 `update()` 就什么都不会发生"
    `connect()` 只是发出连接请求，握手要靠后续的 `update()` 推进；
    收到的消息也只在 `update()` 里被分发。漏掉 `update()` 时，连接建立与消息分发都不会发生。

!!! warning "`update()` 在没有序列化器时会抛错"
    ```lua
    if not self.deserialize then
        error("Can't deserialize message: deserialize was not set")
    end
    ```
    只要 `bitser` 正常加载（默认如此）就不会触发。手动 `setSerialization` 时别只设一半。

---

## 事件

### 内置事件

| 事件名 | 触发时机 | 回调参数 |
|---|---|---|
| `connect` | 连接建立 | 服务端 `(data, client)` 、客户端 `(data)` ；`data` 是连接码数字 |
| `disconnect` | 断开 | 同上，`data` 是断开码数字 |

### 自定义事件

`on(事件名, 回调)` 注册；同名事件可以挂多个回调，按注册顺序依次执行。

```lua
-- 服务端：多一个 client 参数，代表"谁发来的"
server:on("chat", function(data, client)
    print(client:getConnectId(), "说:", data.text)
    server:sendToAll("chat", data)
end)

-- 客户端：只有 data
client:on("chat", function(data)
    print(data.text)
end)
```

- `removeCallback(callback)` 用注册时的返回值移除。
- 收到没有对应回调的事件时，只在 logger 里记一条 warning，不会报错。

---

## 发送数据

!!! example "服务端"
    - `sendToAll(event, data)` 广播给所有人。
    - `sendToAllBut(client, event, data)` 广播给除某人外的所有人。
        - 传的是 **sock 的 Client 对象**，内部用 `p ~= client.connection` 比对。
    - `sendToPeer(peer, event, data)` 只发给一个 enet peer（比如给刚连进来的人补发初始状态）。

!!! example "客户端"
    - `send(event, data)` 发给服务端。

```lua
-- 玩家移动：用不可靠模式，丢一两帧无所谓
client:setSendMode("unreliable")
client:send("move", { x = px, y = py })

-- 聊天：必须可靠
client:send("chat", { text = "hi" })   -- 默认 reliable
```

### 发送模式

| 模式 | 含义 | 用途 |
|---|---|---|
| `reliable` | 保证到达且按序（**默认**） | 聊天、状态同步、指令 |
| `unsequenced` | 保证到达，不保证顺序 | 不关心先后的可靠消息 |
| `unreliable` | 不保证到达 | 每帧位置、粒子 |

- `setSendMode(mode)` 只对**下一条**消息生效，发完自动还原。
- `setDefaultSendMode(mode)` 改默认值。
- 传了非法值时 `setSendMode` 打一条 warning 并退回 `reliable` ；`setDefaultSendMode` 直接 `error()` 。

### 通道

- `setSendChannel(n)` / `setDefaultSendChannel(n)` ，**从 0 开始**，最大 `maxChannels - 1` 。
- 超出范围会打 warning 并退回 0。

---

## Schema：省带宽

默认发送的是带键的表，键名也要占字节。两端约定好顺序后，可以只发数组：

```lua
-- 服务端（接收方）声明顺序
server:setSchema("move", { "x", "y", "vx", "vy" })

-- 客户端（发送方）只发数组
client:send("move", { 100, 200, -4.5, 23.1 })

-- 服务端回调里拿到的还是带键的表
server:on("move", function(data, client)
    print(data.x, data.y)
end)
```

!!! warning "Schema 要设在**接收方**上"
    转换发生在 `Listener:trigger` 里 —— 也就是**谁 `on` 这个事件，谁 `setSchema`** 。
    客户端发数组、就让服务端 `setSchema` ；服务端发数组、就让客户端 `setSchema` 。设反了没效果。

!!! note "两个方向要各设一次"
    服务端和客户端各有一个 `listener` ，互相独立。双向都用 schema 就两边都要设。

---

## 连接状态

```lua
if (client:isConnected())    then ... end   -- 已连接
if (client:isConnecting())   then ... end   -- 正在连（connect() 之后几帧内）
if (client:isDisconnecting())then ... end
if (client:isDisconnected()) then ... end
print(client:getState())                    -- 字符串
```

`getState()` 返回 `sock.CONNECTION_STATES` 里的一个：
`disconnected` / `connecting` / `acknowledging_connect` / `connection_pending` /
`connection_succeeded` / `connected` / `disconnect_later` / `disconnecting` /
`acknowledging_disconnect` / `zombie` / `unknown` 。

断开方式有三种：

| 方法 | 行为 |
|---|---|
| `disconnect(code)` | 正常断开 |
| `disconnectLater(code)` | 等队列里的包发完再断 |
| `disconnectNow(code)` | 立刻断 |
| `reset()` | 强制断，**服务端不会收到通知** |

!!! note "连接状态不是即时的"
    `connect()` 之后 `isConnected()` 还是 `false` ，要跑几次 `update()` 才会变 `true` 。
    同理断开也是延迟生效的。UI 上别拿它当"按钮点下去就变了"来用。

---

## 诊断与调优

!!! example "统计"
    - `getRoundTripTime()` 往返延迟（毫秒），连接稳定之后数值才准确。
    - `getTotalSentData()` / `getTotalReceivedData()` 累计字节数。
    - `getTotalSentPackets()` / `getTotalReceivedPackets()` 累计消息条数。
    - 服务端：`getClientCount()` / `getClients()` / `getClient(peer)` / `getClientByConnectId(id)` / `getClientByIndex(i)` 。

!!! example "调参"
    - `setPingInterval(ms)` ping 间隔，默认 500。
    - `setTimeout(limit, minimum, maximum)` 判定掉线的超时（默认 `32, 5000, 30000` ）。
    - `setThrottle(interval, acceleration, deceleration)` 不可靠包丢弃概率的调节。
    - `setBandwidthLimit(incoming, outgoing)` 带宽上限。
    - `setMessageTimeout(ms)` `update()` 里 `host:service()` 的等待毫秒数，默认 0（不阻塞）。
    - `enableCompression()` 开压缩，**两端必须都开或都不开**，且 lua-enet 没有关闭接口。

!!! example "日志"
    - `client.logger.printEventData = true` 打印所有收到的事件。
    - `logger.printErrors` / `printWarnings` 默认开着。
    - `logger.messages` 里存着所有完整日志行。
    - `client:log("error", "...")` 手动记一条。

---

## 一个能跑的最小例子

```lua
-- 服务端进程
local sock = ImportFile("Network.sock")
local server = sock.newServer("*", 22122)

server:setSchema("move", { "x", "y" })

server:on("connect", function(data, client)
    print("新玩家", client:getConnectId())
    server:sendToPeer(client.connection, "welcome", { id = client:getConnectId() })
end)

server:on("move", function(data, client)
    server:sendToAllBut(client, "move", { data.x, data.y })
end)

server:on("disconnect", function(data, client)
    print("玩家离开", client:getConnectId())
end)

function love.update(dt)
    server:update()
end
```

```lua
-- 客户端进程
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

## 注意事项汇总

!!! warning "ENet 是 UDP，没有内网穿透"
    sock 只负责收发，**不提供**打洞、房间匹配、中继服务器。
    需要让外网连入时，由开发者自行配置端口映射、云服务器，或接入 Steam 之类的平台网络。

!!! warning "bitser 不能序列化函数与 userdata"
    能发：表、数字、字符串、布尔、`nil` 。
    不能发：函数、`coroutine` 、 **`Image` / `Source` / `Canvas` 这类 LÖVE 对象（userdata）** 、带 metatable 但没注册过的类实例。
    传贴图/声音请在两端各自加载，只发文件名或索引。

!!! warning "服务端拿到的 Client 对象是不完整的"
    `Server:update` 里是 `sock.newClient(event.peer)` 造出来的，走的是"传 peer"那条分支——
    它的 `host` 字段是 `nil` 。所以对它调 `getSocketAddress()` / `getTotalSentData()` 这类依赖 `self.host` 的方法会报错。
    要用统计就调 `server` 自己的那些方法。

!!! warning "`sendToAllBut` 传的是 Client 不是 peer"
    内部比对的是 `p ~= client.connection` 。把 enet peer 传进去比对不上，结果等于 `sendToAll` 。

!!! note "默认地址是 `localhost`"
    `sock.newServer()` 不传地址的话只监听本机。做主机给别人连要写 `sock.newServer("*", 端口)` 。

!!! note "两个序列化库的区别"
    目录里 `bitser.lua` 和 `binser.lua` 是**两个不同的库**（作者不同、API 不同）。
    sock 只认 `bitser` ；`binser.lua` 未被引擎加载，需要使用时通过 `ImportFile("Network.binser")` 手动接入。

!!! note "消息是同步分发的"
    `update()` 里收到消息会**立刻**调用回调。回调里做重活会卡这一帧，
    也要小心在回调里调用会再次触发 `update()` 的代码（重入）。
