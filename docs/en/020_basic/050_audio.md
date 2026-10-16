---
title: Audio
---

In the engine, audio is divided into two categories:

One is music, mainly characterized by being long (over 20 seconds), `.ogg` format;<br>
The other is sound effects, mainly characterized by being short, mostly `.wav` format, but also no lack of `.ogg` format.

The reason for separating them is: these two types have different loading methods.

Audio library location: `Scripts/Libraries/Audio.lua`

The sound effect main directory is `Resources/Sounds/`, and the music main directory is `Resources/Music/`.<br>
If you want to **override** engine-built-in audio, put the same-named file into `Game/Resources/Sounds/` or `Game/Resources/Music/`; the Game region takes priority, with the main directory as fallback. This step is done automatically by `Audio.ResolvePath`; just write the file name when calling.

Both sound effects and music go through `Audio.ResolvePath`; the writings below behave identically (Game region always checked first):

| Writing | Actual lookup order |
| --- | --- |
| `Audio.PlaySound("snd_slam.wav")` | `Game/Resources/Sounds/snd_slam.wav` → `Resources/Sounds/snd_slam.wav` |
| `Audio.PlaySound("Blaster/snd_intro.wav")` | `Game/Resources/Sounds/Blaster/snd_intro.wav` → same-named file in main directory |
| `Audio.PlaySound("/Voices/uifont.wav")` | `Game/Resources/Sounds/Voices/uifont.wav` → `Resources/Sounds/Voices/uifont.wav` |

Starting with `/` means "relative to the audio main directory" (the typer voice uses this writing), so the Game-side override path for voices is `Game/Resources/Sounds/Voices/`.<br>
Paths that already write out `Resources/Sounds/` or `Game/Resources/Sounds/` are also recognized, without duplicating the prefix.

---

## Playing Audio

**About loading methods:**

Sound effects use the `static` loading mode; since sound effect files are generally small, loading them all at once saves a lot of overhead.<br>
In contrast, music uses the `stream` loading mode; music files are usually loaded while playing.

### Playing a Sound Effect

Use `Audio.PlaySound(path, volume, loop)` to play a sound effect; the path starts from the `Resources/Sounds/` folder.

- `path` Audio path, needs the extension.
- `volume` The volume when playing, automatically multiplied by the engine's set volume; see the `Game Initialization` section in [Initialization Configuration](./000_conf.md) in the same directory for details.
- `loop` Whether to loop; normally sound effects are not looped.

Normally, we can also just fill in the first parameter, i.e. what audio to play:
!!! example "Playing a sound effect"

    ```lua
    Audio.PlaySound("snd_slam.wav")
    ```

### Playing Music

Use `Audio.PlayMusic(path, volume, loop)` to play a sound effect; the path starts from the `Resources/Music/` folder.

- `path` Audio path, needs the extension.
- `volume` The volume when playing, automatically multiplied by the engine's set volume; see the `Game Initialization` section in [Initialization Configuration](./000_conf.md) in the same directory for details.
- `loop` Whether to loop; normally music is looped.

!!! example "Playing music"

    ```lua
    Audio.PlayMusic("mus_gameover.ogg")
    ```

### Querying Music

To know whether a certain piece of music is playing now, use `Audio.FindMusic(path)`:

```lua
if (Audio.FindMusic("mus_gameover.ogg")) then
    -- playing
end
```

Internally it follows the **exact same** resolution order as `Audio.PlayMusic` (i.e. the table above), so the Game-region-overridden version is also recognized.

---

## Editing Audio

When audio is created, it is not just the audio file itself, but also comes with a `controller`; we can manipulate the audio through the controller, or directly manipulate the audio file.

### Manipulating Audio

For audio operations, this part belongs to `LOVE2D`, so only a few of the most-used will be explained; for the rest see [With LOVE Development → Audio System](../060_with_love/010_audio.md).

The object we need to manipulate now is `mus`, code as follows:
```lua
local mus = Audio.PlayMusic("mus_gameover.ogg")
```

??? example "Methods"
    - `mus:pause()` Pauses the audio.
    - `mus:play()` Plays the audio; if the audio was paused it actually resumes from where it was paused.
    - `mus:resume()` Already gone; still recommended to use the `play()` function.
    - `mus:stop()` Stops playback and automatically adjusts the position to the beginning.
    - `mus:rewind()` Resets the playback position to the beginning.
    - `mus:setVolume(v) / mus:getVolume()` Set / get volume.
    - `mus:setPitch(p) / mus:getPitch()` Set / get pitch.
    - `mus:setLooping(bool) / mus:isLooping()` Set / query whether to loop.
    - `mus:seek(offset, unit) / mus:tell(unit)` Set / get current playback position. (In seconds or samples)
    - `mus:isPlaying()` Whether the audio is playing.
    - `mus:isPaused()` Whether the audio is in a paused state.
    - `mus:isStopped()` Whether the audio is in a stopped state.
    - `mus:getDuration()` Gets the total audio duration. (Seconds)
    - `mus:getType()` Returns the audio loading type (`static` or `stream`).
    - `mus:clone()` Clones a copy to use, and the newly cloned audio is in `stop` state.

### Manipulating the Controller

The object we need to manipulate now is `ins`, code as follows:
```lua
local mus, ins = Audio.PlayMusic("mus_gameover.ogg")
```

??? example "ins methods"
    - `ins:VolumeTransition(startVolume, targetVolume, duration)` Automatic audio fade, just execute once.
        - `startVolume` Starting volume `(0 ~ 1)`.
        - `targetVolume` Target volume `(0 ~ 1)`.
        - `duration` Execution duration (seconds).
    - `ins:PitchTransition(startPitch, targetPitch, duration)` Automatic audio fade, just execute once.
        - `startPitch` Starting pitch size.
        - `targetPitch` Target pitch size.
        - `duration` Execution duration (seconds).
    - `ins:FadeIn(duration, targetVolume)` Volume fade in.
        - `duration` Execution duration (seconds).
        - `targetVolume` Target volume size.
    - `ins:FadeOut(duration, targetVolume)` Volume fade out.
        - `duration` Execution duration (seconds).
        - `targetVolume` Target volume size.
    - `ins:Pause()` Same as `mus:pause()`.
    - `ins:Resume()` Similar to `mus:play()`.
    - `ins:Stop()` Same as `mus:stop()`.
    - `ins:SetLoopingPoint(introEndTime, outroStartTime)` Sets two loop points; the audio loops between them.
    - `ins:FollowLoop()` After Intro ends, jumps into the loop section.
    - `ins:FollowOutro()` After this loop, jumps out of the loop section into `Outro`.
