---
title: 音频系统
---

音频也一样： `SE.audio` 就是 `love.audio` 的直接转发（见 [本专题首页](./index.md) ）。

```lua
SE.audio.setVolume(0.5)                                     -- 全局音量
local src = SE.audio.newSource("Resources/Music/a.ogg", "stream")
src:play()
```

!!! warning "播放音频应使用引擎的 Audio 库"
    `Scripts/Libraries/Audio.lua` 是引擎提供的入口，其**底层调用的即为 `SE.audio`** ：

    ```lua
    function audio.PlaySound(sound, volume, loop)
        local source = SE.audio.newSource(resolved_path, "static")
        source:setVolume(volume or Global.GetVariable("Volume").Master * ...)
        ...
    ```

    自行调用 `SE.audio.newSource` 会绕过 Game 区覆盖、路径解析、音量跟随和生命周期管理，无特殊需求时不采用该方式。

## 用哪个

| 想做的事 | 用什么 |
| --- | --- |
| 播一个音效 | `Audio.PlaySound(path, volume, loop)` |
| 播一首音乐 | `Audio.PlayMusic(path, volume, loop)` |
| 某首音乐在不在播 | `Audio.FindMusic(path)` |
| 暂停 / 继续 / 停止某个音频 | `Audio.Pause(inst)` / `Audio.Resume(inst)` / `Audio.Stop(inst)` |
| 音量、音调渐变，淡入淡出 | 控制器 `ins:FadeIn` / `FadeOut` / `VolumeTransition` / `PitchTransition` |
| 循环段（intro → loop → outro） | `ins:SetLoopingPoint` / `FollowLoop` / `FollowOutro` |
| 一次性停掉所有音频 | `Audio.Clear()` |
| 上面都没有的底层操作 | `SE.audio.*` |

音频文件放哪、Game 区怎么覆盖、控制器有哪些方法，见 [音频](../020_basic/050_audio.md) 。下面只讲 `SE.audio` 这一层。

## 函数一览

### 创建

| 函数 | 作用 |
| --- | --- |
| `newSource` | 建一个音频源。第二个参数是加载类型： `"static"` 整个读进内存（适合短音效）、 `"stream"` 边读边播（适合音乐） |
| `newQueueableSource` | 建一个可自行向队列写入数据块的音频源，用于实时合成或流式播放 |

引擎的 `Audio` 库就是这么分的：音效用 `"static"` 、音乐用 `"stream"` 。

### 全局播放控制

| 函数 | 作用 |
| --- | --- |
| `play` | 播放，可以一次传多个音频源 |
| `pause` | 暂停 |
| `stop` | 停止并回到开头 |
| `setVolume` | 设**全局**音量乘数，作用于所有正在播的音频 |
| `getVolume` | 读全局音量乘数 |
| `setMixWithSystem` | 是否和系统其它声音混在一起播 |

!!! danger "游戏音量设置不使用 SE.audio.setVolume"
    该函数是 LÖVE 层的全局乘数，会覆盖引擎的音量体系。引擎的音量是一个全局变量：

    ```lua
    Global.GetVariable("Volume")   -- { Master = 1, Music = 1, Sounds = 1 }
    ```

    `Audio` 库每次播放时都会读取该变量并自动相乘（音效乘 `Master * Sounds` 、音乐乘 `Master * Music` ），因此调整音量时修改该变量（或使用游戏内的设置界面），不修改 `SE.audio` 。

### 3D 定位

| 函数 | 作用 |
| --- | --- |
| `setPosition` / `getPosition` | 听者的位置 |
| `setOrientation` / `getOrientation` | 听者的朝向 |
| `setVelocity` / `getVelocity` | 听者的速度，多普勒效果用 |
| `setDistanceModel` / `getDistanceModel` | 距离衰减模型 |
| `setDopplerScale` / `getDopplerScale` | 多普勒强度 |

该组函数用于 3D 音效（配合 `Source:setPosition` 等方法），2D 像素游戏通常不使用。

### 效果器

| 函数 | 作用 |
| --- | --- |
| `setEffect` | 挂一个场景效果器（混响、回声等） |
| `getEffect` | 取当前挂着的效果器 |
| `getActiveEffects` | 当前生效的效果器列表 |
| `getMaxSceneEffects` | 场景最多能挂几个效果器 |
| `getMaxSourceEffects` | 单个音频源最多能挂几个效果器 |
| `isEffectsSupported` | 当前设备支不支持效果器 |

!!! tip "使用效果器前先检测支持情况"
    效果器在部分平台上不生效。使用前先通过 `if (SE.audio.isEffectsSupported()) then` 判断，不直接挂载。

### 录音与统计

| 函数 | 作用 |
| --- | --- |
| `getRecordingDevices` | 拿到录音设备列表 |
| `getActiveSourceCount` | 当前正在播的音频源数量 |

## 常见问题

!!! warning "newSource 未指定加载类型时，大文件会被整体读入内存"
    第二个参数省略时 LÖVE 会按文件大小推断，推断错误会导致数十 MB 的音乐被一次性读入内存（移动端容易出现内存不足）。**显式传入 `"static"` / `"stream"` 。**

!!! warning "自行创建的音频源需自行管理"
    引擎的 `Audio` 库会登记它创建的所有音频源，统一执行渐变更新和清理；自行调用 `SE.audio.newSource` 创建的对象**不在该登记列表内**，停止与释放的时机由创建方负责。

---

## 相关

- [本专题首页](./index.md)：`SE` 这一层的作用、引擎自制函数
- [音频](../020_basic/050_audio.md)：引擎的 `Audio` 库、Game 区覆盖、控制器方法
- [图像绘制](./000_graphics.md)：`SE.graphics` 与全部绘制函数
