---
title: ❕️ Bundled Assets
---

The engine's `Resources/` folder plays two roles at once: part of it is **defaults the engine itself reads** (fonts, the battle UI skeleton, a couple dozen sounds), and part of it is **an asset library for authors to pick from** (thousands of sprites, hundreds of sounds).

This page lists which bundled assets are actually in use and where. Read it before renaming, replacing, or cleaning anything — or when you want to know where a sound comes from.

---

## Overview

| Folder | Files | Referenced by engine | Role |
|---|---:|---:|---|
| `Resources/Fonts/` | 21 | 8 | Fonts. Two workhorses (Latin + CJK) carry all text; six more cover specific slots |
| `Resources/Sounds/` | 271 | ~20 | Sounds. Mostly a library; what actually plays is battle UI and player feedback |
| `Resources/Music/` | 9 | 3 | Music. Only the intro, the ending and GAME OVER are hard-coded |
| `Resources/Sprites/` | 5384 | ~75 | Sprites. Mostly a library; what is used is the UI skeleton and the main character |
| `Resources/Libs/` | 4 groups | on demand | Native libraries: `https.dll`, Discord RPC, the secret store |

!!! note "How these numbers were produced"
    "Referenced" means a **string-literal scan** over `Scripts/`, `Game/`, `Maps/` and the root `main.lua` / `conf.lua`.

    - Paths assembled at runtime (animation frame numbers, music fields in map data) cannot be seen this way, so **actual usage may be slightly higher**.
    - Being referenced does not guarantee it plays: `snd_pierce.wav`, for example, is not shipped here, so the impact frame falls back to two other files.

---

## Overriding: the Game area wins

`Game/Resources/` is the per-game resource root, and a file there **takes precedence** over the engine copy of the same name:

| Engine default | Game override |
|---|---|
| `Resources/Fonts/x.ttf` | `Game/Resources/Fonts/x.ttf` |
| `Resources/Sounds/x.wav` | `Game/Resources/Sounds/x.wav` |
| `Resources/Music/x.ogg` | `Game/Resources/Music/x.ogg` |
| `Resources/Sprites/...` | `Game/Resources/Sprites/...` |

So **you never need to touch `Resources/` to replace a default font or sound** — drop a same-named file into `Game/Resources/`. Resolution rules are in [Audio](../020_basic/050_audio.md) and [Game Area](../020_basic/110_game_area.md).

!!! warning "Do not delete files from Resources/"
    "Not referenced" here means the engine does not load it by default, not that nobody wants it. These are author-facing assets; before pruning, check that nothing under `Game/` points at them.

---

## Fonts: 21 shipped, 8 in use

!!! example "Two workhorses"
    - **Latin**: `determination_mono.ttf` at size **27** (dialogue / titles) or **13** (body text / debug panels).
    - **CJK**: `simsun.ttc` at size **13 only**; use `scale = 2` when you want the 27 px look.

    InstText's bondfont combines the two and switches per byte, so mixed Latin/CJK text needs no manual font handling. See [Typers](../020_basic/030_typers.md) and [GUI](../020_basic/160_gui.md).

### In use

| Font | Where | Size | Referenced by |
|---|---|---|---|
| `determination_mono.ttf` | Default Latin font of all four Typers (etext / ntext / stext / insttext); the GUI library; DevTool / Debugger panels; naming, locked, logo and TweenEase scenes | 27 / 13 / 9 depending on site | `Scripts/Libraries/Typers/`, `GUI/primitives.lua`, `Engine/DevTool.lua`, several `Scripts/Scenes/` |
| `simsun.ttc` | CJK half of the Typers and battle UI; virtual keyboard CJK keys | 13 (27 via `scale = 2`) | same as above plus `Controller/VirtualKeyboard.lua` |
| `Mars Needs Cunnilingus.ttf` | Battle bottom bar text: name, `LV`, HP numbers | 24 (monospace, 1 char = 15 px) | `Scripts/Libraries/Battle/UI/init.lua` |
| `8bit-wonder.TTF` | The small `HP` / `KR` labels in that bar | 12 | `Scripts/Libraries/Battle/UI/init.lua` |
| `DAMAGEBACK.TTF` | **Black outline layer** of bouncing text (damage numbers, MISS) | 32 | `Scripts/Libraries/Battle/UI/init.lua` |
| `Hachicro.ttf` | **Colored top layer** of the same text (damage = red, MISS = white), stacked over the black copy | 32 | `Scripts/Libraries/Battle/UI/init.lua` |
| `Crypt Of Tomorrow.ttf` | Overworld shop text pointer and the STAT page | set by the caller | `Overworld/shop.lua`, `Overworld/stat.lua` |
| `Wingdings.ttf` | Only as a `[font:Wingdings.ttf]` tag in a sample line and the test scene | inherits current size | `Scenes/Overworld/scene_ow_main_0.lua`, `Scenes/TEST/scene_wingdings.lua` |

