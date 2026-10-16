---
title: ❕️ Native Secret Store
---

Move secrets such as GameJolt's `private_key` out of `.lua` files and into a compiled `.dll` / `.so`, then read them back through LuaJIT FFI. Someone who unzips `game.love` finds no plain text.

See [Networking → GameJolt](../090_network/000_gamejolt.md) for why the key ends up in the package at all.

---

## Know the boundary first

This layer is **obfuscation, not encryption**. What it stops and what it does not are both quite specific:

| Attack | Stopped? | Why |
|---|---|---|
| Unzip the game and grep for the key | Yes | The key never lives in Lua |
| Run `strings` on the dll / so | Yes | Bytes are XOR-masked and are not a contiguous blob |
| Disassemble the fill function | No | Single assignment statements; a few lines in and it is reconstructed |
| Hook the exported function | No | Anything inside the process can be intercepted |
| `print(Gamejolt.private_key)` | No | The key still ends up in Lua memory |

That last row is the fundamental limit: **as long as the key signs something on the client, it is public**. GameJolt's own stance is the same. The only way to actually keep a private key is to leave it on a server.

What this buys is a cheap shift: from "anyone can find it in two minutes" to "you need to know a disassembler".

!!! warning "Two rules of thumb"
    - **Only hide what genuinely needs hiding.** GameJolt's `game_id` is public information; putting it here adds maintenance cost for nothing.
    - **Do not rely on it for high-value assets.** If a leaked key causes real damage, put a server-side proxy in front instead.

---

## Quick start

Work from `Packager/Secrets/`:

```bash
# 1. Fill in the key (this file is gitignored)
cp secrets.local.example.json secrets.local.json
#    edit it -- only gamejolt_pk is needed

# 2. Build
python build.py
```

Output lands in:

```
Resources/Libs/Secrets/secrets.dll                  Windows
Resources/Libs/Secrets/android/<abi>/libsecrets.so  Android
```

Windows needs a **64-bit** MinGW gcc — LÖVE on Windows is a 64-bit process, and a 32-bit toolchain produces a dll that fails to load *silently*. The script probes for the `MinGW64/bin/gcc.exe` that ships with Dev-Cpp; if it misses, pass `--gcc`.

Android needs the NDK. When it is absent the build **skips** with a notice instead of failing outright, because the Windows artifact is what day-to-day development uses. Once the NDK is installed:

```bash
python build.py --ndk D:/android-sdk/ndk/27.3.13750724
```

---

## Two Platforms, two landing spots

This is where the whole scheme most easily goes wrong: `ffi.load` goes through the **OS loader** (`LoadLibrary` / `dlopen`), not through LÖVE's virtual filesystem. A `"Resources/Libs/..."` path means something to `love.filesystem` and nothing at all to the OS.

| Target | Where the library must sit | Who puts it there |
|---|---|---|
| Source mode on Windows | `Resources/Libs/Secrets/` | `build.py` |
| Fused exe | **Next to the exe** — a fused exe has no source tree on disk | `build_tool.py: copy_secret_dll` |
| Android | `app/src/main/jniLibs/<abi>/` in the love-android template | `build_tool.py: copy_secret_sos`, run before gradlew |
| Web (love.js) | Impossible — no native libraries | Falls back automatically |

!!! danger "A .so inside game.love can never load"
    `game.love` is a zip sitting in `assets`. `dlopen` only searches the app's extracted native library dir, so a `.so` packed into the archive is unreachable. It has to go into `jniLibs/<abi>/` so Gradle ships it to `lib/<abi>/`.

---

## Lua API

```lua
local Secrets = ImportFile("Utils.Secrets")
```

| Call | Returns | Notes |
|---|---|---|
| `Secrets.init()` | `boolean` | Whether the native library loaded. Safe to call repeatedly; `get()` also triggers it lazily |
| `Secrets.available()` | `boolean` | True when values come from the native library |
| `Secrets.source()` | `string` | `"native"` / `"fallback"` / `"none"` |
| `Secrets.status()` | `string` | Diagnostics: the path that hit, or every candidate and why it failed |
| `Secrets.get(slot)` | `string` or `nil` | Fetch by slot index |
| `Secrets.gamejoltPK()` | `string` or `nil` | Shorthand for the GameJolt private key |
| `Secrets.setFallback(slot, value)` | — | Register a plain-text fallback (this is what the web target uses) |

### Three-step fallback

```
native library  ->  Secrets.fallback  ->  nil
```

`Secrets.fallback` is filled from `conf_pure.lua`'s `GamejoltPK` at init, so a dev machine with no build still works. A missing library is a **normal** state, not an error: no build on this machine, or the web target which has no native libraries at all. Callers must treat `nil` as "feature unavailable" and degrade quietly.

!!! warning "Nothing in the engine calls this yet"
    The module ships, but no engine code reads it — not even `Gamejolt.init`. You wire it up yourself at your own entry point:

    ```lua
    local Secrets = ImportFile("Utils.Secrets")
    local pk = Secrets.gamejoltPK()

    if pk then
        Gamejolt.init(Global.GetVariable("GamejoltID"), pk)
    end
    -- else: silently disable trophies / scoreboards. Never error out on the player.
    ```

    The failure path has to be silent. No build on the dev machine, or no native library on web — both are ordinary situations, not exceptions.

---

## Maintenance

**Rotate a key**: edit `secrets.local.json`, re-run `build.py`, repackage. Already published builds break, which is unavoidable.

**Add a key**: append the name to `SLOT_ORDER` in `gen_source.py` and add a matching `Secrets.SLOT_XXX` constant in `Secrets.lua`.

!!! danger "Slot indices are a binary contract — append only"
    Never reorder or remove slots. Doing so makes every already published build read the **wrong** key.

**New machine**: `secrets.local.json` is gitignored and has to be transferred out of band (a password manager, say).

---

## Troubleshooting

Start with `Secrets.status()` — it prints every candidate path and why each one failed.

| Symptom | Cause |
|---|---|
| No gcc found / build fails | Pass `--gcc <path>`, and confirm it is 64-bit MinGW |
| Windows fails to load | dll not beside the exe (fused), or a 32/64-bit mismatch |
| Android fails to load | `.so` not in `jniLibs/<abi>/`, or the ABI does not match the device |
| Loads, but the value is `nil` | That slot is empty in `secrets.local.json` |
| Probe mismatch | Library version disagrees with `PROBE_MAGIC` in `Secrets.lua` — regenerate |

---

## How the obfuscation works

`gen_source.py` XORs every byte with a mask that varies by index, then emits **individual assignment statements** instead of a static array:

```c
static void se_fill_0(unsigned char *p)
{
    p[0] = 0x10;
    p[1] = 0x2E;
    ...
}
```

So no blob exists in `.rodata` and `strings` finds nothing. The build adds `-s` (strip) and `-fvisibility=hidden`, leaving two exported symbols.

The export names are deliberately bland (`se_cfg` / `se_cfg_probe`) — no `secret`, `key` or `gamejolt` — so the library does not announce what it is at a glance.
