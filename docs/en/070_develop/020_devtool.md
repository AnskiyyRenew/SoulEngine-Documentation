---
title: Variable Debugger
---

`DevTool` is the engine's **runtime variable debugger**. Pressing `F8` pops up a separate tool window with two tabs:

- **Tree (variable tree)**: Expand the objects in the engine's memory level by level, and view and edit them directly.
- **Console**: A sandboxed REPL where you can run expressions and assignment statements against the engine's global variables.

It differs in responsibility from the [Object Debugger](./010_debugger.md): the object debugger handles **sprites on screen**, while the variable debugger handles **any table / field value**.

Library path: `Scripts/Libraries/Engine/DevTool.lua`

!!! warning "Development build only"
    Like the object debugger, `DevTool` is loaded only when `_RELEASED` is `false` (see `conf.lua`, imported by `main.lua`, which calls `Update` / `Draw`). In the release build, `F8` opens nothing.

!!! note "Depends on SDL3"
    `DevTool` relies on `Scripts/Libraries/Utils/Windows.lua` to create a child window, which requires **LÖVE 12 (ships with SDL3)**. If that library is unavailable, it prints `[DevTool] Windows.lua / SDL3 not available.` to the terminal and disables itself, without affecting the game itself.

---

## Opening and closing

| Key | Action |
| --- | --- |
| `F8` | Open / close the tool window |

The window **stays closed until you first press `F8`**. You can also call `DevTool.Toggle()` directly in code for the same effect.

The top-right of the title bar shows a `KF:YES` / `KF:NO` indicator, meaning whether this child window currently has system keyboard focus (see "The keyboard-input pitfall" below).

---

## Tab: Variable tree

You land on the Tree tab by default. At the top is a **quick-edit bar**, below it the variable-tree list. The top level of the tree is fixed to these root nodes:

| Root node | Content |
| --- | --- |
| `Player` | The Player object |
| `Battle` | The Battle system |
| `Overworld` | The Overworld system |
| `Scenes.current` | The current Scene |
| `Global (config)` | Global configuration |
| `_G (all globals)` | All global variables |

These are **live-read** references; after a scene switch or when an object is replaced, they automatically re-point, with no manual refresh needed.

### Operations on the tree

- **Expand / collapse**: Click a table node's arrow or the node itself. A table node shows its child count, like `table(12)`.
- **Edit number / string**: Click such a leaf node to enter inline edit; press `Enter` when done to write back to real memory.
- **Toggle boolean**: Click a boolean leaf node to negate it directly.
- **Rebuild children**: Select a table node and press `R` to drop the cache and re-scan its children, used to refresh dynamically added/removed containers.

!!! tip "Cyclic references and functions"
    The tree automatically skips function fields and detects cyclic references (self-reference or mutual reference), avoiding infinite recursive expansion.

### Quick-edit bar

The two top inputs `path` / `value` read and write directly by path, handy for quickly changing a deeply nested field:

- Fill a path in `path`, e.g. `Player.hp`, and press `Enter` to read the current value into the `value` box.
- Fill a new value in `value`, and press `Enter` to write it back.
- Press `Tab` to switch between the two inputs, `Esc` to exit input.

Paths support dots and brackets, e.g. `Player.hp`, `Battle.enemies[1].hp`.

---

## Tab: Console

The Console tab is a **sandboxed REPL**; type a line and press `Enter` to execute:

- It first tries to evaluate as an **expression**; on success it prints the return value with an `=` prefix, e.g. typing `1 + 2` echoes `= 3`.
- If the expression doesn't hold, it is then executed as a **statement**, e.g. `Player.hp = 999`.

Available global variables: `Player`, `Battle`, `Overworld`, `Scenes`, `Global`, `_G`.

!!! note "The sandbox is mounted read-only and won't pollute globals"
    The console reads the engine globals via `__index = _G`; **statements write to those tables in the engine itself** (so `Player.hp = 999` really does change the Player), but the sandbox environment itself won't stuff new global variables into `_G`.

Calling `print(...)` inside this sandbox is also **redirected to the console** rather than the terminal, handy for inserting debug output.

Scroll the wheel to review past output; press `Esc` to clear the current input.

---

## Hotkey quick reference

| Location | Key | Action |
| --- | --- | --- |
| Global | `F8` | Open / close the tool window |
| Tabs | Click the title bar, or press `T` / `C` | Switch to Tree / Console |
| Quick-edit bar | `Enter` | Read value in path box, write value in value box |
| Quick-edit bar | `Tab` | Switch between path / value boxes |
| Quick-edit bar | `Esc` | Exit input |
| Tree | `R` | Rebuild the selected node's children |
| Tree | Click number / string | Inline edit, `Enter` applies |
| Tree | Click boolean | Negate directly |
| Console | `Enter` | Execute |
| Console | `Esc` | Clear input |

---

## The keyboard-input pitfall

This tool window is implemented with an SDL child window, but in the current LÖVE build, **SDL child-window keyboard events are unreliable** (you don't get key presses even when the window has focus). So the engine does this instead:

- Key presses in the main window's `love.keypressed` are **forwarded** to `DevTool.HandleKey`, which handles character input and hotkeys uniformly;
- Forwarding happens only when the tool window **has focus**, or **the mouse is hovering over the tool window** (decided by `DevTool.WantsKeys()`);
- While forwarding, **the game scene still receives these keys** as usual, so using the tool and playing the game don't steal input from each other.

When you click into the tool window, it tries to request keyboard focus from the system — that's where the title-bar `KF:YES` / `KF:NO` indicator comes from. If focus can never be obtained, just **move the mouse over the tool window** and input works normally too.
