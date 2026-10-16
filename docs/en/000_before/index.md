---
title: Before You Start
---

Before using `SoulEngine`, figure out what you actually need —<br>
I'm not going to ask you grand questions like "why make a game", but rather practical needs:

---

## Which One Are You

!!! tip "Guide for Different Roles"
    If you are a <u>translator</u>, after finishing [Environment Setup](./000_download.md) (the game needs to run on SoulEngine), you can jump straight to the [Localization](../080_l10n/index.md) topic to start translating.

    If you are a <u>user learning game development</u>, please follow the recommended path below, or browse as needed.

    If you are a <u>member working on the Overworld</u>, after installation jump to the [Overworld Main World System](../040_overworld/index.md) topic for the relevant docs.

    If you are just <u>curious</u>, wanting to borrow ideas or simply browse the docs, feel free to look around.

---

## What's in This Documentation

Listed by topic, with a one-line description of each, so you can jump as needed.

| Topic | Content |
|---|---|
| **Before You Start** (this topic) | Environment setup, pre-development prep, Lua crash course |
| [**Quick Start**](../010_quick_start/index.md) | A step-by-step guide from "just downloaded" to "made your first battle / first map" |
| [**Basic Development**](../020_basic/index.md) | Config, scenes, sprites, typewriter, layers, audio, global variables, screen, masks, borders, Tween, the Game area, game logic |
| [**Battle System**](../030_battle_system/index.md) | Battle init, battle box, player and souls, attacks, enemy turns, bullet patterns, battle scenes |
| [**Overworld Main World System**](../040_overworld/index.md) | Maps, STI and tilesets, characters, interaction and dialogue, menus, encounters, shops |
| [**Intermediate Development**](../050_intermediate/index.md) | JSON library, ShaderToy, shaders, collision library, math tutorial |
| [**Working with LÖVE**](../060_with_love/index.md) | Using the native LÖVE API directly 🚧 |
| [**Developer Tools**](../070_develop/index.md) | Tool scenes and dev assistance 🚧 |
| [**Localization**](../080_l10n/index.md) | Where language files go, looking up and replacing text |
| [**Networking**](../090_network/index.md) | GameJolt, Discord Rich Presence, sock multiplayer |
| [**Export & Release**](../100_export/index.md) | Packaging into exe / APK / web, plus a pre-release checklist |

!!! note "Icon Meanings"
    The `🔧` / `❕️` / `🚧` before a page title mean "requires extra software", "updated since last version", and "topic under construction", respectively.<br>
    Full explanation is on the [Home page](../index.md).

---

## Recommended Path

**Don't start by flipping open the `Basic Development` manual pages** — those are for reference. Reading them cover-to-cover from the start is inefficient.

If you're unsure where to begin, follow this order:

1. [Environment Setup](./000_download.md) — install LÖVE and the engine so you can open the project in an editor.
2. [Before Development](./010_getready.md) — check the hardware, system, and math prerequisites so you know what to expect.
3. [Lua Tutorial](./020_lua.md) — **must-read** if you've never written Lua; the pitfalls won't stick until you hit them once.
4. [**Quick Start**](../010_quick_start/index.md) — start actually building here; it tells you what to do at each step.

After that, browse as needed: for battles go to [Battle System](../030_battle_system/index.md), for maps and NPCs go to [Overworld](../040_overworld/index.md), and for complex math or shaders go to [Intermediate Development](../050_intermediate/index.md).

When your game is done and you want to ship it, see [Export & Release](../100_export/index.md).

---

***If you're ready to install, head to the next page.***
