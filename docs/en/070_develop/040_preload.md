---
title: ❕️ Asset Preloading
---

Decode an entire directory of assets into the cache in advance, so that the first use of `Sprites.CreateSprite` and `Audio.PlaySound` / `PlayMusic` afterwards **no longer stutters**.

Once the resources under `Game/Resources/` grow, entering a scene often "hitches" for a moment — because each image and each piece of audio is decoded only the first time it is referenced. `SE.Preload` lets you decode them all at the right moment (e.g. during a scene transition, or in a loading screen), so subsequent calls hit the cache directly.

Preloading only walks the **Game area** (`Game/Resources/`), and won't touch the main `Resources/`. The main resource directory often has thousands of files; running through it all could freeze for tens of seconds, so the engine deliberately leaves it alone.

---

## SE.Preload

```lua
SE.Preload("Sprites/Test")          -- All images under Game/Resources/Sprites/Test/
SE.Preload("Music", "Sounds/ui")    -- Preload multiple directories at once
SE.Preload("Sprites/")              -- Trailing slash optional
```

The parameter is a variable number of path strings; each path is normalized to a Game-area directory and then traversed **recursively** (including all subfolders).

| Path syntax | Directory actually traversed |
|---|---|
| `"Music"` | The whole `Game/Resources/Music/` tree |
| `"Sprites/Test"` | The whole `Game/Resources/Sprites/Test/` tree |
| `"Sounds/ui/voice"` | The whole `Game/Resources/Sounds/ui/voice/` tree (multi-level sub-paths also work) |
| `"Game/Resources/Music"` | Equivalent to `"Music"` |

The return value is **the actual number of files handed to the loader**, which you can use to show progress in a loading screen.

### Type names in the path

The first segment of the path must be a resource type the engine knows:

| Type name | Loaded into | Corresponding basics page |
|---|---|---|
| `Sprites` | Sprite cache (`sprites.cache`) | [Sprites](../020_basic/020_sprites.md) |
| `Sounds` | Sound cache (`Audio.cache`, static) | [Audio](../020_basic/050_audio.md) |
| `Music` | Music cache (`Audio.cache`, stream) | [Audio](../020_basic/050_audio.md) |
| `Fonts` | Font cache | Fonts |

A non-matching type name prints a WARNING and skips that path, without crashing.

### Extension dispatch

The loader is chosen by file extension, and when it disagrees with the folder type, **the extension wins** (a `.wav` placed under `Sprites/` is still treated as audio):

- Images: `png` / `jpg` / `jpeg` / `bmp` / `tga` / `hdr` / `dds`
- Audio: `wav` / `ogg` / `mp3` / `flac` / `aiff` / `it` / `xm` / `mod` / `s3m`
- Fonts: `ttf` / `ttc` / `otf` / `fnt`

Other suffixes (`README.md`, `.txt`, etc.) are silently skipped.

---

## SE.PreloadAll

```lua
SE.PreloadAll()
```

Run through the entire `Game/Resources/` once. Returns the number of files loaded.

!!! warning "Use PreloadAll with care"
    This traverses all resources in the Game area; if your Game area also has hundreds of files, calling it once before entering the game still causes noticeable stutter. The recommended approach is to `SE.Preload` just those sub-directories per scene, on demand.

---

## When to call

Preloading itself is a one-time synchronous operation (traverse + decode), best placed at **moments with no rendering pressure**:

- A loading screen (if you have a custom loading scene).
- Inside a scene's init callback, **before creating the first batch of sprites / playing the first batch of audio**.
- A transition frame before switching scenes.

Don't call it every frame, and don't stuff it into `update` — the whole point of preloading is "once ahead of time"; repeated calls only refresh the timestamp and won't redo the decode, but they still traverse the directory for nothing.

---

## Relationship with CreateSprite / PlaySound

After preloading, the caller is **completely unaware**:

- `Sprites.CreateSprite("foo.png")` still looks up `sprites.cache` by path as usual — hits it and uses it directly, otherwise decodes; preloading just makes the "hit" happen earlier.
- `Audio.PlaySound("foo.wav")` / `PlayMusic` **clones** a template Source from `Audio.cache` to use; the clone shares the underlying decoded buffer (sound) or file handle (music), so it doesn't re-decode on every play.

In other words: **after calling `SE.Preload`, write your game logic's `CreateSprite` / `PlaySound` exactly as before** — cache reuse is automatic.

---

## Design notes

- **Game area only**: The main `Resources/` is deliberately left alone. Put the resources you want to preload under `Game/Resources/Sprites/<subdir>/` and the like, then use `SE.Preload("Sprites/<subdir>")` to precisely warm them up.
- **Idempotent**: Re-preloading the same path won't re-decode, only refreshes the cache timestamp. So repeatedly entering/leaving a scene is safe.
- **Doesn't create instances**: `Sprites.PreloadFile` only stuffs the image and ImageData into the cache, it doesn't actually draw to the screen. Whether to display it, and where, is still decided by your later `CreateSprite`.
- **LRU still applies**: Images loaded by preloading are still subject to LRU reclamation via `OPT_LRU_SPRITES`; those not referenced by any sprite for a long time get cleared — following the same lifecycle as normally loaded images.
