---
title: Audio System
---

Audio is the same: `SE.audio` is a direct forward of `love.audio` (see [this topic's home page](./index.md)).

```lua
SE.audio.setVolume(0.5)                                     -- global volume
local src = SE.audio.newSource("Resources/Music/a.ogg", "stream")
src:play()
```

!!! warning "For daily audio playback, go through the engine's Audio library"
    `Scripts/Libraries/Audio.lua` is the engine's entry point for you, and it **uses `SE.audio` at the bottom layer**:

    ```lua
    function audio.PlaySound(sound, volume, loop)
        local source = SE.audio.newSource(resolved_path, "static")
        source:setVolume(volume or Global.GetVariable("Volume").Master * ...)
        ...
    ```

    Creating `SE.audio.newSource` yourself bypasses its Game-area override, path resolution, volume-follow, and lifecycle management; don't do it unless necessary.

## Which to use

| What to do | Use what |
| --- | --- |
| Play a sound effect | `Audio.PlaySound(path, volume, loop)` |
| Play a music track | `Audio.PlayMusic(path, volume, loop)` |
| Whether a music is playing | `Audio.FindMusic(path)` |
| Pause / resume / stop an audio | `Audio.Pause(inst)` / `Audio.Resume(inst)` / `Audio.Stop(inst)` |
| Volume, pitch fade, fade in/out | Controller `ins:FadeIn` / `FadeOut` / `VolumeTransition` / `PitchTransition` |
| Loop segment (intro → loop → outro) | `ins:SetLoopingPoint` / `FollowLoop` / `FollowOutro` |
| Stop all audio at once | `Audio.Clear()` |
| Low-level operations none of the above cover | `SE.audio.*` |

Where audio files go, how the Game area overrides, what methods the controller has — see [Audio](../020_basic/050_audio.md). Below only covers the `SE.audio` layer.

## Function overview

### Creation

| Function | Effect |
| --- | --- |
| `newSource` | Build an audio source. Second argument is the load type: `"static"` reads the whole thing into memory (good for short SFX), `"stream"` reads while playing (good for music) |
| `newQueueableSource` | Build an audio source you can push data chunks into a queue yourself, for real-time synthesis or streaming playback |

The engine's `Audio` library splits it this way: SFX use `"static"`, music uses `"stream"`.

### Global playback control

| Function | Effect |
| --- | --- |
| `play` | Play; can take multiple audio sources at once |
| `pause` | Pause |
| `stop` | Stop and return to the beginning |
| `setVolume` | Set the **global** volume multiplier, applied to all playing audio |
| `getVolume` | Read the global volume multiplier |
| `setMixWithSystem` | Whether to mix with other system sounds when playing |

!!! danger "Don't use SE.audio.setVolume for game volume settings"
    It is the LÖVE-level global multiplier, which overrides the engine's volume system. The engine's volume is a global variable:

    ```lua
    Global.GetVariable("Volume")   -- { Master = 1, Music = 1, Sounds = 1 }
    ```

    The `Audio` library reads it every time it plays and auto-multiplies (SFX × `Master * Sounds`, music × `Master * Music`), so to change volume, change this variable (or use the in-game settings), don't touch `SE.audio`.

### 3D positioning

| Function | Effect |
| --- | --- |
| `setPosition` / `getPosition` | Listener position |
| `setOrientation` / `getOrientation` | Listener orientation |
| `setVelocity` / `getVelocity` | Listener velocity, for Doppler effect |
| `setDistanceModel` / `getDistanceModel` | Distance attenuation model |
| `setDopplerScale` / `getDopplerScale` | Doppler strength |

This group is for 3D sound (along with `Source:setPosition` etc.), 2D pixel games generally don't need it; just know it exists.

### Effects

| Function | Effect |
| --- | --- |
| `setEffect` | Attach a scene effect (reverb, echo …) |
| `getEffect` | Get the currently attached effect |
| `getActiveEffects` | List of currently active effects |
| `getMaxSceneEffects` | Max scene effects attachable |
| `getMaxSourceEffects` | Max effects attachable to a single audio source |
| `isEffectsSupported` | Whether the current device supports effects |

!!! tip "Check before use"
    Effects don't take effect on some platforms. When using them, first check `if (SE.audio.isEffectsSupported()) then`, don't attach directly.

### Recording and stats

| Function | Effect |
| --- | --- |
| `getRecordingDevices` | Get the list of recording devices |
| `getActiveSourceCount` | Number of audio sources currently playing |

## Common pitfalls

!!! warning "Omitting the load type in newSource, large files go entirely into memory"
    When the second argument is omitted, LÖVE guesses by file size; guess wrong and tens of MB of music gets read into memory at once (easily crashes on mobile). **Get into the habit of explicitly writing `"static"` / `"stream"`.**

!!! warning "Audio sources you create yourself you must manage yourself"
    The engine's `Audio` library registers all audio sources it creates, uniformly doing fade updates and cleanup; the objects you `SE.audio.newSource` yourself are **not on its list** — you are responsible for when to stop and when to release them.

---

## Related

- [This topic's home page](./index.md) — what the `SE` layer is, engine-built functions
- [Audio](../020_basic/050_audio.md) — the engine's `Audio` library, Game-area override, controller methods
- [Graphics Drawing](./000_graphics.md) — `SE.graphics` and all drawing functions
