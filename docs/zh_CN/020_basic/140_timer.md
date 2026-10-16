---
title: 计时器
---

计时器用于在指定的帧数或秒数之后执行代码。

计时器库路径： `Scripts/Libraries/Timer.lua`

!!! warning "需要手动接线"
    和节拍库一样，本仓库的 `main.lua` **没有**加载 `Timer` ，也**不会**每帧调用它的 `Update` 。<br>
    使用前需先获取模块，并每帧调用 `Update` ：

    ```lua
    local timers = ImportFile("Timer")   -- 等价于 require("Scripts.Libraries.Timer")
    ```

---

## 两种时间单位

计时器分成两族，区别只有一个：按 **帧** 数还是按 **秒** 数计时。

| 作用 | 按帧 | 按秒 |
|---|---|---|
| 每隔一段时间执行 | `runFrame` | `runSecond` |
| 延迟后持续执行 | `duringFrame` | `duringSecond` |

按帧的版本每次 `Update` 把内部计数 `+1` ，所以间隔写 `60` 表示每 60 帧；按秒的版本累加 `dt` ，写 `1.5` 表示每 1.5 秒。

---

## 每隔一段时间执行：`runFrame` / `runSecond`

```lua
timers.runFrame(func, interval, count)
timers.runSecond(func, interval, count)
```

- `func` 到点执行的回调。
- `interval` 间隔。`runFrame` 单位是**帧**（默认 `60` ），`runSecond` 单位是**秒**（默认 `1.0` ）。
- `count` 一共执行多少次（默认 `1` ）。

!!! example "示例"

    ```lua
    -- 每 30 帧触发一次，共 4 次
    timers.runFrame(function()
        print("tick")
    end, 30, 4)

    -- 每 0.5 秒触发一次，共 3 次
    timers.runSecond(function()
        print("half second")
    end, 0.5, 3)
    ```

---

## 延迟后持续执行：`duringFrame` / `duringSecond`

```lua
timers.duringFrame(func, delay, during, afterfunc)
timers.duringSecond(func, delay, during, afterfunc)
```

先等 `delay` 个（帧 / 秒），然后在接下来的 `during` 个（帧 / 秒）里**每帧**执行 `func` ，整段结束后再调用一次 `afterfunc`（可省略）。

- `delay` 延迟，默认 `0` 。
- `during` 持续时长，默认 `1` 。
- `afterfunc` 结束回调，可不填。

!!! example "示例"

    ```lua
    -- 等 1 秒后，持续 2 秒每帧执行，最后收尾
    timers.duringSecond(function()
        -- 每帧执行
    end, 1, 2, function()
        -- 结束回调
    end)
    ```

---

## 每帧推进 `Update`

```lua
function scene.update(dt)
    timers.Update(dt)
end
```

---

## 返回的计时器对象

上面四个函数都会返回一个计时器对象，可以中途控制它：

!!! example "计时器字段与方法"
    - `t.time` 当前累计（帧或秒）。
    - `t.count` 已经触发过几次。
    - `t.running` 是否在跑（暂停时为 `false` ）。
    - `t.active` 是否还活着（为 `false` 时会在下一次 `Update` 被回收）。
    - `t:pause()` / `t:unpause()` / `t:togglePause()` 暂停 / 恢复 / 切换。
    - `t:isPaused()` 是否处于暂停。
    - `t:stop()` 直接停掉并回收。
    - `t:restart()` 归零重来（时间与计数都回到起点）。

```lua
local t = timers.runSecond(function()
    print("loop")
end, 1, 999)

t:pause()     -- 先别跑
t:unpause()   -- 继续
```

---

## 注意事项

- **必须每帧调用 `Update`**：不调用时计时器不会推进。
- **按帧的版本与帧率相关**：`runFrame` 的帧由 `Update` 的调用频次决定，掉帧或更换设备时计时间隔会随之变化；需要固定的时间间隔时使用 `runSecond` 。
- **自动回收**：`runFrame` / `runSecond` 触发满 `count` 次后自行结束；`during*` 在持续段跑完后结束。结束后会在下一次 `Update` 被移除。
