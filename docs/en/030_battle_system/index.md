---
title: Battle System
---

It wouldn't be an exaggeration to call this `SoulEngine`'s most complex module. Here you'll see...

Battle UI Player PlayerAttacks Game Wave Animation — all these libraries working together.

> These modules are not standalone libraries, but rather tightly-coupled responsibility layers within the battle system. They cooperate closely through battle state and turn flow. They're separated only to make each part easier to locate and modify, not so they can run independently.

> The `Game area` concept and resource lookup order that recur throughout this topic are explained in one place: **[Basic Development → Game Area & Resource Override](../020_basic/110_game_area.md)**.

First, the flow:
```
Enter battle
  ↓
Game provides encounter data
  ↓
Wave initializes the wave
  ↓
UI enters battle state (stateinner)
  ↓
Player receives input → PlayerAttacks resolves
  ↓
Animation plays visuals
  ↓
Wave advances the turn
  ↓
UI updates state / checks for end
  ↓
(loop back to Player or exit)
```

---

---

## Pages in This Topic

| Page | Content |
|---|---|
| [Battle Initialization](./000_init.md) | Battle scene layers, encounter files, enemy animations |
| [UI](./010_ui.md) | The interface under the battle box, buttons, the state hub |
| [Battle Box](./020_arena.md) | Arena creation, scaling, hole-punching, masking |
| [Player & Souls](./030_player.md) | Player data, the four souls, one-way platforms |
| [Attack Modes](./040_attack.md) | Calibration bar, damage formula, custom weapons |
| [Wave Scripts](./050_waves.md) | How to write enemy turns |
| [Bullet Library](./060_bullets.md) | Bones, bone walls, 3D skeletons, tracking blasters |
| [Battle Scene & Callbacks](./070_scene.md) | Scene skeleton, callback overview, flow control |

---

## Game

Responsible for customizing encounter data and enemies.

Encounter path: `Game/Encounter/`.

Game area path: `Game/` (the root directory containing `Animations`, `Encounter`, `Waves`, `Souls`, etc.).

---

## Monster Animation

Responsible for playing enemy animations.

Path: `Game/Animations/`.

---

## UI

Path: `Scripts/Libraries/Battle/UI/`.

All other visible content on screen is directed through the `UI` library; the most representative is the `stateinner.lua` library, which handles everything from entering battle at the start, through various options, enemy turns, and ending the game.

Details beyond `stateinner` will be covered later in [UI](./010_ui.md).

---

## Player

Path: `Scripts/Libraries/Battle/Player/`.

Player's standalone soul path: `Game/Souls/` (Game area, takes priority), `Scripts/Libraries/Battle/Player/Souls/` (engine default, fallback).

Player attack path: `Game/Attacks/` (Game area, takes priority), `Scripts/Libraries/Battle/PlayerAttacks/` (engine default, fallback).

---

## Turns

Responsible for enemy turns.

Path: `Game/Waves/` (Game area, takes priority), `Scripts/Waves/` (engine default, fallback).

Following the engine's convention of "`Game` first, main directory as fallback": it first looks for a same-named wave in `Game/Waves/`; if found, it's used directly. Only if not found does it fall back to `Scripts/Waves/`, and a warning is printed to the console.

Bullet library path: `Scripts/Libraries/Attacks/`.
