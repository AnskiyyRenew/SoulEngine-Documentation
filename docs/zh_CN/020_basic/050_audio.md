---
title: 音频
---

引擎中，音频被分为两类：

一是音乐，主要特征为长（20秒以上）， `.ogg` 格式；<br>
二是音效，主要特征为短， `.wav` 格式居多，但也不乏 `.ogg` 格式。

分开的原因是：这两种类型分别有不同的加载方式。

音频库位置： `Scripts/Libraries/Audio.lua`

音效主目录为 `Resources/Sounds/` ，音乐主目录为 `Resources/Music/` 。<br>
如果想**覆盖**引擎自带的音频，把同名文件放到 `Game/Resources/Sounds/` 或 `Game/Resources/Music/` 即可，Game 区优先，主目录兜底。这一步由 `Audio.ResolvePath` 自动完成，调用时写文件名即可。

音效与音乐都会经过 `Audio.ResolvePath` 解析，下面的写法行为一致（Game 区一律先查）：

| 写法 | 实际查找顺序 |
| --- | --- |
| `Audio.PlaySound("snd_slam.wav")` | `Game/Resources/Sounds/snd_slam.wav` → `Resources/Sounds/snd_slam.wav` |
| `Audio.PlaySound("Blaster/snd_intro.wav")` | `Game/Resources/Sounds/Blaster/snd_intro.wav` → 主目录同名文件 |
| `Audio.PlaySound("/Voices/uifont.wav")` | `Game/Resources/Sounds/Voices/uifont.wav` → `Resources/Sounds/Voices/uifont.wav` |

以 `/` 开头表示相对于音频主目录（打字机语音用的就是这种写法），因此 Game 侧对语音的覆盖路径是 `Game/Resources/Sounds/Voices/`。<br>
已经写全 `Resources/Sounds/` 或 `Game/Resources/Sounds/` 的路径也照样识别，不会重复拼接前缀。

---

## 音频的播放

**关于加载方式：**

音效使用 `static` 加载模式，一次性载入完整音频数据。<br>
音乐使用 `stream` 加载模式，边加载边播放。

### 播放音效

使用 `Audio.PlaySound(path, volume, loop)` 来播放一个音效，路径从 `Resources/Sounds/` 文件夹开始算。

- `path` 音频路径，需要带后缀。
- `volume` 播放时的音量大小，会自动乘以引擎设置的音量大小，具体可以看同目录下 [初始化配置](./000_conf.md) 中的 `游戏初始化` 栏目。
- `loop` 是否循环，音效通常不循环。

也可只填写第一个参数，即音频路径：
!!! example "播放音效"

    ```lua
    Audio.PlaySound("snd_slam.wav")
    ```

### 播放音乐

使用 `Audio.PlayMusic(path, volume, loop)` 来播放一段音乐，路径从 `Resources/Music/` 文件夹开始算。

- `path` 音频路径，需要带后缀。
- `volume` 播放时的音量大小，会自动乘以引擎设置的音量大小，具体可以看同目录下 [初始化配置](./000_conf.md) 中的 `游戏初始化` 栏目。
- `loop` 是否循环，音乐通常循环播放。

!!! example "播放音乐"

    ```lua
    Audio.PlayMusic("mus_gameover.ogg")
    ```

### 查询音乐

使用 `Audio.FindMusic(path)` 查询某首音乐是否正在播放：

```lua
if (Audio.FindMusic("mus_gameover.ogg")) then
    -- 正在播
end
```

该函数使用的解析顺序与 `Audio.PlayMusic` **完全一致**（即上表所列），因此 Game 区的覆盖版本同样会被识别。

---

## 编辑音频

音频在创建时除音频文件本身外，还附带一个 `控制器` ，可通过控制器操控音频，也可直接操控音频文件。

### 操纵音频

以下方法属于 `LOVE2D` ，此处列出常用方法，完整说明见 [与LOVE开发 → 音频系统](../060_with_love/010_audio.md) 。

以下方法的操作对象为 `mus` ：
```lua
local mus = Audio.PlayMusic("mus_gameover.ogg")
```

??? example "方法"
    - `mus:pause()` 暂停音频。
    - `mus:play()` 播放音频；音频处于暂停状态时，从暂停位置继续播放。
    - `mus:resume()` 已移除，改用 `play()` 函数。
    - `mus:stop()` 停止播放，并自动将播放位置调整至开头。
    - `mus:rewind()` 将播放位置重置到开头。
    - `mus:setVolume(v) / mus:getVolume()` 设置/获取音量。
    - `mus:setPitch(p) / mus:getPitch()` 设置/获取音调。
    - `mus:setLooping(bool) / mus:isLooping()` 设置/查询是否循环。
    - `mus:seek(offset, unit) / mus:tell(unit)` 设置/获取当前播放位置。（按秒或样本计）
    - `mus:isPlaying()` 音频是否正在播放。
    - `mus:isPaused()` 音频是否处于暂停状态。
    - `mus:isStopped()` 音频是否处于停止状态。
    - `mus:getDuration()` 获取音频总时长。（秒）
    - `mus:getType()` 返回音频加载类型（ `static` 或 `stream` ）。
    - `mus:clone()` 克隆一个副本使用，并且新克隆的音频处于 `stop` 状态。

### 操纵控制器

以下方法的操作对象为 `ins` ：
```lua
local mus, ins = Audio.PlayMusic("mus_gameover.ogg")
```

??? example "ins方法"
    - `ins:VolumeTransition(startVolume, targetVolume, duration)` 自动音频渐变，执行一次即可。
        - `startVolume` 起始音量大小 `(0 ~ 1)` 。
        - `targetVolume` 目标音量大小 `(0 ~ 1)` 。
        - `duration` 执行时长（秒）。
    - `ins:PitchTransition(startPitch, targetPitch, duration)` 自动音频渐变，执行一次即可。
        - `startPitch` 起始音调大小。
        - `targetPitch` 目标音调大小。
        - `duration` 执行时长（秒）。
    - `ins:FadeIn(duration, targetVolume)` 音量淡入
        - `duration` 执行时长（秒）。
        - `targetVolume` 目标音量大小。
    - `ins:FadeOut(duration, targetVolume)` 音量淡出
        - `duration` 执行时长（秒）。
        - `targetVolume` 目标音量大小。
    - `ins:Pause()` 和 `mus:pause()` 一样。
    - `ins:Resume()` 和 `mus:play()` 相似。
    - `ins:Stop()` 和 `mus:stop()` 一样。
    - `ins:SetLoopingPoint(introEndTime, outroStartTime)` 设置两个循环点，音频将在这中间循环。
    - `ins:FollowLoop()` Intro结束后跳转进入循环段。
    - `ins:FollowOutro()` 本次循环后跳出循环段进入 `Outro` 。

---