`conf.lua` also builds LÖVE's own default font (13 / 20) from `determination_mono.ttf` — that is what the **error screen and console** use.

### Spare (not wired up)

Shipped but referenced by no code, free to use:

`Buttons.otf`, `Comic Sans.ttf`, `Determination.otf`, `MonsterFriend.otf`, `MonsterFriendFore.otf`, `Papyrus.ttf`, `speechbubble.ttf`, `undertale-wingdings.ttf`, `unifont_jp.otf`, `方正像素12.ttf`, `方正卡通简体.ttf`, `方正基础像素体.ttf`, `方正少儿简体.ttf`

!!! tip "Swapping in your own font"
    Three options, cheapest first:

    1. Per line: write `[font:your.ttf]` inside the text (affects everything after it).
    2. Global default: put a same-named file in `Game/Resources/Fonts/` to override `determination_mono.ttf` / `simsun.ttc`.
    3. From code: `Fonts.New("name.ttf", size, "mono")`, or set `bondfont` on an InstText.

---

## Sounds: 271 shipped, ~20 in use

### Battle Menu and UI

| File | When it plays | Referenced by |
|---|---|---|
| `snd_menu_0.wav` | Moving the cursor between battle buttons and menu actions (by far the busiest one, twenty-plus call sites) | `Battle/UI/buttons.lua`, `Battle/UI/stateinner.lua`, `Overworld/shop.lua` |
| `snd_menu_1.wav` | Confirm / back style actions in the battle menu; shop confirm | `Battle/UI/stateinner.lua`, `Overworld/shop.lua` |

### Player and Soul

| File | When it plays | Referenced by |
|---|---|---|
| `snd_ding.wav` | Soul switched or a new soul added (when `use_sound` is set) | `Battle/Player/init.lua` |
| `snd_heal.wav` | Healing (`Player.Heal` with a positive amount; overworld heal spots) | `Battle/Player/init.lua`, `Overworld/init.lua` |
| `snd_phurt.wav` | Player hurt (`Player.Hurt` with a positive amount); blue soul impact | `Battle/Player/init.lua`, `Battle/Player/Souls/blue.lua`, `Battle/UI/stateinner.lua` |
| `snd_slam.wav` | Blue soul slam | `Battle/Player/Souls/blue.lua` (and the `Game/Souls/blue.lua` copy) |
| `snd_shoot.wav` | Yellow soul shot | `Battle/Player/Souls/yellow.lua` |
| `snd_heartbreak_0.wav` | GAME OVER heart break, first half | `Scripts/Scenes/scene_gameover.lua` |
| `snd_heartbreak_1.wav` | GAME OVER heart break, second half | `Scripts/Scenes/scene_gameover.lua` |

### Player Attacks

| File | When it plays | Referenced by |
|---|---|---|
| `snd_slice.wav` | Swing startup | `Battle/PlayerAttacks/stick.lua` |
| `snd_damage.wav` | Hit landed on the enemy | `Battle/PlayerAttacks/stick.lua` |

### Enemy Attacks

| File | When it plays | Referenced by |
|---|---|---|
| `snd_warning_0.wav` | Bone attack warning flash (two alternating beeps: red / yellow) | `Attacks/Bones.lua` |
| `snd_warning_1.wav` | The other beep of that pair | `Attacks/Bones.lua` |
| `snd_spearappear.wav` | Stand-in for `snd_pierce.wav`, which this project does not ship — the impact frame falls back here | `Attacks/Bones.lua` |
| `snd_lazer.wav` | Second entry in that fallback list | `Attacks/Bones.lua` |
| `Blaster/snd_intro.wav` | Blaster spawn / charge | `Attacks/Blasters.lua` (path resolved via `sounds_path`) |
| `Blaster/snd_fire.wav` | Blaster fires | `Attacks/Blasters.lua` |

