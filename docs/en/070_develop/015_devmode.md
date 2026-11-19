---
title: ❕️ Developer Mode (Wave Jump)
---

Playing every earlier turn to reach a late one is expensive. Developer mode adds a **wave picker** that jumps straight to any wave script, and can end the current enemy turn immediately.

**Development builds only**: with `_RELEASED = true` the module is never loaded by `main.lua`, so release builds do not contain the feature.

---

## Unlocking

Type `e`, `n`, `d` in order, in any scene (at most 1.5 s between keys, no Ctrl / Alt / Win held):

- the console prints `[DevMode] developer mode ON`;
- when a battle is loaded, the picker opens right away;
- typing `e` `n` `d` again locks developer mode and closes the panel.

!!! note "When the sequence is ignored"
    A text input field with focus (the name-entry scene, for example) keeps the sequence from matching, and so does a held modifier key.

---

## Panel controls

| Action | Key |
|---|---|
| Open / close the picker | `F10` |
| Close the picker | `Esc` |
| Move the cursor | `↑` `↓`, `PageUp` `PageDown`, `Home` `End` |
| Expand / collapse a folder | `→` `←`, or click it |
| Jump to the highlighted wave | `Enter` or `Space` |
| End the current enemy turn | `S` |
| Toggle invincible | `I` |
| Scroll the list | Mouse wheel |

Clicking anywhere on a row selects it. While the panel is open the current scene is paused (`scene.pausing`), so the enemy turn does not advance while the list is being browsed.

---

## What the list shows

The picker lists the wave scripts the engine can actually load, in resolution order:

- `Game/Waves/` (Game area, wins)
- `Scripts/Waves/` (engine defaults, fallback)

**A folder is a namespace.** `Game/Waves/bones/wave1.lua` is the wave `bones.wave1` — exactly the string an encounter puts in its `wave` field:

```lua
return {
    state = "ACTIONSELECT",
    wave  = "bones.wave1",   -- Game/Waves/bones/wave1.lua
}
```

The project's folder layout is therefore the tree in the panel; no registry or numbering is involved. Files whose name starts with `_` (`_template.lua` and the like) are not listed.

The wave playing right now is marked with `*` and highlighted; opening the panel expands its folder and puts the cursor on it.

---

## What a jump does

A jump never writes to `Battle._wave` directly. It goes through the same state transitions the normal flow uses, so nothing is left half torn down:

```
currently DEFENDING
  ↓ Battle.ChangeState("ACTIONSELECT")
  ├─ wave.EndWave() of the running wave (its bullets and objects are destroyed)
  ├─ that wave's module is dropped from the require cache
  ├─ Arenas.Clear(), the main arena restores to 565x130
  ↓ clearWaveModule(target)
  ↓ Battle.wave = target
  ↓ Battle.ChangeState("DEFENDING")
  └─ Battle.Defending(): LoadWave re-runs the target file's top-level code
```

Two details matter:

- **The module cache is dropped**, so jumping to a wave that already played re-runs its top-level code; closures and state are never carried over from the previous visit.
- `ENDED` on the shared `Battle.Waves` table is reset. Left at `true`, the next wave would end the moment it starts.

`S` (end the current turn) takes the same path: `EndWave()`, then back to `ACTIONSELECT`.

---

## Invincible

`I` toggles invincible. While on, `Player.Hurt` returns at the entry point, so **a lethal hit is not applied at all** — healing the damage back a frame later would be too late. `Player.AddKR` is not intercepted: KR still accumulates, but HP never reaches zero.

---

## Script API

The panel is a thin front end for two engine methods, callable from a hack or a test scene:

!!! example "Debug methods"
    - `Battle.DebugJumpWave(wave_name)` loads the wave and enters `DEFENDING` immediately. Returns `ok, error_message`.
    - `Battle.DebugEndWave()` ends the current enemy turn immediately, as if the wave had called `EndWave()`. Returns a boolean.

Both return `false` in a release build and have no side effects there.

---

## How the battle state is decided

The panel only opens by itself inside a battle, and jumping only works inside one. Two separate questions are answered here.

**Whether a battle is running** requires both:

- `Battle.game` and `Battle.game.enemies` exist, i.e. the encounter has called `SetGame`;
- the scene name contains `battle` (case-insensitive), **or** `Battle.TIME_F` changed since the previous frame.

The second condition covers battle scenes with a custom name. `Battle.TIME_F` is only incremented inside `Battle.Update`, and only a battle scene drives that function, so a change means a battle is running.

`Battle` is a global table that outlives the scene and keeps the previous `game`, so its existence alone proves nothing.

**Whether the debug entry points are available** is checked separately, by testing `Battle.DebugJumpWave` and `Battle.DebugEndWave` for a function. The two are kept apart because the first is a run-time state question and the second is an engine-version question; a message about one must not send the reader to the other's file.

!!! note "While the panel is open"
    Opening the panel pauses the scene, so `Battle.TIME_F` stops advancing. The previous frame's verdict is kept, which is what allows a jump while the panel is open.

---

## Porting to another project

The feature has two parts:

| Location | Role |
|---|---|
| `Scripts/Libraries/Engine/DevMode.lua` | The panel and the key sequence |
| `DebugJumpWave` / `DebugEndWave` in `Scripts/Libraries/Battle/init.lua` | Performing the jump and ending a turn |

`main.lua` loads `Engine.DevMode` inside its `_RELEASED = false` branch and hooks it into `update`, `draw`, `keypressed`, the mouse callbacks and `wheelmoved`.

Copying `DevMode.lua` alone onto an older `Battle` still opens the panel and lists the tree, but jumping and ending a turn are refused, and the console and panel footer say why:

```
[DevMode] 此项目的 Battle 缺少 DebugJumpWave，需同步 Battle/init.lua
```

Adding the two methods to that project's `Battle/init.lua` resolves it. They depend only on `clearWaveModule`, `ChangeState`, `narration_text`, `restoring_arena` and `waveModule` from the same file, and on nothing else.

---

## Known limitations

- **Jumping from `ATTACKING`** does not abort an attack that is already running: the attack pattern keeps its own typer until the next entry into `ATTACKING` restarts it. Wave testing normally happens in `ACTIONSELECT` or `DEFENDING`, where this cannot occur.
- **Outside a battle** the panel still opens and the tree can be browsed, but jumping and ending a turn are refused (the console and the panel footer say so).
- The panel lists **files**, not which wave an encounter actually references. Whether a turn is reached in normal play still depends on the encounter's `wave` field and what the scene assigns.
- The panel shares the `determination_mono.ttf` / `simsun.ttc` 13 px fonts used for in-battle small text, so it scales down with the window like the rest of the UI.
