---
title: 节拍
---

节拍库用于将游戏事件与音乐节拍对齐。

节拍库路径： `Scripts/Libraries/Beat.lua`

!!! warning "这是一个需要手动接线的独立库"
    `main.lua` **不会**自动加载 `Beat` ，也**不会**替它每帧调用 `Update` 。<br>
    使用该库时，需先获取模块，再每帧调用 `Update` ：

    ```lua
    local beats = ImportFile("Beat")   -- 等价于 require("Scripts.Libraries.Beat")
    ```

---

## 基本概念

音乐的时间轴用 **BPM（每分钟多少拍）** 来衡量：

- `beats.beat` 是从 `0` 开始、随 `Update` 不断增大的当前拍数累加器。
- 1 拍 = `60 / BPM` 秒。`120 BPM` 时 1 拍是 `0.5` 秒，`180 BPM` 时是 `1/3` 秒。
- 整数拍即第 1 拍、第 2 拍，小数拍（如 `2.5`）表示半拍。

---

## 常用接口

### 设置速度 `SetBPM(bpm)`

```lua
beats.SetBPM(180)   -- 不填或填 nil 时回落到 120
```

### 每帧推进 `Update(dt)`

**必须每帧调用一次**，它负责累加 `beats.beat`，并检查所有登记过的事件是否该触发。放在场景的 `scene.update` 里即可：

```lua
function scene.update(dt)
    beats.Update(dt)
end
```

### 到拍触发回调 `CreateEvent(target, call, offset)`

在第 `target` 拍执行一次 `call`，**触发后自动移除**（一次性的）。

- `target` 目标拍，支持小数。
- `call` 到拍时执行的回调函数。
- `offset` 额外偏移，单位**毫秒**，正数表示往后推。不填时取模块级默认值 `beats.offset`（默认 `0`）。

```lua
beats.CreateEvent(4, function()
    print("第 4 拍")
end)

-- 第 4 拍再往后 200 毫秒
beats.CreateEvent(4, function()
    print("第 4 拍 +200ms")
end, 200)
```

### 到拍判断 `OnBeat(target)`

!!! danger "当前实现无法命中，不要用于到拍判断"
    `OnBeat` 内部是浮点**精确相等**判断（`beats.beat == target`），而 `beats.beat` 是逐帧累加的浮点数，**几乎不可能正好命中**。<br>
    实测：在 `60 / 30 / 144 FPS` 下各跑 600 帧，命中次数全部为 `0` 。<br>
    需要在某一拍执行逻辑时，改用 `CreateEvent` 。

---

## 完整示例

`event.lua` 中在某一拍执行一批事件的写法，接线后如下：

```lua
local beats = ImportFile("Beat")

function scene.load()
    beats.SetBPM(120)

    -- 第 1 拍：一批事件同时触发
    beats.CreateEvent(1, function()
        EventU1()
        EventU2()
        EventU3()
        EventU5()
    end)

    -- 第 2、2.5、3、3.5、4 拍：各触发一次
    for b = 2, 4, 0.5 do
        beats.CreateEvent(b, Event2)
    end
end

function scene.update(dt)
    beats.Update(dt)
end
```

---

## 注意事项

- **一次性**：`CreateEvent` 登记的事件触发后立刻从内部表中移除。重复触发需重新登记。
- **状态不会自动归零**：`beats.beat` 是模块内的累加器；切歌、重开场景时需将 `beats.beat` 复位为 `0` ，并按需重设 BPM。
- **`offset` 随 BPM 换算**：偏移量在触发判断时按**当前** BPM 换算成拍，所以中途改 BPM 会同时影响还没触发的事件偏移。
