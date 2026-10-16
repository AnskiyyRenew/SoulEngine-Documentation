---
title: 输入与控制器
---

引擎将键盘、手柄与触屏统一为同一套输入接口。

输入库路径： `Scripts/Libraries/Controller/` （含 `Keyboard.lua` 、 `Joystick.lua` 、 `VirtualKeyboard.lua` 、 `Controller.lua` ）。

---

## 四个模块

| 模块 | 包装的硬件 | 全局名 |
|---|---|---|
| `Controller/Keyboard.lua` | 键盘 + 鼠标 + 触摸点 | `Keyboard` |
| `Controller/Joystick.lua` | 手柄 / 摇杆 | `Joystick` |
| `Controller/VirtualKeyboard.lua` | 屏幕上的虚拟按键 / 摇杆（手机） | `VirtualKeyboard` |
| `Controller/Controller.lua` | 把上面三者合成统一查询 | `Controller` |

每帧的更新顺序（写在 `love.update` 里，**顺序不能乱**）：先轮询手柄，再把手柄映射到键盘，最后统一结算键盘与虚拟键盘的状态。

```
Joystick.Update()  →  Controller.Update()  →  Keyboard.Update()  →  VirtualKeyboard.Update()
```

---

## 状态语义

所有设备的 `GetState` 共用同一套返回值：

| 值 | 含义 |
|---|---|
| `1` | **本帧刚按下** |
| `2` | 按住不动 |
| `-1` | **本帧刚松开** |
| `0` | 没按 |

判断本帧按下使用 `== 1` ，判断处于按住状态使用 `>= 1` 。

---

## 统一查询 `Controller`

游戏代码读取输入**一律通过 `Controller`** ，不直接读取 `Keyboard` ，否则手柄输入不会生效。

!!! example "常用接口"
    - `Controller.GetState(name)` 查询某个逻辑名的状态（ `0` / `1` / `2` / `-1` ）。
    - `Controller.IsDown(name)` 是否按住（即 `GetState(name) >= 1` ）。
    - `Controller.GetAxis(name)` 读手柄某根轴的模拟值（已过死区并重新归一化）。
    - `Controller.GetVector()` 返回 `(x, y)` 移动向量，左摇杆优先、回落到方向键。
    - `Controller.GetDevices()` 当前连接了哪些设备（键盘 / 手柄数量 / 虚拟键盘）。
    - `Controller.GetSource(name)` 返回该输入来自哪个设备（调试用）。
    - `Controller.AllowPlayerInput(bool)` 一次性开关所有设备的玩家输入。
    - `Controller.SetDeadzone(v)` 设置摇杆死区。
    - `Controller.SetMirrorEnabled(bool)` 开关手柄映射到键盘的桥接（默认开）。

!!! example "示例"

    ```lua
    if (Controller.GetState("confirm") == 1) then
        -- 本帧刚按下确认
    end

    local x, y = Controller.GetVector()
    ```

---

## 逻辑键位表

逻辑名与具体硬件解耦：键盘、手柄各绑一套，查询时只认逻辑名。

| 逻辑名 | 键盘 | 手柄 |
|---|---|---|
| `confirm` | `return` 、 `z` | `a` |
| `cancel` | `x` 、 `shift` | `b` |
| `menu` | `c` 、 `ctrl` | `start` 、 `y` 、 `back` |
| `shift` | `lshift` 、 `rshift` | `leftshoulder` 、 `rightshoulder` |
| `ctrl` | `lctrl` 、 `rctrl` | — |
| `alt` | `lalt` 、 `ralt` | — |
| `up` / `down` / `left` / `right` | 对应方向键 | 十字键 + 左摇杆 |
| `arrows` | `up` / `down` / `left` / `right` | 十字键 + 左摇杆 |
| `letter` | `a` ~ `z` | — |
| `number` | `0` ~ `9` | — |

!!! note "自定义绑定"
    新增逻辑名时，键盘与手柄各绑定一次：

    ```lua
    Keyboard.Bind("dash", "lshift", "rshift")
    Joystick.Bind("dash", "leftshoulder", "rightshoulder")
    ```

---

## 手柄轴与虚拟按键

手柄的模拟轴名： `leftx` / `lefty` / `rightx` / `righty` / `triggerleft` / `triggerright` 。

- 读轴值： `Controller.GetAxis("leftx")` 。
- 摇杆 / 扳机越过死区后，还会**同时**产生一组虚拟按钮名（如 `leftstickleft` 、 `triggerright` ），可像 `confirm` 一样查询。

死区默认 `0.15` ，可以用 `Controller.SetDeadzone(v)` 或配置项 `ControllerDeadzone` 调整。

---

## 触屏与虚拟键盘

手机上会自动启用屏幕虚拟按键（左下 8 向摇杆盘 + 右下 Z / X / C）。桌面环境测试时，使用 [初始化配置](./000_conf.md) 中的 `ControllerSimulation` ：

```lua
Global.SetVariable("ControllerSimulation", {
    virtualKeyboard = true,   -- 启用虚拟键盘，鼠标拖动 = 手指滑动
    joystick        = false,  -- 模拟已连接手柄
})
```

也可以在代码里手动开关： `VirtualKeyboard.SetEnabled(true)` 、 `VirtualKeyboard.SetVisible(false)` 、 `VirtualKeyboard.SetAlpha(0.4)` 。

---

## 相关配置

- `ControllerDeadzone` 手柄死区大小。
- `ControllerSimulation.virtualKeyboard` / `.joystick` 桌面输入模拟。

详见 [初始化配置 → 输入控制](./000_conf.md) 。