### Overworld and Scenes

| File | When it plays | Referenced by |
|---|---|---|
| `snd_encounter.wav` | Encounter triggered | `Overworld/init.lua` |
| `snd_encounter_fall.wav` | The fall in the encounter transition | `Overworld/init.lua` |
| `snd_tong.wav` | A beat inside that transition | `Overworld/init.lua` |
| `snd_save.wav` | Save succeeded | `Overworld/Pages/save.lua` |
| `snd_buyitem.wav` | Shop purchase | `Overworld/shop.lua` |
| `snd_flee.wav` | Fleeing / wrapping up a battle (all three battle scene templates) | `Scripts/Scenes/Battle/` init / ow / template |
| `snd_dust.wav` | A sprite spawns dust particles | `Sprites.lua` |
| `snd_intro.ogg` | Boot logo scene | `Scripts/Scenes/scene_logo.lua` |

### Typer voices

| File | When it plays | Referenced by |
|---|---|---|
| `Voices/v_monster.wav` | The **default** typing voice: picked at random per character | `Typers/etext.lua`, `Typers/ntext.lua`, `Typers/stext.lua` |

The other 40 voices (`v_sans.wav`, `v_papyrus.wav`, `v_flowey.wav`, …) all work — nothing points at them by default. Select one with the `[voice:xxx]` tag or `setVoices({...})`.

### Subfolders

| Folder | Contents | Status |
|---|---|---|
| `Sounds/Blaster/` | 3 blaster-specific clips. The library first tries `Blaster/<style>/snd_intro.wav`, then falls back to the flat `Blaster/` layout | 2 in use, `snd_intro_2.wav` idle |
| `Sounds/Soul Library Sounds/` | 5 clips, three sharing names with the root folder (`snd_ding`, `snd_fire`, `snd_intro`) | Resolution hits the root copies, so these are not referenced directly |
| `Sounds/Voices/` | 41 typing voices | Only `v_monster.wav` is a default |
| `Sounds/Beats/` | 2 metronome clips | Not wired (`Beat.lua` is a standalone library you must load and drive yourself) |
| `Sounds/Weather/` | 2 rain clips | Not wired |

### Not in use

The remaining ~250 clips (`snd_attack_*`, `snd_hurt_*`, `snd_monster_hurt_*`, `snd_mtt*`, the short `mus_*` stings, …) are referenced by no code and are pure library material.

---

## Music: 9 shipped, 3 in use

| File | Where | Referenced by |
|---|---|---|
| `Start.ogg` | Default overworld BGM (`ow.SetMusic`) | `Scripts/Scenes/Overworld/scene_ow_main_0.lua`, `scene_sol.lua` |
| `End.ogg` | Ending scene | `Scripts/Scenes/scene_end.lua` |
| `mus_gameover.ogg` | GAME OVER | `Scripts/Scenes/scene_gameover.lua` |

Not in use: `mus_house1.ogg`, `mus_mysteriousroom2.ogg`, `mus_options_fall.ogg`, `mus_options_summer.ogg`, `mus_options_winter.ogg`, `Weather/mus_rain.ogg`. Map-specific BGM comes from map data, not from this hard-coded list.

---

## Sprites: 5384 shipped, ~75 in use

| Folder | Used | Total | What is used |
|---|---:|---:|---|
| `UI/` | 22 | 230 | Battle buttons (FIGHT / ACT / ITEM / MERCY), target reticle, slash effect, heart shards, GAME OVER background |
| `Overworld/` | 14 | 1344 | Main character walk frames in four directions, the exclamation prompt |
| `Scene/` | 13 | 1550 | Save point, chest, sign, True Lab monitors, Waterfall star pattern |
| `Characters/` | 7 | 1576 | Loox and Migosp idle / hurt frames (the sample enemies) |
| `Soul Library Sprites/` | 7 | 33 | Default heart, heart break, bullet form, blue platform |
| `Attacks/` | 4 | 589 | Papyrus / Sans bone bullet sprites |
| `Bubble/` | 2 | 2 | Dialog bubble corner and tail |
| `Shapes/` | 1 | 3 | Circle (drawing helper) |
| Root loose files | 5 | 8 | `px.png` (the 1×1 pixel every bar and rectangle is built from), `bullet.png`, `heart.png`, `poseur.png`, `Logo.png` |
| Other folders | 0 | ~700 | `Background/`, `Border/`, `Cutscene/`, `Mascots/` and friends — pure library |

