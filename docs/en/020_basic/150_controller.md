---
title: Input and Controller
---

The engine unifies keyboard, gamepad, and touchscreen into a single input interface.

Input library path: `Scripts/Libraries/Controller/` (contains `Keyboard.lua`, `Joystick.lua`, `VirtualKeyboard.lua`, `Controller.lua`).

---

## Four Modules

| Module | Hardware wrapped | Global name |
|---|---|---|
| `Controller/Keyboard.lua` | Keyboard + mouse + touch point | `Keyboard` |
| `Controller/Joystick.lua` | Gamepad / joystick | `Joystick` |
| `Controller/VirtualKeyboard.lua` | On-screen virtual buttons / joystick (mobile) | `VirtualKeyboard` |
| `Controller/Controller.lua` | Merges the above three into a unified query | `Controller` |

The per-frame update order (written in `love.update`, **order must not be changed**): poll the gamepad first, then map the gamepad to the keyboard, then settle the keyboard and virtual keyboard states uniformly.

```
Joystick.Update()  →  Controller.Update()  →  Keyboard.Update()  →  VirtualKeyboard.Update()
```

---

## State Semantics

All devices' `GetState` share the same set of return values:

| Value | Meaning |
|---|---|
| `1` | **Just pressed this frame** |
| `2` | Held down |
| `-1` | **Just released this frame** |
| `0` | Not pressed |

So to check "pressed once" use `== 1`, and to check "is held" use `>= 1`.

---

## Unified Query `Controller`

Game code should **always read input through `Controller`**, not directly from `Keyboard` — otherwise the gamepad won't be picked up.

!!! example "Common interfaces"
    - `Controller.GetState(name)` query the state of a logical name (`0` / `1` / `2` / `-1`).
    - `Controller.IsDown(name)` whether it is held (i.e. `GetState(name) >= 1`).
    - `Controller.GetAxis(name)` read the analog value of a gamepad axis (deadzone-applied and re-normalized).
    - `Controller.GetVector()` returns the `(x, y)` movement vector, left stick preferred, falling back to the d-pad.
    - `Controller.GetDevices()` which devices are currently connected (keyboard / gamepad count / virtual keyboard).
    - `Controller.GetSource(name)` which device provided this input (for debugging).
    - `Controller.AllowPlayerInput(bool)` toggle all device player input at once.
    - `Controller.SetDeadzone(v)` set the joystick deadzone.
    - `Controller.SetMirrorEnabled(bool)` toggle the "gamepad mapped to keyboard" bridge (on by default).

!!! example "Example"

    ```lua
    if (Controller.GetState("confirm") == 1) then
        -- confirm was just pressed this frame
    end

    local x, y = Controller.GetVector()
    ```

---

## Logical Key Map

Logical names are decoupled from specific hardware: keyboard and gamepad each bind a set, and queries only recognize the logical name.

| Logical name | Keyboard | Gamepad |
|---|---|---|
| `confirm` | `return`, `z` | `a` |
| `cancel` | `x`, `shift` | `b` |
| `menu` | `c`, `ctrl` | `start`, `y`, `back` |
| `shift` | `lshift`, `rshift` | `leftshoulder`, `rightshoulder` |
| `ctrl` | `lctrl`, `rctrl` | — |
| `alt` | `lalt`, `ralt` | — |
| `up` / `down` / `left` / `right` | corresponding arrow keys | d-pad + left stick |
| `arrows` | `up` / `down` / `left` / `right` | d-pad + left stick |
| `letter` | `a` ~ `z` | — |
| `number` | `0` ~ `9` | — |

!!! note "Custom bindings"
    To add your own logical name, bind it once for keyboard and once for gamepad:

    ```lua
    Keyboard.Bind("dash", "lshift", "rshift")
    Joystick.Bind("dash", "leftshoulder", "rightshoulder")
    ```

---

## Gamepad Axes and Virtual Buttons

Gamepad analog axis names: `leftx` / `lefty` / `rightx` / `righty` / `triggerleft` / `triggerright`.

- Read an axis: `Controller.GetAxis("leftx")`.
- Once a stick / trigger crosses the deadzone, a set of virtual button names also emerges (e.g. `leftstickleft`, `triggerright`), which can be queried directly like `confirm`.

The default deadzone is `0.15`, adjustable via `Controller.SetDeadzone(v)` or the `ControllerDeadzone` config option.

---

## Touchscreen and Virtual Keyboard

On mobile, the on-screen virtual buttons open automatically (an 8-direction stick pad at bottom-left + Z / X / C at bottom-right). To test on desktop, use `ControllerSimulation` from [Initialization Configuration](./000_conf.md):

```lua
Global.SetVariable("ControllerSimulation", {
    virtualKeyboard = true,   -- open the virtual keyboard, mouse drag = finger swipe
    joystick        = false,  -- pretend a gamepad is plugged in
})
```

You can also toggle manually in code: `VirtualKeyboard.SetEnabled(true)`, `VirtualKeyboard.SetVisible(false)`, `VirtualKeyboard.SetAlpha(0.4)`.

---

## Related Configuration

- `ControllerDeadzone` gamepad deadzone size.
- `ControllerSimulation.virtualKeyboard` / `.joystick` desktop input simulation.

See [Initialization Configuration → Input Control](./000_conf.md).