??? note "Full list (75 files)"
    ```text
    Logo.png  bullet.png  heart.png  poseur.png  px.png

    Attacks/Papyrus/spr_bonebottom_0.png      Attacks/Papyrus/spr_bonetop_0.png
    Attacks/Sans/spr_s_bonebul_bottom_0.png   Attacks/Sans/spr_s_bonebul_top_0.png

    Bubble/spr_bubblecorner.png               Bubble/spr_bubbletail.png

    Characters/Ruins/spr_loox_0..2.png        Characters/Ruins/spr_looxhurt_0.png
    Characters/Ruins/spr_migosp_0..1.png      Characters/Ruins/spr_migosphurt_0.png

    Overworld/spr_exc.png                     Overworld/spr_exc_f.png
    Overworld/Frisk/spr_f_maincharad_0..3.png
    Overworld/Frisk/spr_f_maincharal_0..1.png
    Overworld/Frisk/spr_f_maincharar_0..1.png
    Overworld/Frisk/spr_f_maincharau_0..3.png

    Scene/Everywhere/spr_chestbox_0.png       Scene/Everywhere/spr_savepoint_0..1.png
    Scene/Everywhere/spr_sign.png
    Scene/True Lab/spr_monitor_dark_0.png     Scene/True Lab/spr_monitor_lit_0..3.png
    Scene/Waterfall/spr_starpattern_0..3.png

    Shapes/circle.png

    Soul Library Sprites/platform.png         Soul Library Sprites/platformline.png
    Soul Library Sprites/spr_default_heart.png
    Soul Library Sprites/spr_heartbreak_0.png
    Soul Library Sprites/spr_heartbullet_1.png
    Soul Library Sprites/spr_heartgtfo_0..1.png

    UI/Battle Screen/spr_actbt_center_0..1.png     UI/Battle Screen/spr_fightbt_0..1.png
    UI/Battle Screen/spr_itembt_0..1.png           UI/Battle Screen/spr_sparebt_0..1.png
    UI/Battle Screen/spr_target_0.png              UI/Battle Screen/spr_gameoverbg_0.png
    UI/Battle Screen/Player Attack/spr_slice_o_0..5.png
    UI/Battle Screen/Player Attack/spr_targetchoice_0..1.png
    UI/Battle Screen/Shards/spr_heartshards_0..3.png
    ```

!!! tip "Reskin from the Game area"
    Content assets — enemy portraits, backgrounds, bullet sprites — belong in `Game/Resources/Sprites/` and are fetched by path with `Sprites.CreateSprite`. Only override engine files by name when you want to replace the engine's own look (the battle buttons, say).

---

## Libs: native Libraries

| Path | Used by | Notes |
|---|---|---|
| `Resources/Libs/https.dll` | `GamejoltAPI.lua` (`require("https")`) | lua-https, required for GameJolt calls; when missing, networking reports a clear error instead of crashing |
| `Resources/Libs/DiscordRPC/discord-rpc-x64.dll`, `-x86.dll` | `DiscordRPC.lua` | Discord rich presence |
| `Resources/Libs/DiscordGameSDK/x64/`, `x86/` | not loaded | Legacy Game SDK kept as an alternative; comments in the source explain why RPC is used instead |
| `Resources/Libs/Secrets/secrets.dll` | `Utils/Secrets.lua` | Secret store, see [Native Secret Store](./050_secrets.md) |

!!! warning "Shared objects on Android"
    Native libraries **cannot** be loaded out of `game.love` on Android — they have to go into `app/src/main/jniLibs/<abi>/`. Details in [Native Secret Store](./050_secrets.md) and [Export](../100_export/index.md).

---

## Verify it yourself

Every number above comes from a static scan and drifts as the code changes. Two commands reproduce it in your own project:

```bash
# who references a given asset
grep -rn "determination_mono" Scripts Game

# every hard-coded sound, by call count
grep -rn "PlaySound(" Scripts | grep -o '"[^"]*"' | sort | uniq -c | sort -rn
```

`SE.Preload` only walks `Game/Resources/`, never the main `Resources/` — scanning thousands of files there would stall for tens of seconds. To warm up your own assets on a loading screen, see [Asset Preloading](./040_preload.md).
